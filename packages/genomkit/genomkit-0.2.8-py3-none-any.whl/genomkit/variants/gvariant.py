class GVariant:
    __slot__ = ["chrom", "pos", "vid", "ref", "alt", "qual", "filter_status",
                "info"]

    def __init__(self, chrom: str, pos: int, vid: str, ref: str, alt: str,
                 qual: int, filter_status: str, info: str = []):
        self.chrom = chrom
        self.pos = pos
        self.vid = vid
        self.ref = ref
        self.alt = alt
        self.qual = qual
        self.filter_status = filter_status
        self.info = info

    def to_GRegion(self):
        from genomkit import GRegion
        region = GRegion(sequence=self.chrom, start=self.pos, end=self.pos,
                         name=self.vid, data=[self.ref, self.alt, self.qual,
                                              self.filter_status] + self.info)
        return region
