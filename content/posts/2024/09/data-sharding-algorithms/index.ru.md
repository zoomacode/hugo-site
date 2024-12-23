---
title: "Алгоритмы шардинга (разделения) данных"
date: 2024-09-30T17:20:24-07:00
draft: false
author: Anton Golubtsov
summary:
tags:
    - Software Development
    - Sharding
---

Я раньше работал рядом с невероятно умными людьми, которые ежедневно занимались такими вещами, как шардинг данных. У них я многому научился по этой теме. Позже я перешёл на другую роль, где эти знания не требовались, и со временем они забылись. Здесь я пытаюсь восстановить для себя эти давно забытые знания.

### Введение

Шардинг — это процесс назначения элемента конкретному шарду (разделу) — меньшему фрагменту данных из большой базы данных или другого сервиса. Основная идея заключается в том, что мы можем распределить данные или сервис по нескольким местоположениям, обрабатывать большие объёмы данных, справляться с большим количеством запросов, а с репликацией мы можем масштабироваться ещё больше и повысить отказоустойчивость системы. Однако нам нужно иметь чёткие правила, как назначать разделы (шарды), чтобы корректно перенаправлять запросы в нужное место.

Самый простой способ сделать это — взять остаток от деления идентификатора элемента (или его хэша) и использовать его в качестве идентификатора шарда:

```
shard = item.id mod M
```

где `M` — общее количество шардов. Однако у этого подхода есть недостаток: любое изменение общего количества шардов требует перемещения всех элементов в новые шарды. Это может быть приемлемо в некоторых случаях, например, при обработке данных офлайн, но при шардинге базы данных это означает, что все данные нужно перемещать с одного сервера на другой. Например, при увеличении количества шардов с 20 до 21 около 95% элементов придётся переместить.

```
affected_items_pct = shards_before / shards_after * 100
```

### Репликация

Большинство алгоритмов можно модифицировать для поддержки репликации, добавляя, например, суффикс идентификатора реплики. Этот же принцип применяется для множества сервисных узлов.

### Консистентное хеширование

Идея консистентного хеширования довольно проста. Мы берём все возможные значения хэшей узлов и элементов, размещаем их на одной линии, где 0 находится слева, а бесконечность — справа. Затем мы назначаем элемент узлу/шарду/разделу справа от элемента. Элемент назначается первому шарду, у которого `hash(shard) > hash(item)`. Но это создаёт проблему для элементов, находящихся справа от всех шардов, поэтому для них используется первый шард слева. На большинстве сайтов это описывается как круг, но мне больше нравится представлять это как линию — так понятнее.

Благодаря такой настройке при добавлении нового узла перемещается только часть элементов. На практике, чтобы процесс был ещё менее разрушительным, обычно создаётся несколько копий узла с разными хэшами, например: `hash("node-1-1")`, `hash("node-1-2")`, ..., `hash("node-1-20")`. Это создаёт набор равномерно распределённых шардов, и каждый из них принимает лишь часть изменений при перераспределении.

Минусы:

1. Необходимо знать хэши шардов, чтобы определить, к какому из них относится элемент.
2. Для равномерного распределения элементов требуется представить каждый шард около 1000 раз.

