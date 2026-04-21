"""
skill_builder.py
系統性地向 RAG 知識庫提問，整合回答，自動生成 skill.md Agent 技能文件
"""

import argparse
import logging
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_MODEL = "openai/gemini-2.5-flash"
DEFAULT_OUTPUT = "skill.md"

# ═════════════════════════════════════════════════════════
# 全域問題清單（針對 Cascade 語音虛擬病人系統設計）
# 每個問題對應 skill.md 的一個 section，並鎖定具體技術模組
# ═════════════════════════════════════════════════════════

GLOBAL_QUESTIONS = [
    # ── Overview ──────────────────────────────────────────
    {
        "section": "overview",
        "question": (
            "這個知識庫的核心主題是什麼？"
            "請說明 Cascade 語音虛擬病人系統的整體架構，"
            "包含 VAD、ASR、SER、LLM+RAG、TTS 各模組的功能定位，"
            "以及這套系統在醫學教育中的應用目標。"
            "請用 200 字以內回答。"
        ),
    },

    # ── ASR ───────────────────────────────────────────────
    {
        "section": "core_concepts_asr",
        "question": (
            "在自動語音辨識（ASR）方面，知識庫中提到哪些模型與技術？"
            "特別說明：(1) Whisper 的架構特色與各版本規格差異；"
            "(2) Faster Whisper 相較原版的優化方式；"
            "(3) ASR 在醫療場景的挑戰（醫學術語、中文辨識、即時性）；"
            "(4) ASR 錯誤如何影響下游的 LLM 輸入，以及錯誤修正方法。"
        ),
    },

    # ── SER ───────────────────────────────────────────────
    {
        "section": "core_concepts_ser",
        "question": (
            "在語音情緒辨識（SER）方面，知識庫中提到哪些核心技術？"
            "請說明：(1) wav2vec 2.0 用於 SER 的方法與 fine-tuning 策略（V-FT、TAPT、P-TAPT）；"
            "(2) SER 常用的評估資料集（IEMOCAP、RAVDESS 等）與評估指標（WA、UA、CCC）；"
            "(3) SER 在短語音片段的挑戰；"
            "(4) SER 輸出如何整合進虛擬病人的 LLM Prompt，影響病人的情緒回應。"
        ),
    },

    # ── VAD ───────────────────────────────────────────────
    {
        "section": "core_concepts_vad",
        "question": (
            "在語音活動偵測（VAD）方面，知識庫中提到哪些工具與技術？"
            "特別說明 Silero VAD 的特色、使用方式，"
            "以及 VAD 在 Cascade Pipeline 中的角色——"
            "如何與 ASR 配合減少不必要的推論，降低整體系統延遲。"
        ),
    },

    # ── LLM + 虛擬病人 ─────────────────────────────────────
    {
        "section": "core_concepts_llm_vp",
        "question": (
            "在 LLM 驅動的虛擬病人對話生成方面，知識庫提到哪些關鍵技術？"
            "請說明：(1) System Prompt 設計如何設定病人 Persona、行為規則、資訊釋出控制；"
            "(2) 多輪對話歷史的管理方式；"
            "(3) 如何防止 LLM 角色越界（role break）或產生醫學上不正確的回應；"
            "(4) Dynamic Adaptation Module 的功能；"
            "(5) LLM 虛擬病人相較傳統決策樹虛擬病人的優勢與限制。"
        ),
    },

    # ── RAG ───────────────────────────────────────────────
    {
        "section": "core_concepts_rag",
        "question": (
            "在檢索增強生成（RAG）方面，知識庫中提到哪些技術細節？"
            "請說明：(1) Chunking 策略（固定長度、overlap 設計）；"
            "(2) Embedding 模型的選擇（sentence-transformers、多語言模型）；"
            "(3) Vector Database 的選項與適用場景（ChromaDB、pgvector、FAISS）；"
            "(4) RAG 如何為虛擬病人注入醫療知識，確保病人回應的醫學正確性；"
            "(5) RAG 相較純 LLM 的優勢（減少幻覺、知識可更新）。"
        ),
    },

    # ── TTS ───────────────────────────────────────────────
    {
        "section": "core_concepts_tts",
        "question": (
            "在語音合成（TTS）方面，知識庫中提到哪些模型與技術？"
            "請說明：(1) VITS 的架構原理（CVAE + Normalizing Flow + GAN + 隨機時長預測器）與優勢；"
            "(2) XTTS 的多語言零樣本語音複製（zero-shot voice cloning）功能；"
            "(3) 可控 TTS（Controllable TTS）如何調整情緒、語速、音調；"
            "(4) 即時對話系統中 TTS 首字延遲的解決方案；"
            "(5) 中文 TTS 的特殊挑戰（多音字、聲調）。"
        ),
    },

    # ── Cascade 整體架構 ───────────────────────────────────
    {
        "section": "cascade_architecture",
        "question": (
            "在 Cascade 語音虛擬病人系統的整體架構設計方面，知識庫提到哪些工程實踐？"
            "請說明：(1) Cascade 與 End-to-End 架構的比較（優缺點）；"
            "(2) 錯誤傳播（Error Propagation）問題——上游模組錯誤如何影響下游；"
            "(3) 延遲累積問題與解決策略；"
            "(4) 雙工（Duplex）即時互動的設計挑戰；"
            "(5) 各模組串接時的資料格式與介面設計注意事項。"
        ),
    },

    # ── 虛擬病人教育應用 ────────────────────────────────────
    {
        "section": "vp_education",
        "question": (
            "在醫學教育的虛擬病人應用方面，知識庫提到哪些重要概念？"
            "請說明：(1) 虛擬病人 vs 標準化病人（SP）的比較；"
            "(2) OSCE 訓練場景中虛擬病人的應用；"
            "(3) 病人 Persona 的設計要素（病史、情緒、說話風格）；"
            "(4) 如何評估虛擬病人系統的教育效果；"
            "(5) 現有代表性系統（CLiVR、PatientSim、MEDSAGE 等）的特色比較。"
        ),
    },

    # ── 研究趨勢 ───────────────────────────────────────────
    {
        "section": "trends",
        "question": (
            "根據知識庫中的論文，Cascade 語音虛擬病人系統目前最重要的研究趨勢是什麼？"
            "請聚焦在：(1) LLM 驅動虛擬病人的最新進展；"
            "(2) 語音介面（voice-enabled）虛擬病人的發展方向；"
            "(3) 情緒感知對話系統的研究趨勢；"
            "(4) 醫療 AI 在教育場景的評估方法進展。"
        ),
    },

    # ── Key Entities ────────────────────────────────────────
    {
        "section": "entities",
        "question": (
            "知識庫中提到哪些重要的模型、工具、資料集與評估指標？"
            "請分四類條列：\n"
            "1. 模型（ASR/SER/TTS/LLM 各自的代表模型）\n"
            "2. 開源工具與框架（SpeechBrain、Coqui TTS、LiteLLM 等）\n"
            "3. 評估資料集（IEMOCAP、RAVDESS、LibriSpeech 等）\n"
            "4. 評估指標（WER、CER、MOS、WA/UA、CCC 等）"
        ),
    },

    # ── 最佳實踐 ───────────────────────────────────────────
    {
        "section": "methodology",
        "question": (
            "在實際建構 Cascade 語音虛擬病人系統時，知識庫中提到哪些工程最佳實踐？"
            "請針對每個模組給出具體建議：\n"
            "VAD 模組、ASR 模組、SER 模組、LLM+RAG 模組、TTS 模組，"
            "以及各模組串接的介面設計原則。"
        ),
    },

    # ── Knowledge Gaps ────────────────────────────────────
    {
        "section": "gaps",
        "question": (
            "根據知識庫的現有內容，在 Cascade 語音虛擬病人系統的技術面，"
            "目前還有哪些未被充分覆蓋的子主題或未解決的問題？"
            "例如：中文醫療 SER 資料集的缺乏、即時 TTS 的延遲問題、"
            "多模態情緒整合等。請具體說明 3–5 個知識空缺。"
        ),
    },

    # ── Q&A 範例 ───────────────────────────────────────────
    {
        "section": "qa_examples",
        "question": (
            "請列出 5 個這個知識庫最適合回答的實用問題，並給出具體答案。"
            "問題應聚焦在開發者實際會遇到的技術決策，例如：\n"
            "- 「Whisper 哪個版本適合即時醫療語音辨識？」\n"
            "- 「SER 輸出的情緒標籤如何整合進 LLM Prompt？」\n"
            "- 「VITS 和 XTTS 在虛擬病人場景怎麼選擇？」\n"
            "- 「RAG 的 Chunk 大小應該設多少？」\n"
            "- 「如何防止虛擬病人的 LLM 角色越界？」"
        ),
    },
]


