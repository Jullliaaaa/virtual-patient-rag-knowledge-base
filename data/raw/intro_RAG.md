# Retrieval-Augmented Generation (RAG) — 檢索增強生成

## 什麼是 RAG？

檢索增強生成（Retrieval-Augmented Generation, RAG）是一種結合「資訊檢索」與「語言模型生成」的 AI 架構。它在 LLM 生成回應之前，先從外部知識庫中檢索相關文件，再將檢索結果作為上下文（context）提供給 LLM，讓模型的回應更有根據、更準確、更新穎。

- **原始論文**：Lewis et al., 2020（arXiv: 2005.11401）
- **核心概念**：「先查再說」— 不依賴模型訓練時記憶的知識，而是即時從資料庫中找到相關資訊

## RAG 的基本流程

```
使用者問題（Query）
      ↓
[Embedding] 將問題轉為向量
      ↓
[Vector Search] 在向量資料庫中找最相似的文件片段（Top-K Chunks）
      ↓
[Context Construction] 將檢索到的文件組合成 Prompt Context
      ↓
[LLM Generation] LLM 根據 Context 生成回應
      ↓
回應（含引用來源）
```

## RAG 在虛擬病人系統中的角色

在本系統中，RAG 位於 LLM 模組內部，負責為虛擬病人提供醫療知識支撐：

1. **醫療知識注入**：病人描述症狀時，RAG 從醫療知識庫中檢索相關的病症資訊、護理指導等，確保病人角色的回應在醫學上正確
2. **動態更新**：不需重新訓練 LLM，只需更新知識庫即可讓病人具備新知識
3. **回應可追溯**：每個病人回應都可追溯到具體的醫療文件來源

## 核心技術元件

### 1. Chunking（文件切分）
將原始文件切分為適合嵌入的片段（chunks）。常見策略：
- **固定長度 + Overlap**：每個 chunk 固定 512 tokens，相鄰 chunk 重疊 128 tokens，避免語義在邊界處被截斷
- **語義切分**：依據段落、句子邊界切分，保持語義完整性
- **Chunk 大小的 tradeoff**：太大→檢索精度下降；太小→語義不完整

### 2. Embedding（向量化）
將文字轉換為高維向量（dense vector），使語義相似的文字在向量空間中距離相近。

常用免費 Embedding 模型：
| 模型 | 維度 | 語言支援 | 特色 |
|---|---|---|---|
| `all-MiniLM-L6-v2` | 384 | 英文為主 | 輕量快速 |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | 50+ 語言含中文 | 中英文推薦 |
| `text-embedding-3-small` | 1536 | 多語言 | OpenAI（付費）|

### 3. Vector Database（向量資料庫）
儲存 chunk 的向量與元資料，支援快速近似最近鄰搜尋（ANN Search）。

| 工具 | 特色 | 適合情境 |
|---|---|---|
| **ChromaDB** | 純 Python、零設定 | 快速原型、本地開發 |
| **pgvector** | PostgreSQL 擴充，支援 SQL 過濾 | 生產環境、需要 metadata 過濾 |
| **FAISS** | Meta 出品、記憶體內執行、極快 | 大規模離線系統 |
| **Qdrant** | REST API、效能佳 | 進階部署 |

### 4. Retrieval（檢索）
根據查詢向量找出最相似的 K 個 chunks。

- **相似度計算**：Cosine Similarity（最常用）、Dot Product、Euclidean Distance
- **Top-K 選取**：通常取 K=3~5 個最相關的 chunks 作為 context

### 5. Generation（生成）
將檢索到的 chunks 組合成 prompt，送入 LLM 生成最終回應。

Prompt 結構範例：
```
你是一位正在就醫的病人，請根據以下醫療資訊回答醫學生的問題。

[相關醫療資訊]
{retrieved_chunks}

[醫學生的問題]
{user_query}

[病人的情緒狀態]
{ser_output}

請以病人的口吻回答，不要使用醫學專業術語。
```

## RAG 的優缺點

### 優點
- **知識可更新**：新增文件到知識庫即可，不需重新訓練模型
- **減少幻覺（Hallucination）**：回應有具體文件支撐，較難捏造事實
- **可解釋性**：可追溯每個回應引用了哪些來源文件
- **領域適應**：輕鬆針對特定領域（如醫療）建立專屬知識庫

### 缺點
- **Retrieval 品質瓶頸**：若檢索到不相關的 chunks，LLM 的回應品質也會下降
- **Chunk 邊界問題**：跨 chunk 的長依賴資訊可能無法被正確整合
- **延遲增加**：相比直接生成，多了一個檢索步驟的時間開銷

## 進階 RAG 技術

### Hybrid Search（混合搜尋）
結合 Dense Retrieval（向量搜尋）與 Sparse Retrieval（BM25 關鍵字搜尋），提升檢索召回率。

### Re-ranking
在初步檢索出 Top-K chunks 後，再用更精確的 cross-encoder 模型重新排序，選出最相關的 chunks。

### Self-RAG（arXiv: 2310.11511）
讓 LLM 自主決定何時需要檢索、如何評估檢索結果是否有用，不是每次都強制執行 RAG。

## RAG 在醫療領域的應用

醫療 RAG 系統需要特別注意：
1. **資料授權合規**：使用公開授權的醫療文件（如 PubMed CC BY、官方護理指導）
2. **醫療術語 Embedding**：通用 Embedding 模型可能無法正確理解醫療術語的語義
3. **回應的醫學正確性**：LLM 生成的病人回應需符合醫學事實，不能誤導醫學生
4. **隱私保護**：真實病患資料不可直接放入知識庫
