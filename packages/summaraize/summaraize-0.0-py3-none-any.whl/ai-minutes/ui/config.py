"""Texts to show in UI elements"""
# pylint: disable=invalid-name

ffmpeg_missing_text = """
This application requires ffmpeg to be installed and
the directory containing ffmpeg executable needs
to be on the system path.

Please download and install from:
https://ffmpeg.org
"""
api_key_label_text = """
OpenAI API key is required.

Instructions to create an API key can be found from:
https://platform.openai.com/docs/quickstart?context=python

Exporting api key into environment variables skips this manual input phase
"""
select_video_label_text = """
Choose the video recording and the language used in the recording.

Application extracts audio track from video recording with FFmpeg and
converts it to text transcript with OpenAI Whisper speech to text model.
FFmpeg supports most common video formats.

You can create summaries of the transcript with ChatGPT4-turbo
in the next page after the video file is converted to text.

"FFmpeg is a complete, cross-platform solution to record, convert and stream audio and video."
https://ffmpeg.org

"Whisper approaches human level robustness and accuracy
on English speech recognition."
https://openai.com/research/whisper
"""
prompt_template_text = """
Examples:

"Hello, I have a transcript from a [type of event/meeting/discussion,
e.g., 'marketing strategy meeting'] that took place on [date, if relevant].
The main topics discussed were [list main topics briefly].
Given this context, I need a concise summary that captures the key points,
decisions made, and any action items or conclusions drawn from the discussion.
The summary should be clear, neutral, and informative, suitable for
[mention to whom] who wasn’t present at the meeting.
Please keep the summary within [specify word count or paragraph limit, if any]."

"Create a battlecard of [solution] for sales people from the following transcript.
Make an executive summary of the technology.
Summarize all sales key arguments.
Highlight the benefits over competition."
"""

# Supported languages from:
# https://platform.openai.com/docs/guides/speech-to-text/supported-languages
whisper_languages = {'Afrikaans': 'af', 'Arabic': 'ar', 'Armenian': 'hy',
                     'Azerbaijani': 'az', 'Belarusian': 'be', 'Bosnian': 'bs',
                     'Bulgarian': 'bg', 'Chinese': 'zh', 'Croatian': 'hr', 'Czech': 'cs',
                     'Danish': 'da', 'English': 'en', 'Estonian': 'et', 'Finnish': 'fi',
                     'French': 'fr', 'Galician': 'gl', 'German': 'de', 'Hebrew': 'he',
                     'Hindi': 'hi', 'Hungarian': 'hu', 'Icelandic': 'is', 'Indonesian': 'id',
                     'Italian': 'it', 'Japanese': 'ja', 'Kannada': 'kn', 'Kazakh': 'kk',
                     'Korean': 'ko', 'Latvian': 'lv', 'Lithuanian': 'lt', 'Macedonian': 'mk',
                     'Malay': 'ms', 'Maori': 'mi', 'Marathi': 'mr', 'Nepali': 'ne',
                     'Norwegian': 'no', 'Persian': 'fa', 'Polish': 'pl', 'Portuguese': 'pt',
                     'Russian': 'ru', 'Serbian': 'sr', 'Slovak': 'sk', 'Slovenian': 'sl',
                     'Swahili': 'sw', 'Swedish': 'sv', 'Tagalog': 'tl', 'Tamil': 'ta',
                     'Thai': 'th', 'Turkish': 'tr', 'Ukrainian': 'uk', 'Urdu': 'ur',
                     'Vietnamese': 'vi'}
