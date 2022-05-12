---
title: "Book review: Fluent Python by Luciano Romalho (Part 1)"
date: 2022-05-02T22:30:35-07:00
draft: false
author: Anton Golubtsov
---

# Fluent Python: learnings (part 1)

Somebody recommended [Fluent Python by Luciano Romalho](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/) on Twitter as a wonderful book about Python and the data structures part, in particular, is great. On my current project, I do a lot of data transformations and I started wondering if the book could help me sharpen my python skills. I’ve just finished reading the first, Data Structures, part of the book and I have something to say. First of all the book is 1000 pages thick but don’t be afraid - it is full of code snippets so the text is much shorter. Secondly, I discovered a lot of things I didn’t know so I decided to write a short article about what I’ve learned from the book.

#### **Data unpacking**

Data unpacking is a syntax which allows unpacking of a data structure to more simple representation. For example:

```python
    t = (10, 20)
    a, b = t
    c, _ = t
```

Here we unpack a tuple `t` to variables `a`, `b` and `d` and we use `_` to drop one of the values. I use quite often but in simple cases and was not aware that it can do more. For example, we can unpack a tail of a list/tuple a variable:

```python
    >>> t = (1, 2, 3, 4, 5, 6)
    >>> a, _, *c = t
    >>> print(f"{a}, {c}")
    1, [3, 4, 5, 6]
```

We can also unpack more complex data structures, for example:

```python
    >>> s = (1,2, (9,6))
    >>> a, _, (c,d) = s
    >>> print(f"{a}, {c}, {d}")
    1, 9, 6
```

It is called nested unpacking.

#### **Pattern matching (Python 3.10)**

Pattern matching is a way to replace `if … else` statements for checking a data structure fulfills a condition. For example, you have a list of strings, which you got from a csv file, and you need to call different functions depends on the value of the second element. This is how you would probably do it using `if … else`:

```python
    for line in csv_file:
        data = line.split(",")
        if data[0] == "car":
          if data[1] == "new":
            new_cars.append(data[2])
          else:
            old_cars.append(data[2])
        elif: data[0] == "chair":
          if data[1] == "color":
            set_chair_color(data[3])
        else:
          raise ValueError("Unknown")
```

It is a bit hard to read and looks unnatural. With pattern matching you can simplify the code:

```python
    for line in csv_file:
        match data:
          case ["car", "new", car]:
            new_cars.append(car)
          case ["car", _, car]:
            old_cars.append(car)
          case ["chair", "color", color]:
            set_chair_color(color)
          case _:
            raise ValueError("Unknown")
```

As you can see the code is more readable, and concise. Pattern matching is more than that basic example. You can use to match a type, a specific element of a dictionary, or an “or” statement:

```python
    match data:
        case MyWonderfulClass(par1="Wow"):
            ....
        # Check that a dictionary has a key with a string value and then take key's value
        case {"Key": str(value)}:
            print(value)
        # Check that data is a list with "action" is a first item, the second item
        # is one of three values that we store in action variable
        # and let's put everything else into the context variable.
        case ["action", ("run" | "walk" | "jump") as action, *context ]:
            ...
```

Imagine how much code you will need to write to express the same thing through `if … else`.

