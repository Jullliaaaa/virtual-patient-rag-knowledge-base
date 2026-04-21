# Automatic Speech Recognition (ASR) — 自動語音辨識

## 什麼是 ASR？

自動語音辨識（Automatic Speech Recognition, ASR）是將人類語音訊號自動轉換為文字的技術。ASR 系統的輸入是音訊波形，輸出是對應的文字轉錄（transcript）。現代 ASR 系統以深度學習為基礎，能夠處理多語言、多口音、背景噪音等複雜情境。

## ASR 在虛擬病人系統中的角色

在 Cascade Pipeline 中，ASR 位於 SER 之後的第二個模組。它負責將使用者（醫學生）的語音轉為文字，讓後續的 LLM 模組能夠理解使用者問了什麼，進而生成病人的文字回應。

**輸入**：音訊波形（使用者語音）  
**輸出**：文字轉錄（使用者說的話）

## Whisper — 核心 ASR 模型

### 基本介紹
Whisper（Radford et al., 2022）是 OpenAI 提出的大規模多語言語音辨識模型，是目前最廣泛使用的開源 ASR 模型之一。

- **arXiv**: 2212.04356
- **訓練資料**：68 萬小時的多語言網路音訊資料（弱監督學習）
- **架構**：Encoder-Decoder Transformer
- **支援語言**：99 種語言，包含中文（普通話、廣東話）
- **任務**：語音辨識、語音翻譯、語言識別、時間戳記預測

### 模型規格

| 模型大小 | 參數量 | 語言 | 適合場景 |
|---|---|---|---|
| tiny | 39M | 多語言/英文 | 極低延遲需求 |
| base | 74M | 多語言/英文 | 輕量部署 |
| small | 244M | 多語言/英文 | 平衡速度與準確率 |
| medium | 769M | 多語言/英文 | 高準確率 |
| large-v3 | 1550M | 多語言 | 最高準確率 |

### Faster Whisper
Faster Whisper 是基於 CTranslate2 框架對原始 Whisper 進行推論加速的實作，在相同硬體上速度提升 4 倍，記憶體使用量減少約 50%，適合即時對話系統部署。

## 評估指標

### Word Error Rate (WER)
WER 是 ASR 最核心的評估指標，計算公式為：

```
WER = (Substitutions + Deletions + Insertions) / Total Words in Reference
```

WER 越低代表辨識越準確。Whisper large-v3 在英文 LibriSpeech test-clean 上達到約 2.7% WER。

### Character Error Rate (CER)
對於中文等字元型語言，通常使用 CER（字元錯誤率）而非 WER。

## ASR 在醫療場景的挑戰

### 1. 醫學術語辨識
醫療語音包含大量專業術語（如：氣胸、心室顫動、主動脈瓣），這些詞彙在通用 ASR 訓練資料中出現頻率低，辨識準確率通常較差。

**解決方向**：
- 使用醫療領域語言模型進行 n-gram rescoring
- 建立醫療詞彙的熱詞提示（hot-word prompting）
- 在醫療語音資料上 fine-tune Whisper

### 2. ASR 錯誤對下游的影響
ASR 產生的辨識錯誤會直接影響 LLM 的輸入品質。研究顯示，即使是小比例的 WER，也可能導致 LLM 產生不相關或錯誤的回應（Error Propagation）。

**解決方向**：
- ASR 錯誤修正（ASR Error Correction）：在 ASR 輸出後加一個 LLM 修正層
- Confidence-based filtering：低信心度的辨識結果觸發澄清機制

### 3. 即時性需求
虛擬病人對話需要低延遲的 ASR 輸出。Whisper 的預設模式是離線批次處理，需要配合 streaming 或 voice activity detection（VAD）實作即時辨識。

## VAD（Voice Activity Detection）的配合使用

在實際部署中，ASR 通常與 VAD 配合使用：
- **VAD**（如 Silero VAD）負責偵測使用者何時開始/結束說話
- 只在偵測到語音活動時才啟動 ASR，避免對靜音段進行無謂推論
- 大幅降低整體系統延遲與計算成本

## 中文 ASR 特殊考量

中文語音辨識面臨以下額外挑戰：
- **同音字**：大量同音異字（如「期」與「器」）需依賴上下文消歧
- **無空格**：中文詞語間無自然分隔，增加斷詞難度
- **口語化表達**：台灣中文混雜台語、英文的語碼混用（code-switching）現象

Whisper large-v3 在中文辨識上表現優異，是目前醫療中文語音應用的首選基礎模型。
