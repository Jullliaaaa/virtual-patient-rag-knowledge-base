[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mhxNhwtV)
# Build-Your-Personal-RAG  

# Cascade 語音虛擬病人系統技術知識 RAG

## 1. 專案簡介

### 主題選擇與理由

本專案以**「Cascade 語音虛擬病人系統所涉及的技術」**作為 RAG 知識庫主題。

選擇這個主題的原因是：我正在開發一套用於醫療技術訓練的語音虛擬病人系統，採用 Cascade 架構串接 VAD → ASR → SER → LLM → TTS。在開發過程中需要不斷查詢各模組的技術細節、模型選型依據、以及架構設計取捨——因此這個 RAG 系統對我有真實的使用價值，而非單純的作業繳交。  

### 資料來源規模

- **總計檔案數**：36 份
- **格式**：PDF（arXiv 論文）、Markdown（技術文件與個人筆記）
- **語言**：中英混合
- **類型與規模**：
  - **學術論文 (arXiv PDFs)**：17 份
    - 涵蓋 ASR 錯誤校正、SER 特徵提取、TTS 零樣本複製、以及最新的 LLM 虛擬病人架構論文。
  - **開源工具 README**：7 份
    - 包含 Faster Whisper, Silero VAD, XTTS, pgvector 等技術規格與實作指南。
  - **個人中文筆記**：9 份
    - 採 **AI 協作撰寫 (AI-assisted drafting)** 並經人工針對醫療術語與技術參數進行校閱。針對 Cascade Pipeline 各模組提供中文導讀與開發手記。
  - **醫療教育資料**：3 份
    - 包含「插管步驟」、「導尿管留置護理指導」以及「醫病溝通原則」等臨床 SOP。


### 系統技術選型概覽

| 元件 | 選擇 | 理由 |
|---|---|---|
| Embedding | `paraphrase-multilingual-MiniLM-L12-v2` | 支援中英混合，完全免費 |
| Vector DB | pgvector（PostgreSQL） | 業界常見，SQL 查詢能力強 |
| LLM 介面 | LiteLLM + openai SDK fallback | 避免單點失敗 |
| PDF 解析 | pdfplumber | 對學術論文排版解析效果佳 |

---

## 2. 系統架構說明

```mermaid
graph LR
    A[data/raw/\nPDF + MD] --> B[data_update.py\n清理 + Chunking]
    B --> C[paraphrase-multilingual\n-MiniLM-L12-v2]
    C --> D[(pgvector\nDocker)]
    B --> E[data/processed/\n清理後 .txt]
    D --> F[rag_query.py\nCLI 問答]
    F --> G[LiteLLM\ngemini-2.5-flash]
    G --> F
    F --> H[skill_builder.py\n全域問題查詢]
    H --> G
    H --> I[skill.md\nAgent 技能文件]
```

### 資料流說明

1. `data/raw/` 存放原始 PDF 與 Markdown 檔案
2. `data_update.py` 讀取、清理、Chunking、Embedding，寫入 pgvector
3. 同時將清理後純文字存至 `data/processed/`（解耦清理與向量化流程）
4. `rag_query.py` 提供 CLI 問答介面，執行完整 RAG 流程（含 HyDE）
5. `skill_builder.py` 發出 13 個全域問題，整合後生成 `skill.md`

---

## 3. 設計決策說明（Design Decisions）

### Chunking 策略

採用**固定長度 + overlap** 策略：`chunk_size=400`，`overlap=80`（chunk_size 的 20%）。

選擇理由：
- 學術論文段落長度不一，依段落切分容易產生過長或過短的 chunk
- 400 字元對中英混合資料約等於 200 個中文字，語意完整度足夠且不過度稀釋向量
- overlap 設為 chunk_size 的 20%，依據課程 W6 建議：「相鄰 Chunk 保留重疊區域建議為 chunk_size 的 20%，確保跨段落的關鍵資訊不會因切割而遺失」
- 相較於純英文資料建議的 150–300 字元，中文密度較高（400 字元 ≈ 200 中文字），因此取 400 字元作為折衷

### Embedding 模型選擇

選用 `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`：

- **中英混合**：資料同時包含英文 arXiv 論文與中文筆記，此模型支援 50+ 語言
- **完全免費**：本地執行，無需 API Key，無速率限制
- **向量維度 384**：在準確度與計算速度之間取得平衡
- 相較於 `all-MiniLM-L6-v2`（英文優先），此模型對中文語意的捕捉效果明顯更佳

首次執行會自動從 HuggingFace 下載約 420MB，之後完全離線。

### Vector DB 選型：pgvector

評估過 ChromaDB 與 pgvector，最終選擇 pgvector：

- **冪等性設計**：利用 `UNIQUE (source, chunk_index)` constraint 搭配 `ON CONFLICT DO UPDATE`，確保重複執行不累積髒資料
- **metadata 過濾**：未來可依 `source` 欄位過濾特定子主題（如只查 ASR 相關論文）
- **業界標準**：pgvector 是生產環境最常見的向量資料庫之一，有實際學習價值
- 代價是需要 Docker，但 `docker-compose.yml` 已標準化啟動流程

