import wave
from kairos.logging import get_logger


class AudioRecorder:
    def __init__(self, filename: str = "output.wav", channels=1, rate=44100, chunk=1024):
        self.filename = filename
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self._pa = None
        self.stream = None
        self.log = get_logger("kairos.audio.recorder")

    def _ensure_pa(self):
        if self._pa is None:
            try:
                from pyaudio import PyAudio, paInt16  # type: ignore
            except Exception as e:  # noqa: BLE001
                raise RuntimeError("PyAudio is required for recording but is not installed") from e
            self._pa = (PyAudio, paInt16)
        return self._pa

    def start_recording(self):
        PyAudio, paInt16 = self._ensure_pa()
        audio = PyAudio()
        self.stream = audio.open(
            format=paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )
        self.log.info("Recording started")

        frames = []
        try:
            while True:
                data = self.stream.read(self.chunk)
                frames.append(data)
        except KeyboardInterrupt:
            self.log.info("Recording stopped by user")

        self.stop_recording(frames, audio, paInt16)

    def stop_recording(self, frames, audio=None, paInt16=None):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if audio:
            audio.terminate()

        if paInt16 is None:
            # Fetch sample width via fresh PyAudio if available
            PyAudio, paInt16 = self._ensure_pa()
            audio = PyAudio()
            sample_size = audio.get_sample_size(paInt16)
            audio.terminate()
        else:
            sample_size = audio.get_sample_size(paInt16) if audio else 2

        with wave.open(self.filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(sample_size)
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
        self.log.info("Recording saved to %s", self.filename)
