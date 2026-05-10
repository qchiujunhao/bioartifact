from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from bioartifact import inspect_artifact, summarize_directory, validate_artifact
from bioartifact.cli.main import main


class InspectionAndContractTests(unittest.TestCase):
    def test_fastq_inspection_and_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "reads.fastq"
            path.write_text("@r1\nACGT\n+\nFFFF\n@r2\nGA\n+\nFF\n", encoding="utf-8")

            artifact = inspect_artifact(path)
            self.assertTrue(artifact.valid)
            self.assertEqual(artifact.artifact_type, "fastq")
            self.assertEqual(artifact.summary["records"], 2)

            contract = validate_artifact(path, "fastq")
            self.assertTrue(contract.passed)

    def test_invalid_fastq_fails_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "reads.fastq"
            path.write_text("@r1\nACGT\n+\nFFF\n", encoding="utf-8")

            contract = validate_artifact(path, "fastq")
            self.assertFalse(contract.passed)
            self.assertTrue(
                any(check.name == "sequence_quality_lengths" for check in contract.checks)
            )

    def test_paired_fastq_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            first = Path(tmpdir) / "sample_R1.fastq"
            second = Path(tmpdir) / "sample_R2.fastq"
            first.write_text("@read1/1\nACGT\n+\nFFFF\n@read2/1\nTT\n+\nFF\n", encoding="utf-8")
            second.write_text("@read1/2\nTGCA\n+\nFFFF\n@read2/2\nAA\n+\nFF\n", encoding="utf-8")

            contract = validate_artifact(first, "paired_fastq", mate=second)
            self.assertTrue(contract.passed)

    def test_vcf_inspection_and_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "variants.vcf"
            path.write_text(
                "##fileformat=VCFv4.2\n"
                "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tsample1\n"
                "chr1\t42\t.\tA\tG\t50\tPASS\t.\tGT\t0/1\n",
                encoding="utf-8",
            )

            artifact = inspect_artifact(path)
            self.assertTrue(artifact.valid)
            self.assertEqual(artifact.summary["records"], 1)

            contract = validate_artifact(path, "valid_vcf")
            self.assertTrue(contract.passed)

    def test_narrowpeak_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "peaks.narrowPeak"
            path.write_text("chr1\t10\t50\tpeak1\t100\t.\t12.5\t4.2\t3.8\t20\n", encoding="utf-8")

            contract = validate_artifact(path, "narrowpeak")
            self.assertTrue(contract.passed)

    def test_de_table_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "de.tsv"
            path.write_text(
                "gene\tlog2FoldChange\tpvalue\tpadj\n"
                "geneA\t1.2\t0.01\t0.02\n"
                "geneB\t-0.5\t0.30\t0.40\n",
                encoding="utf-8",
            )

            contract = validate_artifact(path, "de_table")
            self.assertTrue(contract.passed)

    def test_summarize_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "reads.fastq").write_text("@r1\nA\n+\nF\n", encoding="utf-8")
            (root / "notes.md").write_text("ignore me\n", encoding="utf-8")
            nested = root / "nested"
            nested.mkdir()
            (nested / "variants.vcf").write_text(
                "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n",
                encoding="utf-8",
            )

            shallow = summarize_directory(root)
            self.assertEqual(shallow["counts"], {"fastq": 1})

            recursive = summarize_directory(root, recursive=True)
            self.assertEqual(recursive["counts"], {"fastq": 1, "vcf": 1})

    def test_cli_inspect_return_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "reads.fastq"
            path.write_text("@r1\nACGT\n+\nFFFF\n", encoding="utf-8")

            with redirect_stdout(StringIO()):
                self.assertEqual(main(["inspect", str(path), "--json"]), 0)


if __name__ == "__main__":
    unittest.main()
