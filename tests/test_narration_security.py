"""Keep untrusted narration content outside FFmpeg's format autodetection."""

from io import BytesIO
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import wave


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("prepare_narrations", ROOT / "tools/prepare_narrations.py")
narrations = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = narrations
SPEC.loader.exec_module(narrations)


def pcm_wav(seconds=1, rate=8000):
    output = BytesIO()
    with wave.open(output, "wb") as stream:
        stream.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        samples = (round(8000 * math.sin(2 * math.pi * 220 * i / rate))
                   for i in range(round(seconds * rate)))
        stream.writeframes(b"".join(struct.pack("<h", sample) for sample in samples))
    return output.getvalue()


def riff(*chunks):
    body = b"WAVE" + b"".join(tag + struct.pack("<I", len(data)) + data + b"\0" * (len(data) % 2)
                               for tag, data in chunks)
    return b"RIFF" + struct.pack("<I", len(body)) + body


def format_chunk(codec=1, channels=1, rate=8000, bits=16, *, byte_rate=None, alignment=None):
    align = channels * (bits // 8) if alignment is None else alignment
    return struct.pack("<HHIIHH", codec, channels, rate,
                       rate * align if byte_rate is None else byte_rate, align, bits)


class NarrationSecurityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.input = self.directory / "input"
        self.input.mkdir()

    def load(self, content, name="narration.WAV"):
        loader = getattr(narrations, "load_narration", None)
        self.assertTrue(callable(loader), "Narrations need a validated, retained-byte input boundary")
        path = self.input / name
        path.write_bytes(content)
        return loader(self.input, name)

    def test_disguised_playlist_is_rejected_before_any_source_decoder(self):
        (self.input / "story.WAV").write_text("#EXTM3U\nhttp://example.invalid/never-request.mp3\n")
        selection = self.directory / "selection.json"
        selection.write_text(json.dumps({"island": {"file": "story.WAV"}}))
        decoders = []

        def tool(command, **kwargs):
            if command == ["ffmpeg", "-version"]:
                return subprocess.CompletedProcess(command, 0, b"ffmpeg test\n", b"")
            decoders.append(command)
            raise RuntimeError("A source decoder was reached")

        failure = None
        arguments = ["prepare_narrations.py", "--input-dir", str(self.input), "--selection", str(selection),
                     "--output-dir", str(self.directory / "output")]
        with patch.object(sys, "argv", arguments), patch.object(narrations, "run", side_effect=tool):
            try:
                narrations.main()
            except (ValueError, RuntimeError) as error:
                failure = error
        self.assertIsInstance(failure, ValueError)
        self.assertEqual(decoders, [], "Unsafe content must not reach ffprobe or ffmpeg")

    def test_wav_content_is_validated_independently_of_its_filename(self):
        data = pcm_wav()
        source = self.load(data, "narration.binary")
        self.assertEqual(source.data, data)
        self.assertEqual(source.name, "narration.binary")
        self.assertEqual(source.seconds, 1)

    def test_accepts_pcm_float_and_extensible_audio_with_consistent_frames(self):
        for codec, widths in [(1, [8, 16, 24, 32]), (3, [32, 64])]:
            for bits in widths:
                for extensible in [False, True]:
                    with self.subTest(codec=codec, bits=bits, extensible=extensible):
                        sample = b"\0" * (bits // 8)
                        fmt = format_chunk(codec=codec, bits=bits)
                        if extensible:
                            fmt = (format_chunk(codec=0xFFFE, bits=bits) + struct.pack("<HHI", 22, bits, 4)
                                   + struct.pack("<I", codec) + bytes.fromhex("00001000800000aa00389b71"))
                        source = self.load(riff((b"JUNK", b"padding"), (b"fmt ", fmt), (b"data", sample)))
                        self.assertEqual(source.seconds, 1 / 8000)

    def test_rejects_excessive_chunk_counts(self):
        data = riff((b"fmt ", format_chunk()), *[(b"JUNK", b"")] * 10000, (b"data", b"\0\0"))
        with self.assertRaises(ValueError):
            self.load(data)

    def test_rejects_malformed_riff_and_unsafe_audio_parameters(self):
        valid = pcm_wav()
        malformed = {
            "fake-riff": b"RIFF\x04\0\0\0WAVE",
            "renamed-concat": b"ffconcat version 1.0\nfile '../outside.wav'\n",
            "wrong-form": valid[:8] + b"AVI " + valid[12:],
            "trailing-bytes": valid + b"http://example.invalid/other.wav",
            "truncated": valid[:-1],
            "oversized-chunk": riff((b"fmt ", format_chunk())) + b"data\xff\xff\xff\xff",
            "missing-data": riff((b"fmt ", format_chunk())),
            "duplicate-data": riff((b"fmt ", format_chunk()), (b"data", b"\0\0"), (b"data", b"\0\0")),
            "duplicate-format": riff((b"fmt ", format_chunk()), (b"fmt ", format_chunk()), (b"data", b"\0\0")),
            "data-before-format": riff((b"data", b"\0\0"), (b"fmt ", format_chunk())),
            "compressed-codec": riff((b"fmt ", format_chunk(codec=85)), (b"data", b"\0\0")),
            "bad-byte-rate": riff((b"fmt ", format_chunk(byte_rate=1)), (b"data", b"\0\0")),
            "bad-alignment": riff((b"fmt ", format_chunk(alignment=1)), (b"data", b"\0\0")),
            "bad-channels": riff((b"fmt ", format_chunk(channels=0)), (b"data", b"\0\0")),
            "too-many-channels": riff((b"fmt ", format_chunk(channels=3)), (b"data", b"\0" * 6)),
            "bad-rate": riff((b"fmt ", format_chunk(rate=0)), (b"data", b"\0\0")),
            "excessive-rate": riff((b"fmt ", format_chunk(rate=192001)), (b"data", b"\0\0")),
            "bad-width": riff((b"fmt ", format_chunk(bits=7)), (b"data", b"\0\0")),
            "bad-float-width": riff((b"fmt ", format_chunk(codec=3, bits=16)), (b"data", b"\0\0")),
            "missing-extensible-fields": riff((b"fmt ", format_chunk(codec=0xFFFE)), (b"data", b"\0\0")),
            "secondary-wavl": riff((b"fmt ", format_chunk()), (b"LIST", b"wavl"), (b"data", b"\0\0")),
            "secondary-video": riff((b"fmt ", format_chunk()), (b"SMV0", b"\0" * 32), (b"data", b"\0\0")),
            "partial-frame": riff((b"fmt ", format_chunk()), (b"data", b"\0")),
            "empty-data": riff((b"fmt ", format_chunk()), (b"data", b"")),
        }
        for label, data in malformed.items():
            with self.subTest(label=label), self.assertRaises(ValueError):
                self.load(data)

    def test_rejects_duration_and_byte_limits_before_decoding(self):
        with patch.object(narrations, "MAX_NARRATION_SECONDS", 0.5, create=True), self.assertRaises(ValueError):
            self.load(pcm_wav())
        with patch.object(narrations, "MAX_INPUT_BYTES", 100, create=True), self.assertRaises(ValueError):
            self.load(pcm_wav())

    def test_rejects_paths_and_symlinks_that_can_escape_the_input_directory(self):
        loader = getattr(narrations, "load_narration", None)
        self.assertTrue(callable(loader))
        outside = self.directory / "outside.wav"
        outside.write_bytes(pcm_wav())
        (self.input / "link.wav").symlink_to(outside)
        (self.input / "nested").symlink_to(self.directory, target_is_directory=True)
        for filename in ["../outside.wav", str(outside), "link.wav", "nested/outside.wav"]:
            with self.subTest(filename=filename), self.assertRaises(ValueError):
                loader(self.input, filename)

    def test_portable_reader_preserves_valid_wav_and_rejects_escaping_paths(self):
        data = pcm_wav()
        (self.input / "story.wav").write_bytes(data)
        outside = self.directory / "outside.wav"
        outside.write_bytes(data)
        (self.input / "link.wav").symlink_to(outside)
        with patch.dict(narrations.os.__dict__):
            narrations.os.__dict__.pop("O_DIRECTORY", None)
            narrations.os.supports_dir_fd = set()
            try:
                source = narrations.load_narration(self.input, "story.wav")
            except (AttributeError, TypeError, NotImplementedError) as error:
                self.fail(f"Normal WAV input must also work without POSIX descriptor traversal: {error}")
            self.assertEqual(source.data, data)
            for filename in ["../outside.wav", str(outside), "link.wav"]:
                with self.subTest(filename=filename), self.assertRaises(ValueError):
                    narrations.load_narration(self.input, filename)

    def test_source_decoders_use_retained_validated_bytes_and_pipe_only(self):
        data = pcm_wav()
        source = self.load(data)
        (self.input / "narration.WAV").write_bytes(b"#EXTM3U\nhttp://example.invalid/changed\n")
        commands = []
        measurements = b'{"input_i":"-19","input_tp":"-4","input_lra":"1","input_thresh":"-30","target_offset":"0"}'

        def tool(command, **kwargs):
            commands.append((command, kwargs))
            return subprocess.CompletedProcess(command, 0, struct.pack("<f", 0.1) * 8000, measurements)

        with patch.object(narrations, "run", side_effect=tool):
            seconds = narrations.duration(source)
            narrations.trim_bounds(source, seconds)
            try:
                narrations.normalize_voice(source, 0, seconds)
            except RuntimeError as error:
                if "NumPy" not in str(error):
                    raise
        self.assertGreaterEqual(len(commands), 1)
        for command, kwargs in commands:
            self.assertEqual(command[command.index("-i") + 1], "pipe:0")
            self.assertEqual(command[command.index("-protocol_whitelist") + 1], "pipe")
            self.assertEqual(command[command.index("-f") + 1], "wav")
            self.assertIn("-c:a", command, "The decoder must use the validated sample container width")
            self.assertEqual(command[command.index("-c:a") + 1], "pcm_s16le")
            self.assertEqual(kwargs["data"], data)
            self.assertNotIn(str(self.input / "narration.WAV"), command)

    def test_tools_are_stopped_on_timeout_and_output_overflow(self):
        with patch.object(narrations, "TOOL_TIMEOUT_SECONDS", 0.1, create=True):
            start = time.monotonic()
            with self.assertRaisesRegex(RuntimeError, "timed out"):
                narrations.run([sys.executable, "-c", "import time; time.sleep(5)"])
            self.assertLess(time.monotonic() - start, 3)
        for target in ["stdout", "stderr"]:
            with self.subTest(target=target), self.assertRaisesRegex(RuntimeError, "output limit"):
                narrations.run([sys.executable, "-c", f"import sys; sys.{target}.write('x'*2000000)"],
                               stdout_limit=1024)

    def test_generated_mp3_duration_is_decoded_only_as_mp3_over_pipe(self):
        commands = []

        def tool(command, **kwargs):
            commands.append((command, kwargs))
            return subprocess.CompletedProcess(command, 0,
                b'{"packets":[{"duration":368640},{"duration":368640}],"streams":[{"time_base":"1/14112000"}]}', b"")

        with patch.object(narrations, "run", side_effect=tool):
            self.assertAlmostEqual(narrations.mp3_duration(b"generated mp3 bytes"), 2304 / 44100)
        command, kwargs = commands[0]
        self.assertEqual(command[command.index("-protocol_whitelist") + 1], "pipe")
        self.assertEqual(command[command.index("-f") + 1], "mp3")
        self.assertEqual(command[command.index("-i") + 1], "pipe:0")
        self.assertEqual(kwargs["data"], b"generated mp3 bytes")


class NarrationAudioControlTests(unittest.TestCase):
    def test_real_extensible_pcm_decoder_obeys_container_width(self):
        if not shutil.which("ffmpeg"):
            self.skipTest("The optional decoder control needs FFmpeg")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for bits, valid_bits in [(32, 8), (32, 24), (24, 16)]:
                with self.subTest(bits=bits, valid_bits=valid_bits):
                    fmt = (format_chunk(codec=0xFFFE, bits=bits) + struct.pack("<HHI", 22, valid_bits, 4)
                           + struct.pack("<I", 1) + bytes.fromhex("00001000800000aa00389b71"))
                    half_scale = (1 << (bits - 2)).to_bytes(bits // 8, "little")
                    (root / "container.wav").write_bytes(riff((b"fmt ", fmt), (b"data", half_scale * 8000)))
                    source = narrations.load_narration(root, "container.wav")
                    builder = getattr(narrations, "wav_input_arguments", None)
                    self.assertTrue(callable(builder), "All source decoders need one validated container-width boundary")
                    decoded = narrations.ffmpeg(*builder(source), "-f", "f32le", "-c:a", "pcm_f32le", "pipe:1",
                                                data=source.data)
                    self.assertEqual(source.seconds, 1)
                    self.assertEqual(len(decoded.stdout), 8000 * 4)
                    self.assertEqual(struct.unpack_from("<f", decoded.stdout)[0], 0.5)

    def test_real_normalization_trims_pipe_input_before_processing(self):
        if importlib.util.find_spec("numpy") is None or not shutil.which("ffmpeg"):
            self.skipTest("The optional DSP control needs NumPy and FFmpeg")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "story.wav").write_bytes(pcm_wav(seconds=3, rate=44100))
            source = narrations.load_narration(root, "story.wav")
            voice, _ = narrations.normalize_voice(source, 0.4, 2.7)
            self.assertEqual(voice.size, 101430)

    def test_real_cli_preserves_source_and_produces_both_narrations(self):
        if importlib.util.find_spec("numpy") is None or not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            self.skipTest("The optional DSP control needs NumPy and FFmpeg")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "story.WAV"
            source.write_bytes(pcm_wav(seconds=3, rate=44100))
            original = source.read_bytes()
            selection = root / "selection.json"
            selection.write_text(json.dumps({"test-island": {"file": "story.WAV", "ambience": "sea"}}))
            output = root / "output"
            report = root / "report.json"
            result = subprocess.run([sys.executable, str(ROOT / "tools/prepare_narrations.py"),
                                     "--input-dir", str(root), "--selection", str(selection),
                                     "--output-dir", str(output), "--report", str(report)],
                                    capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(source.read_bytes(), original)
            recording = json.loads(report.read_text())["recordings"]["test-island"]
            self.assertEqual(recording["original_sha256"], hashlib.sha256(original).hexdigest())
            self.assertEqual(recording["original_duration_seconds"], 3)
            self.assertEqual(recording["normalization"]["passes"], 2)
            self.assertEqual(recording["sound_recreation"]["profile"], "sea")
            for kind in ["voice", "ambient"]:
                artifact = output / recording[kind]["file"]
                self.assertGreater(artifact.stat().st_size, 1000)
                self.assertEqual(hashlib.sha256(artifact.read_bytes()).hexdigest(), recording[kind]["sha256"])
                self.assertLessEqual(recording[kind]["true_peak_dbfs"], -1.5)
                self.assertGreater(recording[kind]["duration_seconds"], 2.9 if kind == "voice" else 7.9)


if __name__ == "__main__":
    unittest.main()
