## 🐸Coqui.ai News
- 📣 [🐶Bark](https://github.com/suno-ai/bark) is now available for inference with uncontrained voice cloning. [Docs](https://tts.readthedocs.io/en/dev/models/bark.html)
- 📣 You can use [~1100 Fairseq models](https://github.com/facebookresearch/fairseq/tree/main/examples/mms) with 🐸TTS.
- 📣 🐸TTS now supports 🐢Tortoise with faster inference. [Docs](https://tts.readthedocs.io/en/dev/models/tortoise.html)
- 📣 **Coqui Studio API** is landed on 🐸TTS. - [Example](https://github.com/coqui-ai/TTS/blob/dev/README.md#-python-api)
- 📣 [**Coqui Studio API**](https://docs.coqui.ai/docs) is live.
- 📣 Voice generation with prompts - **Prompt to Voice** - is live on [**Coqui Studio**](https://app.coqui.ai/auth/signin)!! - [Blog Post](https://coqui.ai/blog/tts/prompt-to-voice)
- 📣 Voice generation with fusion - **Voice fusion** - is live on [**Coqui Studio**](https://app.coqui.ai/auth/signin).
- 📣 Voice cloning is live on [**Coqui Studio**](https://app.coqui.ai/auth/signin).

##

**🐸TTS is a library for advanced Text-to-Speech generation.**

🚀 Pretrained models in +1100 languages.

🛠️ Tools for training new models and fine-tuning existing models in any language.

📚 Utilities for dataset analysis and curation.
______________________________________________________________________

[![Dicord](https://img.shields.io/discord/1037326658807533628?color=%239B59B6&label=chat%20on%20discord)](https://discord.gg/5eXr5seRrv)
[![License]( )](https://opensource.org/licenses/MPL-2.0)
[![PyPI version](https://badge.fury.io/py/TTS.svg)](https://badge.fury.io/py/TTS)
[![Covenant](https://camo.githubusercontent.com/7d620efaa3eac1c5b060ece5d6aacfcc8b81a74a04d05cd0398689c01c4463bb/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f436f6e7472696275746f72253230436f76656e616e742d76322e3025323061646f707465642d6666363962342e737667)](https://github.com/coqui-ai/TTS/blob/master/CODE_OF_CONDUCT.md)
[![Downloads](https://pepy.tech/badge/tts)](https://pepy.tech/project/tts)
[![DOI](https://zenodo.org/badge/265612440.svg)](https://zenodo.org/badge/latestdoi/265612440)

![GithubActions](https://github.com/coqui-ai/TTS/actions/workflows/aux_tests.yml/badge.svg)
![GithubActions](https://github.com/coqui-ai/TTS/actions/workflows/data_tests.yml/badge.svg)
![GithubActions](https://github.com/coqui-ai/TTS/actions/workflows/docker.yaml/badge.svg)
![GithubActions](https://github.com/coqui-ai/TTS/actions/workflows/inference_tests.yml/badge.svg)
![GithubActions](https://github.com/coqui-ai/TTS/actions/workflows/style_check.yml/badge.svg)
![GithubActions](https://github.com/coqui-ai/TTS/actions/workflows/text_tests.yml/badge.svg)
![GithubActions](https://github.com/coqui-ai/TTS/actions/workflows/tts_tests.yml/badge.svg)
![GithubActions](https://github.com/coqui-ai/TTS/actions/workflows/vocoder_tests.yml/badge.svg)
![GithubActions](https://github.com/coqui-ai/TTS/actions/workflows/zoo_tests0.yml/badge.svg)
![GithubActions](https://github.com/coqui-ai/TTS/actions/workflows/zoo_tests1.yml/badge.svg)
![GithubActions](https://github.com/coqui-ai/TTS/actions/workflows/zoo_tests2.yml/badge.svg)
[![Docs]( )](https://tts.readthedocs.io/en/latest/)

______________________________________________________________________

## 💬 Where to ask questions
Please use our dedicated channels for questions and discussion. Help is much more valuable if it's shared publicly so that more people can benefit from it.

| Type

| Platforms

|
| ------------------------------- | --------------------------------------- |
| 🚨 **Bug Reports**

| [GitHub Issue Tracker]

|
| 🎁 **Feature Requests & Ideas** | [GitHub Issue Tracker]

|
| 👩‍💻 **Usage Questions**

| [GitHub Discussions]

|
| 🗯 **General Discussion**

| [GitHub Discussions] or [Discord]

|

[github issue tracker]: https://github.com/coqui-ai/tts/issues
[github discussions]: https://github.com/coqui-ai/TTS/discussions
[discord]: https://discord.gg/5eXr5seRrv
[Tutorials and Examples]: https://github.com/coqui-ai/TTS/wiki/TTS-Notebooks-and-Tutorials

## 🔗 Links and Resources
| Type

| Links

|
| ------------------------------- | --------------------------------------- |
| 💼 **Documentation**

| [ReadTheDocs](https://tts.readthedocs.io/en/latest/)
| 💾 **Installation**

| [TTS/README.md](https://github.com/coqui-ai/TTS/tree/dev#install-tts)|
| 👩‍💻 **Contributing**

| [CONTRIBUTING.md](https://github.com/coqui-ai/TTS/blob/main/CONTRIBUTING.md)|
| 📌 **Road Map**

| [Main Development Plans](https://github.com/coqui-ai/TTS/issues/378)
| 🚀 **Released Models**

| [TTS Releases](https://github.com/coqui-ai/TTS/releases) and [Experimental Models](https://github.com/coqui-ai/TTS/wiki/Experimental-Released-Models)|
| 📰 **Papers**

| [TTS Papers](https://github.com/erogol/TTS-papers)|

## 🥇 TTS Performance

Underlined "TTS*" and "Judy*" are **internal** 🐸TTS models that are not released open-source. They are here to show the potential. Models prefixed with a dot (.Jofish .Abe and .Janice) are real human voices.

## Features
- High-performance Deep Learning models for Text2Speech tasks.

- Text2Spec models (Tacotron, Tacotron2, Glow-TTS, SpeedySpeech).

- Speaker Encoder to compute speaker embeddings efficiently.

- Vocoder models (MelGAN, Multiband-MelGAN, GAN-TTS, ParallelWaveGAN, WaveGrad, WaveRNN)
- Fast and efficient model training.
- Detailed training logs on the terminal and Tensorboard.
- Support for Multi-speaker TTS.
- Efficient, flexible, lightweight but feature complete `Trainer API`.
- Released and ready-to-use models.
- Tools to curate Text2Speech datasets under```dataset_analysis```.
- Utilities to use and test your models.
- Modular (but not too much) code base enabling easy implementation of new ideas.

## Model Implementations
### Spectrogram models
- Tacotron: [paper](https://arxiv.org/abs/1703.10135)
- Tacotron2: [paper](https://arxiv.org/abs/1712.05884)
- Glow-TTS: [paper](https://arxiv.org/abs/2005.11129)
- Speedy-Speech: [paper](https://arxiv.org/abs/2008.03802)
- Align-TTS: [paper](https://arxiv.org/abs/2003.01950)
- FastPitch: [paper](https://arxiv.org/pdf/2006.06873.pdf)
- FastSpeech: [paper](https://arxiv.org/abs/1905.09263)
- FastSpeech2: [paper](https://arxiv.org/abs/2006.04558)
- SC-GlowTTS: [paper](https://arxiv.org/abs/2104.05557)
- Capacitron: [paper](https://arxiv.org/abs/1906.03402)
- OverFlow: [paper](https://arxiv.org/abs/2211.06892)
- Neural HMM TTS: [paper](https://arxiv.org/abs/2108.13320)
- Delightful TTS: [paper](https://arxiv.org/abs/2110.12612)

### End-to-End Models
- ⓍTTS: [blog]()
- VITS: [paper](https://arxiv.org/pdf/2106.06103)
- 🐸 YourTTS: [paper](https://arxiv.org/abs/2112.02418)
- 🐢 Tortoise: [orig. repo](https://github.com/neonbjb/tortoise-tts)
- 🐶 Bark: [orig. repo](https://github.com/suno-ai/bark)

### Attention Methods
- Guided Attention: [paper](https://arxiv.org/abs/1710.08969)
- Forward Backward Decoding: [paper](https://arxiv.org/abs/1907.09006)
- Graves Attention: [paper](https://arxiv.org/abs/1910.10288)
- Double Decoder Consistency: [blog](https://erogol.com/solving-attention-problems-of-tts-models-with-double-decoder-consistency/)
- Dynamic Convolutional Attention: [paper](https://arxiv.org/pdf/1910.10288.pdf)
- Alignment Network: [paper](https://arxiv.org/abs/2108.10447)

### Speaker Encoder
- GE2E: [paper](https://arxiv.org/abs/1710.10467)
- Angular Loss: [paper](https://arxiv.org/pdf/2003.11982.pdf)

### Vocoders
- MelGAN: [paper](https://arxiv.org/abs/1910.06711)
- MultiBandMelGAN: [paper](https://arxiv.org/abs/2005.05106)
- ParallelWaveGAN: [paper](https://arxiv.org/abs/1910.11480)
- GAN-TTS discriminators: [paper](https://arxiv.org/abs/1909.11646)
- WaveRNN: [origin](https://github.com/fatchord/WaveRNN/)
- WaveGrad: [paper](https://arxiv.org/abs/2009.00713)
- HiFiGAN: [paper](https://arxiv.org/abs/2010.05646)
- UnivNet: [paper](https://arxiv.org/abs/2106.07889)

### Voice Conversion
- FreeVC: [paper](https://arxiv.org/abs/2210.15418)

You can also help us implement more models.

## Installation
🐸TTS is tested on Ubuntu 18.04 with **python >= 3.7, /coqui_studio`

```python
# XTTS model
models = TTS(cs_api_model="XTTS").list_models()
# Init TTS with the target studio speaker
tts = TTS(model_name="coqui_studio/en/Torcull Diarmuid/coqui_studio", progress_bar=False)
# Run TTS
tts.tts_to_file(text="This is a test.", file_path=OUTPUT_PATH)

# V1 model
models = TTS(cs_api_model="V1").list_models()
# Run TTS with emotion and speed control
# Emotion control only works with V1 model
tts.tts_to_file(text="This is a test.", file_path=OUTPUT_PATH, emotion="Happy", speed=1.5)

# XTTS-multilingual
models = TTS(cs_api_model="XTTS-multilingual").list_models()
# Run TTS with emotion and speed control
# Emotion control only works with V1 model
tts.tts_to_file(text="Das ist ein Test.", file_path=OUTPUT_PATH, language="de", speed=1.0)
```

#### Example text to speech using **Fairseq models in ~1100 languages** 🤯.
For Fairseq models, use the following name format: `tts_models/ /fairseq/vits`.
You can find the language ISO codes [here](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html)
and learn about the Fairseq models [here](https://github.com/facebookresearch/fairseq/tree/main/examples/mms).

```python
# TTS with on the fly voice conversion
api = TTS("tts_models/deu/fairseq/vits")
api.tts_with_vc_to_file(

"Wie sage ich auf Italienisch, dass ich dich liebe?",

speaker_wav="target/speaker.wav",

file_path="output.wav"
)
```

### Command-line `tts`
#### Single Speaker Models

- List provided models:

```

$ tts --list_models

```
- Get model info (for both tts_models and vocoder_models):

- Query by type/name:

The model_info_by_name uses the name as it from the --list_models.

```

$ tts --model_info_by_name " / / / "

```

For example:

```

$ tts --model_info_by_name tts_models/tr/common-voice/glow-tts

```

```

$ tts --model_info_by_name vocoder_models/en/ljspeech/hifigan_v2

```

- Query by type/idx:

The model_query_idx uses the corresponding idx from --list_models.

```

$ tts --model_info_by_idx " / "

```

For example:

```

$ tts --model_info_by_idx tts_models/3

```

- Run TTS with default models:

```

$ tts --text "Text for TTS" --out_path output/path/speech.wav

```

- Run a TTS model with its default vocoder model:

```

$ tts --text "Text for TTS" --model_name " / / / " --out_path output/path/speech.wav

```

For example:

```

$ tts --text "Text for TTS" --model_name "tts_models/en/ljspeech/glow-tts" --out_path output/path/speech.wav

```

- Run with specific TTS and vocoder models from the list:

```

$ tts --text "Text for TTS" --model_name " / / / " --vocoder_name " / / / " --out_path output/path/speech.wav

```

For example:

```

$ tts --text "Text for TTS" --model_name "tts_models/en/ljspeech/glow-tts" --vocoder_name "vocoder_models/en/ljspeech/univnet" --out_path output/path/speech.wav

```

- Run your own TTS model (Using Griffin-Lim Vocoder):

```

$ tts --text "Text for TTS" --model_path path/to/model.pth --config_path path/to/config.json --out_path output/path/speech.wav

```

- Run your own TTS and Vocoder models:

```

$ tts --text "Text for TTS" --model_path path/to/model.pth --config_path path/to/config.json --out_path output/path/speech.wav

--vocoder_path path/to/vocoder.pth --vocoder_config_path path/to/vocoder_config.json

```

#### Multi-speaker Models

- List the available speakers and choose a

among them:

```

$ tts --model_name " / / " --list_speaker_idxs

```

- Run the multi-speaker TTS model with the target speaker ID:

```

$ tts --text "Text for TTS." --out_path output/path/speech.wav --model_name " / / " --speaker_idx

```

- Run your own multi-speaker TTS model:

```

$ tts --text "Text for TTS" --out_path output/path/speech.wav --model_path path/to/model.pth --config_path path/to/config.json --speakers_file_path path/to/speaker.json --speaker_idx

```

## Directory Structure
```
|- notebooks/

(Jupyter Notebooks for model evaluation, parameter selection and data analysis.)
|- utils/

(common utilities.)
|- TTS

|- bin/

(folder for all the executables.)

|- train*.py

(train your target model.)

|- ...

|- tts/

(text to speech models)

|- layers/

(model layer definitions)

|- models/

(model definitions)

|- utils/

(model specific utilities.)

|- speaker_encoder/ (Speaker Encoder models.)

|- (same)

|- vocoder/

(Vocoder models.)

|- (same)
```