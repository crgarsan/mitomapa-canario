#!/usr/bin/env python3
"""Prepare narration MP3s and an optional, reproducible sound recreation.

The short introduction models low drum resonances and wooden percussion
inspired by chacaras. Wind and sea are filtered noise, not field recordings.
This is a recreacion sonora, not a recording of authentic Canarian instruments.
The percussion ends before the voice; nature fades within its first six seconds.

Requires Python 3, numpy, ffmpeg (with libmp3lame) and ffprobe. Originals are
never modified. Inputs must contain self-contained RIFF/WAVE PCM or IEEE float
audio (mono/stereo, 8-192 kHz, at most 128 MiB and 600 seconds), regardless of
their filename extension. Playlist inputs and symlink paths are rejected.
Example selection JSON:
  {"la-graciosa": {"file": "cuento.WAV", "ambience": "sea"}}
"""

from __future__ import annotations

import argparse
from contextlib import ExitStack
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import struct
import subprocess
import sys
import threading


SAMPLE_RATE = 44_100
BIT_RATE = "64k"
INTRO_SECONDS = 5.0
NATURE_AFTER_VOICE_SECONDS = 6.0
EFFECT_PEAK_DBFS = -27.0
NATURE_RMS_DBFS = -43.0
MAX_TRUE_PEAK_DBFS = -1.5
LOUDNESS_FILTER = "loudnorm=I=-19:TP=-2:LRA=11"
ROOT = Path(__file__).resolve().parent.parent
MAX_INPUT_BYTES = 128 * 1024 * 1024
MAX_NARRATION_SECONDS = 600.0
MAX_WAV_CHUNKS = 4096
TOOL_TIMEOUT_SECONDS = 120.0
MAX_TOOL_OUTPUT_BYTES = 1024 * 1024
MAX_PCM_BYTES = round(MAX_NARRATION_SECONDS * SAMPLE_RATE) * 4


def require_numpy():
    try:
        import numpy
    except ImportError as error:
        raise RuntimeError("Audio processing requires NumPy; install numpy before preparing narrations") from error
    return numpy


@dataclass(frozen=True)
class ValidatedWav:
    name: str
    data: bytes
    seconds: float
    decoder: str


