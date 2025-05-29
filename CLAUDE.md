# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py

# Run with Docker
docker-compose up --build
```

## High-Level Architecture

### Core Flow
1. **Message Reception**: Bot receives audio/video through Telegram handlers (`handlers/voice.py`, `handlers/audio.py`, `handlers/video.py`)
2. **Transcription**: Audio is sent to Deepgram API via `services/deepgram.py` using Nova-2 model with Russian language support
3. **Text Processing**: Optional style processing through Anthropic Claude API (`services/anthropic.py`) using prompts from `prompts/` directory
4. **Response**: Formatted text is sent back to user with optional style selection keyboard

### Key Integration Points

#### Deepgram Integration (`services/deepgram.py`)
- Uses aiohttp with SSL context for secure connections
- Downloads media files from Telegram servers before transcription
- Returns structured `TranscriptionResult` with word-level timing and confidence scores
- Parameters: Russian language, punctuation, paragraphs, smart formatting

#### Anthropic Integration (`services/anthropic.py`)
- Synchronous client wrapped in async handlers
- Loads prompts dynamically from `prompts/` directory based on selected style
- Uses Claude 3 Haiku model for fast processing
- Styles: proofread, my (informal), business, brief

#### Message Flow Architecture
- All handlers use the same pattern: download file → transcribe → format → send response
- Long messages are automatically split using `utils/formatting.py`
- Style selection is handled via callback queries in `handlers/style.py`
- Each handler includes comprehensive error handling and logging

### Configuration
- Environment variables loaded via Pydantic settings in `config/config.py`
- Required: `BOT_TOKEN`, `DEEPGRAM_API_KEY`, `ANTHROPIC_API_KEY`
- Logging configured with loguru for both console and file output

### Data Models
- `models/transcription.py` defines structured response format
- Pydantic models ensure type safety and validation
- Models include: `Word`, `Paragraph`, `TranscriptionResult`