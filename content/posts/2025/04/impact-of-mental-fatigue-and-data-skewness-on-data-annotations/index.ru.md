---
title: "Влияние умственного утомления, монотонности задач и перекоса данных на эффективность аннотаторов"
date: 2025-04-11T21:12:19-07:00
draft: true
author: Anton Golubtsov
summary:
tags:
    - DeepResearch
    - Gemini
    - Data Annotation
---

# Введение

Существует две темы, о которых редко говорят, когда речь заходит об аннотировании данных.  
Во‑первых, аннотаторы — это не просто «инструменты», которые нужно обучать и чью работу следует неустанно контролировать; это обычные люди, такие же, как мы с вами: они могут уставать или отвлекаться.  
Во‑вторых, на их работу влияет сам набор данных, который мы им предлагаем.

Я испытываю сострадание и глубокое уважение к аннотаторам, с которыми работаю каждый день, поэтому давно хотел затронуть эту тему, но не находил времени и ресурсов для полноценного исследования. С помощью ИИ и благодаря учёным, уже проделавшим основную работу, я могу хотя бы поделиться кратким обзором.

Я перечитал сгенерированный текст и убедился, что он выражает именно то, что хотел сказать.

Если вам лень читать, можно послушать:  
{{< audio "Decoding AIs Human Heart_ Fatigue Boredom and Biased Data.mp3" >}}

---

## **Введение: ключевая роль аннотирования данных и влияние человеческого фактора**

Аннотирование данных является краеугольным камнем при разработке и внедрении моделей искусственного интеллекта (ИИ) и машинного обучения (МО).[^1] Этот процесс, заключающийся в разметке сырых данных, делает их понятными для алгоритмов и критически важен для обучения моделей, способных точно распознавать шаблоны, делать предсказания и извлекать инсайты. Качество аннотаций напрямую определяет точность, надёжность и итоговую эффективность систем ИИ и МО.[^1] Плохая разметка, напротив, вводит предвзятость, снижает точность и ведёт к пустой трате ресурсов.[^1]

Хотя внимание часто сосредоточено на алгоритмической стороне, человеческий фактор играет незаменимую роль.[^1] Когнитивное состояние аннотатора, характер выполняемых задач и свойства самих данных существенно влияют на качество и скорость разметки. Поэтому учёт этих факторов критически важен для оптимизации процессов и получения высококачественных обучающих выборок. Масштабирование ИИ‑проектов лишь усиливает необходимость поддерживать целостность и надёжность аннотаций.[^1]

## **Определение проблем**

### **Умственное утомление при когнитивных задачах: сущность и особенности**

Умственное утомление — это психобиологическое состояние, возникающее при длительной умственной нагрузке.[^73] Оно характеризуется субъективным чувством усталости и нехваткой энергии.[^82] Даже 10‑минутные сложные задания могут вызвать утомление,[^83] влияя на последующие когнитивные и физические показатели.[^73] Симптомы включают сложности с концентрацией,[^89] забывчивость,[^89] рост числа ошибок[^89] и замедление работы.[^89] Возможны раздражительность, апатия, головные боли и проблемы с желудком.[^85][^90]

Важно отличать утомление от стресса: стресс вызывается угрозой и сопровождается гормональной реакцией «бей или беги», тогда как утомление — результат истощения умственных ресурсов.[^73] Нейрофизиологически оно связано с изменениями активности в передней поясной коре.[^84]

**Таблица 1. Симптомы умственного утомления**

| Симптом                              | Описание                                                          | Источник |
| :----------------------------------- | :---------------------------------------------------------------- | :------- |
| Трудности с концентрацией            | Снижение способности удерживать внимание.                         | [^89]    |
| Забывчивость                         | Повышенная склонность к ошибкам памяти.                           | [^89]    |
| Увеличение числа ошибок              | Более частые промахи при выполнении заданий.                      | [^89]    |
| Сложность удерживать фокус           | Трудно долго следить за задачей, принимать решения, вести беседу. | [^89]    |
| Удлинение времени выполнения         | На привычные задания требуется больше времени.                    | [^89]    |
| Снижение способности к решению задач | Сложнее мыслить критически и решать проблемы.                     | [^89]    |
| Снижение креативности                | Меньше новых идей и оригинальных решений.                         | [^89]    |
| Лёгкая отвлекаемость                 | Повышенная чувствительность к внешним раздражителям.              | [^90]    |
| Проблемы с рабочей памятью           | Трудности удерживать и манипулировать информацией в уме.          | [^90]    |
| Раздражительность                    | Лёгкая возбудимость и раздражение.                                | [^90]    |
| Трудно завершать задачи              | Ранее лёгкие задания даются тяжело.                               | [^90]    |
| Ухудшение психического здоровья      | Общее снижение благополучия.                                      | [^90]    |
| Сложность управлять эмоциями         | Трудно адекватно регулировать чувства.                            | [^90]    |
| Чувство опустошённости               | Ощущение полного истощения ресурсов.                              | [^90]    |
| Апатия                               | Отсутствие интереса и энтузиазма.                                 | [^90]    |
| Головные боли                        | Болевые ощущения в области головы.                                | [^85]    |
| Желудочные проблемы                  | Дискомфорт или боли в животе.                                     | [^90]    |
| Снижение бодрствования               | Меньшая бдительность и внимательность.                            | [^91]    |
| Падение мотивации                    | Меньшее желание заниматься задачами.                              | [^91]    |
| Вялость                              | Состояние сонливости и недостатка энергии.                        | [^91]    |
| Трудность формулировать мысли        | Сложно связно выражать идеи.                                      | [^91]    |

### **Монотонные задачи: влияние на вовлечённость и результативность**

Долгая работа с повторяющимися заданиями приводит к снижению внимания[^93], росту ошибок[^93] и падению мотивации.[^93] Монотонность вызывает скуку[^95], неудовлетворённость работой[^95] и даже проблемы со здоровьем.[^95] Парадоксально, но в начале производительность может расти из‑за снижения затрат на переключение контекста[^99]; затем она стабилизируется или падает, а психологическая нагрузка возрастает.[^99] В задачах бдительности ухудшение точности и времени реакции может наступать уже через несколько минут.[^101]

### **Перекос распределения данных: последствия для точности и согласованности**

В реальных проектах данные часто несбалансированы: один класс значительно преобладает.[^105] Это усложняет обучение моделей и снижает качество разметки редких классов.[^19] Аннотаторам сложнее выработать уверенность в редких категориях, что ведёт к ошибкам и низкому межаннотаторному соглашению (IAA).[^112] При этом общая точность модели может вводить в заблуждение, так как отражает успех лишь на большинстве.[^107]

## **Влияние на работу аннотаторов**

### **Умственное утомление и точность классификации**

Утомление снижает способность фильтровать лишнюю информацию, обрабатывать данные и удерживать внимание.[^73] С ростом усталости увеличивается число ошибок[^88] и время реакции.[^117] Даже при сознательном усилии удерживать уровень работы скрытые когнитивные процессы ухудшаются, что видно по изменениям ERP‑компонент N1 и P3.[^120]

### **Повторяемость задач, ошибки и внимание**

