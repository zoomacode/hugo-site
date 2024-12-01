def is_odd(n):
    return n % 2 == 1


class P:
    """Pipeable class"""

    def __init__(self, operator=None):
        self.operator = operator or (lambda x: x)
        self.source = None

    def __or__(self, other):
        other.source = self
        return other

    def __ror__(self, other):
        self.source = (
            iter(other)
            if not isinstance(other, (str, bytes)) and hasattr(other, "__iter__")
            else other
        )
        return self

    def __iter__(self):
        return self

    def __next__(self):
        if self.source is None:
            raise StopIteration
        value = next(self.source)
        result = self.operator(value)
        return result


class F(P):
    def __init__(self, predicate):
        super().__init__()
        self.predicate = predicate

    def __next__(self):
        while True:
            if self.source is None:
                raise StopIteration
            value = next(self.source)
            if self.predicate(value):
                return value


# Example usage with filtering
pipe = range(10) | P(lambda x: x + 3)
print("range(10) | P(lambda x: x + 3):", list(pipe))

pipe = range(10) | P(lambda x: x + 3) | P(lambda x: x * 2)
print("range(10) | P(lambda x: x + 3) | P(lambda x: x * 2):", list(pipe))

pipe = range(10) | F(is_odd)
print("range(10) | F(is_odd):", list(pipe))

pipe = range(10) | F(is_odd) | P(lambda x: x * 2)
print("range(10) | F(is_odd) | P(lambda x: x * 2):", list(pipe))

pipe = list(range(10)) | F(is_odd) | P(lambda x: x * 2)
print("list(range(10)) | F(is_odd) | P(lambda x: x * 2):", list(pipe))


def gen_fn():
    for i in range(10):
        yield i


pipe = gen_fn() | F(is_odd) | P(lambda x: x * 2)
print("gen_fn() | F(is_odd) | P(lambda x: x * 2):", list(pipe))
