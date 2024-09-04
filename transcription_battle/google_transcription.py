import queue
import time

from google.cloud import speech

import os
from transcription_battle.audio_capture import AudioCapture

STREAMING_LIMIT = 240000  # 4 minutes
SAMPLE_RATE = 16000
CHUNK_SIZE = 100  # 100ms

DARK_BLUE = "\033[94m"
DEFAULT = "\033[0m"
PURPLE = "\033[95m"
RED = "\033[91m"


def get_current_time() -> int:
    """Return Current Time in MS."""
    return int(round(time.time() * 1000))


class GoogleTranscription:
    """Controls the audio capture and transcription process."""

    def __init__(self):
        self.transcription_buffer = queue.Queue()
        self._audio_stream = None
        self.start_time = get_current_time()
        self.final_transcripts = []

    def transcribe_voice(self, language_code="en-US", streaming_limit=STREAMING_LIMIT):
        "opens audio stream and serves responses through a generator."

        # starts bidirectional streaming from microphone input to speech API
        client = speech.SpeechClient()

        # configures general seeting for recognition
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code=language_code,
            max_alternatives=1,
            enable_automatic_punctuation=True,
            model="latest_long",
        )

        # configures streaming settings for recognition
        streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)

        # instantiate the audio input stream. The input must be in 16-bit mono format
        audio_capture = AudioCapture(SAMPLE_RATE, CHUNK_SIZE)

        # opens the audio stream and starts recording
        with audio_capture as stream:
            os.system("clear")
            print(RED + f"Listening:\n\n" + DEFAULT)
            stream.audio_input = []
            audio_generator = stream.generator()

            # creates the requests generator that iterates through the audio chunks and sends them to the speech API
            requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)

            # sends the requests generator to the speech API and returns a responses generator
            # print the interim results
            responses = client.streaming_recognize(streaming_config, requests)

            while not stream.closed:
                if get_current_time() - self.start_time > streaming_limit:
                    stream.closed = True
                    self.closed = True
                    break

                for response in responses:
                    if not response.results:
                        continue

                    result = response.results[0]

                    if not result.alternatives:
                        continue

                    transcript = result.alternatives[0].transcript
                    if result.is_final:
                        self.final_transcripts.append(transcript)
                        transcript = ""

                    os.system("clear")
                    print(RED + f"Listening: {transcript}\n\n" + DEFAULT)

                    if self.final_transcripts:
                        transcripts = "\n".join(reversed(self.final_transcripts))
                        print(PURPLE + "** Finalized **" + DEFAULT)
                        print(DARK_BLUE + transcripts + DEFAULT)