You can find official pattern matching tutorial in [PEP 636](https://peps.python.org/pep-0636/).

#### **Slice objects**

I’ve never thought that the slice operation is actually an object that you can create explicitly and the apply to any other object. I don’t want to copy examples from the book they are much fancier than mine. So here is a basic example:

```python
    >>> a = [1,2,3,4,5,6,7]
    >>> coordinates = slice(None,2)
    >>> starting_second = slice(2, None)
    >>> every_second = slice(None, None, 2)
    >>> a[coordinates]
    [1, 2]
    >>> a[starting_second]
    [3, 4, 5, 6, 7]
    >>> a[every_second]
    [1, 3, 5, 7]
```

It can be handy if you need to describe what part of data you need to extract and to have formal names for a slice instead of `5:7`.

#### **Memory view**

Arrays store data in continuous memory like arrays in C++. Memory views help to view the same raw memory in a different shape. For example, you can show an array of bytes as an array of integers, as matrix, or a slice without copying any data.

```python
    >>> a = array("l", range(2000, 2006))
    >>> m = memoryview(a)
    >>> m.hex()
    'd007000000000000d107000000000000d207000000000000d307000000000000d407000000000000d507000000000000'
    >>> m.tobytes()
    b'\xd0\x07\x00\x00\x00\x00\x00\x00\xd1\x07\x00\x00\x00\x00\x00\x00\xd2\x07\x00\x00\x00\x00\x00\x00\xd3\x07\x00\x00\x00\x00\x00\x00\xd4\x07\x00\x00\x00\x00\x00\x00\xd5\x07\x00\x00\x00\x00\x00\x00'
    >>> m.nbytes
    48
    >>> mb = m.cast("b")
    >>> ml = mb.cast("l", [2,3])
    >>> ml.tolist()
    [[2000, 2001, 2002], [2003, 2004, 2005]]
    >>> mb.tolist()
    [-48, 7, 0, 0, 0, 0, 0, 0, -47, 7, 0, 0, 0, 0, 0, 0, -46, 7, 0, 0, 0, 0, 0, 0, -45, 7, 0, 0, 0, 0, 0, 0, -44, 7, 0, 0, 0, 0, 0, 0, -43, 7, 0, 0, 0, 0, 0, 0]
    >>> m.tolist()
    [2000, 2001, 2002, 2003, 2004, 2005]
```

Memory view can be quite handy if you work with raw data like writing binary files, stores data in arrays or something else.

#### **Hashable**

You may be surprised but I’ve never checked what hashable means because I don’t use dictionaries with anything besides strings. Anyhow, if you want to use something as a key in a `dict` you need to know what the hashable is. In short it is something immutable so the key can’t be changed after it is added to a dictionary or a set. For example, things like strings and numbers are hashable because you can’t really modify after creation. Lists are mutable so not hashable. Tuples are immutable but they can contain mutable object so tuples are hashable if all their items are hashable. For example, a tuple with a list in it is not hashable but a tuple of tuples is hashable.

```python
    >>> hash((2,3,4))
    -3165226637586315787
    >>> hash((2,3,"yo"))
    -8824834027793254068
    >>> hash((2,3,"yo", ("d", 15)))
    7078333280866408460
    >>> hash((2,3,"yo", ["d", 15]))
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: unhashable type: 'list'
```

For user defined types hashability is a bit trickier. They are all hashable unless there is a custom `__eq__` implemented then you need to implement `__hash__` as well to make it hashable. If you need it.

#### **Setdefault and defaultdict**

Sometimes you need to update a dictionary item but the item may or may not be there so you need to create a default value before you can update it. Dictionary has a nice `get` function which returns something if the key you requested is abstain. The problem is that `get` does not modify the dictionary. To work around it you can write something like this:

```python
    word_count = {}
    ...
    for word in test:
        if word not in word_count:
            word_count[word] = 0
        word_count[word] += 1
```

There are two problems if this code: 1) it is bulky; 2) it does search twice. To fix it we can use `defaultdict` which is like `dict` but adds missing item per requests. It may or may not what you want, for example, if a part of the code only reads data from a dictionary using `defaultdict` will create an element on each lookup and consume more and more memory.

```python
    >>> from collections import defaultdict
    >>> d = defaultdict(list)
    >>> d[1]
    >>> d[2]
    []
    >>> d
    defaultdict(<class 'list'>, {1: [], 2: []})
    >>> d = dict()
    >>> d.get(1, [])
    []
    >>> d.get(2, [])
    []
    >>> d
    {}
```

Instead of `defaultdict` you can use `setdefault` method of a regular `dict` when you indeed need to create an element.

```python
    >>> d = dict()
    >>> d.setdefault(1, [])
    []
    >>> d.setdefault(2, []).append(2)
    >>> d
    {1: [], 2: [2]}
```

#### **Return** `**None**` **convention for methods which modify data**

I didn’t know that but apparently Python methods should not return any data if they modify data and return a copy of data when they do. We can see it in the previous example when `append` didn’t return anything. It is not a strict rule obviously. It is just a way to indicate that data was modified in place. It may seem in convenient since we can create a chain of appends like `d.append(1).append(2)` but I think it is nice rule to have or follow. Depends on your needs of course.

#### **collections.Chainmap**

`collections.Chainmap` allows to search through multiple maps with one call. It also allows to modify existing keys.

```python
    >>> import collections
    >>> a = {2: 3, 4:5}
    >>> b = {6: 7, 8: 9}
    >>> c = collections.ChainMap(a,b)
    >>> c
    ChainMap({2: 3, 4: 5}, {6: 7, 8: 9})
    >>> c[2]
    3
    >>> c[6]
    7
    >>> c[6] += 1
    >>> c
    ChainMap({2: 3, 4: 5, 6: 8}, {6: 7, 8: 9})
    >>> b
    {6: 7, 8: 9}
```

I’ve never had a need to search through multiple maps but it is a nice option to have.

#### **collections.Counter**

It is a pretty cool thing it ingest a list of items and counts how many time each of unique items is presented in the list.

```python
    >>> a = [1,3,4,5,6,71,2,3,3,1,5]
    >>> c = collections.Counter(a)
    >>> c
    Counter({3: 3, 1: 2, 5: 2, 4: 1, 6: 1, 71: 1, 2: 1})
    >>> c.most_common(3)
    [(3, 3), (1, 2), (5, 2)]
```

It also has a set of methods to count as you go:

```python
    >>> c.
    c.clear(        c.get(          c.pop(          c.update(
    c.copy(         c.items(        c.popitem(      c.values(
    c.elements(     c.keys(         c.setdefault(
    c.fromkeys(     c.most_common(  c.subtract(
```

