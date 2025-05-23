---
title: "Вопрос на собеседовании: библиотека парсинга логов"
date: 2024-09-29T17:30:06-07:00
draft: false
author: Anton Golubtsov
summary:
tags:
    - Interview
    - Software Development
    - Code Challenges
---

Один из вопросов, которые я часто задаю на собеседованиях, - это разработка библиотеки обработки логов:

---

_Вам нужно написать библиотеку для обработки логов в следующем формате:_

```
метка_времени<TAB>сообщение
```

_Библиотека будет передана другой команде для дальнейшей поддержки и улучшений, поэтому **поддерживаемость и расширяемость являются самыми важными требованиями**._

_Библиотека должна поддерживать следующие операции "из коробки":_

-   _фильтрация_
-   _подсчет_
-   _гистограммы_

---

Первоначальная версия также включала некоторые языковые и фоновые особенности, которые я никогда не включаю в свою оценку, потому что считаю, что они ставят кандидата в положение, когда ему нужно угадать мои ожидания.

Тем не менее, есть контрольные пункты, которые кандидат должен выполнить в зависимости от роли. Эти контрольные пункты не связаны с уровнем квалификации, потому что у разных людей разный опыт, и они могут никогда не работать в среде, где выполнение всех пунктов было частью повседневной работы. Однако, чем больше пунктов выполнено, тем лучше.

#### **Контрольный пункт №1: общая структура**

В зависимости от выбранного языка программирования и используемого стиля, вы можете выбрать широкий спектр вариантов - от набора независимых функций до класса.
Ключевая цель - структура кода, которая позволяет добавлять новые функции с минимальными усилиями.

Один из простейших подходов - создать структуру, которая позволяет объединять операции в цепочку[^1], где добавление новой операции практически не требует затрат.

Есть более изящные и менее изящные способы. Это может быть генератор, который потребляет данные из генератора в Python, потоковая операция в Java, канал в Bash или функция, которая возвращает данные в том же формате, в каком получает их. Pandas DataFrame - хороший пример, большинство базовых операций с данными возвращают новый DataFrame, поэтому мы можем объединить несколько операций в одну строку.

Есть и другие способы, но цепочка ответственности, вероятно, самая простая в реализации.

#### **Контрольный пункт №2: потоковая обработка и ленивые вычисления**

В зависимости от выбранного языка программирования, реализация потоковой обработки может быть легкой или сложной, но потоковая обработка, которая часто включает фильтрацию, преобразование, может сделать ваш код более элегантным и, что важнее, более легким в поддержке. Просто посмотрите на эти примеры построения гистограммы сообщений об ошибках по метке времени:

Сначала в Bash:

```bash
grep "^2024-09-10" < file.log | grep "error message" | cut -f 1 | uniq -c | sort -nk1
```

Теперь в Java:

```java
public class LogProcessor {
    public static void main(String[] args) throws Exception {
        Files.lines(Paths.get("file.log"))
            .filter(line -> line.startsWith("2024-09-10"))
            .filter(line -> line.contains("error message"))
            .map(line -> line.split("\t")[0])  // Предполагается разделение по табуляции
            .collect(Collectors.groupingBy(s -> s, Collectors.counting()))
            .entrySet().stream()
            .sorted(Map.Entry.comparingByValue())
            .forEach(e -> System.out.println(e.getValue() + " " + e.getKey()));
    }
}
```

В C++:

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

Во всех случаях мы можем легко добавить новый фильтр или преобразование, не меняя других компонентов.

Другое преимущество написания в потоковом или функциональном стиле заключается в том, что большинство операций выполняются лениво, то есть вычисления не происходят, пока данные не будут запрошены в конце цепочки. В одном из наших проектов мы значительно сократили загрузку ЦПУ, перейдя от серии преобразований, применяемых последовательно ко всем данным, к подходу с ленивыми вычислениями. Это стало возможным, потому что нам были нужны только N верхних результатов на последнем шаге, но без ленивых вычислений мы были вынуждены обрабатывать все данные.

Таким образом, потоковая обработка и ленивые вычисления - это отличные практические методы.

#### **Контрольный пункт №3: алгоритмы**

Часто кандидаты просто реализуют гистограммы с использованием словаря счетчиков.
Это приемлемый подход во многих случаях, но построение временной гистограммы можно выполнить без дополнительного потребления памяти, если логи отсортированы по метке времени, что часто бывает. Понятно, что во время работы над общей структурой кода можно не заметить такой оптимизации. Но было бы здорово, если бы вы её заметили.

#### **Контрольный пункт №4: память**

В ходе моих собеседований я заметил, что кандидаты не особо задумываются об ограничениях реального мира и часто относятся к памяти как к неограниченному ресурсу. Они склонны создавать копию всех данных на каждом шаге, если только не используют потоковую обработку, и даже тогда не всегда. Это не было бы большой проблемой, но есть некоторое сопротивление, когда просишь кандидата уменьшить потребление памяти. Поэтому будьте внимательны к расходу памяти в вашем коде.

#### Бонус-пункт: документация

В оригинальной формулировке этот пункт был обязательным требованием, но я скажу, что если интерфейс решения понятен без документации, то она необязательна.

#### Заключение

Эта задача может показаться очень простой или очень сложной в зависимости от стиля программирования, к которому вы привыкли, но если вы знаете несколько хитростей, задача становится удивительно простой.

[^1]: [Цепочка ответственности](https://ru.wikipedia.org/wiki/Цепочка_ответственности)