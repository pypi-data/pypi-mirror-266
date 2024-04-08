from genomkit import GCoverages
from collections import OrderedDict


class GCoveragesSet:
    """
    GCoveragesSet module

    This module contains functions and classes for working with multiple
    collections of genomic coverages. It provides utilities for handling and
    analyzing the interactions of many genomic coverages.
    """

    def __init__(self, name: str = "", load_dict=None, windows=None):
        """Initiate a GCoveragesSet object which can contain multiple
        GCoverages.

        :param name: Define the name, defaults to ""
        :type name: str, optional
        :param load_dict: Given the file paths of multiple GCoverages as a
                          dictionary with names as keys and values as file
                          paths, defaults to None
        :type load_dict: dict, optional
        """
        self.name = name
        self.collection = OrderedDict()
        if load_dict:
            for name, filename in load_dict.items():
                self.add(name=name,
                         gcov=GCoverages(windows=windows, load=filename))

    def add(self, name, gcov):
        """Add a GCoverages into GCoveragesSet.

        :param name: name of a GCoverages
        :type name: str
        :param gcov: A GCoverages
        :type gcov: GCoverages
        """
        self.collection[name] = gcov

    def __len__(self):
        """Return the number of GCoverages in this set.

        :return: Number of GCoverages
        :rtype: int
        """
        return len(self.collection)

    def __getattr__(self, key):
        if key in self.collection:
            return self.collection[key]
        else:
            raise AttributeError(
                f"'{self.collection.__class__.__name__}'"
                f" object has no attribute '{key}'"
                )

    def __getitem__(self, key):
        return self.collection[key]

    def __iter__(self):
        return iter(self.collection.values())

    def get_names(self):
        """Return the names of all GCoverages.

        :return: Names
        :rtype: list
        """
        return list(self.collection.keys())

    def flip_negative_regions(self):
        """Flip the coverage arrays which are on the negative strands. If the
        coverage arrays are calculated by the whole chromosomes, it won't
        work.
        """
        for cov in self.collection.values():
            cov.flip_negative_regions()
