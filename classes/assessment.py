from .mark import Mark
STRAND_STRINGS = ["k", "t", "c", "a", "f"]


class Assessment():
    def __init__(self, name,
                 mark_list=None):
        self.name = name
        self.marks = {"k": None,
                      "t": None,
                      "c": None,
                      "a": None,
                      "f": None}
        if mark_list is not None:
            for i in range(len(mark_list)):
                if mark_list[i] is not None:
                    self.add_mark_tuple(*mark_list[i],
                                        strand_str=STRAND_STRINGS[i])

    def __eq__(self, other):
        for strand_str in STRAND_STRINGS:
            if self.marks.get(strand_str) != other.marks.get(strand_str):
                return False
        return True

    def __ne__(self, other):
        return not(self == other)

    def add_mark_tuple(self, numerator, denominator, weight, strand_str):
        self.marks[strand_str] = Mark(numerator,
                                      denominator,
                                      weight,
                                      strand_str)
