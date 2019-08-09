from mark import Mark


class Assessment():
    def __init__(self, name,
                 knowledge=None, thinking=None, communication=None,
                 application=None, final=None):
        self.name = name
        self.marks = {"k": knowledge,
                      "t": thinking,
                      "c": communication,
                      "a": application,
                      "f": final}

    def add_mark_tuple(self, numerator, denominator, weight, strand):
        self.marks[strand] = Mark(numerator, denominator, weight, strand)
