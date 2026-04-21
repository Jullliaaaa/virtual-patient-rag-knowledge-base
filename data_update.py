"""
data_update.py
資料收集、清理、Chunking、Embedding、寫入 pgvector
支援 --rebuild 全量重建 / 預設增量更新
"""

import argparse
import hashlib
import json
import logging
import os
import re
import shutil
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── 路徑常數 ──────────────────────────────────────────────
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
HASH_STORE = Path("data/.file_hashes.json")

# ── Chunking 設定 ─────────────────────────────────────────
CHUNK_SIZE = 400        # 每個 chunk 的字元數（中英混合約 200 個中文字）
CHUNK_OVERLAP = 80      # 相鄰 chunk 的重疊字元數（chunk_size 的 20%，依 W6 建議）


# ═════════════════════════════════════════════════════════
# 1. 工具函式
# ═════════════════════════════════════════════════════════

def compute_file_hash(path: Path) -> str:
    """計算檔案 MD5 hash，用於增量更新判斷"""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_hash_store() -> dict:
    if HASH_STORE.exists():
        return json.loads(HASH_STORE.read_text(encoding="utf-8"))
    return {}


def save_hash_store(store: dict):
    HASH_STORE.parent.mkdir(parents=True, exist_ok=True)
    HASH_STORE.write_text(json.dumps(store, indent=2), encoding="utf-8")


# ═════════════════════════════════════════════════════════
# 2. 文字清理
# ═════════════════════════════════════════════════════════

def clean_text(text: str) -> str:
    """移除 HTML 標籤、多餘空白、頁首頁尾雜訊"""
    text = re.sub(r"<[^>]+>", " ", text)           # 移除 HTML tags
    text = re.sub(r"\s{3,}", "\n\n", text)          # 連續空白壓縮
    text = re.sub(r"[ \t]+", " ", text)             # 行內多餘空格
    text = re.sub(r"\n{3,}", "\n\n", text)          # 連續空行壓縮
    text = text.strip()
    return text


def load_raw_file(path: Path) -> str:
    """讀取 .txt / .md / .pdf 並回傳純文字"""
    suffix = path.suffix.lower()
    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8", errors="ignore")
    elif suffix == ".pdf":
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text_parts.append(t)
            return "\n\n".join(text_parts)
        except ImportError:
            logger.warning("pdfplumber 未安裝，嘗試 PyPDF2")
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(str(path))
                return "\n\n".join(
                    page.extract_text() or "" for page in reader.pages
                )
            except ImportError:
                logger.error("請安裝 pdfplumber 或 PyPDF2 以支援 PDF 讀取")
                return ""
    else:
        logger.warning(f"不支援的檔案格式：{path.suffix}，跳過")
        return ""


# ═════════════════════════════════════════════════════════
# 3. Chunking
# ═════════════════════════════════════════════════════════

