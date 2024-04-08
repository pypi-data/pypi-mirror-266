import gzip
from tqdm import tqdm


class GAnnotation:
    """GAnnotation module

    This module contains functions and classes for working with genomic
    annotation files in the format of gtf, gtf.gz, gff, or gff.gz.
    """
    def __init__(self, file_path: str, file_format: str):
        """Initiate a GAnnotation object.

        :param file_path: File path to gtf, gtf.gz, gff, or gff.gz
        :type file_path: str
        :param file_format: File format, gtf or gff
        :type file_format: str
        """
        self.file_path = file_path
        self.file_format = file_format.lower()
        self.genes = {}
        self.transcripts = {}
        self.exons = {}
        self.load_data()

    def load_data(self):
        """Load the file."""
        open_func = gzip.open if self.file_path.endswith('.gz') else open
        total_lines = sum(1 for _ in open_func(self.file_path, 'rt'))
        with open_func(self.file_path, 'rt') as f:
            for line in tqdm(f, total=total_lines, desc="Loading GTF"):
                if line.startswith('#'):
                    continue
                fields = line.strip().split('\t')
                if self.file_format == 'gtf':
                    feature_type = fields[2]
                    attributes = dict(item.strip().split(' ')
                                      for item in fields[8].split(';')
                                      if item.strip())
                elif self.file_format == 'gff':
                    feature_type = fields[2]
                    attributes = dict(item.strip().split('=')
                                      for item in fields[8].split(';')
                                      if item.strip())
                else:
                    raise ValueError("Invalid file format. "
                                     "Supported formats are 'gtf' and 'gff'.")

                if feature_type == 'gene':
                    gene_id = attributes['gene_id'].strip('"')
                    self.genes[gene_id] = {
                        'id': gene_id,
                        'chr': fields[0],
                        'start': int(fields[3]),
                        'end': int(fields[4]),
                        'strand': fields[6],
                        'gene_name': attributes.get(
                            'gene_name', '').replace('"', ''),
                        'gene_type': attributes.get(
                            'gene_type', '').replace('"', '')
                    }
                elif feature_type == 'transcript':
                    transcript_id = attributes['transcript_id'].strip('"')
                    gene_id = attributes['gene_id'].strip('"')
                    self.transcripts[transcript_id] = {
                        'id': transcript_id,
                        'gene_id': gene_id,
                        'chr': fields[0],
                        'start': int(fields[3]),
                        'end': int(fields[4]),
                        'strand': fields[6],
                        'transcript_type':
                            attributes.get('transcript_type', '')
                    }
                    if gene_id in self.genes:
                        self.genes[gene_id].setdefault(
                            'transcripts', set()).add(transcript_id)
                elif feature_type == 'exon':
                    exon_id = attributes['exon_id'].strip('"')
                    transcript_id = attributes['transcript_id'].strip('"')
                    gene_id = attributes['gene_id'].strip('"')
                    self.exons[exon_id] = {
                        'id': exon_id,
                        'transcript_id': transcript_id,
                        'gene_id': gene_id,
                        'chr': fields[0],
                        'start': int(fields[3]),
                        'end': int(fields[4]),
                        'strand': fields[6]
                    }
                    if transcript_id in self.transcripts:
                        self.transcripts[transcript_id].setdefault(
                            'exons', set()).add(exon_id)

    def get_gene(self, gene_id: str):
        """Get the annotation of a gene by gene id.

        :param gene_id: Define gene id.
        :type gene_id: str
        :return: annotation of a gene
        :rtype: dict
        """
        return self.genes.get(gene_id)

    def get_gene_names(self):
        """Return all gene names in the annotation.

        :return: A list of all gene names
        :rtype: list
        """
        gene_names = [gene_info['gene_name']
                      for gene_info in self.genes.values()
                      if gene_info.get('gene_name')]
        return gene_names

    def get_gene_ids(self):
        """Return all gene ids in the annotation.

        :return: A list of all gene ids
        :rtype: list
        """
        gene_ids = list(self.genes.keys())
        return gene_ids

    def get_transcript(self, transcript_id):
        """Get the annotation of a transcript by transcript id.

        :param transcript_id: Define transcript id.
        :type transcript_id: str
        :return: annotation of a transcript
        :rtype: dict
        """
        return self.transcripts.get(transcript_id)

    def get_exon(self, exon_id):
        """Get the annotation of an exon by exon id.

        :param exon_id: Define exon id.
        :type exon_id: str
        :return: annotation of an exon
        :rtype: dict
        """
        return self.exons.get(exon_id)

    def get_transcript_ids(self):
        """Return all transcript ids in the annotation.

        :return: A list of all transcript ids
        :rtype: list
        """
        transcript_ids = list(self.transcripts.keys())
        return transcript_ids

    def get_exon_ids(self):
        """Return all exon ids in the annotation.

        :return: A list of all exon ids
        :rtype: list
        """
        exon_ids = list(self.exons.keys())
        return exon_ids

    def filter_elements(self, element_type, attribute=None, value=None):
        """
        Filter elements (genes, transcripts, exons) based on attribute
        criteria.

        :param element_type: Type of elements to filter ('gene', 'transcript',
                             'exon').
        :param attribute: Attribute to filter on (e.g., 'biotype').
        :param value: Value of the attribute to filter on.
        :return: List of filtered elements.
        """
        if element_type == 'gene':
            elements = self.genes.values()
        elif element_type == 'transcript':
            elements = self.transcripts.values()
        elif element_type == 'exon':
            elements = self.exons.values()
        else:
            raise ValueError("Invalid element type. Supported types are"
                             "'gene', 'transcript', 'exon'.")
        filtered_elements = []
        for element in elements:
            if attribute and value:
                if attribute in element and element[attribute] == value:
                    filtered_elements.append(element)
            else:
                filtered_elements.append(element)
        return filtered_elements

    def get_regions(self, element_type: str,
                    attribute: str = None,
                    value=None):
        """Return GRegions according to the filtering method.

        :param element_type: gene, transcript, or exon
        :type element_type: str
        :param attribute: Attribute for filtering such as 'chr', 'start',
                          'end', 'strand', 'gene_name', 'gene_type',
                          defaults to None
        :type attribute: str, optional
        :param value: Value of the attribute, defaults to None
        :type value: str or int, optional
        :return: GRegions
        :rtype: GRegions
        """
        from genomkit import GRegion, GRegions
        filtered_elements = self.filter_elements(
            element_type, attribute=attribute, value=value)
        res = GRegions()
        for element in filtered_elements:
            extra_data = [":".join([attribute, element[attribute]])
                          for attribute in element.keys()
                          if attribute not in ["id", "chr", "start", "end",
                                               "strand", "transcripts"]]
            if "transcripts" in element.keys():
                transcripts = "transcripts:" + ",".join(element["transcripts"])
                extra_data += [transcripts]
            if "gene_name" in element.keys():
                name = element["gene_name"]
                extra_data = ["gene_id:"+element["id"]] + extra_data
            else:
                name = element["id"]
            region = GRegion(sequence=element["chr"],
                             start=element["start"],
                             end=element["end"],
                             orientation=element["strand"],
                             name=name,
                             data=extra_data)
            res.add(region)
        return res
