from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

from bioartifact import inspect_artifact, summarize_directory, validate_artifact

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class FixtureSuiteTests(unittest.TestCase):
    def test_fixture_files_are_present(self) -> None:
        expected = [
            "reference.fa",
            "reads_R1.fastq",
            "reads_R2.fastq",
            "reads_R1.fastq.gz",
            "aligned.sorted.sam",
            "aligned.sorted.bam",
            "variants.vcf",
            "variants.vcf.gz",
            "regions.bed",
            "peaks.narrowPeak",
            "annotation.gtf",
            "de_table.tsv",
            "multiqc_report.html",
        ]
        for relative_path in expected:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((FIXTURES / relative_path).is_file())

    def test_binary_fixtures_are_deterministic(self) -> None:
        expected_hashes = {
            "reads_R1.fastq.gz": "be1e3f34f1ccae7919a45637c206749393ec221c65776e768f19eaa2e1acd427",
            "variants.vcf.gz": "4fec2f94edef8698f2c207ce03a61f03d82adbe4f6954417d2ce4df164ce3cd4",
            "aligned.sorted.bam": "686d06af35cff1fd3907dbd27a534a2f2973d483cf045a85abce0039c44d96c1",
        }
        for relative_path, expected_hash in expected_hashes.items():
            with self.subTest(relative_path=relative_path):
                digest = hashlib.sha256((FIXTURES / relative_path).read_bytes()).hexdigest()
                self.assertEqual(digest, expected_hash)

    def test_inspects_valid_fixture_files(self) -> None:
        expected_types = {
            "reference.fa": "fasta",
            "reads_R1.fastq": "fastq",
            "reads_R1.fastq.gz": "fastq",
            "aligned.sorted.sam": "sam",
            "aligned.sorted.bam": "bam",
            "variants.vcf": "vcf",
            "variants.vcf.gz": "vcf",
            "regions.bed": "bed",
            "peaks.narrowPeak": "narrowPeak",
            "annotation.gtf": "gtf",
            "de_table.tsv": "tsv",
            "multiqc_report.html": "html",
        }
        for relative_path, expected_type in expected_types.items():
            with self.subTest(relative_path=relative_path):
                artifact = inspect_artifact(FIXTURES / relative_path)
                self.assertTrue(artifact.valid, artifact.errors)
                self.assertEqual(artifact.artifact_type, expected_type)

    def test_valid_fixture_contracts_pass(self) -> None:
        contracts = [
            ("reads_R1.fastq.gz", "fastq", {}),
            ("reads_R1.fastq", "paired_fastq", {"mate": FIXTURES / "reads_R2.fastq"}),
            ("aligned.sorted.sam", "sorted_bam", {}),
            ("aligned.sorted.bam", "sorted_bam", {}),
            ("variants.vcf.gz", "valid_vcf", {}),
            ("peaks.narrowPeak", "narrowpeak", {}),
            ("de_table.tsv", "de_table", {}),
        ]
        for relative_path, contract_name, kwargs in contracts:
            with self.subTest(relative_path=relative_path, contract_name=contract_name):
                result = validate_artifact(FIXTURES / relative_path, contract_name, **kwargs)
                self.assertTrue(result.passed, result.to_dict())

    def test_invalid_fixtures_fail_expected_contracts(self) -> None:
        contracts = [
            ("invalid/bad.fastq", "fastq"),
            ("invalid/bad.narrowPeak", "narrowpeak"),
            ("invalid/bad_de_table.tsv", "de_table"),
            ("invalid/bad.vcf", "valid_vcf"),
            ("aligned.sorted.bam", "indexed_bam"),
        ]
        for relative_path, contract_name in contracts:
            with self.subTest(relative_path=relative_path, contract_name=contract_name):
                result = validate_artifact(FIXTURES / relative_path, contract_name)
                self.assertFalse(result.passed)
                self.assertTrue(any(check.status == "fail" for check in result.checks))
                self.assertTrue(
                    any(check.remediation for check in result.checks if check.status == "fail")
                )

    def test_fixture_directory_summary(self) -> None:
        summary = summarize_directory(FIXTURES)
        self.assertTrue(summary["valid"])
        self.assertEqual(
            summary["counts"],
            {
                "bam": 1,
                "bed": 1,
                "fasta": 1,
                "fastq": 3,
                "gtf": 1,
                "html": 1,
                "narrowPeak": 1,
                "sam": 1,
                "tsv": 1,
                "vcf": 2,
            },
        )


if __name__ == "__main__":
    unittest.main()
