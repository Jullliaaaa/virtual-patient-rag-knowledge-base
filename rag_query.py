"""
rag_query.py
RAG 問答 CLI 介面
流程：Embed Query → Similarity Search → Prompt 組裝 → LiteLLM → 回應含引用來源
"""

import argparse
import os
import logging
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_TOP_K = 5
DEFAULT_MODEL = "gemini-2.5-flash"


# ═════════════════════════════════════════════════════════
# 1. Embedding（查詢向量化）
# ═════════════════════════════════════════════════════════

def get_embedding_model():
    from sentence_transformers import SentenceTransformer
    model_name = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
    return SentenceTransformer(model_name)


def embed_query(model, query: str) -> list[float]:
    return model.encode([query])[0].tolist()


# ═════════════════════════════════════════════════════════
# 2. Retrieval（向量搜尋）
# ═════════════════════════════════════════════════════════

def get_db_connection():
    import psycopg2
    conn_str = os.getenv(
        "PGVECTOR_CONNECTION_STRING",
        "postgresql://raguser:ragpassword@localhost:5432/ragdb"
    )
    return psycopg2.connect(conn_str)


def retrieve_chunks(conn, query_vec: list[float], top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """
    從 pgvector 取得最相關的 top-k chunks（cosine similarity）
    """
    vec_str = "[" + ",".join(str(v) for v in query_vec) + "]"
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT source, chunk_index, content,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM documents
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
            """,
            (vec_str, vec_str, top_k)
        )
        rows = cur.fetchall()
    return [
        {
            "source": r[0],
            "chunk_index": r[1],
            "content": r[2],
            "similarity": round(float(r[3]), 4),
        }
        for r in rows
    ]


# ═════════════════════════════════════════════════════════
# 3. Prompt 組裝
# ═════════════════════════════════════════════════════════

SYSTEM_PROMPT = """你是一個專業的語音虛擬病人系統技術顧問，擅長 ASR、SER、LLM、TTS 與 Cascade 架構設計。
請根據以下提供的參考資料回答問題。
回答時必須：
1. 引用來源，格式為 [來源：檔名, chunk #編號]
2. 若參考資料不足以回答，請明確說明知識庫中沒有相關資訊
3. 回答以繁體中文為主，技術術語可保留英文
"""

def build_prompt(query: str, chunks: list[dict]) -> str:
    context_parts = []
    for i, c in enumerate(chunks):
        context_parts.append(
            f"[參考資料 {i+1}] 來源：{c['source']}，chunk #{c['chunk_index']}（相似度：{c['similarity']}）\n{c['content']}"
        )
    context = "\n\n---\n\n".join(context_parts)
    return f"以下是相關參考資料：\n\n{context}\n\n問題：{query}"


# ═════════════════════════════════════════════════════════
# 4. LiteLLM 呼叫
# ═════════════════════════════════════════════════════════

def call_llm(messages: list[dict], model: str = DEFAULT_MODEL) -> str:
    api_key = os.getenv("LITELLM_API_KEY", "")
    base_url = os.getenv("LITELLM_BASE_URL", "")

    if not api_key or not base_url:
        logger.warning("LITELLM_API_KEY / LITELLM_BASE_URL 未設定，回傳 placeholder 回應")
        return "[LLM Placeholder] 請設定 .env 中的 LITELLM_API_KEY 與 LITELLM_BASE_URL 後再查詢。"

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"LLM 呼叫失敗：{e}")
        return f"[錯誤] LLM 呼叫失敗：{e}"

# ═════════════════════════════════════════════════════════
# 5. 單次查詢
# ═════════════════════════════════════════════════════════

def run_query(query: str, top_k: int, model_name: str, embed_model, conn) -> str:
    logger.info(f"查詢：{query}")

    # Embed
    query_vec = embed_query(embed_model, query)

    # Retrieve
    chunks = retrieve_chunks(conn, query_vec, top_k)
    if not chunks:
        return "知識庫中尚無資料，請先執行 data_update.py。"

    logger.info(f"取得 {len(chunks)} 個相關 chunks")

    # Prompt
    user_prompt = build_prompt(query, chunks)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    # LLM
    answer = call_llm(messages, model=model_name)

    # 顯示引用來源
    sources_info = "\n".join(
        f"  [{i+1}] {c['source']} chunk #{c['chunk_index']} (similarity={c['similarity']})"
        for i, c in enumerate(chunks)
    )
    return f"{answer}\n\n📚 引用來源：\n{sources_info}"


# ═════════════════════════════════════════════════════════
# 6. 主程式
# ═════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="RAG 問答 CLI：查詢語音虛擬病人系統相關技術知識庫"
    )
    parser.add_argument("--query", "-q", type=str, help="單次查詢模式：輸入問題")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help=f"取回最相關的 chunk 數量（預設：{DEFAULT_TOP_K}）")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help=f"LLM 模型名稱（預設：{DEFAULT_MODEL}）")
    args = parser.parse_args()

    # 初始化
    embed_model = get_embedding_model()
    conn = get_db_connection()

    if args.query:
        # 單次查詢模式
        result = run_query(args.query, args.top_k, args.model, embed_model, conn)
        print("\n" + "="*60)
        print(result)
        print("="*60)
    else:
        # 互動式多輪對話模式（保留至少 3 輪歷史）
        print("=== RAG 問答系統（語音虛擬病人技術知識庫）===")
        print("輸入 'exit' 或 'quit' 結束\n")
        history: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
        MAX_HISTORY_TURNS = 3

        while True:
            try:
                query = input("你的問題：").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n結束對話")
                break

            if query.lower() in ("exit", "quit", ""):
                print("結束對話")
                break

            # Retrieve
            query_vec = embed_query(embed_model, query)
            chunks = retrieve_chunks(conn, query_vec, args.top_k)

            if not chunks:
                print("知識庫中尚無資料，請先執行 data_update.py。\n")
                continue

            user_prompt = build_prompt(query, chunks)
            history.append({"role": "user", "content": user_prompt})

            # 限制歷史長度（system + 最近 MAX_HISTORY_TURNS*2 條）
            trimmed = [history[0]] + history[-(MAX_HISTORY_TURNS * 2):]

            answer = call_llm(trimmed, model=args.model)
            history.append({"role": "assistant", "content": answer})

            sources_info = "\n".join(
                f"  [{i+1}] {c['source']} chunk #{c['chunk_index']} (sim={c['similarity']})"
                for i, c in enumerate(chunks)
            )
            print(f"\n回答：\n{answer}")
            print(f"\n📚 引用來源：\n{sources_info}\n")
            print("-" * 50)

    conn.close()


if __name__ == "__main__":
    main()
