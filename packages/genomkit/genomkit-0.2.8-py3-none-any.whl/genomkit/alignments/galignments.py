import pysam


class GAlignments:
    """
    GAlignments module

    This module contains functions and classes for working with a collection of
    genomic alignments. It provides utilities for handling and analyzing the
    interactions of many genomic alignments.
    """
    def __init__(self, file_path, file_format):
        """Initialize GAlignments object.

        Parameters:
            file_path (str): Path to the BAM/SAM file.
            file_format (str): File format ('bam' or 'sam').
        """
        self.file_path = file_path
        self.file_format = file_format
        self.bam = None
        self._open_file()

    def _open_file(self):
        """
        Open BAM/SAM file.
        """
        if self.file_format == 'bam':
            self.bam = pysam.AlignmentFile(self.file_path, 'rb')
        elif self.file_format == 'sam':
            self.bam = pysam.AlignmentFile(self.file_path, 'r')
        else:
            raise ValueError("Unsupported file format. "
                             "Supported formats: 'bam', 'sam'.")

    def load_reads(self):
        """
        Load reads from BAM/SAM file.

        Returns:
            list: List of reads.
        """
        reads = []
        for read in self.bam.fetch():
            reads.append(read)
        return reads

    def calculate_coverage(self):
        """
        Calculate coverage from loaded reads.

        Returns:
            dict: Coverage information.
        """
        coverage = {}
        for pileupcolumn in self.bam.pileup():
            coverage[pileupcolumn.pos] = pileupcolumn.n
        return coverage