# ═════════════════════════════════════════════════════════
# 從 rag_query.py 引用核心函式（避免重複程式碼）
# ═════════════════════════════════════════════════════════

def get_embedding_model():
    from sentence_transformers import SentenceTransformer
    model_name = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
    return SentenceTransformer(model_name)


def get_db_connection():
    import psycopg2
    conn_str = os.getenv(
        "PGVECTOR_CONNECTION_STRING",
        "postgresql://raguser:ragpassword@localhost:5432/ragdb"
    )
    return psycopg2.connect(conn_str)


def embed_query(model, query: str) -> list[float]:
    return model.encode([query])[0].tolist()


def retrieve_chunks(conn, query_vec: list[float], top_k: int = 6) -> list[dict]:
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
        {"source": r[0], "chunk_index": r[1], "content": r[2], "similarity": round(float(r[3]), 4)}
        for r in rows
    ]


def call_llm(messages: list[dict], model: str = DEFAULT_MODEL) -> str:
    api_key = os.getenv("LITELLM_API_KEY", "")
    base_url = os.getenv("LITELLM_BASE_URL", "")

    if not api_key or not base_url:
        return "[LLM 未設定] 請確認 .env 中的 LITELLM_API_KEY 與 LITELLM_BASE_URL"

    try:
        from litellm import completion
        import litellm
        litellm.api_key = api_key
        litellm.api_base = base_url
        response = completion(model=model, messages=messages, api_base=base_url, api_key=api_key)
        return response.choices[0].message.content
    except Exception as e:
        logger.warning(f"LiteLLM 失敗（{e}），嘗試 fallback...")

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        clean_model = model.removeprefix("openai/")
        response = client.chat.completions.create(model=clean_model, messages=messages)
        return response.choices[0].message.content
    except Exception as e2:
        logger.error(f"Fallback 也失敗：{e2}")
        return f"[錯誤] {e2}"