def chunk_text(text: str, source: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """
    固定長度 + overlap 切分策略
    回傳 list of {"text": str, "source": str, "chunk_index": int}
    """
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append({
                "text": chunk,
                "source": source,
                "chunk_index": idx,
            })
            idx += 1
        start += chunk_size - overlap
    return chunks


# ═════════════════════════════════════════════════════════
# 4. Embedding
# ═════════════════════════════════════════════════════════

def get_embedding_model():
    """載入 sentence-transformers 本地模型（完全免費）"""
    from sentence_transformers import SentenceTransformer
    model_name = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
    logger.info(f"載入 Embedding 模型：{model_name}")
    return SentenceTransformer(model_name)


def embed_chunks(model, chunks: list[dict]) -> list[dict]:
    """為每個 chunk 產生向量"""
    texts = [c["text"] for c in chunks]
    vectors = model.encode(texts, show_progress_bar=True, batch_size=32)
    for chunk, vec in zip(chunks, vectors):
        chunk["embedding"] = vec.tolist()
    return chunks


# ═════════════════════════════════════════════════════════
# 5. pgvector 操作
# ═════════════════════════════════════════════════════════

def get_db_connection():
    import psycopg2
    conn_str = os.getenv(
        "PGVECTOR_CONNECTION_STRING",
        "postgresql://raguser:ragpassword@localhost:5432/ragdb"
    )
    return psycopg2.connect(conn_str)


def setup_db(conn):
    """建立 pgvector extension 與資料表"""
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id          SERIAL PRIMARY KEY,
                source      TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content     TEXT NOT NULL,
                embedding   vector(384),
                UNIQUE (source, chunk_index)
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_embedding ON documents USING ivfflat (embedding vector_cosine_ops);")
    conn.commit()
    logger.info("pgvector 資料表已就緒")


def clear_db(conn):
    """清空所有向量資料（--rebuild 時使用）"""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM documents;")
    conn.commit()
    logger.info("已清空 documents 資料表")


def upsert_chunks(conn, chunks: list[dict]):
    """將 chunks 寫入 pgvector（有則更新，無則插入）"""
    from psycopg2.extras import execute_values
    rows = [
        (c["source"], c["chunk_index"], c["text"], c["embedding"])
        for c in chunks
    ]
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO documents (source, chunk_index, content, embedding)
            VALUES %s
            ON CONFLICT (source, chunk_index)
            DO UPDATE SET content = EXCLUDED.content, embedding = EXCLUDED.embedding;
            """,
            rows,
            template="(%s, %s, %s, %s::vector)"
        )
    conn.commit()
    logger.info(f"已寫入 {len(rows)} 個 chunks")


def delete_chunks_by_source(conn, source: str):
    """刪除特定來源的舊 chunks（增量更新時使用）"""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM documents WHERE source = %s;", (source,))
    conn.commit()


# ═════════════════════════════════════════════════════════
# 6. 主流程
# ═════════════════════════════════════════════════════════

def process_file(raw_path: Path, model, conn, rebuild: bool, hash_store: dict) -> bool:
    """
    處理單一原始檔案，回傳是否有實際更新
    """
    file_hash = compute_file_hash(raw_path)
    source = raw_path.name

    # 增量更新：hash 未變則跳過
    if not rebuild and hash_store.get(source) == file_hash:
        logger.info(f"[跳過] {source}（未變動）")
        return False

    logger.info(f"[處理] {source}")

    # 讀取 & 清理
    raw_text = load_raw_file(raw_path)
    if not raw_text.strip():
        logger.warning(f"  {source} 無法提取文字，跳過")
        return False
    cleaned = clean_text(raw_text)

    # 儲存 processed
    processed_path = PROCESSED_DIR / (raw_path.stem + ".txt")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    processed_path.write_text(cleaned, encoding="utf-8")

    # Chunking
    chunks = chunk_text(cleaned, source)
    logger.info(f"  → {len(chunks)} chunks")

    # Embedding
    chunks = embed_chunks(model, chunks)

    # 寫入 DB（先刪舊資料再寫入，保證冪等）
    delete_chunks_by_source(conn, source)
    upsert_chunks(conn, chunks)

    # 更新 hash
    hash_store[source] = file_hash
    return True


def main():
    parser = argparse.ArgumentParser(
        description="RAG 資料更新腳本：將 data/raw/ 的文件索引至 pgvector"
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="清空並全量重建索引（忽略 hash 快取）"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/raw",
        help="原始資料目錄（預設：data/raw）"
    )
    args = parser.parse_args()

    raw_dir = Path(args.data_dir)
    if not raw_dir.exists():
        logger.error(f"資料目錄不存在：{raw_dir}")
        return

    # 取得所有支援的檔案
    supported = (".txt", ".md", ".pdf")
    files = [f for f in raw_dir.iterdir() if f.suffix.lower() in supported]
    if not files:
        logger.warning(f"{raw_dir} 中沒有支援的檔案（.txt / .md / .pdf）")
        return

    logger.info(f"找到 {len(files)} 個檔案")

    # 連線 DB
    conn = get_db_connection()
    setup_db(conn)

    if args.rebuild:
        logger.info("=== REBUILD 模式：清空所有資料 ===")
        clear_db(conn)
        # 清空 processed 目錄
        if PROCESSED_DIR.exists():
            shutil.rmtree(PROCESSED_DIR)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        hash_store = {}
    else:
        hash_store = load_hash_store()

    # 載入 Embedding 模型
    model = get_embedding_model()

    # 逐檔處理
    updated = 0
    current_sources = set()
    for f in sorted(files):
        current_sources.add(f.name)
        if process_file(f, model, conn, args.rebuild, hash_store):
            updated += 1

    # ── 冪等性保證：刪除 DB 中已不存在於 data/raw/ 的資料 ──
    if not args.rebuild:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT source FROM documents;")
            db_sources = {row[0] for row in cur.fetchall()}
        orphans = db_sources - current_sources
        if orphans:
            logger.info(f"清除已刪除的檔案資料：{orphans}")
            for orphan in orphans:
                delete_chunks_by_source(conn, orphan)
                hash_store.pop(orphan, None)
                # 同步清除 processed/ 的對應檔案
                processed_path = PROCESSED_DIR / (Path(orphan).stem + ".txt")
                if processed_path.exists():
                    processed_path.unlink()
                    logger.info(f"  已刪除 processed：{processed_path.name}")

    save_hash_store(hash_store)
    conn.close()
    logger.info(f"完成！共更新 {updated} / {len(files)} 個檔案")


if __name__ == "__main__":
    main()
