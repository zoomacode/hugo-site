---
title: "Book review: Fluent Python by Luciano Romalho (Part 2)"
date: 2022-05-16T21:38:13-07:00
draft: false
summary: The second part of the book focuses on different callables. You will know about type hints for Callables, protocols, closures, decorators and other related things.
author: Anton Golubtsov
toc: true
---

## Intro

I'm continuing writing about the gems I discovered in [Fluent Python by Luciano Romalho](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/). The second part of the book called "Functions as Object" and focuses on, as you may guess, on different `Callable` and tricks around them. So buckle up.

## Docstrings are actually a thing in Python

I didn't know that but Python adds Docstrings to a function object under `__doc__` member. The `help` function uses that information to show help messages.

```python
>>> def foo(x: str) -> bool:
...     """Some description
...
...     param x, (str) some X
...
...     return (bool) result I suppose
...     """
...     return x == "YO"
...
>>> print(foo.__doc__)
Some description

    param x, (str) some X

    return (bool) result I suppose
```

## Positional and keyword-only parameters

Sometimes when your function have a lot of parameters, parameters of the same time or both, you may want to enforce Python make all parameters keyword only. Or you may want the opposite your function have one or two parameters and you don't want people to use keyword parameters. Python provides ways to do both. You can `*` into the `def` statement to tell that all parameters after the asterisk are keyword-only. Or you can add `/` after the last positional argument.

**Default setup**:

```python
>>> def foo(a,b,c):
...     print(a,b,c)
...
>>> foo(1,2,3)
1 2 3
>>> foo(c=1,b=2,a=3)
3 2 1
```

**Keyword-only arguments**:

```python
>>> def foo(a,*,b,c):
...     print(a,b,c)
...
>>> foo(1,2,3)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: foo() takes 1 positional argument but 3 were given
>>> foo(1,b=2,c=3)
1 2 3
>>> foo(a=1,b=2,c=3)
1 2 3
```

**Positional arguments**:

```python
>>> def foo(a,/,b,c):
...     print(a,b,c)
...
>>> foo(a=1,b=2,c=3)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: foo() got some positional-only arguments passed as keyword arguments: 'a'
>>> foo(1,b=2,c=3)
1 2 3
>>> foo(1,2,c=3)
1 2 3
```

**Positional and keyword-only all together**:

```python
>>> def foo(a,/,*,b,c):
...     print(a,b,c)
...
>>> foo(1,b=2,c=3)
1 2 3
>>> foo(1,2,c=3)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: foo() takes 1 positional argument but 2 positional arguments (and 1 keyword-only argument) were given
```

## The `operator` module

