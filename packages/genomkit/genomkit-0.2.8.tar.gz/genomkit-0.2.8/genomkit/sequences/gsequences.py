from .io import load_FASTA, load_FASTA_from_file, \
                load_FASTQ, load_FASTQ_from_file, \
                write_FASTA, write_FASTQ
import gzip


###########################################################################
# GSequences
###########################################################################
class GSequences:
    """
    GSequences module

    This module contains functions and classes for working with a collection of
    genomic sequences. It provides utilities for handling and analyzing the
    interactions of many genomic sequences.
    """
    def __init__(self, name: str = "", load: str = ""):
        self.elements = []
        self.name = name
        if load:
            self.load(load)

    def __len__(self):
        """Return the number of regions in this GSequences.

        :return: Number of sequences
        :rtype: int
        """
        return len(self.elements)

    def __getitem__(self, key):
        return self.elements[key]

    def add(self, sequence):
        """Append a GSequence at the end of the elements of GSequences.

        :param sequence: A GSequence
        :type sequence: GSequence
        """
        self.elements.append(sequence)

    def load(self, filename: str):
        """Load a FASTA/FASTQ file into the GSequences.

        :param filename: Path to the FASTA/FASTQ file
        :type filename: str
        """
        if filename.endswith(".fasta") or filename.endswith(".fa"):
            res = load_FASTA(filename)
        elif filename.endswith(".fastq") or filename.endswith(".fq"):
            res = load_FASTQ(filename)
        elif filename.endswith(".fasta.gz") or filename.endswith(".fa.gz"):
            with gzip.open(filename, 'rt') as f:
                res = load_FASTA_from_file(f)
        elif filename.endswith(".fastq.gz") or filename.endswith(".fq.gz"):
            with gzip.open(filename, 'rt') as f:
                res = load_FASTQ_from_file(f)
        else:
            raise ValueError("Unsupported file format")
        self.elements = res.elements

    def complement(self):
        """Convert the sequences into complement sequences.
        """
        for seq in self.elements:
            seq.complement()

    def reverse(self):
        """Convert the sequences into reverse sequences.
        """
        for seq in self.elements:
            seq.reverse()

    def reverse_complement(self):
        """Convert the sequences into reverse complement sequences.
        """
        for seq in self.elements:
            seq.reverse_complement()

    def trim(self, start: int = 0, end: int = 0):
        """Remove the nucleotides from the starting or ending according to the
        defined length.

        :param start: Define the length to remove from starting, defaults to 0
        :type start: int, optional
        :param end: Define the length to remove from ending, defaults to 0
        :type end: int, optional
        """
        for seq in self.elements:
            seq.trim(start=start, end=end)

    def dna2rna(self):
        """Convert DNA sequences to RNA sequences by replacing "T" with "U"."""
        for seq in self.elements:
            seq.dna2rna()

    def rna2dna(self):
        """Convert RNA sequences to DNA sequences by replacing "U" with "T"."""
        for seq in self.elements:
            seq.rna2dna()

    def count_table(self):
        """Return a dictionary for the counting frequency of all nucleic acids.

        :return: A count table
        :rtype: dict
        """
        result = {}
        for seq in self.elements:
            count_dict = seq.count_table()
            for key, count in count_dict.items():
                result[key] = result.get(key, 0) + count
        return result

    def get_sequence(self, name, start, end):
        """Return the sequence according to the given name, start and end.

        :param name: Sequence name
        :type name: str
        :param start: Start position
        :type start: int
        :param end: End position
        :type end: int
        :return: GSequence
        :rtype: GSequence
        """
        for seq in self.elements:
            if seq.name == name:
                return seq.slice_sequence(start, end)

    def write_FASTA(self, filename: str, data: bool = False,
                    gz: bool = False):
        write_FASTA(seqs=self, filename=filename, data=data, gz=gz)

    def write_FASTQ(self, filename: str, data: bool = False,
                    gz: bool = True):
        write_FASTQ(seqs=self, filename=filename, data=data, gz=gz)