### Retrieval 策略

- `top_k=5`（rag_query.py 預設）、`top_k=6`（skill_builder.py 使用較多 context）
- 使用 **cosine similarity**（`<=>` operator）
- 未實作 reranking，但 source metadata 已保存，未來可加入 MMR（Maximal Marginal Relevance）去除重複來源

### HyDE（Hypothetical Document Embeddings）— 解決 Lexical Gap

**問題背景**：實際測試中發現，即使知識庫裡明確有某個概念，直接用問句做向量搜尋有時仍會找不到。原因是問句（「Whisper 支援幾個語言？」）與文件片段（「Whisper 在 68 萬小時的多語言資料集上訓練...」）的語意空間不一致——問句是疑問句語氣，文件是陳述句語氣，embedding 後距離被放大。

**HyDE 的核心想法**：先讓 LLM 生成一段與文件語氣相近的假設性內容，再用這段內容做向量搜尋，因為假設答案的術語和語氣與文件更接近，cosine similarity 因此更準確。

**實作版本的演化**：

最初是讓 LLM 把問題「換句話說（paraphrase）」，但實測發現 paraphrase 有時反而引入語意偏移（例如把「延遲」改成「latency bottleneck」，反而搜到不相關的 chunks）。

目前改為**生成多個搜尋關鍵字組合**：

```
請根據使用者的問題，提供 3 個不同的搜尋關鍵字組合，
以繁體中文與英文術語呈現。僅回傳關鍵字，不需解釋。
```

改用關鍵字的優點：比完整句子更貼近文件高頻詞、多組關鍵字能涵蓋中英混合的不同表述、且回傳內容簡短不會污染 embedding。HyDE 可透過 `--no-hyde` 旗標停用，預設開啟。

### Prompt Engineering

RAG prompt 設計原則：
1. System prompt 明確說明角色（語音虛擬病人系統技術顧問）
2. Context 區塊標明來源與 chunk 編號，方便 LLM 引用
3. 明確要求回應中必須包含引用格式 `[來源：檔名, chunk #編號]`
4. 告知 LLM 若資料不足應明確說明，避免幻覺

### LiteLLM 統一呼叫 + Fallback

使用 LiteLLM 的原因是它提供統一的 `completion()` 介面，讓模型切換（Gemini / 本地模型）不需改程式碼。設計了雙層 fallback，避免單點失敗：

1. **LiteLLM `completion()`** → 若失敗（網路、quota 問題）
2. **OpenAI SDK 直打 endpoint**（去掉 `openai/` 前綴後直接呼叫）→ 若也失敗
3. **回傳 placeholder 錯誤訊息**（不讓整個 pipeline crash）

這個設計讓 `rag_query.py` 在未設定 API Key 時仍能執行並回傳 placeholder，通過 CI 的基本可執行性檢查。

### 冪等性設計

`data_update.py` 的冪等性透過兩層保證：

1. **檔案層**：以 MD5 hash 快取（`data/.file_hashes.json`）判斷檔案是否變動，未變動的檔案跳過處理
2. **DB 層**：寫入時使用 `ON CONFLICT (source, chunk_index) DO UPDATE`，即使重跑也不會累積重複資料
3. `--rebuild` 旗標會清空 `data/processed/` 與 DB，強制全量重建

**孤兒清理（Orphan Cleanup）**：若某份原始檔案從 `data/raw/` 刪除，下次執行 `data_update.py` 時，程式會比對 DB 中現存的 sources 與當前 `data/raw/` 的檔案清單，自動刪除 DB 中已不存在的 chunks，同時清除 `data/processed/` 中對應的 `.txt` 以及 hash store 中的紀錄，確保 DB 狀態永遠與 `data/raw/` 保持一致。

### skill_builder.py 問題設計

設計了 13 個全域問題，涵蓋：
- Overview（整體知識範疇）
- 各子主題核心概念（ASR / SER / VAD / LLM+RAG / TTS 各一題）
- Cascade 整體架構設計（含 Duplex 議題）
- 虛擬病人教育應用（VP vs SP、OSCE、代表系統比較）
- 研究趨勢、重要實體、方法論、知識空缺、Q&A 範例

設計理由：單一問題無法覆蓋跨子主題的知識庫，分題查詢再整合能讓每個 section 都有充足的 retrieved context，最終 skill.md 的每個章節都有實質內容。

---

## 4. 環境設定與執行方式

> ⚠️ **本專案在 Windows 環境下開發**，以下指令以 Windows（PowerShell / CMD）為主，並附上 Linux/macOS 對應指令。

### 4-1. Python 版本與虛擬環境

本作業使用 **Python 3.10.11**（`requirements.txt` 第一行亦有標注）。

```powershell
# 確認 Python 版本（需 >= 3.10）
python --version

# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境（Windows PowerShell）
.venv\Scripts\Activate.ps1

# 啟動虛擬環境（Windows CMD）
.venv\Scripts\activate.bat

# 啟動虛擬環境（Linux / macOS）
# source .venv/bin/activate

# 安裝套件
pip install -r requirements.txt
```

