from collections import Counter


class GSequence:
    """
    GSequence module

    This module contains functions and classes for working with a genomic
    sequence.
    """
    __slot__ = ["sequence", "quality", "name", "data"]

    def __init__(self, sequence: str, quality: str = "",
                 name: str = "", data: list = []):
        """Create a GSequence object.

        :param sequence: Nucleotide sequence
        :type sequence: str
        :param quality: Quality of FASTQ, defaults to ""
        :type quality: str, optional
        :param name: Name of the sequence, defaults to ""
        :type name: str, optional
        :param data: Additional information from the sequence header,
                     defaults to []
        :type data: list, optional
        """
        self.sequence = sequence.upper()
        self.quality = quality
        self.name = name
        self.data = data

    def __len__(self):
        """
        Return the length of the sequence.

        :return: length
        :rtype: int
        """
        return len(self.sequence)

    def __hash__(self):
        return hash((self.sequence, self.name))

    def __eq__(self, other):
        return self.sequence == other.sequence

    def complement(self):
        """Convert the sequence into a complement sequence.
        """
        conversion = {"A": "T",
                      "T": "A",
                      "C": "G",
                      "G": "C"}
        self.sequence = ''.join(conversion.get(char, char)
                                for char in self.sequence)

    def reverse(self):
        """Convert the sequence into a reverse sequence as well as the quality
        if applicable.
        """
        self.sequence = self.sequence[::-1]
        if self.quality:
            self.quality = self.quality[::-1]

    def reverse_complement(self):
        """Convert the sequence into a reverse complement sequence as well as
        the quality if applicable.
        """
        self.reverse()
        self.complement()

    def trim(self, start: int = 0, end: int = 0):
        """Remove the nucleotides from the starting or ending according to the
        defined length.

        :param start: Define the length to remove from starting, defaults to 0
        :type start: int, optional
        :param end: Define the length to remove from ending, defaults to 0
        :type end: int, optional
        """
        if start:
            self.sequence = self.sequence[start:]
            if self.quality:
                self.quality = self.quality[start:]
        if end:
            self.sequence = self.sequence[:-end]
            if self.quality:
                self.quality = self.quality[:-end]

    def dna2rna(self):
        """Convert DNA sequence to RNA sequence by replacing "T" with "U"."""
        self.sequence = self.sequence.replace("T", "U")

    def rna2dna(self):
        """Convert RNA sequence to DNA sequence by replacing "U" with "T"."""
        self.sequence = self.sequence.replace("U", "T")

    def count_table(self):
        """Return a dictionary for the counting frequency of all nucleic acids.

        :return: A count table
        :rtype: dict
        """
        return Counter(self.sequence)

    def slice_sequence(self, start, end):
        """Return the sequence by the given start and end positions.

        :param start: Start position
        :type start: int
        :param end: End position
        :type end: int
        :return: Sequence
        :rtype: str
        """
        seq = GSequence(sequence=self.sequence[start:end],
                        name=self.name, data=self.data)
        return seq
