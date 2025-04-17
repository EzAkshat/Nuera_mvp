import pyaudio
import pvporcupine
import speech_recognition as sr
import time

class SST:
    def __init__(self, access_key, keyword_path):
        self.porcupine = pvporcupine.create(access_key=access_key, keyword_paths=[keyword_path])
        self.pa = pyaudio.PyAudio()
        self.audio_stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.5

    def listen_for_wake_word(self):
        last_print_time = time.time()
        start_time = time.time()
        timeout = 60  # 1 minute timeout before switching to fallback
        while True:
            try:
                pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm = [int.from_bytes(pcm[i:i+2], 'little', signed=True) for i in range(0, len(pcm), 2)]
                result = self.porcupine.process(pcm)
                if result >= 0:
                    return True
                if time.time() - start_time > timeout:
                    return self.listen_for_wake_word_fallback()
            except Exception as e:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = self.pa.open(
                    rate=self.porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=self.porcupine.frame_length
                )
                start_time = time.time()
            time.sleep(0.01)

    def listen_for_wake_word_fallback(self):
        with sr.Microphone() as source:
            try:
                audio = self.recognizer.listen(source, timeout=10)
                command = self.recognizer.recognize_google(audio).lower()
                if "nuera" in command:
                    return True
                else:
                    return False
            except Exception as e:
                return False

    def listen_for_command(self):
        with sr.Microphone() as source:
            try:
                audio = self.recognizer.listen(source, timeout=30, phrase_time_limit=None)
                command = self.recognizer.recognize_google(audio)
                return command
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None
            except sr.RequestError as e:
                return None

    def close(self):
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.pa.terminate()
        self.porcupine.delete()