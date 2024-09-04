from transcription_battle.google_transcription import GoogleTranscription
from transcription_battle.deepgram_transcription import DeepgramTranscription

import os

DARK_GREEN = "\033[92m"
DEFAULT = "\033[0m"

if __name__ == "__main__":
    os.system("clear")
    try:
        selection = input(DARK_GREEN + "Enter g for google or d for deepgram: \n" + DEFAULT)
        if selection == "g":
            GoogleTranscription().transcribe_voice()
        else:
            DeepgramTranscription().transcribe_voice()
    except KeyboardInterrupt:
        print("Transcription stopped.")
