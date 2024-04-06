import intervals as I
from abc import ABC, abstractmethod
from .timer import *

class IntervalReader(ABC):
    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def validate(self, fields):
        pass

class BedIntervalReader(IntervalReader):
    def __init__(self, filename):
        self.file = open(filename)
        
    def __iter__(self):
        for line in self.file:
            fields = line.split()
            if not self.validate(fields):
                raise Exception(f"Line is not valid bed format:\n{line}")
            yield (fields[0], int(fields[1]), int(fields[2]))
    
    def validate(self, fields):
        return [f.isdigit() for f in fields[1:]] and len(fields) == 3

class ChromlinesIntervalReader(IntervalReader):
    def __init__(self, filename):
        self.file = open(filename)

    def __iter__(self):
        for line in self.file:
            fields = line.split()
            if not self.validate(fields):
                raise Exception(f"Line is not valid chromlines format:\n{line}")
            chrom, ends = fields[0], [int(f) for f in fields[1:]]
            start = 1
            for end in ends:
                yield([chrom, start, end])
                start = end

    def validate(self, fields):
        return [f.isdigit() for f in fields[1:]] and len(fields) > 1


class FragFinder:
    def __init__(self, reader):
        self.reader = reader

    def find(self, chrom, pos):
        """
        Use interpolation search to find index of interval containing position.
        This is slightly faster than bisect's bisect_left
        If not found, return [-1, 0, 0]
        """

        not_found = [-1, 0, 0]
        if chrom not in self.chroms:
            return not_found

        add_idx = 0
        for chroms in self.chroms:
            if chroms == chrom:
                break
            else:
                add_idx += len(self.chroms[chrom])

        ivls = self.chroms[chrom]

        if isinstance(pos, int):
            pos = I.closed(pos, pos)

        ivl_dist = lambda lo, hi: hi.upper - lo.lower
        frac_dist = lambda lo, hi, pos: ivl_dist(lo, pos)/ivl_dist(lo, hi)
        
        lo_i, hi_i = 0, len(ivls)-1
        interp_idx = lambda: round(frac_dist(ivls[lo_i], ivls[hi_i], pos) * (hi_i - lo_i)) + lo_i
        
        cur_i = interp_idx()
        cur_ivl = lambda: ivls[cur_i]
        found = lambda: pos in ivls[cur_i] or pos in ivls[lo_i] or pos in ivls[hi_i]

        ivl_range = I.closed(ivls[0].lower, ivls[-1].upper)

        if not pos in ivl_range:
            return not_found


        while not found():
            if lo_i == hi_i - 1 and cur_i in [lo_i, hi_i] and not found():
                return not_found

            if cur_ivl().upper < pos.upper:
                lo_i = cur_i
            else:
                hi_i = cur_i
            
            prev = cur_i
            cur_i = interp_idx()

            if cur_i == prev and not found():
                if cur_ivl() < pos:
                    cur_i += 1
                else:
                    cur_i -= 1
        
        if pos in ivls[lo_i]:
            result = lo_i
        elif pos in ivls[cur_i]:
            result = cur_i
        else:
            result = hi_i

        return [result + add_idx, ivls[result].lower, ivls[result].upper]

    def load(self):
        self.chroms = dict()
        for chrom, start, end in self.reader:
            self.chroms.setdefault(chrom, [])
            if self.chroms[chrom]:
                if self.chroms[chrom][-1].upper == start:
                    start += 1
                if start -1 != self.chroms[chrom][-1].upper:
                    raise Exception(
                        f"{chrom} {start} {end} is not adjacent to previous "
                        "fragment.\nChromosomes should be partitioned by fragment "
                        "intervals and intervals should be sorted by chromosome "
                        "first, then by start position.")
            if not self.chroms[chrom] and start != 1:
                raise Exception(f"{chrom} {start} {end} is first fragment on "
                    "chromosome, but does not start at position 1. Fragment "
                    "file may not be sorted.")
            self.chroms[chrom].append(I.closed(start, end))
        return self

