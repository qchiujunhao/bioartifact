from __future__ import annotations

import gzip
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BGZF_EOF = bytes.fromhex("1f8b08040000000000ff0600424302001b0003000000000000000000")


def write_gzip(source: Path, target: Path) -> None:
    with (
        source.open("rb") as source_handle,
        target.open("wb") as raw_target,
        gzip.GzipFile(
            filename="", mode="wb", fileobj=raw_target, compresslevel=9, mtime=0
        ) as target_handle,
    ):
        target_handle.write(source_handle.read())


def bgzf_block(payload: bytes) -> bytes:
    compressor = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=-15)
    compressed = compressor.compress(payload) + compressor.flush()
    block_size = 18 + len(compressed) + 8
    if block_size > 65_536:
        raise ValueError("fixture payload is too large for one BGZF block")

    header = (
        b"\x1f\x8b\x08\x04"
        + b"\x00\x00\x00\x00"
        + b"\x00\xff"
        + struct.pack("<H", 6)
        + b"BC"
        + struct.pack("<H", 2)
        + struct.pack("<H", block_size - 1)
    )
    trailer = struct.pack("<II", zlib.crc32(payload) & 0xFFFFFFFF, len(payload) & 0xFFFFFFFF)
    return header + compressed + trailer


def bam_header_payload() -> bytes:
    header = "@HD\tVN:1.6\tSO:coordinate\n@SQ\tSN:chr1\tLN:32\n@SQ\tSN:chr2\tLN:32\n"
    payload = bytearray()
    payload.extend(b"BAM\x01")
    payload.extend(struct.pack("<i", len(header)))
    payload.extend(header.encode("ascii"))
    references = [("chr1", 32), ("chr2", 32)]
    payload.extend(struct.pack("<i", len(references)))
    for name, length in references:
        encoded_name = name.encode("ascii") + b"\x00"
        payload.extend(struct.pack("<i", len(encoded_name)))
        payload.extend(encoded_name)
        payload.extend(struct.pack("<i", length))
    return bytes(payload)


def write_bam(target: Path) -> None:
    target.write_bytes(bgzf_block(bam_header_payload()) + BGZF_EOF)


def main() -> None:
    write_gzip(ROOT / "reads_R1.fastq", ROOT / "reads_R1.fastq.gz")
    write_gzip(ROOT / "variants.vcf", ROOT / "variants.vcf.gz")
    write_bam(ROOT / "aligned.sorted.bam")


if __name__ == "__main__":
    main()
