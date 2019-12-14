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

    def add_mark_tuple(self, numerator, denominator, weight, strand_str):
        self.marks[strand_str] = Mark(numerator,
                                      denominator,
                                      weight,
                                      strand_str)
