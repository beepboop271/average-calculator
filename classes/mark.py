class Mark(object):
    def __init__(self, numerator, denominator, weight, strand_str):
        self.numerator = numerator
        self.denominator = denominator
        self.weight = weight
        self.strand_str = strand_str
        self.decimal = float(numerator)/denominator

    def __eq__(self, other):
        if(other is None
           or type(other) != type(self)):
            return False
        return (self.numerator == other.numerator
                and self.denominator == other.denominator
                and self.weight == other.weight
                and self.strand_str == other.strand_str)

    def __ne__(self, other):
        return not(self == other)

    def __str__(self):
        return ("Mark({0} W{1} {2}/{3} {4}%)"
                .format(self.strand_str,
                        self.weight,
                        self.numerator,
                        self.denominator,
                        round(self.decimal*100, 1)))
