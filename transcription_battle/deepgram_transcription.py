import queue
import time

from deepgram import DeepgramClient, DeepgramClientOptions, LiveTranscriptionEvents, LiveOptions

import os
from transcription_battle.audio_capture import AudioCapture

STREAMING_LIMIT = 240000  # 4 minutes
SAMPLE_RATE = 16000
CHUNK_SIZE = 100  # 100ms

DARK_BLUE = "\033[94m"
DEFAULT = "\033[0m"
PURPLE = "\033[95m"
RED = "\033[91m"

OPTIONS = LiveOptions(
    model="nova-2",
    language="en-US",
    # Apply smart formatting to the output
    smart_format=True,
    # Raw audio format details
    encoding="linear16",
    channels=1,
    sample_rate=16000,
    # To get UtteranceEnd, the following must be set:
    interim_results=True,
    utterance_end_ms="1000",
    vad_events=True,
    # Time in milliseconds of silence to wait for before finalizing speech
    endpointing=300,
)


def get_current_time() -> int:
    """Return Current Time in MS."""
    return int(round(time.time() * 1000))


class DeepgramTranscription:
    """Controls the audio capture and transcription process."""

    def __init__(self):
        self.transcription_buffer = queue.Queue()
        self._audio_stream = None
        self.start_time = get_current_time()
        self.final_transcripts = []
        self.dg_connection = self._build_connection()

    def _build_connection(self):
        config = DeepgramClientOptions(options={"keepalive": "true"})

        deepgram = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"), config)

        dg_connection = deepgram.listen.websocket.v("1")
        dg_connection.on(LiveTranscriptionEvents.Transcript, self.on_message)
        options = OPTIONS

        dg_connection.start(options)
        return dg_connection

    def transcribe_voice(self, language_code="en-US", streaming_limit=STREAMING_LIMIT):
        "opens audio stream and serves responses through a generator."

        # instantiate the audio input stream. The input must be in 16-bit mono format
        audio_capture = AudioCapture(SAMPLE_RATE, CHUNK_SIZE)

        # opens the audio stream and starts recording
        with audio_capture as stream:
            os.system("clear")
            print(RED + f"Listening:\n\n" + DEFAULT)
            stream.audio_input = []
            audio_generator = stream.generator()

            while not stream.closed:
                for content in audio_generator:
                    self.dg_connection.send(content)

    def on_message(self, _socket_client, result):
        transcript = result.channel.alternatives[0].transcript
        if transcript:
            if result.speech_final:
                self.final_transcripts.append(transcript)
                transcript = ""

            os.system("clear")
            print(RED + f"Listening: {transcript}\n\n" + DEFAULT)

            if self.final_transcripts:
                transcripts = "\n".join(reversed(self.final_transcripts))
                print(PURPLE + "** Finalized **" + DEFAULT)
                print(DARK_BLUE + transcripts + DEFAULT)