# ═════════════════════════════════════════════════════════
# 單次 RAG 查詢
# ═════════════════════════════════════════════════════════

QUERY_SYSTEM_PROMPT = """你是一個 Cascade 語音虛擬病人系統的技術知識萃取助手。
根據提供的參考資料，詳細且有條理地回答問題。
回答以繁體中文為主，技術術語保留英文。
請聚焦在與語音處理（ASR、SER、VAD、TTS）、LLM 對話生成、RAG 系統、
以及醫療虛擬病人應用直接相關的內容。
盡可能具體，引用資料中的模型名稱、方法、數據與工具。
如果參考資料中沒有足夠資訊，請明確說明知識空缺，不要捏造答案。"""


def run_single_query(question: str, embed_model, conn, model_name: str) -> tuple[str, list[dict]]:
    """執行一次 RAG 查詢，回傳 (答案, chunks)"""
    vec = embed_query(embed_model, question)
    chunks = retrieve_chunks(conn, vec, top_k=6)

    if not chunks:
        return "知識庫尚無資料。", []

    context = "\n\n---\n\n".join(
        f"[來源：{c['source']}，chunk #{c['chunk_index']}，相似度：{c['similarity']}]\n{c['content']}"
        for c in chunks
    )
    messages = [
        {"role": "system", "content": QUERY_SYSTEM_PROMPT},
        {"role": "user", "content": f"參考資料：\n\n{context}\n\n問題：{question}"},
    ]
    answer = call_llm(messages, model=model_name)
    return answer, chunks


# ═════════════════════════════════════════════════════════
# 統計知識庫資訊
# ═════════════════════════════════════════════════════════

def get_kb_stats(conn) -> dict:
    """取得知識庫的基本統計資訊"""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(DISTINCT source) FROM documents;")
        doc_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM documents;")
        chunk_count = cur.fetchone()[0]
        cur.execute("SELECT DISTINCT source FROM documents ORDER BY source;")
        sources = [r[0] for r in cur.fetchall()]
    return {"doc_count": doc_count, "chunk_count": chunk_count, "sources": sources}


# ═════════════════════════════════════════════════════════
# 整合所有查詢結果 → 生成 skill.md
# ═════════════════════════════════════════════════════════

INTEGRATION_SYSTEM_PROMPT = """你是一個技術文件撰寫專家，專精於語音 AI 與醫療對話系統。
你會收到多個 RAG 查詢的結果，請整合成一份結構清晰、資訊密度高的 Agent Skill 文件。
要求：
- 繁體中文為主，技術術語保留英文
- 每個 section 都要有實質且具體的內容，不可空泛
- Core Concepts 必須涵蓋 ASR、SER、VAD、LLM、RAG、TTS、虛擬病人等所有模組，列出 10–14 個概念
- Key Trends 列出 4–6 個目前最重要的發展方向，聚焦語音虛擬病人領域
- Methodology 針對每個模組（VAD/ASR/SER/LLM+RAG/TTS）各給具體建議
- Example Q&A 的問題必須是開發者實際會問的技術決策問題
- 整份文件讀起來像一份「Cascade 語音虛擬病人系統開發指南」"""


