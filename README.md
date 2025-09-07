realtime_transcription.py
This script uses the faster_whisper model to transcribe audio from an audio/video file or live from your microphone.  Simply run python realtime_transcription.py to begin live
transcription; the application will process audio in real-time, show the language that has been detected, and print the text every few seconds.  The script will transcribe the entire
file with timestamps and display the detected language if you run python realtime_transcription.py --file /path/to/file.  To end live transcription, press Ctrl + C.  Make sure you
have installed Python 3.8+ and the necessary packages (faster-whisper, numpy, and sounddevice).
