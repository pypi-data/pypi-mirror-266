import unittest
from genomkit import GCoverages, GRegions, GRegion
# from genomkit.sequences.io import load_FASTA, load_FASTQ
import os

script_path = os.path.dirname(__file__)


class TestGCoverages(unittest.TestCase):

    def test_load_coverage_from_bigwig(self):
        cov = GCoverages(bin_size=1,
                         load=os.path.join(script_path,
                                           "test_files/bigwig/test.bw"),
                         windows=None)
        # cov.load_coverage_from_bigwig(filename="tests/test_files/bigwig/test.bw")
        # {'1': 195471971, '10': 130694993}
        self.assertEqual(len(cov.coverage), 2)
        self.assertEqual(list(cov.coverage.keys())[0].sequence, "1")
        self.assertEqual(list(cov.coverage.keys())[1].sequence, "10")
        windows = GRegions(name="windows")
        windows.add(GRegion(sequence="1", start=0, end=1000))
        cov = GCoverages(bin_size=1,
                         load=os.path.join(script_path,
                                           "test_files/bigwig/test.bw"),
                         windows=windows)
        self.assertEqual(len(cov.coverage), 1)
        self.assertEqual(list(cov.coverage.keys())[0].sequence, "1")
        self.assertEqual(list(cov.coverage.keys())[0].end, 1000)
        cov = GCoverages(bin_size=2,
                         load=os.path.join(script_path,
                                           "test_files/bigwig/test.bw"),
                         windows=windows)
        # cov.load_coverage_from_bigwig(filename="tests/test_files/bigwig/test.bw")
        # {'1': 195471971, '10': 130694993}
        self.assertEqual(len(cov.coverage), 1)
        self.assertEqual(list(cov.coverage.keys())[0].sequence, "1")
        self.assertEqual(list(cov.coverage.keys())[0].end, 1000)
        cov = GCoverages()
        cov.load_coverage_from_bigwig(
            filename=os.path.join(script_path,
                                  "test_files/bigwig/test.bigwig")
            )
        self.assertEqual(len(cov.coverage.keys()), 2)

    def test_calculate_coverage_from_bam(self):
        cov = GCoverages()
        cov.calculate_coverage_from_bam(
            filename=os.path.join(script_path,
                                  "test_files/bam/Col0_C1.100k.bam")
            )
        # cov.calculate_coverage_from_bam(filename="tests/test_files/bam/Col0_C1.100k.bam")
        # ['1']
        self.assertEqual(len(cov.coverage.keys()), 1)
        windows = GRegions(name="windows")
        windows.add(GRegion(sequence="1", start=0, end=1000))
        cov = GCoverages(bin_size=1,
                         load=os.path.join(script_path,
                                           "test_files/bam/Col0_C1.100k.bam"),
                         windows=windows)
        self.assertEqual(len(cov.coverage.keys()), 1)
        self.assertEqual(len(cov.coverage[windows[0]]), 1000)
        cov = GCoverages(bin_size=2,
                         load=os.path.join(script_path,
                                           "test_files/bam/Col0_C1.100k.bam"),
                         windows=windows)
        self.assertEqual(len(cov.coverage.keys()), 1)
        self.assertEqual(len(cov.coverage[windows[0]]), 500)

    def test_calculate_coverage_GRegions(self):
        regions = GRegions(name="test",
                           load=os.path.join(script_path,
                                             "test_files/bed/example2.bed"))
        cov = GCoverages()
        cov.calculate_coverage_GRegions(windows=regions, scores=regions)
        self.assertEqual(len(cov.coverage.keys()), 4)
        self.assertEqual(cov.coverage[regions[0]][0], 10)
        self.assertEqual(cov.coverage[regions[1]][0], 20)
        self.assertEqual(cov.coverage[regions[2]][0], 30)
        self.assertEqual(cov.coverage[regions[3]][0], 40)

    def test_get_coverage(self):
        cov = GCoverages()
        cov.load_coverage_from_bigwig(
            filename=os.path.join(script_path,
                                  "test_files/bigwig/test.bw")
            )
        res = cov.get_coverage(GRegion(sequence="10",
                                       start=0,
                                       end=130694993))
        self.assertEqual(len(res), 130694993)
        cov = GCoverages()
        cov.calculate_coverage_from_bam(
            filename=os.path.join(script_path,
                                  "test_files/bam/Col0_C1.100k.bam")
            )
        res = cov.get_coverage(GRegion(sequence="1",
                                       start=0,
                                       end=30427671))
        self.assertEqual(len(res), 30427671)

    def test_filter_regions_coverage(self):
        cov = GCoverages()
        cov.load_coverage_from_bigwig(
            filename=os.path.join(script_path,
                                  "test_files/bigwig/test.bw")
            )
        regions = GRegions(name="test")
        regions.add(GRegion(sequence="1", start=100, end=500))
        regions.add(GRegion(sequence="10", start=100, end=500))
        res = cov.filter_regions_coverage(regions)
        self.assertEqual(len(res), 2)
        self.assertEqual(list(res.keys())[0],
                         GRegion(sequence="1", start=100, end=500))

    def test_total_sequencing_depth(self):
        cov = GCoverages()
        cov.load_coverage_from_bigwig(
            filename=os.path.join(script_path,
                                  "test_files/bigwig/test.bw")
            )
        res = cov.total_sequencing_depth()
        self.assertEqual(int(res), 272)

    def test_scale_coverage(self):
        cov = GCoverages()
        cov.load_coverage_from_bigwig(
            filename=os.path.join(script_path,
                                  "test_files/bigwig/test.bw")
            )
        cov.scale_coverage(0.1)
        res = cov.total_sequencing_depth()
        self.assertEqual(int(res), 27)