def build_skill_md(results: dict, stats: dict, model_name: str) -> str:
    """將所有查詢結果整合成 skill.md 內容"""

    sections_text = "\n\n".join(
        f"=== {key} ===\n{val['answer']}"
        for key, val in results.items()
    )

    sources_list = "\n".join(f"- {s}" for s in stats["sources"])

    integration_prompt = f"""以下是針對「Cascade 語音虛擬病人系統技術知識庫」的多個查詢結果：

{sections_text}

知識庫統計：
- 文件數量：{stats['doc_count']} 份
- Chunk 數量：{stats['chunk_count']} 個
- 來源清單：
{sources_list}

請根據以上所有資訊，生成一份完整的 skill.md，格式如下（請嚴格遵守，包含所有 section）：

# Skill: Cascade 語音虛擬病人系統技術知識庫

## Metadata
- **知識領域**：語音處理 / 醫療對話系統 / Cascade 架構
- **資料來源數量**：{stats['doc_count']} 份文件
- **最後更新時間**：{date.today().isoformat()}
- **適用 Agent 類型**：語音系統技術顧問 / 虛擬病人系統開發助手

## Overview
[200字以內，說明這個 Skill 的核心知識範疇，需提及 VAD、ASR、SER、LLM+RAG、TTS 五個模組]

## Core Concepts
[10–14 個最重要的概念，涵蓋所有模組，每個附 1–2 句具體說明]
[必須包含：wav2vec2、Whisper、Silero VAD、VITS/XTTS、RAG、Persona Consistency、
Error Propagation、Chunking、SER fine-tuning、Virtual Patient vs SP 等]

## Key Trends
[4–6 個目前最重要的發展趨勢，聚焦語音虛擬病人領域]

## Key Entities
### ASR 模型
### SER 模型
### TTS 模型
### LLM 模型
### 開源工具與框架
### 評估資料集
### 評估指標

## Methodology & Best Practices
### VAD 模組
### ASR 模組
### SER 模組
### LLM + RAG 模組
### TTS 模組
### 模組串接原則

## Knowledge Gaps & Limitations
[3–5 個具體的知識空缺，聚焦技術面]

## Example Q&A
[5 組開發者實際會問的技術決策問題與具體答案]

## Source References
[列出資料來源清單，包含文件名稱、類型、日期等]
"""

    messages = [
        {"role": "system", "content": INTEGRATION_SYSTEM_PROMPT},
        {"role": "user", "content": integration_prompt},
    ]
    return call_llm(messages, model=model_name)


# ═════════════════════════════════════════════════════════
# 主程式
# ═════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="skill_builder.py：自動查詢 RAG 知識庫，生成 Agent 技能文件 skill.md"
    )
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT, help=f"輸出檔案路徑（預設：{DEFAULT_OUTPUT}）")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help=f"LLM 模型名稱（預設：{DEFAULT_MODEL}）")
    parser.add_argument("--top-k", type=int, default=6, help="每次查詢取回的 chunk 數量（預設：6）")
    args = parser.parse_args()

    logger.info("=== skill_builder 啟動 ===")

    # 初始化
    embed_model = get_embedding_model()
    conn = get_db_connection()

    # 知識庫統計
    stats = get_kb_stats(conn)
    logger.info(f"知識庫：{stats['doc_count']} 份文件，{stats['chunk_count']} 個 chunks")

    if stats["chunk_count"] == 0:
        logger.error("知識庫是空的，請先執行 data_update.py --rebuild")
        return

    # 逐一執行全域問題查詢
    results = {}
    total = len(GLOBAL_QUESTIONS)
    for i, item in enumerate(GLOBAL_QUESTIONS, 1):
        section = item["section"]
        question = item["question"]
        logger.info(f"[{i}/{total}] 查詢：{section}")

        answer, chunks = run_single_query(question, embed_model, conn, args.model)
        results[section] = {
            "question": question,
            "answer": answer,
            "sources": [f"{c['source']} chunk#{c['chunk_index']}" for c in chunks],
        }
        logger.info(f"  → 回答長度：{len(answer)} 字，引用 {len(chunks)} 個 chunks")

    # 整合生成 skill.md
    logger.info("整合所有查詢結果，生成 skill.md...")
    skill_content = build_skill_md(results, stats, args.model)

    # 寫出檔案
    output_path = Path(args.output)
    output_path.write_text(skill_content, encoding="utf-8")
    logger.info(f"skill.md 已輸出至：{output_path}（{len(skill_content)} 字元）")

    conn.close()
    logger.info("=== 完成 ===")


if __name__ == "__main__":
    main()
