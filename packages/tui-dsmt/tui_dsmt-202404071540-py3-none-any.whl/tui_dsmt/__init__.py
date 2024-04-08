color_primary = '99, 110, 250'
color_secondary = '0, 204, 150'
color_error = '239, 85, 59'

colors = [
    color_primary,
    color_secondary,
    color_error,
    '171, 99, 250',
    '255, 161, 90',
    '25, 211, 243',
    '255, 102, 146',
    '182, 232, 128',
    '255, 151, 255',
    '254, 203, 82',
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
