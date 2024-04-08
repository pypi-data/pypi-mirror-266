import os
from tqdm import tqdm
from intervaltree import Interval, IntervalTree
from collections import defaultdict, OrderedDict


###########################################################################
# IO functions
###########################################################################
def load_BED(filename: str):
    def get_score(score):
        if score == ".":
            score = 0
        else:
            score = float(score)
        return score
    from genomkit import GRegion, GRegions
    if not os.path.exists(filename):
        raise FileNotFoundError(f"The file '{filename}' does not exist.")
    else:
        res = GRegions()
        with open(filename, 'r') as file:
            for line in tqdm(file,
                             desc=os.path.basename(filename),
                             unit=" lines"):
                if not line.startswith("#"):
                    infos = line.strip().split()
                    if len(infos) == 3:
                        res.add(GRegion(sequence=infos[0],
                                        start=int(infos[1]),
                                        end=int(infos[2])))
                    elif len(infos) == 4:
                        res.add(GRegion(sequence=infos[0],
                                        start=int(infos[1]),
                                        end=int(infos[2]),
                                        name=infos[3]))
                    elif len(infos) == 5:
                        res.add(GRegion(sequence=infos[0],
                                        start=int(infos[1]),
                                        end=int(infos[2]),
                                        name=infos[3],
                                        score=get_score(infos[4])))
                    elif len(infos) == 6:
                        res.add(GRegion(sequence=infos[0],
                                        start=int(infos[1]),
                                        end=int(infos[2]),
                                        name=infos[3],
                                        score=get_score(infos[4]),
                                        orientation=infos[5]))
                    elif len(infos) > 6:
                        res.add(GRegion(sequence=infos[0],
                                        start=int(infos[1]),
                                        end=int(infos[2]),
                                        name=infos[3],
                                        score=get_score(infos[4]),
                                        orientation=infos[5],
                                        data=infos[6:]))
        return res


def load_BED_intervaltree(filename: str):
    def get_score(score):
        if score == ".":
            score = 0
        else:
            score = float(score)
        return score
    from genomkit import GRegion
    if not os.path.exists(filename):
        raise FileNotFoundError(f"The file '{filename}' does not exist.")
    else:
        res = defaultdict(lambda: IntervalTree())
        with open(filename, 'r') as file:
            for line in tqdm(file,
                             desc=os.path.basename(filename),
                             unit=" lines"):
                if not line.startswith("#"):
                    infos = line.strip().split()
                    if len(infos) == 3:
                        region = GRegion(sequence=infos[0],
                                         start=int(infos[1]),
                                         end=int(infos[2]))
                    elif len(infos) == 4:
                        region = GRegion(sequence=infos[0],
                                         start=int(infos[1]),
                                         end=int(infos[2]),
                                         name=infos[3])
                    elif len(infos) == 5:
                        region = GRegion(sequence=infos[0],
                                         start=int(infos[1]),
                                         end=int(infos[2]),
                                         name=infos[3],
                                         score=get_score(infos[4]))
                    elif len(infos) == 6:
                        region = GRegion(sequence=infos[0],
                                         start=int(infos[1]),
                                         end=int(infos[2]),
                                         name=infos[3],
                                         score=get_score(infos[4]),
                                         orientation=infos[5])
                    elif len(infos) > 6:
                        region = GRegion(sequence=infos[0],
                                         start=int(infos[1]),
                                         end=int(infos[2]),
                                         name=infos[3],
                                         score=get_score(infos[4]),
                                         orientation=infos[5],
                                         data=infos[6:])
                    res[infos[0]].add(
                        Interval(int(infos[1]),
                                 int(infos[2]),
                                 region))
        return res
