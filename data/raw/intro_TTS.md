# Text-to-Speech (TTS) — 文字轉語音

## 什麼是 TTS？

文字轉語音（Text-to-Speech, TTS），又稱語音合成（Speech Synthesis），是將文字自動轉換為自然語音的技術。現代神經網路 TTS 系統能夠合成接近真人品質的語音，並支援多說話者、多語言、情緒控制等進階功能。

## TTS 在虛擬病人系統中的角色

在 Cascade Pipeline 中，TTS 是最後一個模組。它負責將 LLM 生成的病人回應文字轉換為語音輸出，讓虛擬病人「開口說話」。

**輸入**：病人回應文字（LLM 生成）  
**輸出**：語音音訊（.wav 或串流音訊）

TTS 的語音品質直接影響使用者對虛擬病人的沉浸感與真實感，是系統使用者體驗的最後一道關卡。

## 傳統兩階段 TTS 架構

傳統 TTS 系統分為兩個獨立訓練的模組：
1. **聲學模型（Acoustic Model）**：文字 → 聲學特徵（mel-spectrogram）
   - 代表模型：Tacotron 2、FastSpeech 2
2. **聲碼器（Vocoder）**：聲學特徵 → 音訊波形
   - 代表模型：WaveNet、HiFi-GAN

這種架構的缺點是兩個模組的訓練目標不完全一致，可能導致合成品質下降。

## VITS — 端對端單階段 TTS

### 基本介紹
VITS（Variational Inference with adversarial learning for Text-to-Speech）由 Kim et al.（2021）提出，是目前最具影響力的端對端 TTS 模型之一。

- **arXiv**: 2106.06103
- **核心創新**：將聲學模型與聲碼器整合為單一模型，聯合訓練
- **技術基礎**：
  - 條件變分自編碼器（CVAE）
  - 正規化流（Normalizing Flows）
  - 對抗訓練（GAN）
  - 隨機時長預測器（Stochastic Duration Predictor）

### VITS 的優勢
- 合成速度快（平行推論，非自回歸）
- 語音自然度接近真人水準（MOS 分數超越兩階段系統）
- 支援多說話者訓練
- 隨機時長預測器使同一文字可產生多種節奏的語音，更自然

## XTTS — 多語言零樣本 TTS

### 基本介紹
XTTS（Casanova et al., 2024）是 Coqui AI 開發的多語言零樣本語音複製 TTS 系統，基於 VITS 架構擴展。

- **arXiv**: 2406.04904
- **支援語言**：16 種語言（含中文、英文、葡萄牙文等）
- **零樣本語音複製（Zero-shot Voice Cloning）**：只需提供 3–10 秒的參考語音，即可以該說話者的聲音合成任意文字

### Zero-shot Voice Cloning 的意義
對於虛擬病人應用，zero-shot voice cloning 允許系統：
1. 為不同病人角色設定獨特聲音（只需錄製少量樣本）
2. 動態調整語音風格，不需重新訓練模型
3. 建立符合特定年齡、性別、病況的病人聲音特徵

## 可控 TTS（Controllable TTS）

可控 TTS 讓系統能夠根據情境動態調整語音的特徵，包括：

| 控制維度 | 應用於虛擬病人 |
|---|---|
| **情緒（Emotion）** | 病人在痛苦時語氣顫抖、在焦慮時語速加快 |
| **語速（Speaking Rate）** | 老年病人說話較慢，兒科病人語速不穩定 |
| **音調（Pitch）** | 不同年齡與性別的聲音特徵 |
| **音量（Loudness）** | 虛弱病人聲音較小，情緒激動時音量提高 |

## 評估指標

| 指標 | 說明 |
|---|---|
| **MOS（Mean Opinion Score）** | 人工評估自然度，滿分 5 分，真人語音約 4.5 |
| **UTMOS** | 自動化 MOS 預測，避免大規模人工評估 |
| **Speaker Similarity** | 合成語音與目標說話者的聲紋相似度（用於 voice cloning 評估）|
| **RTF（Real-Time Factor）** | 合成 1 秒語音所需的計算時間，RTF < 1 代表可即時合成 |

## TTS 在即時對話系統的挑戰

### 1. 首字延遲（First Token Latency）
自回歸 TTS 模型需等待完整文字輸入才能開始合成，導致延遲。解決方案：
- 使用串流 TTS（Streaming TTS），文字生成到一定長度就開始合成
- 使用非自回歸模型（如 VITS）實現平行推論

### 2. 情緒一致性
SER 偵測到的使用者情緒如何影響 TTS 的語音風格，是 Cascade 系統的核心整合問題。

### 3. 中文 TTS 特殊問題
- **多音字（Polyphone）**：「行」在「行走」與「銀行」中發音不同，需要 G2P（Grapheme-to-Phoneme）處理
- **語調（Tone）**：中文聲調是語義的一部分，合成錯誤的聲調會改變詞義

## 推薦工具

| 工具 | 特色 | 適合場景 |
|---|---|---|
| **Coqui TTS / XTTS v2** | 開源、支援中文、zero-shot cloning | 虛擬病人系統首選 |
| **edge-tts** | 微軟 Azure TTS 免費 API | 快速原型開發 |
| **pyttsx3** | 完全離線、輕量 | 低資源環境 |
