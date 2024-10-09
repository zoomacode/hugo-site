---
title: "Interview Question: Logging Library"
date: 2024-09-29T17:30:06-07:00
draft: false
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

#### **Checkbox #1: overall structure**

Depends on you language of choice and the style you used to you may pick a broad variety of options from bunch of independent functions to a class.
The key goal is a code structure which allows to add new features with minimal effort.

On of the easiest approach is to create a structure which allows to combine operations into a chain[^1] of operation where adding a new operation is almost zero-cost.

There are fancy and less-fancier ways, it can be a generator which consume data from a generator in Python, a streaming operation in Java, a pipe in Bash, or a function which returns data in the same format at it receives it. Pandas dataframe is a good example, most of the basic data operations return a new dataframe so we can chain a bunch of operations in one line.

There are other ways but a chain of responsibility probably the easiest to implement.

#### **Checkbox #2: streaming and lazy evaluation**

Again depends on the language of your choice it be hard or easy
to do but streaming, which often includes things like filtering, transformation, can do your code look
better and more importantly easier to maintain. Just see this examples of building a histogram for error message per timestamp:

First in bash:

```bash
grep "^2024-09-10" < file.log | grep "error message" | cut -f 1 | uniq -c | sort -nk1
```

Now Java:

```java
public class LogProcessor {
    public static void main(String[] args) throws Exception {
        Files.lines(Paths.get("file.log"))
            .filter(line -> line.startsWith("2024-09-10"))
            .filter(line -> line.contains("error message"))
            .map(line -> line.split("\t")[0])  // Assumes tab-delimited fields
            .collect(Collectors.groupingBy(s -> s, Collectors.counting()))
            .entrySet().stream()
            .sorted(Map.Entry.comparingByValue())
            .forEach(e -> System.out.println(e.getValue() + " " + e.getKey()));
    }
}
```

In C++:

```cpp
int main() {
    std::ifstream file("file.log");
    std::map<std::string, int> counts;

    auto lines = std::ranges::istream_view<std::string>(file);

    for (const auto& key : lines
        | std::views::filter([](const std::string& s) { return s.starts_with("2024-09-10"); })
        | std::views::filter([](const std::string& s) { return s.find("error message") != std::string::npos; })
        | std::views::transform([](const std::string& s) { return s.substr(0, s.find('\t')); })) {
        counts[key]++;
    }

    std::vector<std::pair<std::string, int>> vec(counts.begin(), counts.end());
    std::ranges::sort(vec, std::less{}, &std::pair<const std::string, int>::second);

    for (const auto& [key, count] : vec) {
        std::cout << count << " " << key << '\n';
    }

    return 0;
}
```

In all cases we can easily add a new filter or transformation without changing other components.

Another benefit of writing in streaming or maybe function style is that most of the operations
are lazy so there is no computation until the data is requested on the other of the chain. On one of our
projects we significantly reduces the CPU utilization by switching from a series of transformations
applied one by one on a whole data to a lazy evaluation approach. That was possible because we needed only top-N
results out of the last steps but without lazy evaluation, we were forced to process all data.

So streaming and lazy evaluation are great practical techniques.

#### **Checkbox #3: algorithms**

Often candidates just implement histograms using a dictionary of counters.
Which is an ok approach in many cases but building a time based histogram can be done without consuming extra memory if logs are sorted by timestamp which is quite often the case. It is understandable though that
you may not notice that optimization while you were thinking about the overall code structure.
But it is great if you can.

#### **Checkbox #4: memory**

Through my interviews I've notice that the candidates are not concerned about
limitations of the physical world and often treat memory as unlimited. They tend to create a copy of the
whole data on every step, unless they use streaming but even then not always. It wouldn't be a big deal
but there is some resistance when you ask a candidate to reduce memory consumption. So be mindful for the memory consumption in your code.

#### **Bonus box: documentation**

the original wording of that task described this box as a requirement but I'd say if the interface of the solution is easy to understand without any documentation then the documentation is optional.

#### Conclusion

This task can be very simple or very challenging to you depends on the style of writing you used to but if you know a few tricks then the tasks becomes surprisingly easy one.

[^1]: [Chain of Responsibility](https://en.wikipedia.org/wiki/Chain-of-responsibility_pattern)
