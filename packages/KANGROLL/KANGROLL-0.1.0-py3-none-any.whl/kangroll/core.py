class KangRollSet:
    def __init__(self, elements):
        if isinstance(elements, list):
            self.elements = elements
        elif isinstance(elements, set):
            self.elements = list(elements)
        else:
            raise TypeError("Elements should be a list or set")

    def __repr__(self):
        return f"KangRollSet({self.elements})"

    def union(self, other_set):
        return KangRollSet(list(set(self.elements) | set(other_set.elements)))

    def intersection(self, other_set):
        return KangRollSet(list(set(self.elements) & set(other_set.elements)))

    def roll_transform(self, transform_function):
        return KangRollSet([transform_function(element) for element in self.elements])
