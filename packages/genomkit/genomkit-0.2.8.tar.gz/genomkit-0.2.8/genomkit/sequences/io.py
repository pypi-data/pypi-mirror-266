from tqdm import tqdm
import gzip
import re


###########################################################################
# IO functions
###########################################################################
def load_FASTA(file):
    if isinstance(file, str):  # If file is a filename
        with open(file, 'r') as f:
            return load_FASTA_from_file(f)
    else:  # If file is a file object
        return load_FASTA_from_file(file)


def load_FASTA_from_file(file):
    from genomkit import GSequence, GSequences
    res = GSequences()
    current_sequence_id = None
    current_sequence = ""
    total_lines = sum(1 for line in file if not line.startswith("#"))
    file.seek(0)  # Reset file pointer to the beginning
    with tqdm(total=total_lines, desc="Load FASTA") as pbar:
        for line in file:
            line = line.strip()
            if line.startswith("#"):
                continue
            elif line.startswith(">"):
                # If there was a previously stored sequence, store it
                if current_sequence_id is not None:
                    infos = re.split(r'[ |;,-]', current_sequence_id)
                    name = infos[0].split(".")[0]
                    data = infos[1:]
                    res.add(GSequence(sequence=current_sequence,
                                      name=name, data=data))
                # Extract the sequence ID
                current_sequence_id = line[1:]
                # Start a new sequence
                current_sequence = ""
            else:  # Sequence line
                # Append the sequence line to the current sequence
                current_sequence += line
            pbar.update(1)
        # Store the last sequence
        if current_sequence_id is not None:
            infos = re.split(r'[ |;,-]', current_sequence_id)
            name = infos[0].split(".")[0]
            data = infos[1:]
            res.add(GSequence(sequence=current_sequence,
                              name=name, data=data))
    return res


def load_FASTQ(file):
    if isinstance(file, str):  # If file is a filename
        with open(file, 'r') as f:
            return load_FASTQ_from_file(f)
    else:  # If file is a file object
        return load_FASTQ_from_file(file)


def load_FASTQ_from_file(file):
    from genomkit import GSequence, GSequences
    res = GSequences()
    current_sequence_id = None
    current_sequence = ""
    current_quality = ""
    total_records = sum(1 for _ in file) // 4  # Calculate total records
    file.seek(0)  # Reset file pointer to the beginning

    with tqdm(total=total_records, desc="Load FASTQ") as pbar:
        for line_num, line in enumerate(file):
            line = line.strip()
            if line.startswith("#"):
                continue
            elif line_num % 4 == 0:  # Sequence header line
                # If there was a previously stored sequence, store it
                if current_sequence_id is not None:
                    if len(current_sequence) != len(current_quality):
                        raise ValueError("Invalid FASTQ file: Sequence and "
                                         "quality lines do not match.")
                    res.add(GSequence(sequence=current_sequence,
                                      quality=current_quality,
                                      name=current_sequence_id))
                    pbar.update(1)  # Update progress bar
                # Extract the sequence ID
                current_sequence_id = line[1:]
                # Start new sequence and quality strings
                current_sequence = ""
                current_quality = ""
            elif line_num % 4 == 1:  # Sequence line
                current_sequence = line
            elif line_num % 4 == 3:  # Quality scores line
                current_quality = line
        # Store the last sequence
        if current_sequence_id is not None:
            if len(current_sequence) != len(current_quality):
                raise ValueError("Invalid FASTQ file: Sequence and quality "
                                 "lines do not match.")
            res.add(GSequence(sequence=current_sequence,
                              quality=current_quality,
                              name=current_sequence_id))
            pbar.update(1)  # Update progress bar
    return res


def write_FASTA(seqs, filename: str, data: bool = False,
                gz: bool = False):
    if gz:
        with gzip.open(filename, "wt") as fasta_file:
            write_fasta_content(seqs, fasta_file, data)
    else:
        with open(filename, "w") as fasta_file:
            write_fasta_content(seqs, fasta_file, data)


def write_fasta_content(seqs, fasta_file, data: bool):
    for seq in seqs.elements:
        if data:
            fasta_file.write(">" + seq.name + " " +
                             " ".join(seq.data) + "\n")
        else:
            fasta_file.write(f">{seq.name}\n")
        for i in range(0, len(seq.sequence), 80):
            fasta_file.write(f"{seq.sequence[i:i+80]}\n")


def write_FASTQ(seqs, filename: str, data: bool = False, gz: bool = True):
    if gz:
        with gzip.open(filename, "wt") as fastq_file:
            write_fastq_content(seqs, fastq_file, data)
    else:
        with open(filename, "w") as fastq_file:
            write_fastq_content(seqs, fastq_file, data)


def write_fastq_content(seqs, fastq_file, data: bool):
    for seq in seqs.elements:
        if data:
            fastq_file.write(f"@{seq.name} {' '.join(seq.data)}\n")
        else:
            fastq_file.write(f"@{seq.name}\n")
        fastq_file.write(f"{seq.sequence}\n")
        fastq_file.write("+\n")
        fastq_file.write(f"{seq.quality}\n")
