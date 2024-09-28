---
title: "Interview Question Logging Library"
date: 2024-09-29T17:30:06-07:00
draft: true
author: Anton Golubtsov
summary:
tags:
    - Interview
    - Software Development
    - Code Challenges
---

One of the question I often ask in my interview is to design a log processing library:

---

_You need to write a library for processing logs in the following format:_

```
timestamp<TAB>message
```

_The library will be handed over to a different team for further maintenance and improvements and so **maintainability and expandability is the most most important requirements**._

_The library need to support the following operations out of the box:_

-   _filtering_
-   _counting_
-   _histograms_

---

The original version also included some language and background specific expectations I never include in my assessment because I feel that they put the candidate into a position when they need to read my mind to meet those expectations.

Nonetheless, there are checkboxes a candidate needs to hit depends on a role. The checkboxes are not associated with any seniority level because different people have different experience and might never work in an environment where hitting all checkbox was a part of the daily job. However, the more boxes are hit, the better.

**Checkbox #1: overall structure** Depends on you language of choice and the style you used to you may pick a broad variety of options from bunch of independent functions to a class.
The key goal is a code structure which allows to add new features with minimal effort.

On of the easiest approach is to create a structure which allows to combine operations into a chain[^1] of operation where adding a new operation is almost zero-cost.

There are fancy and less-fancier ways, it can be a generator which consume data from a generator in Python, a streaming operation in Java, a pipe in Bash, or a function which returns data in the same format at it receives it. Pandas dataframe is a good example, most of the basic data operations return a new dataframe so we can chain a bunch of operations in one line.

There are other ways but a chain of responsibility probably the easiest to implement.

**Checkbox #2: streaming and lazy evaluation**

**Checkbox #3: algorithms**

**Checkbox #4: memory**

**Bonus box: documentation** the original wording of that task described this box as a requirement but I'd say if the interface of the solution is easy to understand without any documentation then the documentation is optional.

---

**_Footnotes_**:
[^1] [Chain of Responsibility](https://en.wikipedia.org/wiki/Chain-of-responsibility_pattern)
