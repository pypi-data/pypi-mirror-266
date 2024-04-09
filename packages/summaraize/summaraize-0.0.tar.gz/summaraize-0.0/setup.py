from setuptools import setup, find_packages

long_description = """
A Python library for analyzing meeting/event video recordings with cloud hosted AI.

Save time and enhance efficiency by using AI to generate summaries, battle cards, meeting minutes, 
sales arguments and action item lists directly from recordings.
Hone your prompt engineering skills to distill the desired information.

## Technology

The video recording is transformed into a text transcript using the FFmpeg library 
and the OpenAI Whisper speech-to-text model. 
Then, the OpenAI ChatGPT-4 Turbo model analyzes and summarizes the transcript 
according to the user's prompt. The user interface (UI) is developed with the 
Tkinter library, part of the standard Python distribution, and styled using 
the ttkbootstrap library.

## Supported languages

From: https://platform.openai.com/docs/guides/speech-to-text/supported-languages

OpenAI lists the languages that exceeded <50% word error rate (WER),
which is an industry standard benchmark for speech to text model accuracy.

Afrikaans, Arabic, Armenian, Azerbaijani, Belarusian, Bosnian, Bulgarian, Catalan, Chinese,
Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, Galician, German, Greek,
Hebrew, Hindi, Hungarian, Icelandic, Indonesian, Italian, Japanese, Kannada, Kazakh, Korean,
Latvian, Lithuanian, Macedonian, Malay, Marathi, Maori, Nepali, Norwegian, Persian, Polish,
Portuguese, Romanian, Russian, Serbian, Slovak, Slovenian, Spanish, Swahili, Swedish, Tagalog,
Tamil, Thai, Turkish, Ukrainian, Urdu, Vietnamese, and Welsh.

## Requirements

- Ffmpeg needs to be installed and set in path. https://ffmpeg.org
- OpenAI API key to access Whisper and GPT4-Turbo models. https://platform.openai.com/docs/quickstart
- Python3.7 or newer

## Install Application

```python
python -m pip install ai-minutes
```

## Install FFmpeg

**Mac**

```bash
brew install ffmpeg
```

**Windows**

Follow instructions in this arcticle:
https://phoenixnap.com/kb/ffmpeg-windows


## Run

```python
python -m ai-minutes
```

## UI themes

Application support UI themes from:
https://ttkbootstrap.readthedocs.io/en/latest/themes/

list available themes:

```python
python -m ai-minutes -h
```

use a theme by giving theme name as an argument:

```python
python -m ai-minutes cyborg
```

"""

setup(
    name="summaraize",
    version="0.0",
    author="Jussi Löppönen",
    description="A Python library for analyzing meeting/event video recordings with cloud hosted AI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/juslop/ai-minutes",
    packages=find_packages(where="src"),
    package_dir = {"": "src"},
    install_requires=["openai", "ttkbootstrap"],
    python_requires=">=3.7",
)
