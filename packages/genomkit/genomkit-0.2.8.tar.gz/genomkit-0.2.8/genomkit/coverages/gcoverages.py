import pyBigWig
import numpy as np
import pandas as pd
import pysam
from tqdm import tqdm
from genomkit import GRegions, GRegion
import os


class GCoverages:
    """
    GCoverages module

    This module contains functions and classes for working with a collection of
    genomic coverages. It provides utilities for handling and analyzing the
    interactions of many genomic coverages.
    """
    def __init__(self, bin_size: int = 1, load: str = "", windows=None):
        """Initialize GCoverages object.

        :param bin_size: Size of the bin for coverage calculation.
                         Defaults to 1 (single nucleotide resolution).
        :type bin_size: str
        """
        self.coverage = {}
        self.bin_size = bin_size
        if load.lower().endswith(".bw") or load.lower().endswith(".bigwig"):
            self.load_coverage_from_bigwig(load, windows=windows)
        elif load.lower().endswith(".bam"):
            self.calculate_coverage_from_bam(load, windows=windows)
        elif load.lower().endswith(".bed") or \
                load.lower().endswith(".bedgraph"):
            regions = GRegions(name=os.path.basename(load), load=load)
            self.calculate_coverage_GRegions2(windows=windows,
                                              scores=regions)

    def load_coverage_from_bigwig(self, filename: str, windows=None):
        """Load coverage data from a bigwig file.

        :param filename: Path to the bigwig file.
        :type filename: str
        :param windows: GRegions for extracting the coverage profile
        :type windows: GRegions
        """
        bw = pyBigWig.open(filename)
        if not windows:
            # Get the coverage on the whole genome
            chrom_regions = GRegions(name="chromosomes")
            chromosomes = bw.chroms()
            for chrom, chrom_length in chromosomes.items():
                chrom_regions.add(GRegion(sequence=chrom,
                                          start=0,
                                          end=int(chrom_length)))
            for r in tqdm(chrom_regions,
                          desc=os.path.basename(filename),
                          total=len(chrom_regions)):
                coverage = bw.values(r.sequence, r.start, r.end, numpy=True)
                if self.bin_size > 1:
                    coverage = [np.mean(coverage[i:i+self.bin_size])
                                if i+self.bin_size <= len(coverage)
                                else np.mean(coverage[i:])
                                for i in range(0, len(coverage),
                                               self.bin_size)]
                self.coverage[r] = coverage
        else:
            # Get only the coverage on the defined regions
            assert isinstance(windows, GRegions)
            self.coverage = {}
            for window in tqdm(windows,
                               desc=os.path.basename(filename),
                               total=len(windows)):
                coverage = bw.values(window.sequence,
                                     window.start,
                                     window.end,
                                     numpy=True)
                if self.bin_size > 1:
                    coverage = [np.mean(coverage[i:i+self.bin_size])
                                if i+self.bin_size <= len(coverage)
                                else np.mean(coverage[i:])
                                for i in range(0, len(coverage),
                                               self.bin_size)]
                self.coverage[window] = coverage
        bw.close()

    def calculate_coverage_from_bam(self, filename: str, windows=None):
        """Calculate coverage from a BAM file.

        :param filename: Path to the BAM file.
        :type filename: str
        :param windows: GRegions for extracting the coverage profile
        :type windows: GRegions
        """
        bam = pysam.AlignmentFile(filename, "rb")
        if not windows:
            # Get the coverage of the whole genome
            for pileupcolumn in bam.pileup():
                chrom = bam.get_reference_name(pileupcolumn.reference_id)
                chrom_len = bam.get_reference_length(chrom)
                r = GRegion(sequence=chrom, start=0, end=chrom_len)
                if chrom not in [r.sequence for r in self.coverage.keys()]:
                    self.coverage[r] = [0] * chrom_len
                self.coverage[r][pileupcolumn.reference_pos] += 1
        if windows:
            for w in windows:
                self.coverage[w] = [0] * len(w)
                for pileupcolumn in bam.pileup(w.sequence, w.start, w.end):
                    self.coverage[w][pileupcolumn.reference_pos-w.start] += 1
        bam.close()
        # Adjust for bin size
        for r in self.coverage.keys():
            if self.bin_size > 1:
                self.coverage[r] = [sum(self.coverage[r][i:i+self.bin_size]) /
                                    self.bin_size
                                    for i in range(0,
                                                   len(self.coverage[r]),
                                                   self.bin_size)]

    def calculate_coverage_GRegions2(self, scores, windows=None,
                                     strandness: bool = False):
        """Calculate the coverage from two GRegions. `windows` defines the loci
        for the coverage `scores` contains the scores loaded into the coverage.

        :param windows: Define the windows and the length of the coverage
        :type windows: GRegions
        :param scores: Provide the scores for calculating the coverage
        :type scores: GRegions
        :param strandness: Make this operation strandness specific, defaults
                        to False
        :type strandness: bool, optional
        """
        from genomkit import GRegions
        assert isinstance(windows, GRegions)
        assert isinstance(scores, GRegions)
        print("1")
        filtered_scores = scores.intersect(target=windows, mode="ORIGINAL")
        print("2")
        # Preallocate coverage arrays
        # num_windows = len(windows)
        num_bins = len(windows[0]) // self.bin_size
        self.coverage = {region: np.zeros(shape=num_bins)
                         for region in windows}
        for target in tqdm(filtered_scores, desc=scores.name,
                           total=len(filtered_scores)):
            overlap_regions = [region for region in windows
                               if region.overlap(target,
                                                 strandness=strandness)]
            start_inds = np.maximum(0,
                                    target.start -
                                    np.array([region.start
                                              for region in overlap_regions]))
            start_inds = start_inds // self.bin_size
            end_inds = np.minimum([len(region)
                                   for region in overlap_regions],
                                  target.end -
                                  np.array([region.start
                                            for region in overlap_regions]))
            end_inds = end_inds // self.bin_size
            for region, start_ind, end_ind in zip(overlap_regions,
                                                  start_inds,
                                                  end_inds):
                self.coverage[region][start_ind:end_ind] += target.score

    def calculate_coverage_GRegions(self, scores, windows=None,
                                    strandness: bool = False):
        """Calculate the coverage from two GRegions. `windows` defines the loci
        for the coverage `scores` contains the scores loaded into the coverage.

        :param windows: Define the windows and the length of the coverage
        :type windows: GRegions
        :param scores: Provide the scores for calculating the coverage
        :type scores: GRegions
        :param strandness: Make this operation strandness specific, defaults
                           to False
        :type strandness: bool, optional
        """
        from genomkit import GRegions
        assert isinstance(windows, GRegions)
        assert isinstance(scores, GRegions)
        filtered_scores = scores.intersect(target=windows,
                                           mode="ORIGINAL")
        for region in tqdm(windows, desc=scores.name, total=len(windows)):
            self.coverage[region] = np.zeros(shape=len(region) //
                                             self.bin_size)
            for target in filtered_scores:
                if region.overlap(target, strandness=strandness):
                    start_ind = (max(0, target.start - region.start))
                    start_ind = start_ind // self.bin_size
                    end_ind = (min(len(region), target.end - region.start))
                    end_ind = end_ind // self.bin_size
                    for i in range(start_ind, end_ind):
                        self.coverage[region][i] += target.score

    def get_coverage(self, gregion: str):
        """Get coverage data for a specific sequence by name. This sequence
        can be a chromosome or a genomic region.

        :param seq_name: sequence name.
        :type seq_name: str
        :return: Coverage data for the specified sequence.
        :rtype: numpy array
        """
        return self.coverage.get(gregion, [])

    def filter_regions_coverage(self, regions):
        """Filter regions for their coverages.

        :param regions: GRegions object containing regions.
        :type regions: GRegions
        :return: Dictionary where keys are region objects and values are
                 coverage lists.
        :rtype: dict
        """
        filtered_coverages = {}
        for r in regions:
            for w in self.coverage.keys():
                if r.overlap(w):
                    offset1 = max(r.start - w.start, 0)
                    offset2 = min(r.end - w.start, w.end - w.start)
                    if self.bin_size > 1:
                        offset1 = offset1 // self.bin_size
                        offset2 = offset2 // self.bin_size
                    coverage = self.coverage[w][offset1:offset2]
                    filtered_coverages[r] = coverage
        return filtered_coverages

    def total_sequencing_depth(self):
        """Calculate the total sequencing depth.

        :return: Total sequencing depth.
        :rtype: float
        """
        total_depth = 0
        for chrom, cov in self.coverage.items():
            total_depth += np.nansum(cov)
        return total_depth

    def scale_coverage(self, coefficient):
        """Scale the coverages by a coefficient.

        :param coefficient: Coefficient to scale the coverages.
        :type coefficient: float
        """
        for chrom in self.coverage:
            # Replace NaN values with 0 before scaling
            self.coverage[chrom][np.isnan(self.coverage[chrom])] = 0
            # Scale the non-NaN values
            self.coverage[chrom] = self.coverage[chrom] * coefficient

    def flip_negative_regions(self):
        """Flip the coverage arrays which are on the negative strands. If the
        coverage arrays are calculated by the whole chromosomes, it won't
        work.
        """
        for region, cov in self.coverage.items():
            if region.orientation == "-":
                self.coverage[region] = cov[::-1]

    def get_dataframe(self):
        """Return a pandas dataframe concatenating all coverage arrays."""
        df = pd.DataFrame(self.coverage)
        df = df.transpose()
        df.index.name = None
        return df
