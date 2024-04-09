color_primary = '99, 110, 250'
color_secondary = '0, 204, 150'
color_error = '239, 85, 59'

hsl_color_error = (9, 85, 58)

colors = [
    '171, 99, 250',
    '255, 161, 90',
    '25, 211, 243',
    '255, 102, 146',
    '182, 232, 128',
    '255, 151, 255',
    '254, 203, 82',
]

all_colors = [
    color_primary,
    color_secondary,
    color_error,
    *colors
]

hsl_colors = [
    (268, 93, 68),
    (25, 100, 67),
    (188, 90, 52),
    (342, 100, 70),
    (88, 69, 70),
    (300, 100, 79),
    (42, 98, 65)
]


class OrderedSet(list):
    def __init__(self, *args):
        super().__init__(*args)
        self.sort()

    def __and__(self, other):
        return OrderedSet(set(self) & set(other))

    def add(self, value):
        self.append(value)
        self.sort()