def load_narration(input_directory: Path, filename: str) -> ValidatedWav:
    """Read one regular, contained file once, then accept only bounded PCM WAV."""
    relative = Path(filename)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ValueError(f"Source must be a file inside --input-dir: {filename!r}")
    # Use descriptor traversal where available. On Windows, resolve containment
    # and reject exposed reparse points before opening a regular file once.
    # In either case, decoders receive only the retained bytes, never a path.
    with ExitStack() as cleanup:
        try:
            descriptor_walk = (hasattr(os, "O_DIRECTORY") and hasattr(os, "O_NOFOLLOW")
                               and os.open in os.supports_dir_fd)
            if descriptor_walk:
                directory_fd = os.open(input_directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                cleanup.callback(os.close, directory_fd)
                for component in relative.parts[:-1]:
                    directory_fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                           dir_fd=directory_fd)
                    cleanup.callback(os.close, directory_fd)
                source_fd = os.open(relative.parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                                    dir_fd=directory_fd)
            else:
                directory = input_directory.resolve(strict=True)
                candidate = directory
                for component in relative.parts:
                    candidate /= component
                    info = candidate.lstat()
                    if (stat.S_ISLNK(info.st_mode)
                            or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)):
                        raise ValueError(f"Narration paths must not contain symlinks or reparse points: {filename!r}")
                resolved = candidate.resolve(strict=True)
                if not resolved.is_relative_to(directory) or not stat.S_ISREG(info.st_mode):
                    raise ValueError(f"Source must be a regular file inside --input-dir: {filename!r}")
                source_fd = os.open(resolved, os.O_RDONLY | getattr(os, "O_BINARY", 0)
                                    | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
            source = cleanup.enter_context(os.fdopen(source_fd, "rb"))
            info = os.fstat(source.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_INPUT_BYTES:
                raise ValueError(f"Narration must be a regular file of at most {MAX_INPUT_BYTES} bytes: {filename!r}")
            data = source.read(MAX_INPUT_BYTES + 1)
        except OSError as error:
            raise ValueError(f"Source must be a regular file inside --input-dir without symlinks: {filename!r}") from error
    if len(data) > MAX_INPUT_BYTES:
        raise ValueError(f"Narration exceeds the input byte limit: {filename!r}")
    if (len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WAVE"
            or struct.unpack_from("<I", data, 4)[0] != len(data) - 8):
        raise ValueError(f"Narration must contain a complete RIFF/WAVE file: {filename!r}")

    audio_format = None
    data_size = None
    position = 12
    chunk_count = 0
    metadata_chunks = {b"JUNK", b"PAD ", b"bext", b"iXML", b"axml", b"LIST",
                       b"fact", b"cue ", b"smpl", b"PEAK", b"DISP"}
    while position < len(data):
        chunk_count += 1
        if chunk_count > MAX_WAV_CHUNKS:
            raise ValueError(f"WAV exceeds the chunk count limit: {filename!r}")
        if len(data) - position < 8:
            raise ValueError(f"Truncated WAV chunk: {filename!r}")
        tag = data[position:position + 4]
        size = struct.unpack_from("<I", data, position + 4)[0]
        start = position + 8
        end = start + size
        position = end + size % 2
        if position > len(data):
            raise ValueError(f"WAV chunk exceeds the file bounds: {filename!r}")
        if tag == b"fmt ":
            if audio_format is not None or data_size is not None or size not in (16, 18, 40):
                raise ValueError(f"Invalid or duplicate WAV format chunk: {filename!r}")
            codec, channels, rate, byte_rate, alignment, bits = struct.unpack_from("<HHIIHH", data, start)
            if codec == 0xFFFE:
                if size != 40 or struct.unpack_from("<H", data, start + 16)[0] != 22:
                    raise ValueError(f"Invalid extensible WAV format: {filename!r}")
                valid_bits, mask = struct.unpack_from("<HI", data, start + 18)
                guid = data[start + 24:start + 40]
                if (guid[4:] != bytes.fromhex("00001000800000aa00389b71")
                        or not 1 <= valid_bits <= bits or (mask and mask.bit_count() != channels)):
                    raise ValueError(f"Invalid extensible WAV audio parameters: {filename!r}")
                codec = int.from_bytes(guid[:4], "little")
                if codec == 3 and valid_bits != bits:
                    raise ValueError(f"Invalid float WAV sample width: {filename!r}")
            elif size not in (16, 18) or (size == 18 and struct.unpack_from("<H", data, start + 16)[0]):
                raise ValueError(f"Unsupported WAV format extension: {filename!r}")
            if (codec not in (1, 3) or bits not in ((8, 16, 24, 32) if codec == 1 else (32, 64))
                    or channels not in (1, 2) or not 8000 <= rate <= 192000
                    or alignment != channels * (bits // 8) or byte_rate != rate * alignment):
                raise ValueError(f"Unsupported or inconsistent PCM/float WAV parameters: {filename!r}")
            decoder = {(1, 8): "pcm_u8", (1, 16): "pcm_s16le", (1, 24): "pcm_s24le",
                       (1, 32): "pcm_s32le", (3, 32): "pcm_f32le", (3, 64): "pcm_f64le"}[codec, bits]
            audio_format = rate, alignment, decoder
        elif tag == b"data":
            if audio_format is None or data_size is not None or not size or size % audio_format[1]:
                raise ValueError(f"Invalid or duplicate WAV sample data: {filename!r}")
            data_size = size
        elif tag not in metadata_chunks or (tag == b"LIST" and data[start:start + 4] != b"INFO"):
            raise ValueError(f"Unsupported WAV chunk {tag!r}: {filename!r}")
    if audio_format is None or data_size is None:
        raise ValueError(f"WAV must contain format and sample data: {filename!r}")
    seconds = data_size / audio_format[1] / audio_format[0]
    if not 0 < seconds <= MAX_NARRATION_SECONDS:
        raise ValueError(f"Narration exceeds the {MAX_NARRATION_SECONDS:g}-second duration limit: {filename!r}")
    return ValidatedWav(relative.as_posix(), data, seconds, audio_format[2])


def run(command: list[str], *, data: bytes | None = None,
        stdout_limit: int = MAX_TOOL_OUTPUT_BYTES) -> subprocess.CompletedProcess:
    """Drain both pipes concurrently, killing a tool before retaining excess output."""
    output = [bytearray(), bytearray()]
    overflow = threading.Event()
    with subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        def read_pipe(stream, destination, limit):
            with stream:
                while True:
                    block = stream.read(min(65536, limit - len(destination) + 1))
                    if not block:
                        return
                    if len(destination) + len(block) > limit:
                        overflow.set()
                        process.kill()
                        return
                    destination.extend(block)

        def write_input():
            try:
                with process.stdin:
                    if data is not None:
                        process.stdin.write(data)
            except (BrokenPipeError, OSError):
                pass  # A failed, timed-out, or output-limited tool may close stdin.

        workers = [threading.Thread(target=read_pipe, args=(process.stdout, output[0], stdout_limit)),
                   threading.Thread(target=read_pipe, args=(process.stderr, output[1], MAX_TOOL_OUTPUT_BYTES)),
                   threading.Thread(target=write_input)]
        for worker in workers:
            worker.start()
        timed_out = False
        try:
            process.wait(timeout=TOOL_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            process.wait()
        finally:
            for worker in workers:
                worker.join()
        if timed_out:
            raise RuntimeError(f"{command[0]} timed out after {TOOL_TIMEOUT_SECONDS:g} seconds")
        if overflow.is_set():
            raise RuntimeError(f"{command[0]} exceeded its output limit")
        result = subprocess.CompletedProcess(command, process.returncode, bytes(output[0]), bytes(output[1]))
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace")[-4000:]
        raise RuntimeError(f"{command[0]} failed ({result.returncode}):\n{detail}")
    return result


def ffmpeg(*arguments: str, data: bytes | None = None,
           stdout_limit: int = MAX_TOOL_OUTPUT_BYTES) -> subprocess.CompletedProcess:
    return run(["ffmpeg", "-hide_banner", "-nostdin", "-y", *arguments], data=data, stdout_limit=stdout_limit)


def duration(source: ValidatedWav) -> float:
    # Nonseekable WAV inputs do not expose a reliable ffprobe duration. The
    # validated PCM frame count gives the exact duration without decoding.
    return source.seconds


def wav_input_arguments(source: ValidatedWav) -> list[str]:
    # FFmpeg may choose a different PCM width from extensible valid-bits fields.
    # Force the decoder for the validated physical sample container so actual
    # frames and duration agree with validation, including 24 valid bits in 32.
    return ["-protocol_whitelist", "pipe", "-f", "wav", "-c:a", source.decoder, "-i", "pipe:0"]


def mp3_duration(data: bytes) -> float:
    result = run([
        "ffprobe", "-v", "error", "-protocol_whitelist", "pipe", "-f", "mp3", "-i", "pipe:0",
        "-show_entries", "packet=duration:stream=time_base", "-of", "json",
    ], data=data, stdout_limit=4 * MAX_TOOL_OUTPUT_BYTES)
    measurements = json.loads(result.stdout)
    streams = measurements.get("streams", [])
    if len(streams) != 1:
        raise ValueError("Generated MP3 must contain one audio stream")
    value = float(sum(packet["duration"] for packet in measurements.get("packets", []))
                  * Fraction(streams[0]["time_base"]))
    if not math.isfinite(value) or not 0 < value <= MAX_NARRATION_SECONDS + INTRO_SECONDS + 1:
        raise ValueError("Invalid generated MP3 duration")
    return value


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def loudness_json(stderr: bytes) -> dict:
    text = stderr.decode("utf-8", errors="replace")
    candidates = re.findall(r'\{\s*"input_i"\s*:.*?\}', text, flags=re.S)
    if not candidates:
        raise ValueError("ffmpeg did not return loudness measurements")
    result = json.loads(candidates[-1])
    for key in ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset"):
        if not math.isfinite(float(result[key])):
            raise ValueError("Audio contains insufficient measurable sound for normalization")
    return result


def trim_bounds(source: ValidatedWav, seconds: float) -> tuple[float, float, dict]:
    result = ffmpeg(
        *wav_input_arguments(source), "-af",
        "aformat=channel_layouts=mono,silencedetect=noise=-45dB:d=0.35",
        "-f", "null", "-", data=source.data,
    )
    entries = re.findall(
        r"silence_(start|end):\s*([-+]?\d+(?:\.\d+)?)",
        result.stderr.decode("utf-8", errors="replace"),
    )
    intervals: list[tuple[float, float]] = []
    beginning: float | None = None
    for kind, number in entries:
        value = float(number)
        if kind == "start":
            beginning = value
        elif beginning is not None:
            intervals.append((beginning, value))
            beginning = None
    if beginning is not None:
        intervals.append((beginning, seconds))

    start, end = 0.0, seconds
    for first, last in intervals:
        # Whole-file silence or ambiguous intervals are never trimmed.
        if first <= 0.03 and 0.35 <= last < seconds - 0.35:
            start = max(0.0, last - 0.15)
        if last >= seconds - 0.03 and 0.35 < first <= seconds - 0.35:
            end = min(seconds, first + 0.15)
    if end - start < 0.7:
        start, end = 0.0, seconds
    report = {
        "threshold_dbfs": -45,
        "minimum_silence_seconds": 0.35,
        "retained_margin_seconds": 0.15,
        "start_seconds": round(start, 6),
        "end_seconds": round(end, 6),
        "removed_leading_seconds": round(start, 6),
        "removed_trailing_seconds": round(seconds - end, 6),
        "interior_silences_preserved": True,
    }
    return start, end, report


def normalize_voice(source: ValidatedWav, start: float, end: float) -> tuple[np.ndarray, dict]:
    np = require_numpy()
    input_arguments = wav_input_arguments(source)
    # A pipe cannot seek. Trim decoded frames before loudness analysis, keeping
    # the same samples that input seeking selected from regular WAV files.
    trimmed = f"atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS,"
    first = ffmpeg(
        *input_arguments, "-af", f"{trimmed}aformat=sample_rates=44100:channel_layouts=mono,highpass=f=70,{LOUDNESS_FILTER}:print_format=json",
        "-ac", "1", "-f", "null", "-", data=source.data,
    )
    measured = loudness_json(first.stderr)
    second_filter = (
        f"{trimmed}aformat=sample_rates=44100:channel_layouts=mono,highpass=f=70,{LOUDNESS_FILTER}:"
        f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
        f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
        f"offset={measured['target_offset']}:linear=true:print_format=json"
    )
    second = ffmpeg(
        *input_arguments, "-af", second_filter, "-ar", str(SAMPLE_RATE),
        "-ac", "1", "-f", "f32le", "-", data=source.data, stdout_limit=MAX_PCM_BYTES,
    )
    voice = np.frombuffer(second.stdout, dtype="<f4").copy()
    if not voice.size or not np.isfinite(voice).all():
        raise ValueError(f"Invalid normalized audio: {source.name}")
    return voice, {
        "target_integrated_lufs": -19,
        "target_true_peak_dbfs": -2,
        "target_lra_lu": 11,
        "highpass_hz": 70,
        "passes": 2,
        "first_pass": measured,
        "second_pass": loudness_json(second.stderr),
    }


def band_noise(size: int, rng: np.random.Generator, low: float, high: float) -> np.ndarray:
    np = require_numpy()
    white = rng.normal(0.0, 1.0, size)
    frequencies = np.fft.rfftfreq(size, d=1.0 / SAMPLE_RATE)
    spectrum = np.fft.rfft(white)
    # Smooth spectral edges avoid ringing and tonal artefacts.
    weights = (frequencies / low) ** 2 / (1.0 + (frequencies / low) ** 2)
    weights /= 1.0 + (frequencies / high) ** 4
    return np.fft.irfft(spectrum * weights, n=size)


def percussion_intro() -> np.ndarray:
    """Return the same quiet, damped drum/wood recreation for every island."""
    np = require_numpy()
    size = round(INTRO_SECONDS * SAMPLE_RATE)
    sound = np.zeros(size, dtype=np.float64)
    rng = np.random.default_rng(2026100601)

    drum_time = np.arange(round(0.60 * SAMPLE_RATE)) / SAMPLE_RATE
    drum_phase = 2 * np.pi * (78 * drum_time + 12 * 0.04 * (1 - np.exp(-drum_time / 0.04)))
    drum = np.sin(drum_phase) * np.exp(-drum_time / 0.17)
    drum += 0.24 * np.sin(2 * np.pi * 133 * drum_time) * np.exp(-drum_time / 0.09)
    for index, onset in enumerate((0.20, 0.87, 1.54, 2.21, 2.88, 3.55)):
        beginning = round(onset * SAMPLE_RATE)
        sound[beginning:beginning + drum.size] += drum * (0.8 if index % 2 else 1.0)

    wood_time = np.arange(round(0.14 * SAMPLE_RATE)) / SAMPLE_RATE
    for index, onset in enumerate((0.40, 0.55, 1.07, 1.22, 1.74, 1.89, 2.41, 2.56, 3.08, 3.23, 3.75, 3.90)):
        # Damped modes plus a short noisy contact reproduce a wooden knock.
        scale = 1.0 if index % 2 else 0.91
        wood = sum(
            amplitude * np.sin(2 * np.pi * frequency * scale * wood_time)
            * np.exp(-wood_time / decay)
            for frequency, amplitude, decay in ((680, 0.55, 0.024), (1120, 0.35, 0.015), (1870, 0.16, 0.010))
        )
        wood += 0.17 * band_noise(wood_time.size, rng, 650, 4500) * np.exp(-wood_time / 0.006)
        beginning = round(onset * SAMPLE_RATE)
        sound[beginning:beginning + wood.size] += 0.48 * wood

    timeline = np.arange(size) / SAMPLE_RATE
    envelope = np.minimum(timeline / 0.15, 1.0) * np.clip((4.5 - timeline) / 0.8, 0, 1)
    sound *= envelope
    peak = float(np.max(np.abs(sound)))
    return (sound * (10 ** (EFFECT_PEAK_DBFS / 20) / peak)).astype(np.float32)


def nature_sound(kind: str) -> np.ndarray:
    np = require_numpy()
    seconds = INTRO_SECONDS + NATURE_AFTER_VOICE_SECONDS
    size = round(seconds * SAMPLE_RATE)
    timeline = np.arange(size) / SAMPLE_RATE
    rng = np.random.default_rng(2026100602 if kind == "sea" else 2026100603)
    if kind == "sea":
        sound = band_noise(size, rng, 90, 2400)
        sound *= 0.48 + 0.52 * (0.5 + 0.5 * np.sin(2 * np.pi * timeline / 3.9 - 1.1)) ** 2
    else:
        sound = band_noise(size, rng, 60, 650)
        sound *= 0.68 + 0.20 * np.sin(2 * np.pi * timeline / 4.7) + 0.12 * np.sin(2 * np.pi * timeline / 1.9)
    rms = float(np.sqrt(np.mean(sound * sound)))
    sound *= 10 ** (NATURE_RMS_DBFS / 20) / rms
    peak_limit = 10 ** (EFFECT_PEAK_DBFS / 20)
    sound *= min(1.0, peak_limit / float(np.max(np.abs(sound))))
    # Nature follows the percussion; separate their peaks to keep all effects
    # below -27 dBFS while leaving a half-second transition before the voice.
    fade_in = np.clip((timeline - 4.5) / 0.5, 0, 1)
    fade_out = np.clip((seconds - timeline) / NATURE_AFTER_VOICE_SECONDS, 0, 1)
    fade_out = np.where(timeline < INTRO_SECONDS, 1.0, fade_out)
    return (sound * fade_in * fade_out).astype(np.float32)


def with_ambience(voice: np.ndarray, kind: str) -> tuple[np.ndarray, dict]:
    np = require_numpy()
    intro = percussion_intro()
    nature = nature_sound(kind)
    offset = intro.size
    combined = np.zeros(offset + voice.size, dtype=np.float32)
    combined[:intro.size] += intro
    nature_size = min(combined.size, nature.size)
    applied_nature = nature[:nature_size].copy()
    if nature_size < nature.size:
        # Short recordings also end with a smooth nature fade.
        fade_samples = min(nature_size, round(0.4 * SAMPLE_RATE))
        applied_nature[-fade_samples:] *= np.linspace(1.0, 0.0, fade_samples)
    combined[:nature_size] += applied_nature
    combined[offset:] += voice
    return combined, {
        "description": "Recreación sonora original: tambor grave, percusión de madera y naturaleza sintetizados",
        "authentic_instrument_recording": False,
        "profile": kind,
        "intro_seconds": INTRO_SECONDS,
        "voice_offset_seconds": INTRO_SECONDS,
        "percussion_ends_before_voice": True,
        "percussion_peak_dbfs": round(20 * math.log10(float(np.max(np.abs(intro)))), 3),
        "nature_target_rms_before_fades_dbfs": NATURE_RMS_DBFS,
        "nature_rms_dbfs": round(20 * math.log10(float(np.sqrt(np.mean(nature.astype(float) ** 2)))), 3),
        "nature_after_voice_seconds_max": NATURE_AFTER_VOICE_SECONDS,
        "continuous_bed": False,
        "random_seeds": [2026100601, 2026100602 if kind == "sea" else 2026100603],
    }


def encode_mp3(samples: np.ndarray, path: Path) -> dict:
    np = require_numpy()
    attenuation_db = 0.0
    for attempt in range(3):
        # A final limiter catches summing peaks without increasing output gain.
        filters = f"volume={attenuation_db:.5f}dB,alimiter=limit=0.794328:level=false:latency=true"
        ffmpeg(
            "-protocol_whitelist", "pipe", "-f", "f32le", "-ar", str(SAMPLE_RATE), "-ac", "1", "-i", "pipe:0",
            "-af", filters, "-map_metadata", "-1", "-c:a", "libmp3lame",
            "-b:a", BIT_RATE, "-ar", str(SAMPLE_RATE), "-ac", "1", str(path),
            data=samples.astype("<f4", copy=False).tobytes(),
        )
        encoded = path.read_bytes()
        measurements = loudness_json(ffmpeg(
            "-protocol_whitelist", "pipe", "-f", "mp3", "-i", "pipe:0",
            "-af", f"{LOUDNESS_FILTER}:print_format=json", "-f", "null", "-", data=encoded,
        ).stderr)
        true_peak = float(measurements["input_tp"])
        if true_peak <= MAX_TRUE_PEAK_DBFS:
            return {
                "file": path.name,
                "sha256": digest(path),
                "bytes": path.stat().st_size,
                "duration_seconds": round(mp3_duration(encoded), 6),
                "sample_rate_hz": SAMPLE_RATE,
                "channels": 1,
                "bit_rate": BIT_RATE,
                "integrated_lufs": float(measurements["input_i"]),
                "true_peak_dbfs": true_peak,
                "lra_lu": float(measurements["input_lra"]),
                "encoding_attenuation_db": round(attenuation_db, 5),
            }
        attenuation_db -= true_peak - MAX_TRUE_PEAK_DBFS + 0.15
    raise ValueError(f"Unable to meet encoded true-peak limit: {path.name}")


def ambience_kind(route_id: str, entry: dict) -> str:
    selected = str(entry.get("ambience", "sea" if route_id == "la-graciosa" else "wind")).lower()
    aliases = {"sea": "sea", "mar": "sea", "ocean": "sea", "wind": "wind", "viento": "wind"}
    if selected not in aliases:
        raise ValueError(f"Unknown ambience {selected!r} for {route_id}; use sea or wind")
    return aliases[selected]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--selection", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "assets" / "audio")
    parser.add_argument("--report", type=Path)
    arguments = parser.parse_args()
    input_directory = arguments.input_dir.resolve(strict=True)
    if not input_directory.is_dir():
        raise ValueError("--input-dir must be a directory")
    selection = json.loads(arguments.selection.read_text(encoding="utf-8"))
    if not isinstance(selection, dict) or not selection:
        raise ValueError("Selection must be a nonempty JSON object mapping island ids to files")
    output_directory = arguments.output_dir.resolve()
    output_directory.mkdir(parents=True, exist_ok=True)
    report = {
        "generator": "tools/prepare_narrations.py",
        "ffmpeg_version": run(["ffmpeg", "-version"]).stdout.decode("utf-8").splitlines()[0],
        "numpy_version": None,
        "sample_rate_hz": SAMPLE_RATE,
        "channels": 1,
        "bit_rate": BIT_RATE,
        "narration_pitch_changed": False,
        "sound_description": "Recreación sonora; no son grabaciones auténticas de instrumentos ni de naturaleza",
        "recordings": {},
    }
    for route_id, entry in selection.items():
        if not isinstance(route_id, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", route_id):
            raise ValueError(f"Unsafe island id: {route_id!r}")
        if not isinstance(entry, dict) or not isinstance(entry.get("file"), str):
            raise ValueError(f"Selection for {route_id} must contain a file name")
        source = load_narration(input_directory, entry["file"])
        report["numpy_version"] = require_numpy().__version__
        kind = ambience_kind(route_id, entry)
        original_duration = duration(source)
        start, end, trim = trim_bounds(source, original_duration)
        voice, normalization = normalize_voice(source, start, end)
        ambient, sound = with_ambience(voice, kind)
        voice_result = encode_mp3(voice, output_directory / f"{route_id}.mp3")
        ambient_result = encode_mp3(ambient, output_directory / f"{route_id}-ambiente.mp3")
        report["recordings"][route_id] = {
            "original_file": source.name,
            "original_sha256": hashlib.sha256(source.data).hexdigest(),
            "original_duration_seconds": round(original_duration, 6),
            "trim": trim,
            "normalization": normalization,
            "sound_recreation": sound,
            "voice": voice_result,
            "ambient": ambient_result,
        }
        print(f"{route_id}: {voice.size / SAMPLE_RATE:.2f}s voice; {kind}; {voice_result['bytes'] + ambient_result['bytes']} bytes")
    if arguments.report:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Report written to {arguments.report}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
