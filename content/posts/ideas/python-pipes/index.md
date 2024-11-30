---
title: "Python Pipes"
date: 2024-11-29T19:38:26-07:00
draft: false
author: Anton Golubtsov
summary:
tags:
    - Software Development
---

I've always wanted to have a way to build data processing pipelines in Python
using pipes, like this `range(10) | F(is_odd) | P(lambda x: x * 2)`, instead of functions and generators and maps and loops.
So I've tried ...

The idea is pretty simple: let's create a class with implemented `OR` and `ROR` operators, the pipes.

```python
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
```

The tricky part was implementation of `__next__` since I wanted it to be a lazy operation. After a few trials and errors I've ended up with a pretty simple
approach where the wrapping class implementing the pipe will call `next` to its
source, added by `OR` or `ROR`, apply a transformation and then return
the result of the transformation.

```python
    def __next__(self):
        if self.source is None:
            raise StopIteration
        value = next(self.source)
        result = self.operator(value)
        return result
```

It did the trick for standard transformations but not for the filters like `is_odd` since those skips some data rather than return it like a transformation.
To filters easily addable I've implemented a wrapper that works similar to the pipe class but applies a filter to the data going through it.

```python
    def __next__(self):
        while True:
            if self.source is None:
                raise StopIteration
            value = next(self.source)
            if self.predicate(value):
                return value
```

The resulting code allowed me to do things like this:

```python
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
```

**Results:**

```
range(10) | P(lambda x: x + 3): [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
range(10) | P(lambda x: x + 3) | P(lambda x: x * 2): [6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
range(10) | F(is_odd): [1, 3, 5, 7, 9]
range(10) | F(is_odd) | P(lambda x: x * 2): [2, 6, 10, 14, 18]
list(range(10)) | F(is_odd) | P(lambda x: x * 2): [2, 6, 10, 14, 18]
gen_fn() | F(is_odd) | P(lambda x: x * 2): [2, 6, 10, 14, 18]
```

The complete code can be found here: [`pipe.py`](./pipe.py)