#### **Printing unicode characters by their names and names lookup**

`print` supports a pretty feature that allows to print and lookup characters by their names. I like different unicode symbols like emojis but I’m not sure that will be happy to see them in the code just for the fonts compatibility reason.

```python
    >>> print('\N{GREEK SMALL LETTER ALPHA}')
    α
    >>> print('\N{INFINITY}')
    ∞
    >>> import unicodedata
    >>> unicodedata.name("よ")
    'HIRAGANA LETTER YO'
    >>> unicodedata.lookup('HIRAGANA LETTER RO')
    'ろ'
```

#### **Normalizing unicode**

Unicode has different ways to encode visually identical characters. For example, diacritics can be presented in two different ways a character + a diacritical modifier or as a character with diacritic.

```python
    >>> po = "ぽ"
    >>> po
    'ぽ'
    >>> nfc_po = unicodedata.normalize("NFC", po)
    >>> nfd_po = unicodedata.normalize("NFD", po)
    >>> nfc_po == nfd_po
    False
    >>> print(po, nfc_po, nfd_po)
    ぽ ぽ ぽ
    >>> print(len(po), len(nfc_po), len(nfd_po))
    1 1 2
```

I entered Japanese po using key board and then tried to normalize to the compact form which is one character and then to the longer form. As you can see the characters looks the same but they are differently encoded so `nfc_po == nfd_po` gives us `False`.

From the python documentation: https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize

> For each character, there are two normal forms: normal form C and normal form D. Normal form D (NFD) is also known as canonical decomposition, and translates each character into its decomposed form. Normal form C (NFC) first applies a canonical decomposition, then composes pre-combined characters again.

There are more ways to normalize unicode strings some of them makes sense only if you deal with data indexing for a search engine or something like that. They are described at the great detail in the book.

#### **Pyuca/Sorting unicode**

[Pyuca](https://github.com/jtauber/pyuca) is a pure python library that sorts not English text properly. If you work with text or you build a UI you might want to sort non-English text as it supposed be sorted.

#### **Numeric Meaning of Characters**

I was surprised to discover that `unicodedata` module allows to get numeric values for characters I would never expect to be convertible to a number without extra effort. Here are just a few examples:

```python
    >>> sample = '\xbc\u0969\u136b\u216b\u2480\u3285'
    >>> print("\n".join([f"{c}:{c.isnumeric()}:{unicodedata.numeric(c)}" for c in sample]))
    ¼:True:0.25
    ३:True:3.0
    ፫:True:3.0
    Ⅻ:True:12.0
    ⒀:True:13.0
    ㊅:True:6.0
```

Try to play with `isdigit`, `isnumeric`, and regular expressions.

#### **Everything is a reference**

It is not something I learned from the book but in the very early days of my work with python. My first production language was C++ which has its ways to express whether a variable: a value, a reference, a pointer, a const value, a const reference, or a const point or a point to const data. And it also have all sorts of optimizations like return value optimization. So from the very first days I was curious what exactly is a function argument and what operations like `b = a` do.

In C++ a lot of things are explicit, not everything but you can be explicit enough especially when it is important. In Python everything is implicit. Everything in python is a reference so if you don’t keep it mind and don’t take actions to create a copy when of a object you may see interesting and probably not solicited side-effects.

Before we go jump to the examples I need to mention that those side-effects take place only for mutable objects. For immutable you will be forced to create a copy implicitly or explicitly if you try to change those immutable objects. Here is the first example:

```python
    >>> a = [2,3,4]
    >>> b = a
    >>> b.append(7)
    >>> a
    [2, 3, 4, 7]
    >>> s = "123"
    >>> s2 = s
    >>> s2 += "4"
    >>> s
    '123'
    >>> print(id(a), id(b), id(s), id(s2))
    4486725184 4486725184 4489247792 4489247728
```

As you can see `a` and `b` refer to the same object when `s` and `s2` refer to different objects. The same thing happens when you use mutable objects as a default parameter or accept them as parameter for a class or a function. For example:

```python
    >>> def foo(a=[]):
    ...     a.append(1)
    ...     return a
    ...
    >>> foo()
    [1]
    >>> foo()
    [1, 1]
    >>> foo()
    [1, 1, 1]
```

Python creates a single list and then reuse if for every call with a default parameter. It gives us a hint why `defaultdict` accepts a factory rather than value for lists.

```python
    >>> k = []
    >>> foo(k)
    [1]
    >>> foo(k)
    [1, 1]
    >>> foo(k)
    [1, 1, 1]
    >>> k
    [1, 1, 1]
```

here we see the same patter. Now imagine that your class accepted a list and then started to modify it or share it with other methods and over time as the code evolves that list can be modified at any random point. Now when I’m thinking about it I probably should revisit some of the code.

#### **Summary**

Python is a wonderful and full of surprises and reading books like [Fluent Python by Luciano Romalho](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/) really helps to uncover unknown gems or re-discover forgotten ones.