Монотонные задания быстро приводят к снижению бдительности и росту ошибок.[^93] Недостаток стимуляции вызывает «когнитивную недогрузку», когда система внимания переключается в пассивный режим.[^101] Введение большей вариативности или повышение сложности помогает смягчить эффект.[^104]

### **Согласованность и предвзятость при перекосе данных**

При сильном перекосе аннотаторы легко согласуются на большинстве, но расходятся на меньшинстве.[^112] Это ведёт к неустойчивой разметке и усилению смещений.[^19] Ошибки чаще встречаются в редких классах, а модели наследуют эти перекосы.[^115]

## **Оценка влияния**

-   **Умственное утомление**: опросники (KSS), метрики реакции/точности, физиология (ЭЭГ, трекинг глаз), задачи типа антисакад.[^73]
-   **Монотонность**: рост ошибок, замедление реакции, субъективные отчёты о скуке, сравнение с более вариативными задачами.[^101]
-   **Перекос данных**: анализ IAA по классам, распределение ошибок, метрики precision/recall/F1 для каждого класса, сравнение на сбалансированных поднаборах.[^3]

## **Стратегии смягчения и оптимизации**

### **Борьба с умственным утомлением**

-   Регулярные перерывы.[^24]
-   Ротация задач и разнообразие.[^25]
-   Эргономичное рабочее место.[^39]
-   Поддержка здоровых привычек (сон, питание, спорт).[^\70]
-   Корректировка формы подачи данных (размер, формат) при усталости.[^71]

### **Снижение негативного эффекта монотонности**

-   Ротация и микротаски.[^25]
-   Геймификация и система поощрений.[^22]
-   Лёгкое повышение когнитивной сложности.[^104]
-   Чёткие гайдлайны, обратная связь и фильтры в инструментах.[^19][^25]
-   Автоматизация рутинных частей (AI‑ассист).[^15]

### **Работа с перекошенными данными**

-   Сбалансированная выборка (over/undersampling).[^19]
-   Расширенные инструкции и примеры для меньшинства.[^1]
-   Генерация синтетических данных или аугментация.[^19]
-   Стоимостно‑чувствительное обучение и стратифицированная выборка.[^105]
-   Ансамблевые методы на этапе моделирования.[^105]

### **Ясные инструкции и механизмы обратной связи**

Подробные, иллюстрированные гайдлайны минимизируют разночтения.[^1] Регулярная обратная связь и обновление правил по итогам аудитов и анализа ошибок поддерживают качество.[^3][^1]

### **Автоматизация и AI‑инструменты**

Предразметка простых случаев, выявление аномалий и активное обучение (active learning) повышают эффективность и снижают нагрузку на людей.[^19][^10]

## **Рекомендации**

-   Проектируйте рабочие процессы с перерывами, ротацией и микротасками.
-   Внедряйте систему контроля качества, метрики IAA и циклы обратной связи.
-   Поддерживайте мотивацию через обучение, признание достижений и справедливую оплату.

## **Заключение: путь к высококачественной разметке через человеко‑центричный дизайн**

Качество аннотаций критично для успеха ИИ‑систем и во многом определяется человеческими факторами: усталостью, монотонностью и перекосом данных. Комплексные стратегии, ориентированные на благополучие аннотаторов и сбалансированность данных, помогают минимизировать ошибки и создавать надёжные обучающие выборки.

#### **Использованная литература**

