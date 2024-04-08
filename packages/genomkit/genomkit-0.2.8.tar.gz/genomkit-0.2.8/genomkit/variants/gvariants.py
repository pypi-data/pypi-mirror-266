from genomkit import GVariant


###########################################################################
# GVariants
###########################################################################
class GVariants:
    """
    GVariants module

    This module contains functions and classes for working with a collection of
    genomic variants. It provides utilities for handling and analyzing the
    interactions of many genomic variants.
    """
    def __init__(self, name: str = "", load: str = ""):
        """Initiate GVariants object.

        :param name: Define the name, defaults to ""
        :type name: str, optional
        :param load: Define the filename for loading a VCF file, defaults to ""
        :type load: str, optional
        """
        self.name = name
        self.variants = []
        if load:
            self.load(filename=load)

    def load(self, filename):
        """Load variants from a VCF file.

        :param filename: Define the filename for loading a VCF file
        :type filename: str
        """
        with open(filename, 'r') as vcf_file:
            for line in vcf_file:
                if line.startswith('#'):
                    continue  # Skip header lines
                fields = line.strip().split('\t')
                chrom = fields[0]
                pos = int(fields[1])
                vid = fields[2]
                ref = fields[3]
                alt = fields[4]
                qual = fields[5]
                filter_status = fields[6]
                info = fields[7:]
                variant = GVariant(chrom=chrom, pos=pos, vid=vid, ref=ref,
                                   alt=alt, qual=qual,
                                   filter_status=filter_status,
                                   info=info)
                self.variants.append(variant)

    def to_GRegions(self):
        """Convert the GVariants to a GRegions object.

        :return: A GRegions object
        :rtype: GRegions
        """
        from genomkit import GRegions
        regions = GRegions(name=self.name)
        for variant in self.variants:
            regions.add(variant.to_GRegion())
        return regions
