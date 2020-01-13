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
        if(other is None
           or type(other) != type(self)
           or other.name != self.name):
            return False
        for strand_str in STRAND_STRINGS:
            if self.marks.get(strand_str) != other.marks.get(strand_str):
                return False
        return True

    def __ne__(self, other):
        return not(self == other)

    def __str__(self):
        return ("Assessment({0}: K:{1} T:{2} C:{3} A:{4} F:{5})"
                .format(self.name,
                        self.marks.get("k"),
                        self.marks.get("t"),
                        self.marks.get("c"),
                        self.marks.get("a"),
                        self.marks.get("f")))

    def add_mark_tuple(self, numerator, denominator, weight, strand_str):
        self.marks[strand_str] = Mark(numerator,
                                      denominator,
                                      weight,
                                      strand_str)

    def copy_from(self, other):
        self.marks = other.marks
