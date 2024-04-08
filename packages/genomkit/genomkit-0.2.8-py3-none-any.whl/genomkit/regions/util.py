import pkg_resources
import os

# Get the path to the data folder within your package
data_folder = pkg_resources.resource_filename('genomkit', 'data')


def load_chromosome_sizes(file_path):
    chromosome_sizes = {}
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():
                chromosome, size = line.strip().split('\t')
                chromosome_sizes[chromosome] = int(size)
    return chromosome_sizes


def get_chrom_size(organism):
    """Return a dictionary for the chromosome sizes for the given organism.

    :param organism: Define the organism
    :type organism: str
    """
    file_path = os.path.join(data_folder, "chrom_size/chrom.sizes."+organism)
    if not os.path.exists(file_path):
        print("chrom.sizes."+organism+" is not found.")
    else:
        chromosome_sizes = load_chromosome_sizes(file_path)
        return chromosome_sizes
