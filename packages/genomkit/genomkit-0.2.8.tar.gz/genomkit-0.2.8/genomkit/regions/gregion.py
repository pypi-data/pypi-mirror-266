class GRegion:
    """
    GRegion module

    This module contains functions and classes for working with a genomic
    region. It provides utilities for handling and analyzing a single genomic
    coordinate.
    """
    __slot__ = ["sequence", "start", "end", "orientation", "name", "score",
                "data"]

    def __init__(self, sequence: str, start: int, end: int,
                 orientation: str = ".",
                 name: str = "", score: float = 0, data: list = []):
        """Create a GRegion object.

        :param sequence: sequence name such as chr2
        :type sequence: str
        :param start: starting position
        :type start: int
        :param end: ending position
        :type end: int
        :param orientation: orientation of the region "+", "-" or "."
                            (defaults to ".")
        :type orientation: str, optional
        :param name: Name of the region, defaults to ""
        :type name: str, optional
        :param score: Score of the region, defaults to 0
        :type score: float, optional
        :param data: Further data of the region, defaults to []
        :type data: list, optional
        """
        self.sequence = sequence
        self.start = start
        self.end = end
        self.orientation = orientation
        self.name = name
        self.score = score
        self.data = data

    def __len__(self):
        """
        Return the length of the region.

        :return: length
        :rtype: int
        """
        return abs(self.start - self.end)

    def __str__(self):
        """
        Return the string format of the region in the form such as
        'chr4:400-500 name orientation'

        :return: string of the region
        :rtype: str
        """
        return "{}:{}-{} {} {}".format(self.sequence,
                                       str(self.start), str(self.end),
                                       self.name, self.orientation)

    def bed_entry(self, data: bool = False):
        """Export regions in BED format

        :param data: Define whether to export extra data, defaults to False
        :type data: bool, optional
        :return: A string in BED format
        :rtype: str
        """
        if data:
            return "\t".join([self.sequence,
                              str(self.start),
                              str(self.end),
                              self.name,
                              str(self.score),
                              self.orientation,
                              "\t".join(self.data)
                              ])
        else:
            return "\t".join([self.sequence,
                              str(self.start),
                              str(self.end),
                              self.name,
                              str(self.score),
                              self.orientation
                              ])

    def __hash__(self):
        return hash((self.sequence, self.start,
                     self.end, self.orientation))

    def __eq__(self, other):
        return (self.sequence, self.start, self.end, self.orientation) == \
               (other.sequence, other.start, other.end, other.orientation)

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return (self.sequence, self.start, self.end) < \
               (other.sequence, other.start, other.end)

    def __le__(self, other):
        return (self.sequence, self.start, self.end) <= \
               (other.sequence, other.start, other.end)

    def __gt__(self, other):
        return (self.sequence, self.start, self.end) > \
               (other.sequence, other.start, other.end)

    def __ge__(self, other):
        return (self.sequence, self.start, self.end) >= \
               (other.sequence, other.start, other.end)

    def extend(self, upstream: int = 0, downstream: int = 0,
               strandness: bool = False, inplace: bool = True):
        """
        Extend GRegion region with the given extension length.

        :param upstream: Define how many bp to extend toward upstream
                         direction.
        :type upstream: int
        :param downstream: Define how many bp to extend toward downstream
                          direction.
        :type downstream: int
        :param strandness: Define whether strandness is considered.
        :type strandness: bool
        :param inplace: Define whether this operation will be applied on the
                        same object (True) or return a new object..
        :type inplace: bool
        :return: None or a GRegion object
        """
        if strandness and self.orientation == "-":
            new_start = max(0, self.start - downstream)
            new_end = self.end + upstream
        else:  # + or .
            new_start = max(0, self.start - upstream)
            new_end = self.end + downstream

        if inplace:
            self.start = new_start
            self.end = new_end
        else:
            return GRegion(sequence=self.sequence, start=new_start,
                           end=new_end, name=self.name,
                           orientation=self.orientation, data=self.data)

    def extend_fold(self, upstream: float = 0.0, downstream: float = 0.0,
                    strandness: bool = False, inplace: bool = True):
        """
        Extend GRegion region with the given extension length in percentage.

        :param upstream: Define the percentage of the region length to extend
                         toward upstream direction.
        :type upstream: float
        :param downstream: Define the percentage of the region length to extend
                           toward downstream direction.
        :type downstream: float
        :param strandness: Define whether strandness is considered.
        :type strandness: bool
        :param inplace: Define whether this operation will be applied on the
                        same object (True) or return a new object..
        :type inplace: bool
        :return: None or a GRegion object
        """
        upstream_length = int(len(self)*upstream)
        downstream_length = int(len(self)*downstream)
        if inplace:
            self.extend(upstream=upstream_length, downstream=downstream_length,
                        strandness=strandness, inplace=True)
        else:
            return self.extend(upstream=upstream_length,
                               downstream=downstream_length,
                               strandness=strandness,
                               inplace=False)

    def overlap(self, region, strandness=False):
        """
        Return True, if GRegion overlaps with the given region, else False.

        :param region: A given GRegion object
        :type region: GRegion
        :param strandness: Define whether strandness is considered.
        :type strandness: bool
        :return: True or False
        :rtype: bool
        """
        if region.sequence == self.sequence:
            if self.start <= region.start:
                if self.end > region.start:
                    if not strandness:
                        return True
                    elif self.orientation == region.orientation:
                        return True
            else:
                if self.start < region.end:
                    if not strandness:
                        return True
                    elif self.orientation == region.orientation:
                        return True
        return False

    def distance(self, region):
        """
        Return the distance between two GRegions. If overlapping, return 0;
        if on different chromosomes, return None.

        :param region: A given GRegion object
        :type region: GRegion
        :return: distance
        :rtype: int or None if distance is not available
        """
        if self.sequence == region.sequence:
            if self.overlap(region):
                return 0
            elif self < region:
                return region.start - self.end
            else:
                return self.start - region.end
        else:
            return None

    def resize(self, extend_upstream: int, extend_downstream: int,
               center="mid_point"):
        """Return a resized GRegion according to the defined center and
        extension.

        :param extend_upstream: Define extension length toward upstream
        :type extend_upstream: int
        :param extend_downstream: Define extension length toward downstream
        :type extend_downstream: int
        :param center: Define the new center, defaults to "mid_point", other
                       options are "5prime" and "3prime"
        :type center: str, optional
        :return: A resized GRegion
        :rtype: GRegion
        """
        if center == "mid_point":
            center = self.start + int(0.5*(self.end-self.start))
            if self.orientation == "-":
                start = center-extend_downstream
                end = center+extend_upstream
            else:
                start = center-extend_upstream
                end = center+extend_downstream
        elif center == "5prime":
            if self.orientation == "-":
                center = self.end
                start = center-extend_downstream
                end = center+extend_upstream
            else:
                center = self.start
                start = center-extend_upstream
                end = center+extend_downstream
        elif center == "3prime":
            if self.orientation == "-":
                center = self.start
                start = center-extend_downstream
                end = center+extend_upstream
            else:
                center = self.end
                start = center-extend_upstream
                end = center+extend_downstream
        if start < 0:
            start = 0
        if end < 0:
            end = 0
        res = GRegion(sequence=self.sequence, start=start, end=end,
                      orientation=self.orientation, score=self.score,
                      name=self.name, data=self.data)
        return res