[^1]: Avoiding Common Pitfalls in Data Annotation \- Labelvisor, accessed April 11, 2025, [https://www.labelvisor.com/avoiding-common-pitfalls-in-data-annotation/](https://www.labelvisor.com/avoiding-common-pitfalls-in-data-annotation/)
[^2]: Why Quality Dataset Annotation Is Key to Machine Learning \- Voxel51, accessed April 11, 2025, [https://voxel51.com/resources/learn/why-quality-dataset-annotation-is-key-to-machine-learning/](https://voxel51.com/resources/learn/why-quality-dataset-annotation-is-key-to-machine-learning/)
[^3]: Ensuring Quality in Data Annotation \- Keymakr, accessed April 11, 2025, [https://keymakr.com/blog/ensuring-quality-in-data-annotation/](https://keymakr.com/blog/ensuring-quality-in-data-annotation/)
[^4]: What is Data Annotation: A Basic to Advanced Guide for 2025 \- Shaip, accessed April 11, 2025, [https://www.shaip.com/blog/the-a-to-z-of-data-annotation/](https://www.shaip.com/blog/the-a-to-z-of-data-annotation/)
[^5]: The Impact of Quality Data Annotation on Machine Learning Model Performance \- Datafloq, accessed April 11, 2025, [https://datafloq.com/read/the-impact-of-quality-data-annotation-on-machine-learning-model-performance/](https://datafloq.com/read/the-impact-of-quality-data-annotation-on-machine-learning-model-performance/)
[^6]: Data annotation guidelines and best practices \- Snorkel AI, accessed April 11, 2025, [https://snorkel.ai/blog/data-annotation/](https://snorkel.ai/blog/data-annotation/)
[^7]: Data Labeling: What Factors To Consider With The Most Impact | Keylabs, accessed April 11, 2025, [https://keylabs.ai/blog/what-is-data-labeling-and-how-to-use-it-to-create-specialized-answers-and-predictions/](https://keylabs.ai/blog/what-is-data-labeling-and-how-to-use-it-to-create-specialized-answers-and-predictions/)
[^8]: Mastering data labeling for ML: A comprehensive guide \- CloudFactory, accessed April 11, 2025, [https://www.cloudfactory.com/data-labeling-guide](https://www.cloudfactory.com/data-labeling-guide)
[^9]: The Building Blocks of an Efficient Data Labeling Process \- Label Studio, accessed April 11, 2025, [https://labelstud.io/blog/the-building-blocks-of-an-efficient-data-labeling-process/](https://labelstud.io/blog/the-building-blocks-of-an-efficient-data-labeling-process/)
[^10]: Improving Data Quality With an Efficient Data Labeling Process \- Dataiku blog, accessed April 11, 2025, [https://blog.dataiku.com/improving-data-quality-with-an-efficient-data-labeling-process](https://blog.dataiku.com/improving-data-quality-with-an-efficient-data-labeling-process)
[^11]: Data labeling: why it is important to manage it efficiently \- Labellerr, accessed April 11, 2025, [https://www.labellerr.com/blog/data-labeling-why-it-is-important-to-manage-it-efficiently/](https://www.labellerr.com/blog/data-labeling-why-it-is-important-to-manage-it-efficiently/)
[^12]: Master data annotation: Tools, tips, and best practices \- Viam, accessed April 11, 2025, [https://www.viam.com/post/data-annotation-machine-learning](https://www.viam.com/post/data-annotation-machine-learning)
[^13]: Unlocking Data Annotation: Best Practices Guide \- Keymakr, accessed April 11, 2025, [https://keymakr.com/blog/unlocking-data-annotation-best-practices-guide/](https://keymakr.com/blog/unlocking-data-annotation-best-practices-guide/)
[^14]: A Beginner's Guide to Data Annotation: Tips and Best Practices \- Springbord, accessed April 11, 2025, [https://www.springbord.com/blog/beginners-guide-to-data-annotation-tips-and-best-practices/](https://www.springbord.com/blog/beginners-guide-to-data-annotation-tips-and-best-practices/)
[^15]: The Full Guide to Automated Data Annotation \- Encord, accessed April 11, 2025, [https://encord.com/blog/automated-data-annotation-guide/](https://encord.com/blog/automated-data-annotation-guide/)
[^16]: Best Practices for Managing Data Annotation Projects : r/MachineLearning \- Reddit, accessed April 11, 2025, [https://www.reddit.com/r/MachineLearning/comments/izjhwm/best_practices_for_managing_data_annotation/](https://www.reddit.com/r/MachineLearning/comments/izjhwm/best_practices_for_managing_data_annotation/)
[^17]: Best Practices for Managing Data Annotation Projects \- Bloomberg Professional Services, accessed April 11, 2025, [https://assets.bbhub.io/company/sites/40/2020/09/Annotation-Best-Practices-091020-FINAL.pdf](https://assets.bbhub.io/company/sites/40/2020/09/Annotation-Best-Practices-091020-FINAL.pdf)
[^18]: The influence of data annotation process requirements on performance criteria of ML models \- GUPEA, accessed April 11, 2025, [https://gupea.ub.gu.se/bitstream/handle/2077/77954/CSE%2023-02%20MA%20MM.pdf?sequence=1\&isAllowed=y](https://gupea.ub.gu.se/bitstream/handle/2077/77954/CSE%2023-02%20MA%20MM.pdf?sequence=1&isAllowed=y)
[^19]: Top Challenges in Data Annotation And How To Overcome Them \- Labellerr, accessed April 11, 2025, [https://www.labellerr.com/blog/how-to-overcome-challenges-in-data-annotation/](https://www.labellerr.com/blog/how-to-overcome-challenges-in-data-annotation/)
[^20]: 5 Ways to Improve The Quality of Labeled Data | Encord, accessed April 11, 2025, [https://encord.com/blog/improve-quality-of-labeled-data-guide/](https://encord.com/blog/improve-quality-of-labeled-data-guide/)
[^21]: Data Labeling: The Authoritative Guide \- Scale AI, accessed April 11, 2025, [https://scale.com/guides/data-labeling-annotation-guide](https://scale.com/guides/data-labeling-annotation-guide)
[^22]: Building Annotation Performance Dashboards | Keymakr, accessed April 11, 2025, [https://keymakr.com/blog/building-annotation-performance-dashboards-for-continuous-improvement/](https://keymakr.com/blog/building-annotation-performance-dashboards-for-continuous-improvement/)
[^23]: Looking out for the humans in AI & Data Annotation \- Mindkosh AI, accessed April 11, 2025, [https://mindkosh.com/blog/looking-out-for-the-humans-in-ai-data-annotation/](https://mindkosh.com/blog/looking-out-for-the-humans-in-ai-data-annotation/)
[^24]: Mental fatigue in cybersecurity defense \- RangeForce, accessed April 11, 2025, [https://www.rangeforce.com/blog/mental-fatigue-in-cybersecurity-defense](https://www.rangeforce.com/blog/mental-fatigue-in-cybersecurity-defense)
[^25]: 10 Tips to Supercharge Your Data Labeling Efficiency | HumanSignal, accessed April 11, 2025, [https://humansignal.com/blog/10-tips-to-supercharge-your-data-labeling-efficiency/](https://humansignal.com/blog/10-tips-to-supercharge-your-data-labeling-efficiency/)
[^26]: Challenges In Data Annotation And How To Overcome Them \- Techasoft, accessed April 11, 2025, [https://www.techasoft.com/post/challenges-in-data-annotation-and-how-to-overcome-them](https://www.techasoft.com/post/challenges-in-data-annotation-and-how-to-overcome-them)
[^27]: Best Practices for Managing Data Annotation Projects \- Kili Technology, accessed April 11, 2025, [https://kili-technology.com/data-labeling/best-practices-for-managing-data-annotation-projects](https://kili-technology.com/data-labeling/best-practices-for-managing-data-annotation-projects)
[^28]: How to Understand and Improve the Quality of Annotated Data \- Scale AI, accessed April 11, 2025, [https://scale.com/blog/improve-data-annotation](https://scale.com/blog/improve-data-annotation)
[^29]: The Impact of Unrepresentative Data on AI Model Biases, accessed April 11, 2025, [https://www.anolytics.ai/blog/the-impact-of-unrepresentative-data-on-ai-model-biases/](https://www.anolytics.ai/blog/the-impact-of-unrepresentative-data-on-ai-model-biases/)
[^30]: Elevating Data Quality: The Crucial Role of Proper Data Annotation \- Cleanlab, accessed April 11, 2025, [https://cleanlab.ai/blog/learn/data-annotation/](https://cleanlab.ai/blog/learn/data-annotation/)
[^31]: Annotation fatigue: Why human data quality declines over time \- Pareto.AI, accessed April 11, 2025, [https://pareto.ai/blog/annotation-fatigue](https://pareto.ai/blog/annotation-fatigue)
[^32]: The impact of inconsistent human annotations on AI driven clinical decision making \- PMC, accessed April 11, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC9944930/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9944930/)
[^33]: Active Label Refinement for Robust Training of Imbalanced Medical Image Classification Tasks in the Presence of High Label Noise, accessed April 11, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC11981598/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11981598/)
[^34]: Challenges In Data Labeling \- FasterCapital, accessed April 11, 2025, [https://fastercapital.com/topics/challenges-in-data-labeling.html](https://fastercapital.com/topics/challenges-in-data-labeling.html)
[^35]: Minority Class Oriented Active Learning for Imbalanced Datasets \- ResearchGate, accessed April 11, 2025, [https://www.researchgate.net/publication/358291229_Minority_Class_Oriented_Active_Learning_for_Imbalanced_Datasets](https://www.researchgate.net/publication/358291229_Minority_Class_Oriented_Active_Learning_for_Imbalanced_Datasets)
[^36]: Error Handling in Data Annotation Pipelines \- clickworker.com, accessed April 11, 2025, [https://www.clickworker.com/customer-blog/error-handling-in-data-annotation-pipelines/](https://www.clickworker.com/customer-blog/error-handling-in-data-annotation-pipelines/)
[^37]: Explanation of Annotation Error Analysis | Sapien's AI Glossary, accessed April 11, 2025, [https://www.sapien.io/glossary/definition/annotation-error-analysis](https://www.sapien.io/glossary/definition/annotation-error-analysis)
[^38]: Things that Can go Wrong During Annotation and How to Avoid Them \- Kili Technology, accessed April 11, 2025, [https://kili-technology.com/data-labeling/things-that-can-go-wrong-during-annotation-and-how-to-avoid-them](https://kili-technology.com/data-labeling/things-that-can-go-wrong-during-annotation-and-how-to-avoid-them)
[^39]: How Stressful/Tiring is Data Annotation Compared To a 9/5? \- Reddit, accessed April 11, 2025, [https://www.reddit.com/r/DataAnnotationTech/comments/1gkkrfp/how_stressfultiring_is_data_annotation_compared/](https://www.reddit.com/r/DataAnnotationTech/comments/1gkkrfp/how_stressfultiring_is_data_annotation_compared/)
[^40]: Annotator in the Loop: A Case Study of In-Depth Rater Engagement to Create a Bridging Benchmark Dataset \- arXiv, accessed April 11, 2025, [https://arxiv.org/html/2408.[^00880]v1](https://arxiv.org/html/2408.00880v1)
[^41]: Career Development in Data Annotation 2024 \- Ubiai, accessed April 11, 2025, [https://ubiai.tools/career-development-in-data-annotation/](https://ubiai.tools/career-development-in-data-annotation/)
[^42]: Unveiling the Crucial Role of Data Annotators in AI Projects \- Labelvisor, accessed April 11, 2025, [https://www.labelvisor.com/unveiling-the-crucial-role-of-data-annotators-in-ai-projects/](https://www.labelvisor.com/unveiling-the-crucial-role-of-data-annotators-in-ai-projects/)
[^43]: Annotation Sensitivity: Training Data Collection Methods Affect Model Performance \- arXiv, accessed April 11, 2025, [https://arxiv.org/html/2311.14212v2](https://arxiv.org/html/2311.14212v2)
[^44]: Quality aspects of annotated data: A research synthesis \- ResearchGate, accessed April 11, 2025, [https://www.researchgate.net/publication/375974210_Quality_aspects_of_annotated_data_A_research_synthesis](https://www.researchgate.net/publication/375974210_Quality_aspects_of_annotated_data_A_research_synthesis)
[^45]: Task Configuration Impacts Annotation Quality and Model Training Performance in Crowdsourced Image Segmentation \- CVF Open Access, accessed April 11, 2025, [https://openaccess.thecvf.com/content/WACV2025/papers/Bauchwitz_Task_Configuration_Impacts_Annotation_Quality_and_Model_Training_Performance_in_WACV_2025_paper.pdf](https://openaccess.thecvf.com/content/WACV2025/papers/Bauchwitz_Task_Configuration_Impacts_Annotation_Quality_and_Model_Training_Performance_in_WACV_2025_paper.pdf)
[^46]: Active Learning with a Noisy Annotator | AI Research Paper Details \- AIModels.fyi, accessed April 11, 2025, [https://www.aimodels.fyi/papers/arxiv/active-learning-noisy-annotator](https://www.aimodels.fyi/papers/arxiv/active-learning-noisy-annotator)
[^47]: Analyzing Dataset Annotation Quality Management in the Wild \- MIT Press Direct, accessed April 11, 2025, [https://direct.mit.edu/coli/article/50/3/817/120233/Analyzing-Dataset-Annotation-Quality-Management-in](https://direct.mit.edu/coli/article/50/3/817/120233/Analyzing-Dataset-Annotation-Quality-Management-in)
[^48]: Modeling and mitigating human annotation errors to design efficient stream processing systems with human-in-the-loop machine learning \- NSF Public Access Repository, accessed April 11, 2025, [https://par.nsf.gov/servlets/purl/10323612](https://par.nsf.gov/servlets/purl/10323612)
[^49]: arXiv:2311.00619v3 \[cs.LG\] 4 Jun 2024, accessed April 11, 2025, [https://arxiv.org/pdf/2311.00619](https://arxiv.org/pdf/2311.00619)
[^50]: Optimizing Microtasking for Data Annotation \- Labelvisor, accessed April 11, 2025, [https://www.labelvisor.com/designing-microtasks-breaking-down-annotation-jobs-for-faster-completion/](https://www.labelvisor.com/designing-microtasks-breaking-down-annotation-jobs-for-faster-completion/)
[^51]: Balancing Speed and Quality in Data Annotation | The AI Journal, accessed April 11, 2025, [https://aijourn.com/balancing-speed-and-quality-in-data-annotation/](https://aijourn.com/balancing-speed-and-quality-in-data-annotation/)
[^52]: Closing the Knowledge Gap in Designing Data Annotation Interfaces for AI-powered Disaster Management Analytic Systems \- arXiv, accessed April 11, 2025, [https://arxiv.org/html/2403.01722v1](https://arxiv.org/html/2403.01722v1)
[^53]: \[2312.14565\] Improving Task Instructions for Data Annotators: How Clear Rules and Higher Pay Increase Performance in Data Annotation in the AI Economy \- arXiv, accessed April 11, 2025, [https://arxiv.org/abs/2312.14565](https://arxiv.org/abs/2312.14565)
[^54]: The mundane work of designing precise data annotation / labelling tasks – Nocode functions \- blog, accessed April 11, 2025, [https://seinecle.github.io/blog/designing-precise-data-annotation-tasks/](https://seinecle.github.io/blog/designing-precise-data-annotation-tasks/)
[^55]: www.sapien.io, accessed April 11, 2025, [https://www.sapien.io/blog/balancing-speed-quality-and-efficiency-in-data-labeling-for-ai\#:\~:text=Several%20factors%20can%20impede%20the,down%20the%20labeling%20process%20significantly.](https://www.sapien.io/blog/balancing-speed-quality-and-efficiency-in-data-labeling-for-ai#:~:text=Several%20factors%20can%20impede%20the,down%20the%20labeling%20process%20significantly.)
[^56]: Data Labeling Challenges and Solutions \- DATAVERSITY, accessed April 11, 2025, [https://www.dataversity.net/data-labeling-challenges-and-solutions/](https://www.dataversity.net/data-labeling-challenges-and-solutions/)
[^57]: Balancing Speed, Quality & Efficiency In Data Labeling For AI \- Sapien, accessed April 11, 2025, [https://www.sapien.io/blog/balancing-speed-quality-and-efficiency-in-data-labeling-for-ai](https://www.sapien.io/blog/balancing-speed-quality-and-efficiency-in-data-labeling-for-ai)
[^58]: Challenges Of Data Labelling And How To Overcome Them \- Springbord, accessed April 11, 2025, [https://www.springbord.com/blog/challenges-of-data-labeling/](https://www.springbord.com/blog/challenges-of-data-labeling/)
[^59]: Measuring Success: Data Annotator Performance Metrics \- Labelvisor, accessed April 11, 2025, [https://www.labelvisor.com/measuring-success-data-annotator-performance-metrics/](https://www.labelvisor.com/measuring-success-data-annotator-performance-metrics/)
[^60]: Mastering Quality Control in Data Annotation: Explore the KPIs, Metrics, and Best Practices, accessed April 11, 2025, [https://www.damcogroup.com/blogs/mastering-quality-control-in-data-annotation](https://www.damcogroup.com/blogs/mastering-quality-control-in-data-annotation)
[^61]: Top Data Quality Metrics for Assessing Your Labeled Data \- Kili Technology, accessed April 11, 2025, [https://kili-technology.com/data-labeling/top-data-quality-metrics-for-assessing-your-data-labeling-quality](https://kili-technology.com/data-labeling/top-data-quality-metrics-for-assessing-your-data-labeling-quality)
[^62]: Guide: how to evaluate the quality of annotated data \- Toloka, accessed April 11, 2025, [https://toloka.ai/blog/quality-evaluation/](https://toloka.ai/blog/quality-evaluation/)
[^63]: Measure the Effectiveness of A Data Annotation Project \- Keylabs, accessed April 11, 2025, [https://keylabs.ai/blog/how-to-measure-the-effectiveness-of-a-data-annotation-project-and-machine-learning-data-labeling-tools/](https://keylabs.ai/blog/how-to-measure-the-effectiveness-of-a-data-annotation-project-and-machine-learning-data-labeling-tools/)
[^64]: 5 Proven Strategies for Accurate Data Annotation \- Damco Solutions, accessed April 11, 2025, [https://www.damcogroup.com/blogs/strategies-to-enhance-data-annotation-accuracy](https://www.damcogroup.com/blogs/strategies-to-enhance-data-annotation-accuracy)
[^65]: Quality Assurance Techniques in Data Annotation \- iMerit, accessed April 11, 2025, [https://imerit.net/blog/quality-assurance-techniques-in-data-annotation/](https://imerit.net/blog/quality-assurance-techniques-in-data-annotation/)
[^66]: Annotation Error Detection: Analyzing the Past and Present for a More Coherent Future, accessed April 11, 2025, [https://direct.mit.edu/coli/article/49/1/157/113280/Annotation-Error-Detection-Analyzing-the-Past-and](https://direct.mit.edu/coli/article/49/1/157/113280/Annotation-Error-Detection-Analyzing-the-Past-and)
[^67]: Generalizable Error Modeling for Human Data Annotation: Evidence from an Industry-Scale Search Data Annotation Program \- Apple Machine Learning Research, accessed April 11, 2025, [https://machinelearning.apple.com/research/error-modeling](https://machinelearning.apple.com/research/error-modeling)
[^68]: Clinical text annotation – what factors are associated with the cost of time? \- PMC, accessed April 11, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC6371268/](https://pmc.ncbi.nlm.nih.gov/articles/PMC6371268/)
[^69]: Annotation Quality Framework \- Accuracy, Credibility, and Consistency \- Data-centric AI Resource Hub, accessed April 11, 2025, [https://datacentricai.org/neurips21/papers/49_CameraReady_DCAI2021_tex(8).pdf](<https://datacentricai.org/neurips21/papers/49_CameraReady_DCAI2021_tex(8).pdf>)
[^70]: Overcoming Mental Fatigue: A Systematic Approach \- Todoist, accessed April 11, 2025, [https://www.todoist.com/inspiration/mental-fatigue](https://www.todoist.com/inspiration/mental-fatigue)
[^71]: Cognitive Fatigue and Attention \- Effects, Strategies, Scientific Insights \- Taju Coaching, accessed April 11, 2025, [https://www.tajucoaching.com/blog/cognitive-fatigue-and-attention-strategies-for-maintaining-focus-and-alertness](https://www.tajucoaching.com/blog/cognitive-fatigue-and-attention-strategies-for-maintaining-focus-and-alertness)
[^72]: Spring 2020 \- Reducing Mental Fatigue from Sustained Attention Task, accessed April 11, 2025, [https://aggieresearch.tamu.edu/spring-2020-reducing-mental-fatigue-from-sustained-attention-task/](https://aggieresearch.tamu.edu/spring-2020-reducing-mental-fatigue-from-sustained-attention-task/)
[^73]: Understanding mental fatigue and its detection: a comparative analysis of assessments and tools \- PubMed Central, accessed April 11, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC10460155/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10460155/)
[^74]: Best Practices for Scaling Data Annotation Projects in 2024 \- Content Whale, accessed April 11, 2025, [https://content-whale.com/us/blog/best-practices-scaling-data-annotation-projects-2024/](https://content-whale.com/us/blog/best-practices-scaling-data-annotation-projects-2024/)
[^75]: Just been accepted \- what are your top tips? : r/dataannotation \- Reddit, accessed April 11, 2025, [https://www.reddit.com/r/dataannotation/comments/1e0lnns/just_been_accepted_what_are_your_top_tips/](https://www.reddit.com/r/dataannotation/comments/1e0lnns/just_been_accepted_what_are_your_top_tips/)
[^76]: Manual Data Annotation vs. Augmented Annotation: Pros and Cons \- Labelvisor, accessed April 11, 2025, [https://www.labelvisor.com/manual-data-annotation-vs-augmented-annotation-pros-and-cons/](https://www.labelvisor.com/manual-data-annotation-vs-augmented-annotation-pros-and-cons/)
[^77]: Building a Robust Data Annotation Workflow: Best Practices and Tools | CaptchaForum, accessed April 11, 2025, [https://captchaforum.com/threads/building-a-robust-data-annotation-workflow-best-practices-and-tools.4513/](https://captchaforum.com/threads/building-a-robust-data-annotation-workflow-best-practices-and-tools.4513/)
[^78]: Use of Automation to Optimize Quality Control in Data Annotation Projects \- HitechDigital, accessed April 11, 2025, [https://www.hitechdigital.com/blog/quality-control-in-data-annotation](https://www.hitechdigital.com/blog/quality-control-in-data-annotation)
[^79]: Creating Feedback Loops: Using Annotation Insights to Improve Models Iteratively, accessed April 11, 2025, [https://keymakr.com/blog/creating-feedback-loops-using-annotation-insights-to-improve-models-iteratively/](https://keymakr.com/blog/creating-feedback-loops-using-annotation-insights-to-improve-models-iteratively/)
[^80]: Quality Assurance in Annotation | Sapien's AI Glossary, accessed April 11, 2025, [https://www.sapien.io/glossary/definition/quality-assurance-in-annotation](https://www.sapien.io/glossary/definition/quality-assurance-in-annotation)
[^81]: Labeling Done Right: Best Practices for Maintaining Clarity in Data Annotation \- Kotwel, accessed April 11, 2025, [https://kotwel.com/best-practices-for-maintaining-clarity-in-data-annotation/](https://kotwel.com/best-practices-for-maintaining-clarity-in-data-annotation/)
[^82]: pmc.ncbi.nlm.nih.gov, accessed April 11, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC9786280/\#:\~:text=Mental%20fatigue%2C%20defined%20as%20a,et%20al.%2C%202009).](<https://pmc.ncbi.nlm.nih.gov/articles/PMC9786280/#:~:text=Mental%20fatigue%2C%20defined%20as%20a,et%20al.%2C%202009).>)
[^83]: Cognitive tasks elicit mental fatigue and impair subsequent physical ..., accessed April 11, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC9786280/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9786280/)
[^84]: Mental fatigue impairs physical performance in humans | Journal of Applied Physiology, accessed April 11, 2025, [https://journals.physiology.org/doi/full/10.1152/japplphysiol.91324.2008](https://journals.physiology.org/doi/full/10.1152/japplphysiol.91324.2008)
[^85]: Effects of Mental Fatigue on Brain Activity and Cognitive Performance: A Magnetoencephalography Study \- ResearchGate, accessed April 11, 2025, [https://www.researchgate.net/publication/282892276_Effects_of_Mental_Fatigue_on_Brain_Activity_and_Cognitive_Performance_A_Magnetoencephalography_Study](https://www.researchgate.net/publication/282892276_Effects_of_Mental_Fatigue_on_Brain_Activity_and_Cognitive_Performance_A_Magnetoencephalography_Study)
[^86]: Understanding Mental Fatigue and Its Impact on Athletic Performance \- Soma Technologies, accessed April 11, 2025, [https://blog.soma-npt.ch/understanding-mental-fatigue-and-its-impact-on-athletic-performance/](https://blog.soma-npt.ch/understanding-mental-fatigue-and-its-impact-on-athletic-performance/)
[^87]: The Physiological Nature of Mental Fatigue: Current Knowledge and Future Avenues for Sport Science in \- Human Kinetics Journals, accessed April 11, 2025, [https://journals.humankinetics.com/view/journals/ijspp/17/2/article-p149.xml](https://journals.humankinetics.com/view/journals/ijspp/17/2/article-p149.xml)
[^88]: Mental Fatigue: What Happens When Your Brain Is Tired? · Frontiers ..., accessed April 11, 2025, [https://kids.frontiersin.org/articles/10.3389/frym.2023.1080802](https://kids.frontiersin.org/articles/10.3389/frym.2023.1080802)
[^89]: Cognitive fatigue: What it is, symptoms, and how to manage it \- Medical News Today, accessed April 11, 2025, [https://www.medicalnewstoday.com/articles/cognitive-fatigue](https://www.medicalnewstoday.com/articles/cognitive-fatigue)
[^90]: What is Cognitive Fatigue?, accessed April 11, 2025, [https://acognitiveconnection.com/what-is-cognitive-fatigue/](https://acognitiveconnection.com/what-is-cognitive-fatigue/)
[^91]: Mental Exhaustion: Definition, Causes, Symptoms, and Treatment \- Healthline, accessed April 11, 2025, [https://www.healthline.com/health/mental-exhaustion](https://www.healthline.com/health/mental-exhaustion)
[^92]: Persistence of Mental Fatigue on Motor Control \- Frontiers, accessed April 11, 2025, [https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.588253/full](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.588253/full)
[^93]: 7 Human Error Statistics For 2025 \- DocuClipper, accessed April 11, 2025, [https://www.docuclipper.com/blog/human-error-statistics/](https://www.docuclipper.com/blog/human-error-statistics/)
[^94]: Effects of Stress, Repetition, Fatigue and Work Environment on Human Error in Manufacturing Industries \- Science Alert, accessed April 11, 2025, [https://scialert.net/fulltext/?doi=jas.2014.3464.3471](https://scialert.net/fulltext/?doi=jas.2014.3464.3471)
[^95]: Repetitive Work: Contrast and Conflict \- LSU Faculty Websites, accessed April 11, 2025, [https://faculty.lsu.edu/bedeian/files/repretitive-work-contrast-and-conflict.pdf](https://faculty.lsu.edu/bedeian/files/repretitive-work-contrast-and-conflict.pdf)
[^96]: Breaking the Cycle: How Repetitive Tasks are Sabotaging Your Business's Success, accessed April 11, 2025, [https://www.esignly.com/electronic-signature/how-repetitive-task-hurting-business.html](https://www.esignly.com/electronic-signature/how-repetitive-task-hurting-business.html)
[^97]: Effects of Stress, Repetition, Fatigue and Work Environment on Human Error in Manufacturing Industries \- ResearchGate, accessed April 11, 2025, [https://www.researchgate.net/publication/266025022_Effects_of_Stress_Repetition_Fatigue_and_Work_Environment_on_Human_Error_in_Manufacturing_Industries](https://www.researchgate.net/publication/266025022_Effects_of_Stress_Repetition_Fatigue_and_Work_Environment_on_Human_Error_in_Manufacturing_Industries)
[^98]: (PDF) Boredom in the workplace: More than monotonous tasks, accessed April 11, 2025, [https://www.researchgate.net/publication/227583849_Boredom_in_the_workplace_More_than_monotonous_tasks](https://www.researchgate.net/publication/227583849_Boredom_in_the_workplace_More_than_monotonous_tasks)
[^99]: (PDF) Experimental evidence for the effects of task repetitiveness on mental strain and objective work performance \- ResearchGate, accessed April 11, 2025, [https://www.researchgate.net/publication/260412582_Experimental_evidence_for_the_effects_of_task_repetitiveness_on_mental_strain_and_objective_work_performance](https://www.researchgate.net/publication/260412582_Experimental_evidence_for_the_effects_of_task_repetitiveness_on_mental_strain_and_objective_work_performance)
[^100]: Sustaining Attention to Simple Tasks: A Meta-Analytic Review of the Neural Mechanisms of Vigilant Attention \- PubMed Central, accessed April 11, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC3627747/](https://pmc.ncbi.nlm.nih.gov/articles/PMC3627747/)
[^101]: archive.acrs.org.au, accessed April 11, 2025, [https://archive.acrs.org.au/files/arsrpe/RS060025.pdf](https://archive.acrs.org.au/files/arsrpe/RS060025.pdf)
[^102]: The effects of monotony on the performance of simple and complex ..., accessed April 11, 2025, [https://www.researchgate.net/publication/289810313_The_effects_of_monotony_on_the_performance_of_simple_and_complex_tasks](https://www.researchgate.net/publication/289810313_The_effects_of_monotony_on_the_performance_of_simple_and_complex_tasks)
[^103]: Mitigating the effects of monotony: The role of task complexity | Request PDF, accessed April 11, 2025, [https://www.researchgate.net/publication/288364062_Mitigating_the_effects_of_monotony_The_role_of_task_complexity](https://www.researchgate.net/publication/288364062_Mitigating_the_effects_of_monotony_The_role_of_task_complexity)
[^104]: Cognitive Engagement Combats Transport Workers' Monotony, accessed April 11, 2025, [https://ohsonline.com/articles/2012/08/30/cognitive-engagement-combats-transport-worker-monotony?m=1](https://ohsonline.com/articles/2012/08/30/cognitive-engagement-combats-transport-worker-monotony?m=1)
[^105]: Handling Imbalanced Data in Classification \- Keylabs, accessed April 11, 2025, [https://keylabs.ai/blog/handling-imbalanced-data-in-classification/](https://keylabs.ai/blog/handling-imbalanced-data-in-classification/)
[^106]: Handling Imbalanced Data to Improve Precision \- Keylabs, accessed April 11, 2025, [https://keylabs.ai/blog/handling-imbalanced-data-to-improve-precision/](https://keylabs.ai/blog/handling-imbalanced-data-to-improve-precision/)
[^107]: Facing Imbalanced Data \- Laszlo A. Jeni, accessed April 11, 2025, [https://www.laszlojeni.com/pub/articles/Jeni13ACII.pdf](https://www.laszlojeni.com/pub/articles/Jeni13ACII.pdf)
[^108]: Full article: Leveraging Researcher Domain Expertise to Annotate Concepts Within Imbalanced Data \- Taylor & Francis Online, accessed April 11, 2025, [https://www.tandfonline.com/doi/full/10.1080/19312458.2023.2182278](https://www.tandfonline.com/doi/full/10.1080/19312458.2023.2182278)
[^109]: Exploring Imbalanced Annotations for Effective In-Context Learning \- arXiv, accessed April 11, 2025, [https://arxiv.org/html/2502.[^04037]v1](https://arxiv.org/html/2502.[^04037]v1)
[^110]: The challenges of automated data annotation and how to overcome them \- SunTec.AI, accessed April 11, 2025, [https://www.suntec.ai/blog/how-to-overcome-challenges-of-automated-data-annotation/](https://www.suntec.ai/blog/how-to-overcome-challenges-of-automated-data-annotation/)
[^111]: Overcoming Label Skew and the AI data crunch \- Innovatiana, accessed April 11, 2025, [https://en.innovatiana.com/post/label-skew-and-data-scarcity](https://en.innovatiana.com/post/label-skew-and-data-scarcity)
[^112]: Inter-Annotator Agreement: a key Labeling metric \- Innovatiana, accessed April 11, 2025, [https://en.innovatiana.com/post/inter-annotator-agreement](https://en.innovatiana.com/post/inter-annotator-agreement)
[^113]: The Challenge of Data Annotation in Deep Learning—A Case Study on Whole Plant Corn Silage, accessed April 11, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC8879292/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8879292/)
[^114]: Accuracy degrade with highly skewed data after handling imbalance problem \[closed\], accessed April 11, 2025, [https://stackoverflow.com/questions/72715345/accuracy-degrade-with-highly-skewed-data-after-handling-imbalance-problem](https://stackoverflow.com/questions/72715345/accuracy-degrade-with-highly-skewed-data-after-handling-imbalance-problem)
[^115]: Correcting Annotator Bias in Training Data: Population-Aligned Instance Replication (PAIR), accessed April 11, 2025, [https://arxiv.org/html/2501.06826v2](https://arxiv.org/html/2501.06826v2)
[^116]: Full article: Investigating the impact of perceived mental fatigue on sustained attention performance: a latent growth curve analysis taking social desirability into account, accessed April 11, 2025, [https://www.tandfonline.com/doi/full/10.1080/02699931.2025.2468281?src=exp-la](https://www.tandfonline.com/doi/full/10.1080/02699931.2025.2468281?src=exp-la)
[^117]: Examining the Landscape of Cognitive Fatigue Detection: A ... \- MDPI, accessed April 11, 2025, [https://www.mdpi.com/2227-7080/12/3/38](https://www.mdpi.com/2227-7080/12/3/38)
[^118]: Mental Fatigue Affects Visual Selective Attention \- PMC, accessed April 11, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC3485293/](https://pmc.ncbi.nlm.nih.gov/articles/PMC3485293/)
[^119]: The Impairing Effect of Mental Fatigue on Visual Sustained Attention under Monotonous Multi-Object Visual Attention Task in Long Durations: An Event-Related Potential Based Study \- PubMed Central, accessed April 11, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC5040418/](https://pmc.ncbi.nlm.nih.gov/articles/PMC5040418/)
[^120]: Overt and Covert Effects of Mental Fatigue on Attention Networks: Evidence from Event-Related Potentials during the Attention Network Test \- MDPI, accessed April 11, 2025, [https://www.mdpi.com/2076-3425/14/8/803](https://www.mdpi.com/2076-3425/14/8/803)
[^121]: Effects of mental fatigue on attention: An ERP study | Request PDF \- ResearchGate, accessed April 11, 2025, [https://www.researchgate.net/publication/7827729_Effects_of_mental_fatigue_on_attention_An_ERP_study](https://www.researchgate.net/publication/7827729_Effects_of_mental_fatigue_on_attention_An_ERP_study)
[^122]: Effects of mental fatigue on the capacity limits of visual attention \- Taylor & Francis Online, accessed April 11, 2025, [https://www.tandfonline.com/doi/abs/10.1080/20445911.2012.658039](https://www.tandfonline.com/doi/abs/10.1080/20445911.2012.658039)
[^123]: Effects of mental fatigue on the capacity limits of visual attention \- ResearchGate, accessed April 11, 2025, [https://www.researchgate.net/publication/241683966_Effects_of_mental_fatigue_on_the_capacity_limits_of_visual_attention](https://www.researchgate.net/publication/241683966_Effects_of_mental_fatigue_on_the_capacity_limits_of_visual_attention)
[^124]: Slowed reaction times in cognitive fatigue are not attributable to declines in motor preparation \- PubMed, accessed April 11, 2025, [https://pubmed.ncbi.nlm.nih.gov/36227342/](https://pubmed.ncbi.nlm.nih.gov/36227342/)
[^125]: SUSTAINED Attention | Examples and Conditions \- Rehametrics, accessed April 11, 2025, [https://rehametrics.com/en/sustained-attention/](https://rehametrics.com/en/sustained-attention/)
[^126]: Vigilance decrement and mind-wandering in sustained attention tasks: Two sides of the same coin? \- Frontiers, accessed April 11, 2025, [https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2023.1122406/full](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2023.1122406/full)
[^127]: Predicting attentional lapses using response time speed in continuous performance tasks \- Frontiers, accessed April 11, 2025, [https://www.frontiersin.org/journals/cognition/articles/10.3389/fcogn.2024.1460349/pdf](https://www.frontiersin.org/journals/cognition/articles/10.3389/fcogn.2024.1460349/pdf)
[^128]: Sustained Attention/ Focus \- Cognitive Ability \- CogniFit, accessed April 11, 2025, [https://www.cognifit.com/science/focus](https://www.cognifit.com/science/focus)
[^129]: Full article: Unique and overlapping contributions of sustained attention and working memory to parent and teacher ratings of inattentive behavior \- Taylor and Francis, accessed April 11, 2025, [https://www.tandfonline.com/doi/full/10.[^1080]/09297049.[^2021].[^2022112]](https://www.tandfonline.com/doi/full/10.[^1080]/09297049.[^2021].[^2022112])
[^130]: The impact of image degradation and temporal dynamics on sustained attention | JOV, accessed April 11, 2025, [https://jov.arvojournals.org/article.aspx?articleid=2778676](https://jov.arvojournals.org/article.aspx?articleid=2778676)
[^131]: Neuroscientists literally change the way we think: Advantages of a wandering mind, accessed April 11, 2025, [https://www.sciencedaily.com/releases/2015/02/150223164531.htm](https://www.sciencedaily.com/releases/2015/02/150223164531.htm)
[^132]: A survey of fatigue measures and models | Request PDF \- ResearchGate, accessed April 11, 2025, [https://www.researchgate.net/publication/369248252_A_survey_of_fatigue_measures_and_models](https://www.researchgate.net/publication/369248252_A_survey_of_fatigue_measures_and_models)
[^133]: Fatigue Detection Model for Older Adults Using Eye-Tracking Data Gathered While Watching Video: Evaluation Against Diverse Fatiguing Tasks | Request PDF \- ResearchGate, accessed April 11, 2025, [https://www.researchgate.net/publication/319871300_Fatigue_Detection_Model_for_Older_Adults_Using_Eye-Tracking_Data_Gathered_While_Watching_Video_Evaluation_Against_Diverse_Fatiguing_Tasks](https://www.researchgate.net/publication/319871300_Fatigue_Detection_Model_for_Older_Adults_Using_Eye-Tracking_Data_Gathered_While_Watching_Video_Evaluation_Against_Diverse_Fatiguing_Tasks)
[^134]: The Inevitability of and Remedy for Human Error \- SureTest, accessed April 11, 2025, [https://suretest.health/blog/the-inevitability-of-and-remedy-for-human-error/](https://suretest.health/blog/the-inevitability-of-and-remedy-for-human-error/)
[^135]: How does the relative perception of boredom influence concentration and task performance? \- EconStor, accessed April 11, 2025, [https://www.econstor.eu/bitstream/10419/295048/1/5224-3528.pdf](https://www.econstor.eu/bitstream/10419/295048/1/5224-3528.pdf)
[^136]: It's so boring \- or is it? Examining mindfulness in monotonous jobs \- \- ResearchPod, accessed April 11, 2025, [https://researchpod.org/informatics-technology/its-so-boring-or-is-it-examining-mindfulness-in-monotonous-jobs](https://researchpod.org/informatics-technology/its-so-boring-or-is-it-examining-mindfulness-in-monotonous-jobs)
[^137]: Measuring Inter-Annotator Agreement \- Amazon S3, accessed April 11, 2025, [https://s3.amazonaws.com/resources.basistech.com/hltcon-presentations/2018/Zach_Yocum_Measuring_Inter-Annotator_Agreement_HLTCon2018.pdf](https://s3.amazonaws.com/resources.basistech.com/hltcon-presentations/2018/Zach_Yocum_Measuring_Inter-Annotator_Agreement_HLTCon2018.pdf)
[^138]: 1 \- The time (in minutes) needed and the obtained quality, for... | Download Scientific Diagram \- ResearchGate, accessed April 11, 2025, [https://www.researchgate.net/figure/The-time-in-minutes-needed-and-the-obtained-quality-for-annotating-a-video-containing_fig22_268358987](https://www.researchgate.net/figure/The-time-in-minutes-needed-and-the-obtained-quality-for-annotating-a-video-containing_fig22_268358987)
[^139]: Measuring Inter-Annotator Agreement: Building Trustworthy Datasets \- Keymakr, accessed April 11, 2025, [https://keymakr.com/blog/measuring-inter-annotator-agreement-building-trustworthy-datasets/](https://keymakr.com/blog/measuring-inter-annotator-agreement-building-trustworthy-datasets/)
[^140]: How accuracy and completeness in data annotation impacts the performance of AI models, accessed April 11, 2025, [https://www.fbspl.com/blogs/accurate-data-annotation-impact-ai-model-performance](https://www.fbspl.com/blogs/accurate-data-annotation-impact-ai-model-performance)
[^141]: Four Key Metrics for Ensuring Data Annotation Accuracy | TELUS Digital, accessed April 11, 2025, [https://www.telusdigital.com/insights/ai-data/article/data-annotation-metrics](https://www.telusdigital.com/insights/ai-data/article/data-annotation-metrics)
[^142]: A Guide to Data Labeling Standards for High-Quality ML Datasets, accessed April 11, 2025, [https://labelyourdata.com/articles/data-labeling-quality-and-how-to-measure-it](https://labelyourdata.com/articles/data-labeling-quality-and-how-to-measure-it)
[^143]: 5 Key Quality Control Metrics in Text Annotation | HitechDigital, accessed April 11, 2025, [https://www.hitechdigital.com/blog/quality-control-metrics-in-text-annotation](https://www.hitechdigital.com/blog/quality-control-metrics-in-text-annotation)
[^144]: Annotation Metrics · Prodigy · An annotation tool for AI, Machine Learning & NLP, accessed April 11, 2025, [https://prodi.gy/docs/metrics](https://prodi.gy/docs/metrics)
[^145]: Inter-annotator Agreement \- DTIC, accessed April 11, 2025, [https://apps.dtic.mil/sti/trecms/pdf/AD1158943.pdf](https://apps.dtic.mil/sti/trecms/pdf/AD1158943.pdf)
[^146]: Inter-Annotator Agreement (IAA) \- Datasaur, accessed April 11, 2025, [https://docs.datasaur.ai/workspace-management/analytics/inter-annotator-agreement](https://docs.datasaur.ai/workspace-management/analytics/inter-annotator-agreement)
[^147]: Inter-rater Reliability Metrics: An Introduction to Krippendorff's Alpha \- Surge AI, accessed April 11, 2025, [https://www.surgehq.ai/blog/inter-rater-reliability-metrics-an-introduction-to-krippendorffs-alpha](https://www.surgehq.ai/blog/inter-rater-reliability-metrics-an-introduction-to-krippendorffs-alpha)
[^148]: Arguing with Language: Inter Annotator Agreement | edrone | CRM for e-commerce & marketing automation, accessed April 11, 2025, [https://edrone.me/blog/arguing-with-language-inter-annotator-agreement](https://edrone.me/blog/arguing-with-language-inter-annotator-agreement)
[^149]: Proper way to calculate inter-annotator agreement for spans/ner? \- Prodigy Support, accessed April 11, 2025, [https://support.prodi.gy/t/proper-way-to-calculate-inter-annotator-agreement-for-spans-ner/5760](https://support.prodi.gy/t/proper-way-to-calculate-inter-annotator-agreement-for-spans-ner/5760)
[^150]: www.clickworker.com, accessed April 11, 2025, [https://www.clickworker.com/customer-blog/error-handling-in-data-annotation-pipelines/\#:\~:text=They%20predict%20errors%20from%20a,labels%20can%20uncover%20annotation%20irregularities.](https://www.clickworker.com/customer-blog/error-handling-in-data-annotation-pipelines/#:~:text=They%20predict%20errors%20from%20a,labels%20can%20uncover%20annotation%20irregularities.)
[^151]: Find and fix model errors (error analysis) \- Labelbox docs, accessed April 11, 2025, [https://docs.labelbox.com/docs/find-model-errors](https://docs.labelbox.com/docs/find-model-errors)
[^152]: How to display data annotation error, the way it's property are decorated? \- Stack Overflow, accessed April 11, 2025, [https://stackoverflow.com/questions/74992279/how-to-display-data-annotation-error-the-way-its-property-are-decorated](https://stackoverflow.com/questions/74992279/how-to-display-data-annotation-error-the-way-its-property-are-decorated)
[^153]: 5 Effective Data Annotation Strategies to Accelerate your AI Projects \- HitechDigital, accessed April 11, 2025, [https://www.hitechdigital.com/blog/data-annotation-strategies-accelerate-your-ai-projects](https://www.hitechdigital.com/blog/data-annotation-strategies-accelerate-your-ai-projects)
[^154]: Addressing Scalability Challenges in Data Annotation for growing AI needs, accessed April 11, 2025, [https://learningspiral.ai/addressing-scalability-challenges-in-data-annotation-for-growing-ai-needs/](https://learningspiral.ai/addressing-scalability-challenges-in-data-annotation-for-growing-ai-needs/)
[^155]: Challenges in Data Annotation: How Fusion CX Solves Them, accessed April 11, 2025, [https://www.fusioncx.com/blog/data-annotation/challenges-in-data-annotation/](https://www.fusioncx.com/blog/data-annotation/challenges-in-data-annotation/)
[^156]: Data Annotator Salaries: Trends and Analysis \- Labelvisor, accessed April 11, 2025, [https://www.labelvisor.com/data-annotator-salaries-trends-and-analysis/](https://www.labelvisor.com/data-annotator-salaries-trends-and-analysis/)
