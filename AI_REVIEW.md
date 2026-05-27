# HW3 AI 評分回饋

> 本份回饋由 **Anthropic Claude Opus 4.7** 與 **OpenAI GPT-5.5** 兩個獨立模型，分別針對 Phase 1 與 Phase 2 程式碼與文件進行評分；最終加權分數為兩模型平均後，進行全班性的 Normalize，以及老師加分。

---

## 本次公布的兩個分數

本次 HW3 作業，每位同學會公布**兩個分數**，計算方式為下列三個候選值中**最高的兩個**：

| 候選 | 來源 | 計算 | 值 |
|---|---|---|---:|
| A | Max(Phase 1 兩模型評分) | max(Opus 78.5, GPT 78.8) | 78.75 |
| B | Max(Phase 2 兩模型評分) | max(Opus 89.4, GPT 90.3) | 90.31 |
| C | 最終加權分數 | 詳見下方加權計算 | 89.36 |

### 你的兩個分數

### **90.31**　／　**89.36**

_（B：Max(Phase 2 兩模型評分) = 90.31；C：最終加權分數 = 89.36）_

## 最終加權分數（候選 C）的計算

| 來源 | Phase 1 (40%) | Phase 2 (60%) | 加權平均 |
|---|---:|---:|---:|
| Anthropic Claude Opus 4.7 | 78.5 | 89.4 | 85.03 |
| OpenAI GPT-5.5 | 78.8 | 90.3 | 85.69 |
| **兩模型平均** | **78.6** | **89.8** | **85.36** |
| 老師加分 (professor_bonus) | | | +4 |
| **最終分數** | | | **89.36** |

## 計算公式

```
Phase 1 平均  = (Opus_P1 + GPT_P1) / 2
Phase 2 平均  = (Opus_P2 + GPT_P2) / 2
加權平均      = 0.4 × Phase 1 平均 + 0.6 × Phase 2 平均
Normalize 後  = 依全班分布做校準
最終分數      = min(100, Normalize 後 + 老師加分)
```

## 專案基本資料

- **github_id**：`Jullliaaaa-1`
- **領域**（Haiku 抽取）：`cascade_voice_virtual_patient_system`
- **領域分類**（taxonomy）：`biomedical_health_domain`
- **Phase 1 CI**：✓ 通過
- **Phase 2 CI**：✓ 通過

## Phase 1 分項評語（40% 權重）

