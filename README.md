# virtual clone

ai powered chat system with audio transcription capabilities. Built with Flask, Whisper AI, and transformer models

## quick start

**prerequisites:** Python 3.11+

```bash
git clone https://github.com/rmant7/VirtualClone
cd VirtualClone
git checkout develop
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

Access: `http://localhost:5050`

## Features

- **AI Chat System**: Context-aware conversations with response diversity
- **Audio Transcription**: Real-time processing with Whisper AI
- **Multilingual Support**: Auto-translation for multiple languages
- **Document Processing**: Upload and process PDFs, audio files
- **Link Processing**: Extract content from YouTube links

## Key Improvements

- Fixed response repetition issues
- Conversation memory and context awareness
- Smart response selection with multiple candidates
- Efficient session management

## Usage

**Chat Interface:** `http://localhost:5050`
**Audio Transcription:** `python realtime_transcription.py`
**Document Upload:** `http://localhost:5050/upload`
**Link Processing:** `http://localhost:5050/links`

## Development

```bash
python test_conversation_context.py  
python test_conversation_demo.py     
```

