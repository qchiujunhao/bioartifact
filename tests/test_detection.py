from __future__ import annotations

import unittest

from bioartifact import detect_artifact_type


class DetectionTests(unittest.TestCase):
    def test_detects_common_extensions(self) -> None:
        cases = {
            "sample.fastq": "fastq",
            "sample.fq.gz": "fastq",
            "reference.fa": "fasta",
            "variants.vcf.gz": "vcf",
            "peaks.narrowPeak": "narrowPeak",
            "regions.bed": "bed",
            "alignment.bam": "bam",
            "annotation.gff3": "gff",
            "counts.tsv": "tsv",
            "report.html": "html",
        }
        for filename, expected in cases.items():
            with self.subTest(filename=filename):
                self.assertEqual(detect_artifact_type(filename), expected)

    def test_unknown_extension(self) -> None:
        self.assertEqual(detect_artifact_type("notes.md"), "unknown")


if __name__ == "__main__":
    unittest.main()
