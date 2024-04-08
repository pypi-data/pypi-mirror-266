import unittest
from genomkit import GRegions
from genomkit.regions.io import load_BED
import os

script_path = os.path.dirname(__file__)


class TestGRegions(unittest.TestCase):

    def test_len(self):
        regions = GRegions(name="test")
        regions.load(filename=os.path.join(script_path,
                                           "test_files/bed/example.bed"))
        self.assertEqual(len(regions), 4)
        regions = GRegions(name="test")
        regions.load(filename=os.path.join(script_path,
                     "test_files/bed/genes_Gencode_hg38_chr22.bed"))
        self.assertEqual(len(regions), 1372)

    def test_extend(self):
        regions = GRegions(name="test")
        regions.load(filename=os.path.join(script_path,
                                           "test_files/bed/example.bed"))
        self.assertEqual(regions.extend(upstream=100,
                                        inplace=False)[0].start, 900)
        self.assertEqual(regions.extend(upstream=100,
                                        inplace=False)[1].start, 2900)
        self.assertEqual(regions.extend(upstream=100, strandness=True,
                                        inplace=False)[1].start, 3000)
        self.assertEqual(regions.extend(downstream=100, strandness=True,
                                        inplace=False)[1].start, 2900)

    def test_extend_fold(self):
        regions = GRegions(name="test")
        regions.load(filename=os.path.join(script_path,
                                           "test_files/bed/example.bed"))
        self.assertEqual(regions.extend_fold(upstream=0.1,
                                             inplace=False)[0].start, 900)
        self.assertEqual(regions.extend_fold(upstream=0.1,
                                             inplace=False)[1].start, 2900)
        self.assertEqual(regions.extend_fold(upstream=0.1, strandness=True,
                                             inplace=False)[1].start, 3000)
        self.assertEqual(regions.extend_fold(downstream=0.1, strandness=True,
                                             inplace=False)[1].start, 2900)

    def test_get_sequences(self):
        regions = GRegions(name="test")
        regions.load(filename=os.path.join(script_path,
                                           "test_files/bed/example.bed"))
        self.assertEqual(regions.get_sequences(),
                         ["chr1", "chr1", "chr2", "chr2"])
        self.assertEqual(regions.get_sequences(unique=True),
                         ["chr1", "chr2"])

    def test_get_names(self):
        regions = GRegions(name="test")
        regions.load(filename=os.path.join(script_path,
                                           "test_files/bed/example.bed"))
        self.assertEqual(regions.get_names(), ["Feature1", "Feature2",
                                               "Feature3", "Feature4"])
        self.assertEqual(regions.get_names(unique=True),
                         ["Feature1", "Feature2", "Feature3", "Feature4"])

    def test_intersect(self):
        regions1 = GRegions(name="test")
        regions1.load(filename=os.path.join(script_path,
                                            "test_files/bed/example.bed"))
        regions2 = GRegions(name="test")
        regions2.load(filename=os.path.join(script_path,
                                            "test_files/bed/example2.bed"))
        intersect = regions1.intersect(regions2, mode='OVERLAP')
        self.assertEqual(len(intersect), 4)
        self.assertEqual(len(intersect[0]), 500)
        self.assertEqual(len(intersect[1]), 500)
        self.assertEqual(len(intersect[2]), 500)
        self.assertEqual(len(intersect[3]), 500)
        intersect = regions1.intersect(regions2, mode='ORIGINAL')
        self.assertEqual(len(intersect), 4)
        self.assertEqual(len(intersect[0]), 1000)
        self.assertEqual(len(intersect[1]), 1000)
        self.assertEqual(len(intersect[2]), 1000)
        self.assertEqual(len(intersect[3]), 1000)
        intersect = regions1.intersect(regions2, mode='COMP_INCL')
        self.assertEqual(len(intersect), 0)

    def test_intersect_array(self):
        regions1 = GRegions(name="test")
        regions1.load(filename=os.path.join(script_path,
                                            "test_files/bed/example.bed"))
        regions2 = GRegions(name="test")
        regions2.load(filename=os.path.join(script_path,
                                            "test_files/bed/example2.bed"))
        intersect = regions1.intersect_array(regions2)
        self.assertEqual(len(intersect), 4)

    def test_merge(self):
        regions = GRegions(name="test")
        regions.load(filename=os.path.join(script_path,
                                           "test_files/bed/example3.bed"))
        merged = regions.merge()
        self.assertEqual(len(merged), 2)
        self.assertEqual(len(merged[0]), 1000)
        self.assertEqual(len(merged[1]), 1000)
        merged = regions.merge(strandness=True)
        self.assertEqual(len(merged), 3)
        self.assertEqual(len(merged[0]), 1000)
        regions.merge(inplace=True)
        self.assertEqual(len(regions), 2)
        self.assertEqual(len(regions[0]), 1000)
        self.assertEqual(len(regions[1]), 1000)

    def test_remove_duplicates(self):
        regions = GRegions(name="test")
        regions.load(filename=os.path.join(script_path,
                                           "test_files/bed/example4.bed"))
        regions.remove_duplicates()
        self.assertEqual(len(regions), 4)

    def test_sort(self):
        regions = GRegions(name="test")
        regions.load(filename=os.path.join(script_path,
                                           "test_files/bed/example4.bed"))
        regions.sort()
        self.assertEqual(len(regions), 6)
        self.assertEqual(regions.get_sequences(),
                         ["chr1", "chr1", "chr1", "chr2", "chr2", "chr2"])

    def test_load_BED(self):
        regions = load_BED(filename=os.path.join(script_path,
                           "test_files/bed/example4.bed"))
        self.assertEqual(len(regions), 6)

    def test_sampling(self):
        regions = load_BED(filename=os.path.join(script_path,
                           "test_files/bed/example4.bed"))
        sampling = regions.sampling(size=3)
        self.assertEqual(len(sampling), 3)

    def test_subtract(self):
        regions1 = GRegions(name="test")
        regions1.load(filename=os.path.join(script_path,
                                            "test_files/bed/example.bed"))
        regions2 = GRegions(name="test")
        regions2.load(filename=os.path.join(script_path,
                                            "test_files/bed/example2.bed"))
        regions1.subtract(regions2)
        self.assertEqual(len(regions1), 4)
        self.assertEqual(len(regions1[0]), 500)
        self.assertEqual(len(regions1[1]), 500)
        self.assertEqual(len(regions1[2]), 500)
        self.assertEqual(len(regions1[3]), 500)

        # regions1 = GRegions(name="test")
        # regions1.load(filename=os.path.join(script_path,
        #                                     "test_files/bed/example.bed"))
        # regions2 = GRegions(name="test")
        # regions2.load(filename=os.path.join(script_path,
        #                                     "test_files/bed/example2.bed"))
        # regions1.subtract(regions2, whole_region=True)
        # self.assertEqual(len(regions1[0]), 0)

    def test_total_coverage(self):
        regions1 = GRegions(name="test")
        regions1.load(filename=os.path.join(script_path,
                                            "test_files/bed/example.bed"))
        self.assertEqual(regions1.total_coverage(), 4000)


if __name__ == '__main__':
    unittest.main()