См. [Consistent hashing algorithm](https://highscalability.com/consistent-hashing-algorithm) и [оригинальную статью](https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf).

### Jump Consistent Hashing

Jump Consistent Hashing использует математическую магию[^1], чтобы "перепрыгивать" между корзинами (шардами), пока внезапно не выходит за пределы всех корзин.

```cpp
int32_t JumpConsistentHash(uint64_t key, int32_t num_buckets) {
    int64_t b = ­1, j = 0;

    while (j < num_buckets) {
        b=j;
        key = key * 2862933555777941757ULL + 1;
        j = (b + 1) * (double(1LL << 31) / double((key >> 33) + 1));
    }

    return b;
}
```

Преимущества:

1. Не нужно знать хэши шардов на каждом "балансировочном" узле.
2. Не нужно создавать 1000 виртуальных узлов для обеспечения равномерного распределения.
3. Быстрее в работе.

Как и другие алгоритмы, его можно комбинировать с репликацией, добавляя виртуальные элементы.

См. [A Fast, Minimal Memory, Consistent Hash Algorithm](https://arxiv.org/pdf/1406.2294).

### Fibonacci Hashing

Существует интересная альтернатива хешированию с использованием модуля — хеширование с использованием чисел Фибоначчи. Очень рекомендую изучить это подробнее, ознакомьтесь с примечаниями. Оно использует числа Фибоначчи для назначения шардов, но мне не удалось заставить его работать с динамическим количеством кластеров за пределами консистентного хеширования.

См. [Fibonacci Hashing: The Optimization that the World Forgot (or: a Better Alternative to Integer Modulo)](https://probablydance.com/2018/06/16/fibonacci-hashing-the-optimization-that-the-world-forgot-or-a-better-alternative-to-integer-modulo/).

### Rendezvous Hashing

Rendezvous Hashing (хеширование по принципу встречи) — интересный подход. Вы берёте ключ шарда и ключ элемента, хэшируете их вместе, повторяете для каждого узла и выбираете максимальный хэш из всех. Работает удивительно хорошо и используется в крупных корпорациях.

Недостатки:

1. Нужно знать ключи узлов.
2. В наивной реализации работает за O(n), а в менее наивной — за O(log n).

См. [Rendezvous Hashing](https://en.wikipedia.org/wiki/Rendezvous_hashing).

### Тест

Чтобы показать, как работают разные стратегии, я написал небольшой [тест](./shards.py). Он проверяет 2 вещи: равномерность распределения данных по шардам (стандартное отклонение) и стабильность назначения шардов при увеличении их числа с 20 до 21 в нашем случае. Я также добавил время выполнения для справки.

| Time (sec) | Title                              | Overlap | Shards (before) | Shards (after) | Items per shard | Items per shard (std) |
| ---------- | ---------------------------------- | ------- | --------------- | -------------- | --------------- | --------------------- |
| 0.19       | Naive modulo                       | 4.77    | 20              | 21             | 47619.05        | 156.67                |
| 0.32       | Jump consistent hashing            | 95.24   | 20              | 21             | 47619.05        | 237.10                |
| 0.80       | Fibonacci hashing                  | 4.80    | 20              | 21             | 47619.05        | 222.53                |
| 2.15       | Consistent hashing (1 replica)     | 93.71   | 20              | 21             | 47619.05        | 39882.89              |
| 2.47       | Consistent hashing (100 replicas)  | 94.68   | 20              | 21             | 47619.05        | 6105.93               |
| 2.81       | Consistent hashing (1000 replicas) | 95.25   | 20              | 21             | 47619.05        | 1227.54               |
| 29.55      | Rendezvous hashing                 | 95.28   | 20              | 21             | 47619.05        | 218.09                |

Как мы видим, консистентное хеширование действительно даёт наименее равномерное распределение данных, но при этом обеспечивает относительную стабильность назначения шардов. Надеюсь, это поможет кому-то выбрать лучший вариант для их задачи. Для меня это было упражнением по восстановлению забытых знаний.

### References

1. [Consistent hashing algorithm](https://highscalability.com/consistent-hashing-algorithm)
1. [A Fast, Minimal Memory, Consistent Hash Algorithm](https://arxiv.org/pdf/1406.2294)
1. [Consistent hashing and random trees: Distributed caching protocols for relieving hot spots on the World Wide Web](https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf)
1. [Fibonacci Hashing: The Optimization that the World Forgot (or: a Better Alternative to Integer Modulo)](https://probablydance.com/2018/06/16/fibonacci-hashing-the-optimization-that-the-world-forgot-or-a-better-alternative-to-integer-modulo/)
1. [Fibonacci Hashing from Data Structures and Algorithms with Object-Oriented Design Patterns in C++ by Bruno R. Preiss](https://book.huihoo.com/data-structures-and-algorithms-with-object-oriented-design-patterns-in-c++/html/page214.html)
1. [Scrambling Eggs for Spotify with Knuth's Fibonacci Hashing](https://pncnmnp.github.io/blogs/fibonacci-hashing.html)
1. [Rendezvous Hashing](https://en.wikipedia.org/wiki/Rendezvous_hashing)

[^1]: [Consistent hashing algorithm](https://highscalability.com/consistent-hashing-algorithm)
