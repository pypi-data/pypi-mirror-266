import unittest
from genomkit import GAnnotation
import os

script_path = os.path.dirname(__file__)
gtf_file = os.path.join(script_path,
                        "test_files/gtf/gencode.v45.annotation_top1000.gtf")
gff_file = os.path.join(script_path,
                        "test_files/gff3/gencode.v45.annotation_top1000.gff3")


class TestGAnnotation(unittest.TestCase):

    def test_load_data(self):
        gtf = GAnnotation(file_path=gtf_file,
                          file_format="gtf")
        self.assertEqual(len(gtf.genes), 69)
        gff = GAnnotation(file_path=gff_file,
                          file_format="gff")
        self.assertEqual(len(gff.genes), 69)

    def test_len(self):
        gtf = GAnnotation(file_path=gtf_file,
                          file_format="gtf")
        self.assertEqual(len(gtf.genes), 69)
        self.assertEqual(len(gtf.transcripts), 202)
        self.assertEqual(len(gtf.exons), 457)
        gff = GAnnotation(file_path=gff_file,
                          file_format="gff")
        self.assertEqual(len(gff.genes), 69)
        self.assertEqual(len(gff.transcripts), 202)
        self.assertEqual(len(gff.exons), 457)

    def test_get_gene(self):
        gtf = GAnnotation(file_path=gtf_file,
                          file_format="gtf")
        self.assertEqual(gtf.get_gene("ENSG00000290825.1")["gene_name"],
                         "DDX11L2")
        gff = GAnnotation(file_path=gff_file,
                          file_format="gff")
        self.assertEqual(gff.get_gene("ENSG00000290825.1")["gene_name"],
                         "DDX11L2")

    def test_gene_names(self):
        gtf = GAnnotation(file_path=gtf_file,
                          file_format="gtf")
        self.assertEqual(len(gtf.get_gene_names()), 69)
        gff = GAnnotation(file_path=gff_file,
                          file_format="gff")
        self.assertEqual(len(gff.get_gene_names()), 69)

    def test_gene_ids(self):
        gtf = GAnnotation(file_path=gtf_file,
                          file_format="gtf")
        self.assertEqual(len(gtf.get_gene_ids()), 69)
        gff = GAnnotation(file_path=gff_file,
                          file_format="gff")
        self.assertEqual(len(gff.get_gene_ids()), 69)

    def test_get_transcript(self):
        gtf = GAnnotation(file_path=gtf_file,
                          file_format="gtf")
        self.assertEqual(gtf.get_transcript("ENST00000456328.2")["gene_id"],
                         "ENSG00000290825.1")
        gff = GAnnotation(file_path=gff_file,
                          file_format="gff")
        self.assertEqual(gff.get_transcript("ENST00000456328.2")["gene_id"],
                         "ENSG00000290825.1")

    def test_get_exon(self):
        gtf = GAnnotation(file_path=gtf_file,
                          file_format="gtf")
        self.assertEqual(gtf.get_exon("ENSE00002234944.1")["gene_id"],
                         "ENSG00000290825.1")
        gff = GAnnotation(file_path=gff_file,
                          file_format="gff")
        self.assertEqual(gff.get_exon("ENSE00002234944.1")["gene_id"],
                         "ENSG00000290825.1")

    def test_get_transcript_ids(self):
        gtf = GAnnotation(file_path=gtf_file,
                          file_format="gtf")
        self.assertEqual(gtf.get_transcript_ids()[0],
                         "ENST00000456328.2")
        gff = GAnnotation(file_path=gff_file,
                          file_format="gff")
        self.assertEqual(gff.get_transcript_ids()[0],
                         "ENST00000456328.2")

    def test_get_exon_ids(self):
        gtf = GAnnotation(file_path=gtf_file,
                          file_format="gtf")
        self.assertEqual(gtf.get_exon_ids()[0],
                         "ENSE00002234944.1")
        gff = GAnnotation(file_path=gff_file,
                          file_format="gff")
        self.assertEqual(gff.get_exon_ids()[0],
                         "ENSE00002234944.1")