> 💡 啟動成功後，命令列提示符會出現 `(.venv)` 前綴。

### 4-2. 設定環境變數

```powershell
# Windows
copy .env.example .env

# Linux / macOS
# cp .env.example .env
```

接著編輯 `.env`，填入助教提供的值：

```env
# LiteLLM 連線設定（由助教提供）
LITELLM_API_KEY=your_api_key_here
LITELLM_BASE_URL=your_base_url_here

# Embedding Model（預設即可，不需修改）
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# pgvector 連線字串（需與 docker-compose.yml 帳密一致）
PGVECTOR_CONNECTION_STRING=postgresql://raguser:ragpassword@localhost:5432/ragdb
```

### 4-3. 啟動 Vector DB（pgvector）

```powershell
# 啟動 pgvector（背景執行）
docker compose up -d

# 確認啟動成功（Status 應顯示 running）
docker compose ps
```

### 4-4. 完整執行流程

```powershell
# ① 全量重建索引（首次執行，或資料有大幅更新時）
python data_update.py --rebuild

# ② 增量更新（新增或修改部分檔案時）
python data_update.py

# ③ 測試 RAG 問答（單次查詢）
python rag_query.py --query "請問這個知識庫的核心主題是什麼？"

# ④ 互動式多輪對話
python rag_query.py

# ⑤ 生成 Skill 文件
python skill_builder.py --output skill.md
```

### 4-5. 複現完整性檢查清單

- [ ] `python --version` 顯示 >= 3.10
- [ ] `docker compose ps` 顯示 pgvector 狀態為 running
- [ ] `.env.example` 存在且不含真實金鑰
- [ ] `requirements.txt` 第一行有 Python 版本備註
- [ ] `data/processed/` 中有清理後的 `.txt` 檔案（已 commit）
- [ ] `python data_update.py --rebuild` 執行後無 Error，Vector DB 有資料
- [ ] `python rag_query.py --query "..."` 回傳含引用來源的答案
- [ ] `python skill_builder.py --output skill.md` 生成 skill.md 且大於 500 字元

---

## 5. 資料來源聲明（Data Sources Statement）

| 來源名稱 | 類型 | 授權 / 合規依據 | 日期 | 數量 |
|---|---|---|---|---|
| arXiv 論文（ASR 相關） | PDF | CC BY 4.0 | 2020–2025 | 5 篇 |
| arXiv 論文（SER 相關） | PDF | CC BY 4.0 | 2020–2021 | 5 篇 |
| arXiv 論文（LLM 醫療對話 / 虛擬病人） | PDF | CC BY 4.0 | 2024–2026 | 6 篇 |
| arXiv 論文（TTS 情緒合成） | PDF | CC BY 4.0 | 2024 | 5 篇 |
| arXiv 論文（Cascade 架構） | PDF | CC BY 4.0 | 2020–2026 | 4 篇 |
| 開源專案 README（Whisper、Silero VAD、SpeechBrain、pgvector、XTTS、Faster Whisper、emotion2vec、Speech-to-Speech） | Markdown | 各專案開源授權（MIT / Apache 2.0） | 2023–2024 | 8 份 |
| 個人研究筆記（`intro_*.md`） | Markdown | 個人筆記(部分AI協作) | 2026-04 | 8 份 |
| 醫療教育資料（護理指導、插管步驟、醫病溝通原則） | PDF / Markdown | 公開醫療教育資料 / 個人筆記 | 2024–2026 | 3 份 |

> **備註：**
> 本資料庫採用多來源整合策略，部分論文具跨領域特性（如同時涵蓋 ASR、SER、LLM 與 TTS），因此在子主題分類統計上可能出現重複計數情形。  不重複檔案總數：36 份
---

## 6. 系統限制與未來改進

### 目前限制

1. **Chunking 不感知語意邊界**：固定長度切分會在句子中間斷開，未來可改用語意邊界切分（如依句號、段落、Markdown header）
2. **無 reranking**：top-k 純靠 cosine similarity，可能取到內容重複的 chunks
3. **HyDE 依賴 LLM 可用性**：當 LiteLLM endpoint 不通時，HyDE 自動退回原始 query，搜尋品質會下降。未來可快取 HyDE 的結果，避免重複呼叫
4. **向量搜尋無 metadata 過濾**：目前 retrieval 不區分文件類型（論文 vs 筆記 vs README），問 ASR 問題可能混入 TTS 的 chunk
5. **多語言 embedding 的質量瓶頸**：`paraphrase-multilingual-MiniLM-L12-v2` 是小型模型（117M 參數），對高度專業的中文醫療術語 embedding 精度有限

### 未來改進方向

- 實作 Hybrid Search（pgvector 向量搜尋 + PostgreSQL 全文搜尋，結合 BM25）
- 加入 MMR（Maximal Marginal Relevance）提升 retrieved chunks 的多樣性
- 加入 Reranker（如 cross-encoder）對 top-k chunks 進行重排序
- 按子主題加上 metadata tag，支援過濾查詢（如只查 ASR 子主題）
- 補充台灣本土醫療情境的中文資料
