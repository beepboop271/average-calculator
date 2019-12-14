class Mark(object):
    def __init__(self, numerator, denominator, weight, strand_str):
        self.numerator = numerator
        self.denominator = denominator
        self.weight = weight
        self.strand_str = strand_str
        self.decimal = float(numerator)/denominator

    def __eq__(self, other):
        if other is None:
            return False
        return (self.numerator == other.numerator
                and self.denominator == other.denominator
                and self.weight == other.weight
                and self.strand_str == other.strand_str)

    def __ne__(self, other):
        return not(self == other)

    # def __str__(self):
    #     return ("("+self.strand+" w"+str(self.weight)+" "
    #             + str(self.numerator)+"/"+str(self.denominator)+" "
    #             + str(round(self.decimal*100, 1))+"%)")
