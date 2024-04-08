import random
from genomkit import GRegion
import copy
import numpy as np
from .io import load_BED_intervaltree
import os
import sys
from copy import deepcopy
from tqdm import tqdm
from intervaltree import Interval, IntervalTree
from collections import defaultdict


###########################################################################
# GRegions
###########################################################################
class GRegionsTree:
    """
    GRegionsTree module

    This module contains functions and classes for working with a collection of
    genomic regions. It provides utilities for handling and analyzing the
    interactions of many genomic coordinates.
    """
    def __init__(self, name: str = "", load: str = ""):
        """Create an empty GRegions object. If a path to a BED file is defined
        in "load", all the regions will be loaded.

        :param name: Name of this GRegions, defaults to ""
        :type name: str, optional
        :param load: Path to a BED file, defaults to ""
        :type load: str, optional
        """
        self.elements = defaultdict(lambda: IntervalTree())
        self.name = name
        if load:
            self.load(load)

    def __len__(self):
        """Return the number of regions in this GRegions.

        :return: Number of regions
        :rtype: int
        """
        return sum([len(tree) for tree in self.elements.values()])

    def __getitem__(self, key):
        rest = key + 1
        for i, tree in self.elements.items():
            if rest > len(tree):
                rest -= len(tree)
            else:
                # print([rest, len(list(tree))])
                return sorted(tree)[rest-1].data

    def __iter__(self):
        for tree in self.elements.values():
            for interval in sorted(tree):
                yield interval.data

    def add(self, region):
        """Append a GRegion at the end of the elements of GRegions.

        :param region: A GRegion
        :type region: GRegion
        """
        self.elements[region.sequence].add(
            Interval(region.start, region.end, region)
        )

    def load(self, filename: str):
        """Load a BED file into the GRegions.

        :param filename: Path to the BED file
        :type filename: str
        """
        self.elements = load_BED_intervaltree(filename=filename)

    def write(self, filename: str, data: bool = False):
        """Write a BED file.

        :param filename: Path to the BED file
        :type filename: str
        :param data: Export extra data or not, defaults to False
        :type data: bool
        """
        with open(filename, "w") as f:
            for region in self:
                print(region.bed_entry(data=data), file=f)

    def get_sequences(self, unique: bool = False):
        """Return all chromosomes.

        :param unique: Only the unique names.
        :type unique: bool
        :return: A list of all chromosomes.
        :rtype: list
        """
        res = [r.sequence for r in self]
        if unique:
            res = list(set(res))
        res = sorted(res)
        return res

    def get_names(self, unique: bool = False):
        """Return a list of all region names. If the name is None,
        it return the region string.

        :return: A list of all regions' names.
        :rtype: list
        """
        names = [r.name for r in self]
        if unique:
            names = list(set(names))
            names.sort()
        return names

    def extend(self, upstream: int = 0, downstream: int = 0,
               strandness: bool = False, inplace: bool = True,
               sort: bool = True):
        """Perform extend step for every element. The extension length can also
        be negative values which shrinkages the regions.

        :param upstream: Define how many bp to extend toward upstream
                         direction.
        :type upstream: int
        :param downstream: Define how many bp to extend toward downstream
                           direction.
        :type downstream: int
        :param strandness: Define whether strandness is considered.
        :type strandness: bool
        :param inplace: Define whether this operation will be applied on the
                        same object (True) or return a new object.
        :type inplace: bool
        :param sort: Define whether to sort the output.
        :type sort: bool
        :return: None or a GRegions object
        """
        res = defaultdict(lambda: IntervalTree())
        for region in self:
            # print(region)
            r = region.extend(upstream=upstream,
                              downstream=downstream,
                              strandness=strandness,
                              inplace=False)
            res[r.sequence].add(
                Interval(r.start,
                         r.end,
                         r)
            )
            assert isinstance(res[r.sequence], IntervalTree)
        if inplace:
            self.elements = res
        else:
            resGR = GRegionsTree(name=self.name)
            resGR.elements = res
            return resGR

    def extend_fold(self, upstream: float = 0.0, downstream: float = 0.0,
                    strandness: bool = False, inplace: bool = True,
                    sort: bool = True):
        """Perform extend step for every element. The extension length can also
        be negative values which shrinkages the regions.

        :param upstream: Define the percentage of the region length to extend
                         toward upstream direction.
        :type upstream: float
        :param downstream: Define the percentage of the region length to extend
                           toward downstream direction.
        :type downstream: float
        :param strandness: Define whether strandness is considered.
        :type strandness: bool
        :param inplace: Define whether this operation will be applied on the
                        same object (True) or return a new object.
        :type inplace: bool
        :param sort: Define whether to sort the output.
        :type sort: bool
        :return: None
        """
        res = defaultdict(lambda: IntervalTree())
        for region in self:
            r = region.extend_fold(upstream=upstream,
                                   downstream=downstream,
                                   strandness=strandness,
                                   inplace=False)
            res[r.sequence].add(
                Interval(r.start,
                         r.end,
                         r)
            )
        if inplace:
            self.elements = res
        else:
            resGR = GRegionsTree(name=self.name)
            resGR.elements = res
            return resGR

    def load_chrom_size_file(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split('\t')
                self.add(GRegion(sequence=parts[0], start=0,
                                 end=int(parts[1])))

    def get_chromosomes(self, organism: str):
        import pkg_resources
        chrome_size_file = 'data/chrom_size/chrom.sizes.' + organism
        file_path = pkg_resources.resource_filename('genomkit',
                                                    chrome_size_file)
        if os.path.exists(file_path):
            self.load_chrom_size_file(file_path)
        elif os.path.exists(organism):
            self.load_chrom_size_file(file_path)
        else:
            print(organism + " chromosome size file does not exist")

    def resize(self, extend_upstream: int, extend_downstream: int,
               center="mid_point", inplace=True):
        """Resize the regions according to the defined center and
        extension.

        :param extend_upstream: Define extension length toward upstream
        :type extend_upstream: int
        :param extend_downstream: Define extension length toward downstream
        :type extend_downstream: int
        :param center: Define the new center, defaults to "mid_point", other
                       options are "5prime" and "3prime"
        :type center: str, optional
        :param inplace: Define whether this operation will be applied on the
                        same object (True) or return a new object.
        :type inplace: bool
        :return: A resized GRegion
        :rtype: GRegion
        """
        res = GRegionsTree(name=self.name+"_resize")
        for region in self.elements:
            res.add(region.resize(extend_upstream=extend_upstream,
                                  extend_downstream=extend_downstream,
                                  center=center))
        if inplace:
            self.elements = res.elements
        else:
            return res

    def intersect(self, target, mode: str = "OVERLAP",
                  rm_duplicates: bool = False):
        """Return a GRegions for the intersections between the two given
        GRegions objects. There are three modes for overlapping:

        *mode = "OVERLAP"*

            Return a new GRegions including only the overlapping regions
            with target GRegions.

            .. note:: it will merge the regions.

            ::

                self       ----------              ------
                target            ----------                    ----
                Result            ---

        *mode = "ORIGINAL"*

            Return the regions of original GenomicRegionSet which have any
            intersections with target GRegions.

            ::

                self       ----------              ------
                target          ----------                    ----
                Result     ----------

        *mode = "COMP_INCL"*

            Return region(s) of the GenomicRegionSet which are 'completely'
            included by target GRegions.

            ::

                self        -------------             ------
                target              ----------      ---------------       ----
                Result                                ------

        :param target: A target GRegions for finding overlaps.
        :type target: GRegions
        :param mode: The mode should be one of the followings: "OVERLAP",
                     "ORIGINAL", or "COMP_INCL".
        :type mode: str
        :param rm_duplicates: Define whether remove the duplicates.
        :type rm_duplicates: bool
        :return: A GRegions.
        :rtype: GRegions
        """
        assert isinstance(target, GRegionsTree)
        common_seq = list(set(self.get_sequences(unique=True)) &
                          set(target.get_sequences(unique=True)))
        res = GRegionsTree()
        # ORIGINAL ###############################
        if mode == "ORIGINAL":
            for seq in common_seq:
                for q in target.elements[seq]:
                    regions = self.elements[seq][q.begin:q.end]
                    for interval in regions:
                        res.elements[seq].add(interval)
        # OVERLAP ###############################
        if mode == "OVERLAP":
            for seq in common_seq:
                for q in target.elements[seq]:
                    for r in self.elements[seq].overlap(q.begin, q.end):
                        begin = max(r.begin, q.begin)
                        end = min(r.end, q.end)
                        gr = GRegion(sequence=seq, start=begin, end=end)
                        res.elements[seq].add(
                            Interval(begin, end, gr))
        # COMP_INCL ###############################
        if mode == "COMP_INCL":
            for seq in common_seq:
                for q in target.elements[seq]:
                    regions = self.elements[seq].envelop(q.begin, q.end)
                    for interval in regions:
                        res.elements[seq].add(interval)
        res.remove_duplicates()
        return res

    def remove_duplicates(self, sort: bool = True):
        """
        Remove any duplicate regions (sorted, by default).
        """
        for seq in self.elements.keys():
            unique_intervals = list(set(self.elements[seq]))
            self.elements[seq] = IntervalTree()
            for interval in unique_intervals:
                self.elements[seq].add(interval)

    def merge(self, by_name: bool = False, strandness: bool = False,
              inplace: bool = False):
        """Merge the regions within the GRegions object.

        :param by_name: Define whether to merge regions by name. If True,
                        only the regions with the same name are merged.
        :type by_name: bool
        :param strandness: Define whether to merge the regions according to
                           strandness.
        :type strandness: bool
        :param inplace: Define whether this operation will be applied on the
                        same object (True) or return a new object.
        :type inplace: bool
        :return: None or a GRegions.
        :rtype: GRegions
        """
        def add_merged_interval(curr_interval, r):
            begin = min(r.begin, curr_interval.begin)
            end = max(r.end, curr_interval.end)
            gr = GRegion(name=r.data.name,
                         sequence=r.data.sequence,
                         start=begin, end=end,
                         score=r.data.score, data=r.data.data,
                         orientation=r.data.orientation)
            curr_interval = Interval(begin, end, gr)
            return curr_interval

        def action_when_not_overlap(seq, curr_interval, r):
            if curr_interval:
                res.elements[seq].add(curr_interval)
            return r

        res = GRegionsTree(name=self.name)
        for seq in self.elements.keys():
            if len(self.elements[seq]) == 1:
                res.elements[seq].add(*self.elements[seq])
                continue
            curr_interval = None
            for r in self.elements[seq]:
                if curr_interval is None or r.begin > curr_interval.end:
                    # No overlap, add current_interval to merged_tree
                    curr_interval = action_when_not_overlap(
                        seq, curr_interval, r)
                else:
                    # Overlap, merge intervals
                    if by_name and strandness:
                        if r.data.name == curr_interval.data.name and \
                            r.data.orientation == \
                                curr_interval.data.orientation:
                            curr_interval = add_merged_interval(
                                curr_interval, r)
                        else:
                            curr_interval = action_when_not_overlap(
                                seq, curr_interval, r)
                    elif by_name:
                        if r.data.name == curr_interval.data.name:
                            curr_interval = add_merged_interval(
                                curr_interval, r)
                        else:
                            curr_interval = action_when_not_overlap(
                                seq, curr_interval, r)
                    elif strandness:
                        if r.data.orientation == \
                                curr_interval.data.orientation:
                            curr_interval = add_merged_interval(
                                curr_interval, r)
                        else:
                            curr_interval = action_when_not_overlap(
                                seq, curr_interval, r)
                    else:
                        curr_interval = add_merged_interval(
                                curr_interval, r)
            # Add the last merged interval to merged_tree
            if curr_interval:
                res.elements[seq].add(curr_interval)
        if inplace:
            self.elements = res.elements
        else:
            return res

    def sampling(self, size: int, seed: int = None):
        """Return a sampling of the elements with a sampling number.

        :param size: Sampling number
        :type size: int
        :param seed: Seed for randomness, defaults to None
        :type seed: int, optional
        :return: Sampling regions
        :rtype: GRegions
        """
        if seed:
            random.seed(seed)
        res = GRegionsTree(name="sampling")
        sampling = random.sample(range(len(self)), size)
        for i in sampling:
            res.add(self[i])
        return res

    def split(self, ratio: float, size: int = None, seed: int = None):
        """Split the elements into two GRegions with the defined sizes.

        :param ratio: Define the ratio for splitting
        :type ratio: float, optional
        :param size: Define the size of the first GRegions, defaults to None
        :type size: int, optional
        :param seed: _description_, defaults to None
        :type seed: int, optional
        :return: Two GRegions
        :rtype: GRegions
        """
        if seed:
            random.seed(seed)
        if size:
            sampling = random.sample(range(len(self)), size)
        elif ratio and not size:
            size = int(len(self)*ratio)
            sampling = random.sample(range(len(self)), size)
        a = GRegionsTree(name=self.name+"_split1")
        b = GRegionsTree(name=self.name+"_split2")
        for i in range(len(self)):
            if i in sampling:
                a.add(self.elements[i])
            else:
                b.add(self.elements[i])
        return a, b

    def close_regions(self, target, max_dis=10000):
        """Return a new GRegions including the region(s) of target which are
        closest to any self region.
        If there are intersection, return False.

        :param target: the GRegions which to compare with
        :type target: GRegions
        :param max_dis: maximum distance, defaults to 10000
        :type max_dis: int, optional
        :return: Close regions
        :rtype: GRegions
        """
        extended_regions = self.extend(upstream=max_dis, downstream=max_dis,
                                       inplace=False)
        potential_targets = target.intersect(extended_regions,
                                             mode="ORIGINAL")
        return potential_targets

    def get_elements_by_seq(self, sequence: str, orientation: str = None):
        if orientation is None:
            regions = GRegionsTree(name=sequence)
            regions.elements = [r for r in self.elements
                                if r.sequence == sequence]
        else:
            regions = GRegionsTree(name=sequence+" "+orientation)
            regions.elements = [r for r in self.elements
                                if r.sequence == sequence and
                                r.orientation == orientation]
        return regions

    def get_array_by_seq(self, sequence: str, orientation: str = None):
        regions = self.get_elements_by_seq(sequence=sequence,
                                           orientation=orientation)
        max_position = max([r.end for r in regions])
        bool_array = np.full(max_position, False, dtype=bool)
        for r in regions:
            bool_array[r.start:r.end] = True
        return bool_array

    def get_positions_by_seq(self, sequence: str,
                             orientation: str = None):
        regions = self.get_elements_by_seq(sequence=sequence,
                                           orientation=orientation)
        ranges = [range(r.start, r.end) for r in regions]
        positions = [pos for sublist in ranges for pos in sublist]
        return set(positions)

    def overlap_count(self, target):
        intersect = self.intersect(target, mode="ORIGINAL")
        return len(intersect)

    def subtract(self, regions, whole_region: bool = False,
                 strandness: bool = False, exact: bool = False,
                 inplace: bool = True):
        """Subtract regions from the self regions.

        :param regions: GRegions which to subtract by
        :type regions: GRegions
        :param whole_region: Subtract the whole region, not partially,
                             defaults to False
        :type whole_region: bool, default to False
        :param strandness: Define whether strandness is considered.
        :type strandness: bool
        :param exact: Only regions which match exactly with a given region are
                      subtracted. If True, whole_region and merge are
                      completely ignored and the returned GRegions is sorted
                      and does not contain duplicates.
        :type exact: bool, default to False
        :param inplace: Define whether this operation will be applied on the
                        same object (True) or return a new object.
        :type inplace: bool, default to True
        :return: Remaining regions of self after subtraction
        :rtype: GRegions

        ::

            self     ----------              ------
            regions         ----------                    ----
            Result   -------                 ------
        """
        assert isinstance(regions, GRegionsTree)

        def remain_interval(seq, begin, end, interval, res):
            gr = GRegion(sequence=seq, start=begin, end=end,
                         name=interval.data.name, score=interval.data.score,
                         orientation=interval.data.orientation)
            remain = Interval(begin, end, gr)
            res.elements[seq].add(remain)

        res = GRegionsTree(name=self.name)
        for seq in self.elements.keys():
            for interval in self.elements[seq]:
                # Check if exact match is required
                if exact:
                    # If interval not found in regions, add it to result
                    if interval not in regions.elements[seq]:
                        res.elements[seq].add(interval)
                elif whole_region:
                    if any(regions.elements[seq].overlap(
                            interval.begin, interval.end)):
                        continue
                elif strandness:
                    for r in regions.elements[seq].overlap(
                            interval.begin, interval.end):
                        # interval       -----
                        # r          --------------
                        # remain
                        if interval.begin > r.begin and \
                                interval.end < r.end and \
                                interval.data.orientation ==\
                                r.data.orientation:
                            continue
                        # interval   --------------
                        # r              -----
                        # remain     ----     -----
                        elif interval.begin < r.begin and \
                                interval.end > r.end and \
                                interval.data.orientation ==\
                                r.data.orientation:
                            remain_interval(seq, interval.begin, r.begin,
                                            interval, res)
                            remain_interval(seq, r.end, interval.end,
                                            interval, res)
                        # interval   -------
                        # r              -------
                        # remain     ----
                        elif interval.begin < r.begin and \
                                interval.end <= r.end and \
                                interval.data.orientation ==\
                                r.data.orientation:
                            remain_interval(seq, interval.begin, r.begin,
                                            interval, res)
                        # interval      -------
                        # r          -------
                        # remain            ---
                        elif interval.begin >= r.begin and \
                                interval.end > r.end and \
                                interval.data.orientation ==\
                                r.data.orientation:
                            remain_interval(seq, r.end, interval.end,
                                            interval, res)
                        else:
                            res.elements[seq].add(interval)
                else:
                    for r in regions.elements[seq].overlap(
                            interval.begin, interval.end):
                        # interval       -----
                        # r          --------------
                        # remain
                        if interval.begin > r.begin and \
                                interval.end < r.end:
                            continue
                        # interval   --------------
                        # r              -----
                        # remain     ----     -----
                        elif interval.begin < r.begin and \
                                interval.end > r.end:
                            remain_interval(seq, interval.begin, r.begin,
                                            interval, res)
                            remain_interval(seq, r.end, interval.end,
                                            interval, res)
                        # interval   -------
                        # r              -------
                        # remain     ----
                        elif interval.begin < r.begin and \
                                interval.end <= r.end:
                            remain_interval(seq, interval.begin, r.begin,
                                            interval, res)
                        # interval      -------
                        # r          -------
                        # remain            ---
                        elif interval.begin >= r.begin and \
                                interval.end > r.end:
                            remain_interval(seq, r.end, interval.end,
                                            interval, res)
                        else:
                            res.elements[seq].add(interval)
        if inplace:
            self.elements = res.elements
        else:
            return res

    def get_GSequences(self, FASTA_file):
        """Return a GSequences object according to the loci on the given
        reference FASTQ file.

        :param FASTA_file: Path to the FASTA file
        :type FASTA_file: str
        :return: A GSequences.
        :rtype: GSequences
        """
        from genomkit import GSequences
        if os.path.exists(FASTA_file):
            fasta = GSequences(load=FASTA_file)
        else:
            print(FASTA_file + " is not found.")
            sys.exit()
        res = GSequences(name=self.name)
        for region in self.elements:
            seq = fasta.get_sequence(name=region.sequence,
                                     start=region.start,
                                     end=region.end)
            seq.name = region.name
            seq.data = region.data
            if region.orientation == "-":
                seq.reverse_complement()
            res.add(seq)
        return res

    def cluster(self, max_distance):
        """Cluster the regions with a certain distance and return a new
        GRegions.

        :param max_distance: Maximal distance for combining
        :type max_distance: int
        :return: Combined regions
        :rtype: GRegions

        ::

            self           ----           ----            ----
                              ----             ----                 ----
            Result(d=1)    -------        ---------       ----      ----
            Result(d=10)   ---------------------------------------------
        """
        if len(self) == 0:
            return GRegionsTree()
        elif len(self) == 1:
            return self
        else:
            z = GRegionsTree('Clustered region set')
            previous = deepcopy(self.elements[0])
            for s in self.elements[1:]:
                s_ext = s.extend(upstream=max_distance,
                                 downstream=max_distance,
                                 inplace=False)
                if s_ext.overlap(previous):
                    previous.start = min(previous.start, s.start)
                    previous.end = max(previous.end, s.end)
                else:
                    z.add(previous)
                    previous = deepcopy(s)
            z.add(previous)
            return z

    def total_coverage(self):
        """Return the total coverage (bp) of all the regions.

        :return: Total coverage (bp)
        :rtype: int
        """
        merged_regions = self.merge(inplace=False)
        cov = sum([len(r) for r in merged_regions])
        return cov

    def filter_by_names(self, names, inplace=False):
        """Filter the elements by the given list of names

        :param names: A list of names for filtering
        :type names: list
        :param inplace: Define whether this operation will be applied on the
                        same object (True) or return a new object.
        :type inplace: bool, default to True
        :return: A GRegions with filtered regions
        :rtype: GRegions
        """
        res = GRegionsTree(name=self.name)
        for r in self.elements:
            if r.name in names:
                res.add(r)
        if inplace:
            self.elements = res.elements
        else:
            return res

    def filter_by_score(self, larger_than=0, smaller_than=0, inplace=False):
        """Filter the elements by the given list of names

        :param larger_than: Define the minimal cutoff. Any region with the
                            score larger than this value will be returned.
        :type larger_than: float
        :param smaller_than: Define the maximal cutoff. Any region with the
                            score smaller than this value will be returned.
        :type smaller_than: float
        :param inplace: Define whether this operation will be applied on the
                        same object (True) or return a new object.
        :type inplace: bool, default to True
        :return: A GRegions with filtered regions
        :rtype: GRegions
        """
        res = GRegionsTree(name=self.name)
        for r in self.elements:
            if r.score > larger_than:
                res.add(r)
            elif r.score < smaller_than:
                res.add(r)
            else:
                continue
        if inplace:
            self.elements = res.elements
        else:
            return res

    def rename_by_GRegions(self, name_source, strandness: bool = True,
                           inplace: bool = True):
        """Rename the regions' names by the given GRegions.

        :param name_source: A GRegions where the names are taken as sources.
        :type name_source: GRegions
        :param strandness: Define whether strandness is considered.
        :type strandness: bool
        :param inplace: Define whether this operation will be applied on the
                        same object (True) or return a new object.
        :type inplace: bool, default to True
        """
        def new_interval(seq, interval, r, res):
            res.elements[seq].add(
                Interval(interval.begin, interval.end,
                         GRegion(sequence=interval.data.sequence,
                                 start=interval.data.start,
                                 end=interval.data.end,
                                 name=r.data.name,
                                 score=interval.data.score,
                                 orientation=interval.data.orientation,
                                 data=interval.data.data)))
        assert isinstance(name_source, GRegionsTree)

        res = GRegionsTree(name=self.name)
        for seq in tqdm(self.elements.keys(), desc="Renaming"):
            for interval in self.elements[seq]:
                if any(name_source.elements[seq].overlap(
                            interval.begin, interval.end)):
                    for r in name_source.elements[seq].overlap(
                            interval.begin, interval.end):
                        if strandness:
                            if interval.data.orientation == r.data.orientation:
                                new_interval(seq, interval, r, res)
                            else:
                                res.elements[seq].add(interval)
                        else:
                            new_interval(seq, interval, r, res)
                else:
                    res.elements[seq].add(interval)
        # names = res.get_names()
        # print(names)
        if inplace:
            self.elements = res.elements
        else:
            return res
