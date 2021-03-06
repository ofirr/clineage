
basecomp = {
    b'A': b'T',
    b'T': b'A',
    b'C': b'G',
    b'G': b'C',
    b'N': b'N',
}

def _rc(seq):
    n = len(seq)
    l = [None]*n
    for i in range(n):
        l[n-i-1] = basecomp[seq[i:i+1]]
    return b''.join(l)

class DNA(object):

    def __init__(self, seq):
        # FIXME: this should change when we fix the db to give us bytes.
        if isinstance(seq, str):
            s = seq.upper()
            for i in s:
                if i not in "ACGTN":
                    raise ValueError("Invalid DNA base - not one of A,C,T,G.")
            self._seq = s.encode("ascii")
        elif isinstance(seq, bytes):
            s = seq.upper()
            for i in s:
                if i not in b"ACGTN":
                    raise ValueError("Invalid DNA base - not one of A,C,T,G.")
            self._seq = s
        else:
            raise TypeError("DNA accepts only string (bytes) objects.")

    @classmethod
    def umi(cls, umi_length):
        if not isinstance(umi_length, int):
            raise TypeError("Bad umi_length type.")
        return cls("N"*umi_length)

    @property
    def seq(self):
        return self._seq

    def rev_comp(self):
        return DNA(_rc(self.seq))

    def __add__(self, other):
        if not isinstance(other,DNA):
            raise TypeError("unsupported operand type(s) for +: '%s' and '%s'"
                            % (type(self), type(other)))
        # Can be optimized to omit ctor check.
        return DNA(self.seq + other.seq)

    def __getitem__(self, num_or_slice):
        if not isinstance(num_or_slice, slice):
            raise ValueError("Only returns slices")
        if num_or_slice.step is not None:
            raise ValueError("No step")
        return DNA(self.seq[num_or_slice])

    def __bytes__(self):
        return self.seq

    def __str__(self):
        return self.seq.decode("ascii")

    def __format__(self, fmt):
        return str(self).format(fmt)

    def __repr__(self):
        return "DNA(\"%s\")" % (self.seq)

    def __eq__(self, other):
        if not isinstance(other, DNA):
            raise TypeError("unsupported operand type(s) for ==: '%s' and '%s'"
                            % (type(self), type(other)))
        return self.seq == other.seq

    def __len__(self):
        return len(self.seq)

    def __hash__(self):
        return self.seq.__hash__()

