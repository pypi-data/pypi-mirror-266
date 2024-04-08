from genomkit import GRegions
from collections import OrderedDict
import numpy as np
import pandas as pd
import glob
import os


class GRegionsSet:
    """
    GRegionsSet module

    This module contains functions and classes for working with a collection of
    multiple GRegions.
    """
    def __init__(self, name: str = "", load_dict=None):
        """Initiate a GRegionsSet object which can contain multiple GRegions.

        :param name: Define the name, defaults to ""
        :type name: str, optional
        :param load_dict: Given the file paths of multiple GRegions as a
                          dictionary with names as keys and values as file
                          paths, defaults to None
        :type load_dict: dict, optional
        """
        self.collection = OrderedDict()
        if load_dict:
            for name, filename in load_dict.items():
                self.add(name=name,
                         regions=GRegions(name=name,
                                          load=filename))

    def add(self, name: str, regions):
        """Add a GRegions object into this set.

        :param name: Define the name
        :type name: str
        :param regions: Given the GRegions
        :type regions: GRegions
        """
        self.collection[name] = regions

    def load_pattern(self, pattern):
        """Load multiple BED files with a regex pattern.

        :param pattern: Regex pattern
        :type pattern: str
        """
        file_paths = glob.glob(pattern)
        for bed in file_paths:
            name = os.path.basename(bed)
            regions = GRegions(name=name,
                               load=bed)
            self.add(name=name, regions=regions)

    def __len__(self):
        """Return the number of GRegions in this set.

        :return: Number of GRegions
        :rtype: int
        """
        return len(self.collection)

    # def __getattr__(self, key):
    #     if key in self.collection:
    #         return self.collection[key]
    #     else:
    #         raise AttributeError(
    #             f"'{self.collection.__class__.__name__}'"
    #             f" object has no attribute '{key}'"
    #             )

    # def __setattr__(self, key, value):
    #     self.collection[key] = value

    def get_names(self):
        """Return the names of all GRegions.

        :return: Names
        :rtype: list
        """
        return list(self.collection.keys())

    def get_lengths(self):
        """Return a list of the number of regions in all GRegions

        :return: A list of region numbers
        :rtype: list
        """
        res = OrderedDict()
        for name, regions in self.collection.items():
            res[name] = len(regions)
        return res

    def count_overlaps(self, query_set, percentage: bool = False):
        """Return a pandas dataframe of the numbers of overlapping regions
        between the reference GRegionsSet (self) and the query GRegionsSet.

        :param query_set: Query GRegionsSet
        :type query_set: GRegionsSet
        :param percentage: Convert the contingency table into percentage. The
                           sum per row (reference) is 100%, defaults to False
        :type percentage: bool, optional
        :return: Matrix of numbers of overlaps
        :rtype: dataframe
        """
        res = np.zeros((len(self), len(query_set)))
        row_names = []
        col_names = []
        for i, (ref_name, ref) in enumerate(self.collection.items()):
            row_names.append(ref_name)
            for j, (query_name, query) in enumerate(query_set.items()):
                col_names.append(query_name)
                c = ref.overlap_count(target=query)
                res[i, j] = c
        df = pd.DataFrame(res,
                          index=row_names,
                          columns=col_names)
        if percentage:
            df = df.div(df.sum(axis=1), axis=0) * 100
        return df

    def test_association(self, another_set):
        from scipy.stats import chi2_contingency
        contingency_table = self.count_overlaps(query_set=another_set)
        chi2_stat, p_val, _, _ = chi2_contingency(contingency_table)
        return chi2_stat, p_val

    def subtract(self, regions, whole_region: bool = False,
                 merge: bool = True, exact: bool = False):
        """Perform inplace subtract in all GRegions.

        :param regions: GRegions which to subtract by
        :type regions: GRegions
        :param whole_region: Subtract the whole region, not partially,
                             defaults to False
        :type whole_region: bool, default to False
        :param merge: Merging the regions before subtracting
        :type merge: bool, default to True
        :param exact: Only regions which match exactly with a given region are
                      subtracted. If True, whole_region and merge are
                      completely ignored and the returned GRegions is sorted
                      and does not contain duplicates.
        :type exact: bool, default to False
        """
        for grs in self.collection.values():
            grs.subtract(regions, whole_region, merge, exact, inplace=True)

    def resize(self, extend_upstream: int, extend_downstream: int,
               center="mid_point"):
        for grs in self.collection.values():
            grs.resize(extend_upstream=extend_upstream,
                       extend_downstream=extend_downstream,
                       center=center, inplace=True)

    def combine(self):
        """Return a GRegions by combining all regions.

        :return: GRegions
        :rtype: GRegions
        """
        res = GRegions(name="combined")
        for grs in self.collection.values():
            for r in grs:
                res.add(r)
        return res
