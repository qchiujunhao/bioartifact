from __future__ import annotations

import gzip
import struct
from collections import Counter
from pathlib import Path

from bioartifact.io import is_gzip, open_text, strip_newline
from bioartifact.models import ArtifactResult


def _parse_sort_order(header_text: str) -> str | None:
    for line in header_text.splitlines():
        if not line.startswith("@HD"):
            continue
        for field in line.split("\t")[1:]:
            if field.startswith("SO:"):
                return field[3:]
    return None


def _bam_index_present(path: Path) -> bool:
    candidates = [
        Path(f"{path}.bai"),
        path.with_suffix(".bai"),
        Path(f"{path}.csi"),
        path.with_suffix(".csi"),
    ]
    return any(candidate.exists() for candidate in candidates)


def inspect_bam(path: Path) -> ArtifactResult:
    errors: list[str] = []
    warnings: list[str] = []
    header_text = ""
    reference_names: list[str] = []
    sorted_order: str | None = None
    index_present = _bam_index_present(path)
    mapped_reads: int | None = None
    unmapped_reads: int | None = None

    try:
        if not is_gzip(path):
            errors.append("BAM file is not BGZF/gzip encoded")
        else:
            with gzip.open(path, "rb") as handle:
                magic = handle.read(4)
                if magic != b"BAM\x01":
                    errors.append("BAM magic header is missing")
                else:
                    header_length_raw = handle.read(4)
                    if len(header_length_raw) != 4:
                        errors.append("BAM header length is truncated")
                    else:
                        header_length = struct.unpack("<i", header_length_raw)[0]
                        if header_length < 0:
                            errors.append("BAM header length is negative")
                        else:
                            header_text = handle.read(header_length).decode(
                                "utf-8", errors="replace"
                            )
                            sorted_order = _parse_sort_order(header_text)
                            reference_count_raw = handle.read(4)
                            if len(reference_count_raw) != 4:
                                errors.append("BAM reference count is truncated")
                            else:
                                reference_count = struct.unpack("<i", reference_count_raw)[0]
                                for _ in range(max(reference_count, 0)):
                                    name_length_raw = handle.read(4)
                                    if len(name_length_raw) != 4:
                                        errors.append("BAM reference name length is truncated")
                                        break
                                    name_length = struct.unpack("<i", name_length_raw)[0]
                                    raw_name = handle.read(name_length)
                                    length_raw = handle.read(4)
                                    if len(raw_name) != name_length or len(length_raw) != 4:
                                        errors.append("BAM reference entry is truncated")
                                        break
                                    reference_names.append(
                                        raw_name.rstrip(b"\x00").decode("utf-8", errors="replace")
                                    )
    except (OSError, EOFError, gzip.BadGzipFile, struct.error) as exc:
        errors.append(f"could not read BAM header: {exc}")

    if not errors:
        try:
            import pysam  # type: ignore[import-not-found]
        except ImportError:
            warnings.append("pysam is not installed; BAM read statistics were not computed")
        else:
            try:
                with pysam.AlignmentFile(str(path), "rb") as handle:
                    if handle.has_index():
                        stats = handle.get_index_statistics()
                        mapped_reads = sum(stat.mapped for stat in stats)
                        unmapped_reads = sum(stat.unmapped for stat in stats)
                    else:
                        warnings.append(
                            "BAM index is absent; mapped/unmapped statistics not computed"
                        )
            except Exception as exc:  # pragma: no cover - depends on optional pysam behavior
                warnings.append(f"pysam could not compute BAM statistics: {exc}")

    return ArtifactResult(
        path=str(path),
        artifact_type="bam",
        valid=not errors,
        summary={
            "references": len(reference_names),
            "reference_names": reference_names,
            "sorted": sorted_order == "coordinate",
            "sort_order": sorted_order,
            "index_present": index_present,
            "mapped_reads": mapped_reads,
            "unmapped_reads": unmapped_reads,
        },
        warnings=warnings,
        errors=errors,
        usable_as=["read_alignment"] if not errors else [],
        suggested_next_steps=["alignment_qc", "variant_calling"] if not errors else [],
    )


def inspect_sam(path: Path) -> ArtifactResult:
    errors: list[str] = []
    warnings: list[str] = []
    header_lines: list[str] = []
    references: list[str] = []
    alignments = 0
    mapped = 0
    unmapped = 0
    flag_counts: Counter[int] = Counter()

    try:
        with open_text(path) as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = strip_newline(raw_line)
                if not line:
                    continue
                if line.startswith("@"):
                    header_lines.append(line)
                    if line.startswith("@SQ"):
                        for field in line.split("\t")[1:]:
                            if field.startswith("SN:"):
                                references.append(field[3:])
                    continue
                fields = line.split("\t")
                if len(fields) < 11:
                    errors.append(f"alignment line {line_number} has fewer than 11 SAM columns")
                    continue
                alignments += 1
                try:
                    flag = int(fields[1])
                except ValueError:
                    errors.append(f"alignment line {line_number} has non-integer FLAG")
                    continue
                flag_counts[flag] += 1
                if flag & 0x4:
                    unmapped += 1
                else:
                    mapped += 1
    except OSError as exc:
        errors.append(f"could not read SAM: {exc}")

    if not header_lines:
        warnings.append("SAM header is absent")
    if alignments == 0 and not errors:
        warnings.append("SAM contains no alignment records")

    header_text = "\n".join(header_lines)
    sort_order = _parse_sort_order(header_text)

    return ArtifactResult(
        path=str(path),
        artifact_type="sam",
        valid=not errors,
        summary={
            "alignments": alignments,
            "mapped_reads": mapped,
            "unmapped_reads": unmapped,
            "references": len(references),
            "reference_names": references,
            "sorted": sort_order == "coordinate",
            "sort_order": sort_order,
            "flag_counts": dict(sorted(flag_counts.items())),
        },
        warnings=warnings,
        errors=errors,
        usable_as=["read_alignment"] if not errors else [],
        suggested_next_steps=["alignment_qc", "bam_conversion"] if not errors else [],
    )
