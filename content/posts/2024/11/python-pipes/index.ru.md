---
title: "Python Pipes"
date: 2024-11-29T19:38:26-07:00
draft: false
author: Anton Golubtsov
summary:
tags:
    - Software Development
---

Я всегда хотел иметь способ создавать конвейеры обработки данных в Python, используя пайпы, что-то вроде `range(10) | F(is_odd) | P(lambda x: x * 2)`, вместо функций, генераторов, map'ов и циклов.  
Так что я попробовал...

Идея довольно простая: давайте создадим класс с реализованными операторами `|` и `||`, то есть пайпами.

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

Сложность заключалась в реализации метода `__next__`, так как я хотел, чтобы это была ленивое вычисление. После нескольких попыток и ошибок я пришёл к довольно простому подходу: обёрточный класс, реализующий пайп, вызывает `next` у своего источника, добавленного через `|` или `||`, применяет трансформацию и затем возвращает результат этой трансформации.

```python
    def __next__(self):
        if self.source is None:
            raise StopIteration
        value = next(self.source)
        result = self.operator(value)
        return result
```

Этот подход сработал для стандартных трансформаций, но не для фильтров вроде `is_odd`, поскольку такие фильтры пропускают часть данных, а не возвращают их, как трансформация. Чтобы фильтры можно было легко добавлять, я реализовал обёртку, которая работает аналогично классу пайпа, но применяет фильтр к данным, проходящим через неё.

```python
    def __next__(self):
        while True:
            if self.source is None:
                raise StopIteration
            value = next(self.source)
            if self.predicate(value):
                return value
```

Получившийся код позволил мне делать что-то вроде этого:

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

**Результаты:**

```
range(10) | P(lambda x: x + 3): [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
range(10) | P(lambda x: x + 3) | P(lambda x: x * 2): [6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
range(10) | F(is_odd): [1, 3, 5, 7, 9]
range(10) | F(is_odd) | P(lambda x: x * 2): [2, 6, 10, 14, 18]
list(range(10)) | F(is_odd) | P(lambda x: x * 2): [2, 6, 10, 14, 18]
gen_fn() | F(is_odd) | P(lambda x: x * 2): [2, 6, 10, 14, 18]
```

Переход от этого:

```python
result = [x * 2 for x in range(10) if is_odd(x)]
```

к этому:

```python
result = list(range(10)) | F(is_odd) | P(lambda x: x * 2)
```

может показаться не таким уж значительным изменением. Но если вы попробуете реализовать что-то вроде:

```python
range(10) | F(f1) | P(op1) | P(op2) | P(op3) | F(f2)
```

и заставить это работать в режиме ленивой оценки, вы довольно быстро поймёте, что это не так просто и интуитивно понятно. Есть способы, например, через `Queue`, но они требуют большого количества шаблонного кода.

Полный код можно найти здесь: [`pipe.py`](./pipe.py)
