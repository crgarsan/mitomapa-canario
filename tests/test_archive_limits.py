"""Bound recursive maintenance reads before inflation, including forged headers."""

from dataclasses import replace
from contextlib import redirect_stdout
from io import BytesIO, StringIO
from pathlib import Path
from types import SimpleNamespace
import os
import stat
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile
import zlib


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import harden_drawing_archives as drawings
import harden_jspdf_exports as pdf


def archive_bytes(entries, *, method=zipfile.ZIP_DEFLATED):
    output = BytesIO()
    with warnings.catch_warnings(), zipfile.ZipFile(output, "w", compression=method) as archive:
        warnings.simplefilter("ignore", UserWarning)
        for name, data in entries:
            archive.writestr(name, data)
    return output.getvalue()


def forged_header(payload, *, expanded=None, flags=None, method=None, crc=None):
    """Change both headers without allocating the expansion they advertise."""
    result = bytearray(payload)
    central = result.index(b"PK\x01\x02")
    for position, size_offset, flags_offset, method_offset in ((0, 22, 6, 8), (central, 24, 8, 10)):
        if expanded is not None:
            struct.pack_into("<I", result, position + size_offset, expanded)
        if flags is not None:
            struct.pack_into("<H", result, position + flags_offset, flags)
        if method is not None:
            struct.pack_into("<H", result, position + method_offset, method)
        if crc is not None:
            struct.pack_into("<I", result, position + (14 if position == 0 else 16), crc)
    return bytes(result)