| 面向 | Opus 分數 | Opus 評語 | GPT 分數 | GPT 評語 |
|---|---:|---|---:|---|
| 資料收集 | 62 | data/raw 僅 5 份且全為 .pdf，格式單一未達多樣性高分標準（Haiku 聲稱 36 份但 scanner 僅見 5）。README 僅 227 字元，幾乎無資料來源描述、授權說明與動機交代，與 phase1_high_anchor「列出指引/論文版本與授權」差距明顯，僅勉強達合格門檻。 | 52 | data/raw 與 processed 各 5 份，達 Phase 1 基本門檻；但全為 .pdf，格式不多元，README 幾乎為模板，未清楚列來源、版本或授權。 |
| RAG 系統完整度 | 82 | data_update.py（326 行）chunking 採固定 500/50 overlap 合理、支援 pdf/txt/md 載入與清理、sentence-transformers embedding 並寫入 pgvector，流程完整。rag_query.py 實作 cosine top-k 檢索、prompt 組裝含 [來源：檔名, chunk #編號] citation、LiteLLM/OpenAI 整合與 fallback。缺 reranking 與 metadata filter，但 Phase 1 核心管線可運作。 | 84 | data_update.py 有 PDF 讀取、clean_text、固定 chunking、embedding 與 pgvector 管線；rag_query.py 有 top-k 檢索、來源提示與 LiteLLM proxy 呼叫，但切分非語意感知。 |
| 冪等性 | 88 | 明確以 MD5 hash diff 實作增量更新（compute_file_hash + HASH_STORE JSON），並支援 --rebuild 全量重建旗標，bonus 條件達成。從程式碼可見 ON CONFLICT 寫入與 orphan cleanup 設計（Haiku 確認），冪等性設計優於多數同儕。 | 95 | data_update.py 可見 MD5 hash store、預設增量更新與 --rebuild 設計；摘要亦顯示 ON CONFLICT 與 orphan cleanup，冪等性相當完整。 |

## Phase 2 分項評語（60% 權重）

| 面向 | Opus 分數 | Opus 評語 | GPT 分數 | GPT 評語 |
|---|---:|---|---:|---|
| 資料收集深度 | 88 | data/raw 共 36 份（17 PDF + 19 MD），超過門檻並涵蓋 arXiv 論文、開源 README、個人筆記與醫療 SOP 多元來源。README §5 以表格列出來源、授權（CC BY 4.0 / MIT / Apache 2.0）、日期與數量，並說明跨領域重複計數，授權合規清晰。個人筆記坦承 AI 協作並經人工校閱，誠實度高。略可再加入隱私與合規處理說明。 | 91 | data/raw 36 份，含 arXiv PDF、開源 README、個人筆記與醫療教育資料；README §5 有授權表與來源類型，但子類數量加總與總數略不一致。 |
| skill.md 品質 | 90 | skill.md 26845 字、八大必要章節齊全。Core Concepts 14 條具體（Silero VAD、wav2vec 2.0、VITS、XTTS 等），Key Entities 分模型/工具/資料集/指標四類含具體名稱（Whisper large-v3、IEMOCAP、CCC）。Methodology 對五模組分別給工程建議、Knowledge Gaps 點出中文醫療 SER 等具體缺口、Example Q&A 五題深入。整體像領域顧問整理而非 LLM 散漫輸出。 | 88 | skill.md 章節齊全，§Core Concepts 14 條、§Key Entities 含 Whisper、Silero、XTTS、IEMOCAP 等具體實體；但部分 Q&A 與前文資訊矛盾，引用密度偏弱。 |
| README 設計決策 | 92 | README 13609 字，§3 完整回答 chunking（400/80 的中文密度取捨）、embedding（多語 vs all-MiniLM 比較）、pgvector（vs ChromaDB）、retrieval、HyDE（從 paraphrase 演化到關鍵字的實測踩坑）、prompt、LiteLLM 雙層 fallback、冪等性（hash + ON CONFLICT + orphan cleanup）、skill_builder 13 題設計理由皆有具體取捨論述，§6 亦坦承限制。 | 94 | README §3 完整回答 chunking、embedding、pgvector、retrieval、HyDE、prompt、fallback、idempotency 與 skill_builder 問題，理由與限制清楚。 |
| skill_builder 品質 | 88 | skill_builder.py 516 行設計 13 個全域問題，覆蓋 Overview/ASR/SER/VAD/LLM+VP/RAG/TTS/Cascade 架構/教育應用/Trends/Entities/Methodology/Gaps/Q&A，明確對應 skill.md 各 section，問題具體鎖定子模組與技術點（如 VITS 的 CVAE+Flow+GAN）。多次 query 結果整合至 skill.md 章節結構清晰，非機械拼貼。 | 90 | skill_builder.py 設計 13 個全域問題，涵蓋 Overview、ASR/SER/VAD/TTS、趨勢、實體、方法與缺口；skill.md 顯示有跨查詢整合，但仍偏章節式拼接。 |

## 整體評語

### 亮點

- 完整的冪等性設計（hash + DB constraint + orphan cleanup）確保重複執行無髒資料
- 詳細的設計決策文件說明每個技術選型的理由與取捨
- 13 個全域問題系統性覆蓋知識庫各面向，skill.md 內容充實具體
- HyDE 關鍵字擴展解決 lexical gap，提升檢索品質
- 中英混合 embedding 模型與 36 份多來源資料適配醫療領域需求

### 改進建議

- 固定長度 chunking 不感知語意邊界，可能在句子中斷開
- 無 reranking 機制，top-k 純靠 cosine similarity 可能重複
- HyDE 依賴 LLM 可用性，endpoint 不通時自動退回原始 query
- 向量搜尋無 metadata 過濾，ASR 問題可能混入 TTS chunks
- 多語言 embedding 質量瓶頸，中文醫療術語辨識仍有限制

---

_本份評分回饋由自動化評分管線（Anthropic + OpenAI 雙模型獨立評分 → 平均 → rescale → 老師加分）產出，僅作為個人學習參考。若對評分有疑問請於課堂或 office hour 提出。_