The [`operator`](https://docs.python.org/3/library/operator.html) module is a collection of functions which can help if you code in the function style or not. For example, it has:

-   [`itemgetter`](https://docs.python.org/3/library/operator.html#operator.itemgetter) that is an equivalent of something like `lambda obj: obj[item]` or `lambda obj: tuple(obj[item] for item in items)`;
-   [`attrgetter`](https://docs.python.org/3/library/operator.html#operator.itemgetter) that is like `itemgetter` but for class attributes;
-   [`methodcaller`](https://docs.python.org/3/library/operator.html#operator.methodcaller) that binds data to a method so you don't need to specify that data every time. Here is an example from the documentation:
    > After `f = methodcaller('name', 'foo', bar=1)`, the call `f(b)` returns `b.name('foo', bar=1)`
    > Similar method you can find similar functions [`partial`](https://docs.python.org/3/library/functools.html#functools.partial) and [`partialmethod`](https://docs.python.org/3/library/functools.html#functools.partialmethod) in the `functools` module.

The module have many other functions like `mul`, `add`, `eq`, `lt` etc. All of them you may find handy in list comprehensions, `for` loops, `sorted`, `reduce`, or somewhere else.

But I would be careful using those methods if you don't code in the functional style a lot. If those methods pop up occasionally, I would consider using `lambda` or defining a similar function next to the code that uses the function. It may reduce cognitive load to understand your code because people don't need to check documentation to understand what is going on.

## Imports from vs imports

The book suggests using `from X import Y` for `typing` module because it reduces the length of the signature. I understand that argument but at sometimes I find myself importing a bunch of types of the `typing` so I may start importing the whole module so I don't need to scroll back and forth.
But honestly I don't know what approach is better for example I appreciate when a module name is visible when you write a function name so you don't need to guess where it came from. On the other side `from X import Y` does reduce the length of calls, and signatures so maybe it is more pythonic.

## Duck-typing and C++

C++ is provably my favorite so I can't stay on track here. :smile: The book does not mention C++ as one of the languages that supports duck-typing. It is not completely true actually the whole STL library is about duck-typing, sort of. The main difference in duck-typing between Python and C++ that in Python you need to be explicit to "disable" it when in C++ you need to be explicit to enable it. In Python, we can use type hints to limit duck-typing. In C++, we can use templates to enable it. For example:

```C++
template <typename T>
void foo(T t) {
    t.method();
}

class A {
public:
    void method() { cout << "A::method()\n"; }
};

class B {
public:
    void methodB() { cout << "B::method()\n"; }
};


int main() {
    A a;
    B b;

    foo(a);
}
```

This will work just fine but if you try to use `foo(b)` instead of `foo(a)` then you will get something like this at the compile time:

```log
 In function 'int main()':
22:7: warning: unused variable 'a' [-Wunused-variable]
 In instantiation of 'void foo(T) [with T = B]':
25:10:   required from here
7:5: error: 'class B' has no member named 'method'
```

You can try the code [here](cpp.sh/7pmck3).

## Ellipsis and unbounded tuples

There were a few time when I needed to specify a type hint for a tuple unknown length. In some cases, I decided to use `list[str]`, in some cases I decided to use tuple but without specifying the type of the elements.
But there is a better way - ellipsis. You can use ellipsis when you need to annotate a tuple of something without specifying its length.

```python
def foo(t: tuple[str, ...]):
    print(t)
```

## Walrus operator

Walrus operator `:=` or _assignment expression_ is syntax sugar that creates a variable in the middle of a larger expression and that variable can be used right away. For example, you need to compute some value checks its value in an `if` statement and then do something with results without `:=` you need assign the results of the expression to a temporary variable then use in the `if` statement. This is an example from [PEP-572](https://peps.python.org/pep-0572/):

```python
match1 = pattern1.match(data)
match2 = pattern2.match(data)
if match1:
    result = match1.group(1)
elif match2:
    result = match2.group(2)
else:
    result = None
```

With the walrus operator the example can be simplified to this:

```python
if match1 := pattern1.match(data):
    result = match1.group(1)
elif match2 := pattern2.match(data):
    result = match2.group(2)
else:
    result = None
```

You can use in list comprehensions, `if` statements, `for` loops and ,it is probably not the best idea but, even as a part of variable declaration. See [PEP-572](https://peps.python.org/pep-0572/) for more details.

## The `collection.abc` module

There are cases when you may want to annotate a type but you want to leave some room for duck-typing. For example, you created a function that works with anything that looks like a dictionary. You can use `Union[dict, defaultdict, OrederedDict]` but it will not any or user types that behaves like a dictionary. Module [`collection.abc`](https://docs.python.org/3/library/collections.abc.html), abc stands for Abstract Base Classes, provides a set of abstract types that can help with it. For example, it provides `Callable`, `Iterable`, `Sequence`, `Mapping` and many more types. So instead of `def foo(l: List[str])` you can write `def foo(l: Sequence[str])` or instead of `def foo(d: Dict[str, str])` you can use `def foo(d: Mapping[str, str])`.

And by the way `typing.Dict` is a legacy since Python 3.10. You can use regular `dict` instead.

## Static Protocols

Python support generic types in type hints, for example, we have a generic function that works any iterable of object that have a certain method. How do we annotate that function?

First of all, we can use [`TypeVar`](https://docs.python.org/3/library/typing.html#typing.TypeVar) to specify all types a base class or a list of allowed classes. Here is an example from the official documentation:

```python
S = TypeVar('S', bound=str)  # Can be any subtype of str
A = TypeVar('A', str, bytes)  # Must be exactly str or bytes

def print_capitalized(x: S) -> S:
    """Print x capitalized, and return x."""
    print(x.capitalize())
    return x


def concatenate(x: A, y: A) -> A:
    """Add two strings or bytes objects together."""
    return x + y
```

The problem with it that we need either a super class or a list of allowed types when we actually need a way to describe a class with specific properties. [PEP-544](https://peps.python.org/pep-0544/) introduces _protocols_. A protocol describes a class or a function without implementing it.

For example:

```python
from typing import Iterator, Iterable

class Bucket:
    ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[int]: ...

def collect(items: Iterable[int]) -> int: ...
result: int = collect(Bucket())  # Passes type check
```

Here we described a class that has at least `__len__` and `__iter__` methods and a function that accepts iterables. `collect(Bucket())` passes type check because `Bucket` has `__iter__` method and it makes `Bucket` iterable.
The ellipsis here just says that the code is only a declaration not a definition.

## Closures and nonlocal

Imagine that we need a way to count the number of function calls, store results in some hidden container of or something like that. Without closures, we would use a class or a global variable:

```python
class A:
    def __init__(self):
        self.count = 0

    def __call__(self, data):
        # do some work here
        self.count += 1
```

The class behaves like this:

```python
>>> a = A()
>>> a(1)
>>> a(100)
>>> a.count
2
```

With closures we can simplify it to:

```python
>>> def create():
...     data = []
...     def do(d):
...         data.append(d)
...         return data
...     return do
...
>>> a = create()
>>> a(1)
[1]
>>> a(2)
[1, 2]
>>> a(1)
[1, 2, 1]
```

As we can see the `data` is available even when the scope of the `create` function is not longer available. But here is the trick, if we change data to a counter we will get something like this:

```python
UnboundLocalError: local variable 'counter' referenced before assignment
```

It is because of the way how Python resolve variable names. It starts from the local scope when extends to global scope. But it works only if we don't replace the object and since `int`, `float`, `str`, `tuple` are immutable, Python replaces them every time we change them.

```python
>>> a = 1
>>> id(a)
4323518768
>>> a +=1
>>> id(a)
4323518800
>>> b = []
>>> b.append(2)
>>> id(b)
4324554368
>>> b.append(5)
>>> id(b)
4324554368
```

As we can see `a`'s object id changes with each increment when `b`'s id remains the same. Python basically don't look outside of the local scope if we change a variable. To extend variable lookup scope Python has two key words `global` and `nonlocal`. The first one tells to lookup in the global scope the second one tells to extend the scope to the nearest non-global scope. For example:

```python
>>> def create():
...     counter = 0
...     def do():
...         nonlocal counter
...         counter +=1
...         return counter
...     return do
...
>>> a = create()
>>> a()
1
>>> a()
2
```

Interestingly, in the [Fluent Python](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/) book I saw the simplest definition of closures so far.

> a closure is a function that remains the bindings of the free variables that exist when the function is defined, so that they can be used later later when the function is invoked and the definition scope is no longer available.

It was of course carefully introduced by an example and longer introduction but it is the first time when it clicked. Interestingly I used closures before without knowing it in C++. C++11 introduced lambda expressions that allows to specify what variable to capture and how.

## Decorators

As you probably know decorators allows to extend an object behavior without modifying the object itself.
Here I'm just sharing interesting thing about the decorators.

### Caching

I occasionally interview candidates for software engineer role in Amazon. At the problem solving section I usually ask
a question where at some point the candidate may suggest using caching. Implementing cache or LRU cache can be tricky especially if you have limited time. So I was surprised to discover that Python provides caching decorators in the standard library. They are [`functools.cache`](https://docs.python.org/3/library/functools.html#functools.cache) and [`functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache). Here are just a few examples from the documentation.

Simple caching

```python
@cache
def factorial(n):
    return n * factorial(n-1) if n else 1

>>> factorial(10)      # no previously cached result, makes 11 recursive calls
3628800
>>> factorial(5)       # just looks up cached value result
120
>>> factorial(12)      # makes two new recursive calls, the other 10 are cached
479001600
```

LRU cache:

```python
@lru_cache(maxsize=32)
def get_pep(num):
    'Retrieve text of a Python Enhancement Proposal'
    resource = 'https://www.python.org/dev/peps/pep-%04d/' % num
    try:
        with urllib.request.urlopen(resource) as s:
            return s.read()
    except urllib.error.HTTPError:
        return 'Not Found'

>>> for n in 8, 290, 308, 320, 8, 218, 320, 279, 289, 320, 9991:
...     pep = get_pep(n)
...     print(n, len(pep))

>>> get_pep.cache_info()
CacheInfo(hits=3, misses=8, maxsize=32, currsize=8)
```

The module also have a nice [`cached_property`](https://docs.python.org/3/library/functools.html#functools.cached_property) which helps to memoize heavy lifting methods.

### Functions overloading

Python does not support function overloading but we can always create a dispatcher function that checks types of the arguments and calls a type specific implementation. The same `functools` module has a partial solution for functions overloading - [`functools.singledispatch`](https://docs.python.org/3/library/functools.html#functools.singledispatch). `singledispatch` is a decorator that returns a generic dispatcher that provides a method for registering type specific implementations.

An example from the documentation:

```python
>>> from functools import singledispatch
>>> @singledispatch
... def fun(arg, verbose=False):
...     if verbose:
...         print("Let me just say,", end=" ")
...     print(arg)
>>> @fun.register
... def _(arg: int, verbose=False):
...     if verbose:
...         print("Strength in numbers, eh?", end=" ")
...     print(arg)
...
>>> fun("Hello, world.")
Hello, world.
>>> fun("test.", verbose=True)
Let me just say, test.
>>> fun(42, verbose=True)
Strength in numbers, eh? 42
```

Unfortunately `singledispatch` uses only the first argument for dispatching but it s probably enough for 99% of use-cases.

## Summary

The second part of the book ushers us through the wonderful world of callables. It starts from seemingly unrelated things like type hints but each piece of the puzzle contributes to the whole picture. And in the end you starts seeing connections between different parts and then at some point it just clicks: "Oh. Wow. Now I see. Now, I get it". For example, I wrote just a few decorators in my career some of them were quite simple some of them were more complex. For the more complex cases I often were a bit confused by how all that magic works. The book showed how closures help to build decorators and decorator actually do. The book showed a few neat tricks like caching, registers, and dispatchers. Also is a also huge fan of type hints I appreciate the level of details the provides on that topic.

I want to mention protocols as well. I always had that concern that I can't use type hints for [`boto3`](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) client classes because there are no public client classes in `boto3`. Hence I couldn't use type hints in my code, which actually led to a few bug in production, with protocols I can finally create definitions for the clients I use so I can check if the clients are called correctly.

In my opinion, [Fluent Python by Luciano Romalho](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/) is definitely worth spending $55 even if you stop reading the book after the part two. Must read.
