import unittest
from genomkit import GSequences
# from genomkit.sequences.io import load_FASTA, load_FASTQ
import os

script_path = os.path.dirname(__file__)


class TestGSequences(unittest.TestCase):

    def test_len(self):
        seqs = GSequences(name="test FASTA")
        seqs.load(filename=os.path.join(script_path,
                  "test_files/fasta/example.fasta"))
        self.assertEqual(len(seqs), 4)
        seqs = GSequences(name="test FASTQ")
        seqs.load(filename=os.path.join(script_path,
                  "test_files/fastq/example_R1.fastq"))
        self.assertEqual(len(seqs), 100)
        seqs = GSequences(name="test FASTQ")
        seqs.load(filename=os.path.join(script_path,
                  "test_files/fastq/example_R2.fastq"))
        self.assertEqual(len(seqs), 100)

    def test_complement(self):
        seqs = GSequences(name="test")
        seqs.load(filename=os.path.join(script_path,
                  "test_files/fasta/example.fasta"))
        seqs.complement()
        self.assertEqual(len(seqs), 4)

    def test_reverse(self):
        seqs = GSequences(name="test")
        seqs.load(filename=os.path.join(script_path,
                  "test_files/fasta/example.fasta"))
        seqs.reverse()
        self.assertEqual(len(seqs), 4)

    def test_reverse_complement(self):
        seqs = GSequences(name="test")
        seqs.load(filename=os.path.join(script_path,
                  "test_files/fasta/example.fasta"))
        seqs.reverse_complement()
        self.assertEqual(len(seqs), 4)

    def test_trim(self):
        seqs = GSequences(name="test")
        seqs.load(filename=os.path.join(script_path,
                  "test_files/fasta/example.fasta"))
        self.assertEqual(len(seqs[0]), 185)
        seqs.trim(start=10)
        self.assertEqual(len(seqs[0]), 175)
        seqs.trim(start=20)
        self.assertEqual(len(seqs[0]), 155)
        seqs = GSequences(name="test FASTQ")
        seqs.load(filename=os.path.join(script_path,
                  "test_files/fastq/example_R1.fastq"))
        self.assertEqual(len(seqs[0].sequence), 75)
        self.assertEqual(len(seqs[0].quality), 75)
        seqs.trim(start=20)
        self.assertEqual(len(seqs[0].sequence), 55)
        self.assertEqual(len(seqs[0].quality), 55)

