---
title: "Book review: Fluent Python by Luciano Romalho (Part 2)"
date: 2022-05-12T21:38:13-07:00
draft: true
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

Add by the way `typing.Dict` is a legacy since Python 3.10. You can use regular `dict` instead.