class ArchiveLimitsTests(unittest.TestCase):
    def budget(self, **changes):
        return pdf.ArchiveBudget(replace(pdf.DEFAULT_ARCHIVE_LIMITS, **changes))

    def file_reader(self, path, **kwargs):
        return pdf.read_archive_file(path, **kwargs)

    def test_compressed_payload_limit_precedes_zip_directory_parsing(self):
        limits = SimpleNamespace(**{**vars(pdf.DEFAULT_ARCHIVE_LIMITS), "max_compressed_bytes": 8})
        for module in (pdf, drawings):
            with self.subTest(module=module.__name__), patch.object(
                    zipfile, "ZipFile", side_effect=AssertionError("Parsed directory before input limit")):
                with self.assertRaisesRegex(ValueError, "compressed.*limit"):
                    module.read_archive(b"123456789", budget=pdf.ArchiveBudget(limits))

    def test_archive_file_stat_limit_precedes_open(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "oversized.zip"
            path.write_bytes(b"123456789")
            with patch("builtins.open", side_effect=AssertionError("Read before stat limit")):
                with self.assertRaisesRegex(ValueError, "compressed.*limit"):
                    self.file_reader(path, max_bytes=8)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "Named pipes are unavailable")
    def test_archive_file_rejects_named_pipes_before_open(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pipe.zip"
            os.mkfifo(path)
            with patch("builtins.open", side_effect=AssertionError("Opened a named pipe")):
                with self.assertRaisesRegex(ValueError, "regular"):
                    self.file_reader(path, max_bytes=8)

    def test_archive_file_rechecks_that_the_open_descriptor_is_regular(self):
        class DescriptorStream(BytesIO):
            def fileno(self):
                return 0

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "swapped.zip"
            path.write_bytes(b"12345678")
            with patch("builtins.open", return_value=DescriptorStream(b"12345678")), patch.object(
                    os, "fstat", return_value=SimpleNamespace(st_size=0, st_mode=stat.S_IFIFO)):
                with self.assertRaisesRegex(ValueError, "regular"):
                    self.file_reader(path, max_bytes=8)

    def test_archive_file_accepts_operator_symlinks_to_regular_files(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "regular.zip"
            path.write_bytes(b"12345678")
            link = Path(directory) / "selected.zip"
            link.symlink_to(path)
            self.assertEqual(self.file_reader(link, max_bytes=8), b"12345678")

    def test_archive_file_read_limit_handles_stale_or_false_stat_size(self):
        class GrowingStream(BytesIO):
            def fileno(self):
                return 0

            def close(self):
                self.bytes_consumed = self.tell()
                super().close()

        stream = GrowingStream(b"123456789012")
        false_stat = SimpleNamespace(st_size=1, st_mode=stat.S_IFREG)
        with patch.object(Path, "stat", return_value=false_stat), patch.object(
                os, "fstat", return_value=false_stat), patch("builtins.open", return_value=stream):
            with self.assertRaisesRegex(ValueError, "compressed.*limit"):
                self.file_reader(Path("growing.zip"), max_bytes=8)
        self.assertEqual(stream.bytes_consumed, 9)

    def test_archive_file_read_accepts_the_exact_compressed_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "exact.zip"
            path.write_bytes(b"12345678")
            self.assertEqual(self.file_reader(path, max_bytes=8), b"12345678")

    def test_artifact_cli_uses_the_bounded_reader_before_parsing_or_writing(self):
        limits = SimpleNamespace(**{**vars(pdf.DEFAULT_ARCHIVE_LIMITS), "max_compressed_bytes": 8})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "oversized.elpx"
            path.write_bytes(b"123456789")
            before = path.read_bytes(), path.stat().st_mtime_ns
            with patch.object(pdf, "DEFAULT_ARCHIVE_LIMITS", limits), patch.object(
                    sys, "argv", ["pdf.py", "--artifact", str(path)]), patch.object(
                    zipfile, "ZipFile", side_effect=AssertionError("Parsed before source limit")):
                with self.assertRaisesRegex(ValueError, "compressed.*limit"):
                    pdf.main()
            self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)

    def test_both_delivery_paths_bound_native_inputs_before_parsing(self):
        limits = SimpleNamespace(**{**vars(pdf.DEFAULT_ARCHIVE_LIMITS), "max_compressed_bytes": 8})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            delivery = root / "delivery"
            delivery.mkdir()
            (root / "downloads").mkdir()
            name = "MitoMapa_canario_GobCan.elpx"
            for path in (delivery / name, root / "downloads" / name):
                path.write_bytes(b"123456789")
            for module, call in ((pdf, lambda: pdf.delivery_update(delivery, True)),
                                 (drawings, lambda: drawings.verify_delivery(delivery, lambda text: None))):
                with self.subTest(module=module.__name__), patch.object(module, "ROOT", root), patch.object(
                        pdf, "DEFAULT_ARCHIVE_LIMITS", limits), patch.object(
                        zipfile, "ZipFile", side_effect=AssertionError("Parsed before source limit")):
                    with self.assertRaisesRegex(ValueError, "compressed.*limit"):
                        call()

    def test_high_compression_ratio_is_rejected_before_opening_members(self):
        payload = archive_bytes([("tiny-bomb.txt", b"A" * 16384)])
        for module in (pdf, drawings):
            with self.subTest(module=module.__name__), patch.object(
                    zipfile.ZipFile, "open", side_effect=AssertionError("Inflated before preflight")):
                with self.assertRaisesRegex(ValueError, "ratio"):
                    module.read_archive(payload)

    def test_declared_member_limit_precedes_crc_and_inflation(self):
        payload = forged_header(archive_bytes([("oversize", b"x")]), expanded=32 * 1024 * 1024 + 1)
        with patch.object(zipfile.ZipFile, "open", side_effect=AssertionError("Inflated before preflight")):
            with self.assertRaisesRegex(ValueError, "member.*limit"):
                pdf.read_archive(payload)

    def test_member_count_is_cumulative_and_checked_before_inflation(self):
        payload = archive_bytes([("one", b"x"), ("two", b"y")])
        with patch.object(zipfile.ZipFile, "open", side_effect=AssertionError("Inflated before preflight")):
            with self.assertRaisesRegex(ValueError, "member.*count"):
                pdf.read_archive(payload, budget=self.budget(max_members=1))

    def test_total_declared_bytes_are_checked_before_first_member(self):
        payload = archive_bytes([("one", b"1234"), ("two", b"5678")])
        with patch.object(zipfile.ZipFile, "open", side_effect=AssertionError("Inflated before preflight")):
            with self.assertRaisesRegex(ValueError, "expanded.*limit"):
                pdf.read_archive(payload, budget=self.budget(max_expanded_bytes=7))

    def test_unsafe_duplicate_encrypted_and_unsupported_entries_reject_before_inflation(self):
        symlink = zipfile.ZipInfo("link")
        symlink.create_system = 3
        symlink.external_attr = 0o120777 << 16
        ordinary = archive_bytes([("safe", b"x")])
        cases = [archive_bytes([(name, b"x")]) for name in
                 ("../escape", "/absolute", "a/../b", "a//b", "a\\b", "C:drive")]
        cases += [archive_bytes([("same", b"a"), ("same", b"b")]),
                  archive_bytes([(symlink, b"target")]),
                  forged_header(ordinary, flags=1), forged_header(ordinary, method=99)]
        for module in (pdf, drawings):
            for index, payload in enumerate(cases):
                with self.subTest(module=module.__name__, case=index), patch.object(
                        zipfile.ZipFile, "open", side_effect=AssertionError("Inflated before preflight")):
                    with self.assertRaises(ValueError):
                        module.read_archive(payload)

    def test_all_members_are_read_to_eof_for_crc_without_testzip(self):
        payload = bytearray(archive_bytes([("safe", b"1234567890")], method=zipfile.ZIP_STORED))
        payload[30 + len("safe")] ^= 1
        with patch.object(zipfile.ZipFile, "testzip", side_effect=AssertionError("Unbounded CRC pass")):
            with self.assertRaisesRegex(ValueError, "CRC"):
                pdf.read_archive(bytes(payload))

    def test_actual_read_bytes_enforce_member_and_total_budgets(self):
        # ZipExtFile normally truncates to the declared size. Substitute only
        # the decoded byte stream to exercise a decoder yielding extra bytes.
        payload = archive_bytes([("safe", b"12345678")], method=zipfile.ZIP_STORED)
        for limits in ({"max_member_bytes": 8}, {"max_expanded_bytes": 8}):
            with self.subTest(limits=limits), patch.object(zipfile.ZipFile, "open", return_value=BytesIO(b"x" * 12)):
                with self.assertRaisesRegex(ValueError, "limit"):
                    pdf.read_archive(payload, budget=self.budget(**limits))

    def test_actual_decoded_bytes_must_match_the_declared_member_size(self):
        payload = archive_bytes([("safe", b"1234")], method=zipfile.ZIP_STORED)
        with patch.object(zipfile.ZipFile, "open", return_value=BytesIO(b"12345")):
            with self.assertRaisesRegex(ValueError, "size"):
                pdf.read_archive(payload)

    def test_real_forged_sizes_cannot_hide_decoded_bytes_from_the_budget(self):
        for method in (zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED):
            # CRC matches the advertised prefix, which ordinary ZipExtFile
            # accepts after silently discarding the rest of its output.
            payload = forged_header(archive_bytes([("safe", b"A" * 16384)], method=method),
                                    expanded=1, crc=zlib.crc32(b"A"))
            for module in (pdf, drawings):
                with self.subTest(method=method, module=module.__name__):
                    with self.assertRaises(ValueError):
                        module.read_archive(payload, budget=self.budget(
                            max_member_bytes=8, max_expanded_bytes=8))

    def test_small_forged_deflate_size_is_rejected_even_after_decoder_eof(self):
        payload = forged_header(archive_bytes([("safe", b"AA")]), expanded=1, crc=zlib.crc32(b"A"))
        with self.assertRaises(ValueError):
            pdf.read_archive(payload)

    def test_deflate_member_must_reach_the_real_end_of_its_stream(self):
        payload = bytearray(archive_bytes([("safe", b"AA")]))
        central = payload.index(b"PK\x01\x02")
        compressed = struct.unpack_from("<I", payload, central + 20)[0]
        # Exclude the last deflate byte while leaving the decoded bytes and
        # CRC intact; ordinary ZipExtFile treats compressed-data exhaustion as EOF.
        struct.pack_into("<I", payload, 18, compressed - 1)
        struct.pack_into("<I", payload, central + 20, compressed - 1)
        with self.assertRaisesRegex(ValueError, "deflate|stream"):
            pdf.read_archive(bytes(payload))

    def test_read_chunks_have_a_fixed_bound(self):
        requests = []

        class RecordingStream(BytesIO):
            def read(self, size=-1):
                requests.append(size)
                return super().read(size)

        data = bytes(range(256)) * 400
        payload = archive_bytes([("safe", data)], method=zipfile.ZIP_STORED)
        with patch.object(zipfile.ZipFile, "open", return_value=RecordingStream(data)):
            self.assertEqual(pdf.read_archive(payload)[1], {"safe": data})
        self.assertTrue(requests and all(0 < size <= 65536 for size in requests))

    def recursive_calls(self, payload, budget):
        return (
            lambda: pdf.verify_archive(payload, budget=budget()),
            lambda: pdf.patched_archive(payload, budget=budget()),
            lambda: drawings.verify_drawing_archive(payload, lambda text: None, budget=budget()),
        )

    def test_nested_siblings_share_the_total_expansion_budget(self):
        inner = archive_bytes([("body", b"12345678")], method=zipfile.ZIP_STORED)
        payload = archive_bytes([("first.zip", inner), ("second.elpx", inner)], method=zipfile.ZIP_STORED)
        # Parent entries plus either child fit. Reading both children exceeds it.
        cap = 2 * len(inner) + 12
        for call in self.recursive_calls(payload, lambda: self.budget(max_expanded_bytes=cap)):
            with self.assertRaisesRegex(ValueError, "expanded.*limit"):
                call()

    def test_nested_siblings_share_the_member_count_budget(self):
        inner = archive_bytes([("body", b"1234")])
        payload = archive_bytes([("first.zip", inner), ("second.elpx", inner)])
        for call in self.recursive_calls(payload, lambda: self.budget(max_members=3)):
            with self.assertRaisesRegex(ValueError, "member.*count"):
                call()

    def test_depth_limit_precedes_opening_the_child_archive(self):
        payload = archive_bytes([("child.zip", b"not even a ZIP")])
        for call in self.recursive_calls(payload, lambda: self.budget(max_depth=0)):
            with self.assertRaisesRegex(ValueError, "depth"):
                call()

    def test_small_nested_exports_pass_at_the_exact_budget(self):
        inner = archive_bytes([("body", b"1234")])
        payload = archive_bytes([("nested.elpx", inner)])
        limits = dict(max_members=2, max_expanded_bytes=len(inner) + 4, max_depth=1)
        self.assertEqual(pdf.verify_archive(payload, budget=self.budget(**limits)), (0, 1))
        self.assertEqual(pdf.patched_archive(payload, budget=self.budget(**limits)), (payload, 0, 1))
        self.assertEqual(drawings.verify_drawing_archive(
            payload, lambda text: None, budget=self.budget(**limits)), (0, 1))

    def test_directory_entries_and_zip_metadata_keep_the_read_write_contract(self):
        folder = zipfile.ZipInfo("folder/")
        folder.external_attr = 0o40755 << 16
        payload = archive_bytes([(folder, b""), ("folder/keep", b"native media")])
        infos, files, comment = pdf.read_archive(payload)
        self.assertEqual(files, {"folder/": b"", "folder/keep": b"native media"})
        result = pdf.write_archive(infos, files, comment)
        after_infos, after_files, after_comment = pdf.read_archive(result)
        self.assertEqual((after_files, after_comment), (files, comment))
        for before, after in zip(infos, after_infos, strict=True):
            for field in pdf.ZIP_INFO_FIELDS:
                self.assertEqual(getattr(before, field), getattr(after, field))


def with_zip64_footer(payload, *, declared=None):
    """Small real ZIP64 end records; no huge data or ZipInfo allocation."""
    end = payload.rindex(b"PK\x05\x06")
    entries, size, offset = struct.unpack_from("<HII", payload, end + 10)
    count = entries if declared is None else declared
    footer = struct.pack("<4sQ2H2I4Q", b"PK\x06\x06", 44, 45, 45, 0, 0,
                         count, count, size, offset)
    locator = struct.pack("<4sIQI", b"PK\x06\x07", 0, end, 1)
    legacy = bytearray(payload[end:])
    struct.pack_into("<HHII", legacy, 8, 0xffff, 0xffff, 0xffffffff, 0xffffffff)
    return payload[:end] + footer + locator + bytes(legacy)


class CentralDirectoryPreflightTests(unittest.TestCase):
    def read_before_constructor(self, payload, *, used=0, maximum=2, error="member.*count"):
        for module in (pdf, drawings):
            budget = pdf.ArchiveBudget(replace(pdf.DEFAULT_ARCHIVE_LIMITS, max_members=maximum),
                                       members=used)
            with self.subTest(module=module.__name__), patch.object(
                    zipfile, "ZipFile", side_effect=AssertionError("Allocated ZipInfo before limit")):
                with self.assertRaisesRegex(ValueError, error):
                    module.read_archive(payload, budget=budget)

    def test_actual_count_rejected_before_zipfile_even_if_footer_understates_it(self):
        original = archive_bytes([(str(i), b"") for i in range(3)])
        end = original.rindex(b"PK\x05\x06")
        understated = bytearray(original)
        struct.pack_into("<HH", understated, end + 8, 1, 1)
        for payload in (original, bytes(understated), with_zip64_footer(original),
                        with_zip64_footer(original, declared=1)):
            self.read_before_constructor(payload)

    def test_twenty_thousand_entries_never_construct_zipinfo(self):
        payload = archive_bytes([(str(i), b"") for i in range(20000)])
        self.assertLess(len(payload), 2 * 1024 * 1024)
        self.read_before_constructor(payload, maximum=2000)

    def test_declared_count_and_remaining_recursive_budget_precede_constructor(self):
        payload = archive_bytes([("a", b""), ("b", b"")])
        self.read_before_constructor(payload, used=1)
        self.read_before_constructor(with_zip64_footer(payload, declared=3))

    def test_understated_count_within_budget_is_invalid_before_constructor(self):
        payload = bytearray(archive_bytes([("a", b""), ("b", b"")]))
        end = payload.rindex(b"PK\x05\x06")
        struct.pack_into("<HH", payload, end + 8, 1, 1)
        self.read_before_constructor(bytes(payload), error="central|count")

    def test_truncated_variable_record_and_invalid_signature_precede_constructor(self):
        original = archive_bytes([("a", b"x")])
        central = original.index(b"PK\x01\x02")
        bad_length = bytearray(original)
        struct.pack_into("<H", bad_length, central + 28, 0xffff)
        bad_signature = bytearray(original)
        bad_signature[central] = 0
        for payload in (bytes(bad_length), bytes(bad_signature)):
            self.read_before_constructor(payload, error="central|ZIP structure")

    def test_normal_zip64_comments_and_concatenated_prefix_keep_metadata(self):
        info = zipfile.ZipInfo("folder/body.txt")
        info.comment = b"member comment"
        info.extra = struct.pack("<HH", 0xcafe, 0)
        output = BytesIO()
        with zipfile.ZipFile(output, "w") as archive:
            archive.comment = b"archive comment"
            archive.writestr(info, b"original bytes")
        ordinary = output.getvalue()
        for payload in (ordinary, with_zip64_footer(ordinary),
                        b"self extracting prefix" + ordinary,
                        b"self extracting prefix" + with_zip64_footer(ordinary)):
            with self.subTest(zip64=b"PK\x06\x06" in payload, prefixed=payload.startswith(b"self")):
                budget = pdf.ArchiveBudget(replace(pdf.DEFAULT_ARCHIVE_LIMITS, max_members=1))
                infos, files, comment = pdf.read_archive(payload, budget=budget)
                self.assertEqual(files, {"folder/body.txt": b"original bytes"})
                self.assertEqual((infos[0].comment, infos[0].extra, comment),
                                 (info.comment, info.extra, b"archive comment"))
                self.assertEqual(budget.members, 1)

    def test_empty_archives_pass_without_entries(self):
        ordinary = archive_bytes([])
        for payload in (ordinary, with_zip64_footer(ordinary)):
            self.assertEqual(pdf.read_archive(payload)[1], {})

    def test_legacy_python_zip64_footer_location_is_bounded_too(self):
        payload = with_zip64_footer(archive_bytes([("a", b""), ("b", b"")]))
        footer = zipfile._EndRecData(BytesIO(payload))
        footer[zipfile._ECD_LOCATION] = payload.rindex(b"PK\x05\x06")
        budget = pdf.ArchiveBudget(replace(pdf.DEFAULT_ARCHIVE_LIMITS, max_members=2))
        with patch.object(zipfile, "_EndRecData", return_value=footer):
            pdf.preflight_central_directory(payload, budget)

    def test_invalid_offsets_are_rejected_before_constructor(self):
        payload = bytearray(archive_bytes([("a", b"x")]))
        end = payload.rindex(b"PK\x05\x06")
        struct.pack_into("<I", payload, end + 16, len(payload) + 1)
        self.read_before_constructor(bytes(payload), error="offset|central")


class ArtifactCommitTests(unittest.TestCase):
    def fixture(self):
        loader = (pdf.LOADER_START + "\n" + pdf.OLD_ASSIGNMENT + "\n"
                  + pdf.APPEND + "\n    },\n")
        return archive_bytes([("idevices/checklist/checklist.js", loader.encode()),
                              ("content.xml", b"untouched native content")])

    def run_cli(self, path, *, check=False):
        args = ["pdf.py", "--artifact", str(path)] + (["--check"] if check else [])
        with patch.object(sys, "argv", args), redirect_stdout(StringIO()):
            pdf.main()

    def test_symlink_or_regular_inode_swap_aborts_without_writing_either_file(self):
        for symlink in (True, False):
            with self.subTest(symlink=symlink), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "artifact.elpx"
                original = self.fixture()
                path.write_bytes(original)
                saved = path.with_name("original.elpx")
                victim = path.with_name("victim.txt")
                victim.write_bytes(b"victim remains intact")
                transform = pdf.patched_archive

                def swap(payload):
                    result = transform(payload)
                    path.rename(saved)
                    if symlink:
                        path.symlink_to(victim)
                    else:
                        path.write_bytes(b"replacement remains intact")
                    return result

                with patch.object(pdf, "patched_archive", side_effect=swap):
                    with self.assertRaises((ValueError, OSError)):
                        self.run_cli(path)
                self.assertEqual(saved.read_bytes(), original)
                self.assertEqual(victim.read_bytes(), b"victim remains intact")
                self.assertEqual(path.read_bytes(), b"victim remains intact" if symlink
                                 else b"replacement remains intact")

    def test_swap_after_writer_identity_check_cannot_redirect_the_write(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact.elpx"
            path.write_bytes(self.fixture())
            saved = path.with_name("original.elpx")
            victim = path.with_name("victim.txt")
            victim.write_bytes(b"victim remains intact")
            fstat = os.fstat
            # The writable descriptor has been opened and checked; change the
            # name immediately afterwards, before its first write.
            opened = os.open
            writer = None

            def record_open(name, flags, *args, **kwargs):
                nonlocal writer
                fd = opened(name, flags, *args, **kwargs)
                if flags & (os.O_WRONLY | os.O_RDWR):
                    writer = fd
                return fd

            def swap_after_check(fd):
                result = fstat(fd)
                if fd == writer and not saved.exists():
                    path.rename(saved)
                    path.symlink_to(victim)
                return result

            with patch.object(os, "open", side_effect=record_open), patch.object(
                    os, "fstat", side_effect=swap_after_check):
                self.run_cli(path)
            self.assertEqual(victim.read_bytes(), b"victim remains intact")
            self.assertTrue(path.is_symlink())
            self.assertEqual(pdf.verify_archive(saved.read_bytes()), (1, 0))

    def test_swap_during_writer_open_is_checked_before_truncation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact.elpx"
            original = self.fixture()
            path.write_bytes(original)
            saved = path.with_name("original.elpx")
            victim = path.with_name("victim.txt")
            victim.write_bytes(b"victim remains intact")
            opened = os.open

            def swap_before_open(name, flags, *args, **kwargs):
                if flags & os.O_WRONLY and not saved.exists():
                    path.rename(saved)
                    path.symlink_to(victim)
                return opened(name, flags, *args, **kwargs)

            # The descriptor identity check also protects platforms without
            # O_NOFOLLOW, after a preliminary symlink check has already passed.
            with patch.object(os, "O_NOFOLLOW", 0, create=True), patch.object(
                    os, "open", side_effect=swap_before_open):
                with self.assertRaises(ValueError):
                    self.run_cli(path)
            self.assertEqual(saved.read_bytes(), original)
            self.assertEqual(victim.read_bytes(), b"victim remains intact")

    def test_regular_update_and_initial_symlink_preserve_inode_mode_and_other_members(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact.elpx"
            path.write_bytes(self.fixture())
            path.chmod(0o640)
            before = path.stat()
            selected = path.with_name("selected.elpx")
            selected.symlink_to(path)
            self.run_cli(selected)
            self.assertTrue(selected.is_symlink())
            self.assertEqual((path.stat().st_ino, stat.S_IMODE(path.stat().st_mode)),
                             (before.st_ino, 0o640))
            self.assertEqual(pdf.verify_archive(path.read_bytes()), (1, 0))
            self.assertEqual(pdf.read_archive(path.read_bytes())[1]["content.xml"],
                             b"untouched native content")

    def test_noop_and_read_only_check_never_open_for_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hardened.elpx"
            path.write_bytes(pdf.patched_archive(self.fixture())[0])
            path.chmod(0o444)
            before = path.read_bytes(), path.stat().st_mtime_ns
            opened = os.open

            def read_only_open(name, flags, *args, **kwargs):
                if flags & (os.O_WRONLY | os.O_RDWR):
                    self.fail("A no-op or --check requested write permission")
                return opened(name, flags, *args, **kwargs)

            with patch.object(os, "open", side_effect=read_only_open):
                self.run_cli(path)
                self.run_cli(path, check=True)
            self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)


if __name__ == "__main__":
    unittest.main()
