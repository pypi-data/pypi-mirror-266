import unittest
from genomkit import GSequence
# from genomkit.sequences.io import load_FASTA, load_FASTQ
import os

script_path = os.path.dirname(__file__)


class TestGSequences(unittest.TestCase):

    def test_len(self):
        seq = GSequence(sequence="CCAGCATGTACCAGCGCCTGGGGCTGGACTATGAGGAGCGAG",
                        name="test", data=["A", "B", "C"])
        self.assertEqual(len(seq), 42)

    def test_eq(self):
        seq = GSequence(sequence="CCAGCATGTACCAGCGCCTGGGGCTGGACTATGAGGAGCGAG",
                        name="test", data=["A", "B", "C"])
        seq1 = GSequence(sequence="CCAGCATGTACCAGCGCCTGGGGCTGGACTATGAGGAGCGAG",
                         name="test1", data=["A", "B", "C"])
        self.assertEqual(seq, seq1)

    def test_complement(self):
        seq = GSequence(sequence="CCAGCATGTACCAGCGCCTGGGGCTGGACTATGAGGAGCGAG",
                        name="test", data=["A", "B", "C"])
        seq.complement()
        self.assertEqual(len(seq), 42)

    def test_reverse(self):
        seq = GSequence(sequence="CCAGCATGTACCAGCGCCTGGGGCTGGACTATGAGGAGCGAG",
                        name="test", data=["A", "B", "C"])
        seq.reverse()
        self.assertEqual(len(seq), 42)

    def test_reverse_complement(self):
        seq = GSequence(sequence="CCAGCATGTACCAGCGCCTGGGGCTGGACTATGAGGAGCGAG",
                        name="test", data=["A", "B", "C"])
        seq.reverse_complement()
        self.assertEqual(len(seq), 42)
