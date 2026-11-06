"""
Audio Speech Recognition (ASR) service for Hausa and English voice notes.
Provides integration points for Whisper / Google Speech-to-Text (ha-NG)
and an intelligent fallback/mock transcriber for local testing.
"""

import os
from typing import Tuple

class ASRService:
    def __init__(self):
        self.google_stt_enabled = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

    async def transcribe_audio_file(self, file_path: str, hint_language: str = "ha") -> Tuple[str, str, float]:
        """
        Transcribes the supplied audio file.
        Returns: (transcription_text, detected_language, duration_seconds)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        file_size_bytes = os.path.getsize(file_path)
        # Approximate duration estimation based on standard audio bitrates
        estimated_duration = round(file_size_bytes / (16000 * 2), 2)

        # In production with API keys:
        # e.g., call google.cloud.speech_v1 or openai.Audio.transcribe with model="whisper-1"
        # For this prototype, we support simulated voice memos and local test samples
        
        # Check if the filename itself or companion .txt gives test transcription
        txt_companion = os.path.splitext(file_path)[0] + ".txt"
        if os.path.exists(txt_companion):
            with open(txt_companion, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return content, hint_language, estimated_duration

        # Default simulated transcription for audio test files
        default_transcript = (
            "Yaro na yana fama da zazzabi da amai tun jiya, kuma ya daina shan nono."
            if hint_language == "ha"
            else "My child has had high fever and vomiting since yesterday and has stopped breastfeed."
        )
        return default_transcript, hint_language, max(estimated_duration, 3.5)

asr_service = ASRService()
