from aiohttp import ClientSession, TCPConnector
from models.transcription import TranscriptionResult, Word
import ssl
import certifi
import json

class DeepgramService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepgram.com/v1/listen"
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    async def download_file(self, url: str) -> bytes:
        async with ClientSession(connector=TCPConnector(ssl=self.ssl_context)) as session:
            async with session.get(url) as response:
                return await response.read()

    async def transcribe_audio(self, file_url: str) -> TranscriptionResult:
        audio_data = await self.download_file(file_url)
        
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/octet-stream"
        }
        
        params = {
            "language": "ru",
            "model": "nova-2",
            "punctuate": "true",
            "paragraphs": "true",
            "smart_format": "true",
            "profanity_filter": "false",
        }

        async with ClientSession(connector=TCPConnector(ssl=self.ssl_context)) as session:
            async with session.post(self.base_url, headers=headers, params=params, data=audio_data) as response:
                result = await response.json()
                alternative = result["results"]["channels"][0]["alternatives"][0]
                
                # Преобразуем слова из Deepgram в наш формат
                words = []
                for word_data in alternative.get("words", []):
                    words.append(Word(
                        word=word_data["word"],
                        start=word_data["start"],
                        end=word_data["end"],
                        confidence=word_data["confidence"]
                    ))
                
                return TranscriptionResult(
                    text=alternative["transcript"],
                    confidence=alternative["confidence"],
                    words=words
                )
