GitHub 仓库：<https://github.com/LB-CC-summer/software-engineering-plagiarism-check>

# 软件工程个人项目：论文查重算法设计与实现

## 一、作业信息

- 学号：3124004429
- 语言：Python 3
- 入口文件：`main.py`
- 代码、测试和截图均位于仓库的 `3124004429/` 目录

程序按下面的方式运行：

```text
python main.py <原文文件绝对路径> <抄袭版文件绝对路径> <答案文件绝对路径>
```

答案文件只包含一个保留两位小数的浮点数，例如 `0.80`。

## 二、开发前 PSP 估算

估算在开始编码之前完成，并随第一次 Git 提交保存。

| PSP2.1 | Personal Software Process Stages | 预估耗时（分钟） |
| --- | --- | ---: |
| Planning | 计划 |  |
| · Estimate | · 估计这个任务需要多少时间 | 20 |
| Development | 开发 |  |
| · Analysis | · 需求分析（包括学习新技术） | 40 |
| · Design Spec | · 生成设计文档 | 30 |
| · Design Review | · 设计复审 | 20 |
| · Coding Standard | · 代码规范（为目前的开发制定合适的规范） | 20 |
| · Design | · 具体设计 | 40 |
| · Coding | · 具体编码 | 120 |
| · Code Review | · 代码复审 | 30 |
| · Test | · 测试（自我测试，修改代码，提交修改） | 70 |
| Reporting | 报告 |  |
| · Test Report | · 测试报告 | 40 |
| · Size Measurement | · 计算工作量 | 15 |
| · Postmortem & Process Improvement Plan | · 事后总结，并提出过程改进计划 | 30 |
| **合计** | **合计** | **475** |

我对任务的主要判断是：算法本身不难，难点在于中文文本不能被英文空格
分词限制、增删改会破坏精确匹配、大文本不能让算法退化到平方级，以及
需要补齐异常处理和测试覆盖率。

## 三、计算模块接口的设计与实现

### 3.1 模块组织

| 模块 | 职责 |
| --- | --- |
| `main.py` | 只负责调用命令行入口 |
| `plagiarism/cli.py` | 解析 3 个路径参数、组织流程、统一处理异常 |
| `plagiarism/io_utils.py` | 读取文件、识别编码、写入两位小数答案 |
| `plagiarism/normalization.py` | HTML 正文提取、Unicode 归一化、标点过滤 |
| `plagiarism/similarity.py` | 生成 n-gram、计算稀疏向量余弦相似度 |
| `plagiarism/errors.py` | 定义命令行、读取、解码、写入异常 |

核心计算函数不依赖文件系统，接收两个字符串并返回 `[0, 1]` 之间的
浮点数，这样单元测试可以直接覆盖边界输入。整体数据流如下：

![设计流程图](https://raw.githubusercontent.com/LB-CC-summer/software-engineering-plagiarism-check/main/3124004429/images/design_flow.png)

### 3.2 文本归一化

中文没有天然空格，使用第三方分词器又会增加模型和性能负担，因此我选择
字符级比较。归一化过程如下：

1. 如果输入是被浏览器另存为 HTML 的 GitHub 文本页面，先提取
   `blob-code js-file-line` 单元格中的正文。
2. 对文本使用 Unicode `NFKC`，统一全角字母、数字和兼容字符。
3. 调用 `casefold()`，消除英文大小写差异。
4. 删除空格和标点，只保留字母、数字与汉字。

```python
def normalize_text(text: str) -> str:
    if not text:
        return ""
    source = extract_embedded_text(text)
    normalized = unicodedata.normalize("NFKC", source).casefold()
    return "".join(character for character in normalized if character.isalnum())
```

课程下载文件中的 `orig_0.8_del.txt` 和 `orig_0.8_dis_*.txt` 实际是
浏览器保存的 GitHub HTML 页面。这个兼容层使程序无需人工修复输入，
并且不会把导航栏、脚本代码当成论文内容。

### 3.3 为什么使用 1/2/3-gram

以“论文查重”为例：

```text
1-gram：论、文、查、重
2-gram：论文、文查、查重
3-gram：论文查、文查重
```

不同阶数的作用不同：

- 1-gram 对增删更宽容，少量字被删除时不会让分数急剧下降。
- 2-gram 保留词语搭配和局部顺序，是主要判别特征。
- 3-gram 对顺序更敏感，可以识别把字符或片段打乱的行为。

最终采用下面的权重：

```text
score = 0.15 * cosine(1-gram)
      + 0.45 * cosine(2-gram)
      + 0.40 * cosine(3-gram)
```

2-gram 和 3-gram 合计占 85%，因此算法不会退化成只比较词频、忽略语序的
简单模型；保留 15% 的 1-gram 则提高对增删改的鲁棒性。

### 3.4 稀疏向量余弦相似度

```python
def count_ngrams(text: str, n: int) -> Counter[str]:
    if len(text) < n:
        return Counter()
    return Counter(text[index : index + n] for index in range(len(text) - n + 1))


def _cosine_similarity(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    if len(left) > len(right):
        left, right = right, left
    dot_product = sum(count * right.get(ngram, 0) for ngram, count in left.items())
    left_norm = sqrt(sum(count * count for count in left.values()))
    right_norm = sqrt(sum(count * count for count in right.values()))
    return dot_product / (left_norm * right_norm)
```

计算点积时只遍历较小的字典，减少哈希查询次数。整体实现只依赖
`collections.Counter`，没有网络请求，也没有第三方运行时依赖。

### 3.5 样例结果

| 抄袭版文件 | 重复率 | 耗时（秒） |
| --- | ---: | ---: |
| `orig_0.8_add.txt` | 0.80 | 0.0227 |
| `orig_0.8_del.txt` | 0.81 | 0.0178 |
| `orig_0.8_dis_1.txt` | 0.96 | 0.0197 |
| `orig_0.8_dis_10.txt` | 0.84 | 0.0197 |
| `orig_0.8_dis_15.txt` | 0.63 | 0.0233 |

结果符合样例文件表达的趋势：增加和删除内容后的重复率约为 0.80，
轻度打乱仍接近 1.00，打乱程度越大，得分越低。

![课程样例运行结果](https://raw.githubusercontent.com/LB-CC-summer/software-engineering-plagiarism-check/main/3124004429/images/sample_results.png)

## 四、计算模块性能改进

### 4.1 初始实现及其问题

第一个可运行版本使用 `difflib.SequenceMatcher` 计算最长匹配块。
它的优点是代码短、容易验证，但 `find_longest_match` 在大文本上会出现
明显的平方级退化。课程要求 5 秒内完成，因此它不能作为最终实现。

### 4.2 性能分析

我使用 Python 标准库 `cProfile` 加上 `pstats` 分析核心函数，并用
相同输入执行 5 次，排除模块导入时间。

优化前，累计耗时最高的函数是：

```text
difflib.py:305(find_longest_match)   cumtime 2.194s
difflib.py:421(get_matching_blocks)  cumtime 2.215s
difflib.py:597(ratio)                cumtime 2.216s
```

![优化前性能分析](https://raw.githubusercontent.com/LB-CC-summer/software-engineering-plagiarism-check/main/3124004429/images/performance_before.png)

![优化前函数调用表](https://raw.githubusercontent.com/LB-CC-summer/software-engineering-plagiarism-check/main/3124004429/images/profile_before_table.png)

### 4.3 改进思路

我把算法替换为线性时间的字符 n-gram 余弦相似度，并做了以下优化：

1. 使用固定阶数 1/2/3-gram，不再维护候选匹配块。
2. 使用 `Counter` 统计稀疏特征，避免构造稠密矩阵。
3. 计算余弦时只遍历较小字典，减少字典查询。
4. 删除不必要的中间列表，直接在生成器上求和。
5. 对极短文本自动跳过长度不足的 n-gram，避免空向量。

优化后，热点转移到真正必要的 n-gram 统计和向量余弦计算：

```text
calculate_similarity   cumtime 0.199s
count_ngrams           cumtime 0.091s
_cosine_similarity     cumtime 0.054s
```

![优化后性能分析](https://raw.githubusercontent.com/LB-CC-summer/software-engineering-plagiarism-check/main/3124004429/images/performance_after.png)

![优化后函数调用表](https://raw.githubusercontent.com/LB-CC-summer/software-engineering-plagiarism-check/main/3124004429/images/profile_after_table.png)

### 4.4 实测结果

| 算法 | 文本规模 | 耗时（秒） |
| --- | ---: | ---: |
| `difflib` 基线 | 8,493 字符 | 0.2382 |
| n-gram 优化版 | 8,493 字符 | 0.0199 |
| `difflib` 基线 | 16,986 字符 | 0.9717 |
| n-gram 优化版 | 16,986 字符 | 0.0352 |
| `difflib` 基线 | 42,465 字符 | 7.6925 |
| n-gram 优化版 | 42,465 字符 | 0.0844 |

在 42,465 字符输入上，优化版把耗时从 **7.69 秒**降到 **0.084 秒**，
约加速 **91 倍**，从超时变为远低于 5 秒限制。

![性能对比结果](https://raw.githubusercontent.com/LB-CC-summer/software-engineering-plagiarism-check/main/3124004429/images/benchmark_results.png)

## 五、单元测试与覆盖率

### 5.1 测试组织

项目共有 44 个测试，按职责分成五个文件：

- `test_similarity.py`：相似度算法、边界、自定义权重。
- `test_normalization.py`：Unicode、HTML 正文提取、标点过滤。
- `test_io_utils.py`：编码回退、读写异常。
- `test_cli.py`：参数、答案文件、错误退出码。
- `test_samples.py`：课程样例的集成范围和单次性能。

代表性测试数据如下：

| 场景 | 测试数据思路 | 期望 |
| --- | --- | --- |
| 完全相同 | 两次传入同一文本 | `1.00` |
| 完全为空 | 空串和空串/非空串组合 | `0.00` |
| 完全不同 | 两篇无关主题 | 小于 `0.20` |
| 增加内容 | 原文后追加新句子 | 不低于 `0.65` |
| 删除内容 | 删除部分句子 | 不低于 `0.65` |
| 打乱语序 | 前后半句交换 | 大于 `0.40` |
| 同义改写 | 星期天/周天，晴/晴朗 | 大于 `0.50` |
| 对称性 | 交换原文和抄袭版 | 两次结果近似相等 |
| 全角字符 | `ＡＢＣ１２３` | 归一化为 `abc123` |
| HTML 输入 | GitHub blob 表格 | 只保留正文 |
| 编码回退 | GB18030 文件 | 正确读取中文 |
| 异常退出 | 缺文件、坏 BOM、目录输出 | 返回 2，不产生答案 |

以下展示测试代码的一部分：

```python
def test_cli_writes_answer_and_prints_score(tmp_path, capsys):
    original = tmp_path / "orig.txt"
    candidate = tmp_path / "copy.txt"
    answer = tmp_path / "answer.txt"
    original.write_text("今天是星期天，天气晴。", encoding="utf-8")
    candidate.write_text("今天是星期天，天气晴朗。", encoding="utf-8")

    exit_code = run([str(original), str(candidate), str(answer)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert answer.read_text(encoding="utf-8").strip() == captured.out.strip()
```

### 5.2 覆盖率结果

执行命令：

```powershell
python -m pytest --cov=plagiarism --cov-branch --cov-report=term-missing
```

最终结果：

```text
44 passed in 1.14s
TOTAL  165 statements  0 miss  48 branches  0 partial  100%
```

![单元测试与覆盖率](https://raw.githubusercontent.com/LB-CC-summer/software-engineering-plagiarism-check/main/3124004429/images/coverage_and_tests.png)

![覆盖率 HTML 页面](https://raw.githubusercontent.com/LB-CC-summer/software-engineering-plagiarism-check/main/3124004429/images/coverage_html.png)

测试覆盖了三个 n-gram 阶数的分支、空向量、零权重、HTML 提取、
编码回退和所有异常出口，因此我认为测试用例能够满足该程序的测试要求。

### 5.3 代码质量分析

项目使用 Ruff 作为静态代码质量分析工具，检查规则包含
`E`、`F`、`I`、`N`、`UP`、`B`、`SIM`、`C4`、`PTH` 和 `RUF`。
第一次检查发现导入顺序和一个嵌套 `with` 警告，修复后结果为：

```text
All checks passed!
26 files already formatted
```

![Ruff 零警告](https://raw.githubusercontent.com/LB-CC-summer/software-engineering-plagiarism-check/main/3124004429/images/ruff_quality.png)

## 六、异常处理说明

异常被分为四类，全部继承自 `PlagiarismError`。命令行层统一捕获并输出
带 `error:` 前缀的可读信息，同时返回退出码 2。错误发生时不写答案文件，
避免评测程序把无效结果当成正常结果。

| 异常 | 设计目标 | 单元测试场景 | 输出 |
| --- | --- | --- | --- |
| `CommandLineError` | 参数必须恰好为 3 个 | 只传一个路径 | usage，退出码 2 |
| `DocumentReadError` | 输入必须是存在且可读的文件 | 缺失文件、目录、读取失败 | 文件错误 |
| `DocumentDecodeError` | 编码损坏时不能静默产生错误答案 | UTF-16 BOM 截断、编码不支持 | 解码错误 |
| `AnswerWriteError` | 输出必须可写且是文件 | 把目录作为答案路径 | 写入错误 |

例如，参数数量错误的测试如下：

```python
def test_cli_requires_exactly_three_arguments(capsys):
    exit_code = run(["only-one.txt"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "usage:" in captured.err
```

文件读取错误由 `read_document()` 抛出：

```python
if not path.exists():
    raise DocumentReadError(f"输入文件不存在：{path}")
if not path.is_file():
    raise DocumentReadError(f"输入路径不是文件：{path}")
```

## 七、实际 PSP 汇总

| PSP2.1 | Personal Software Process Stages | 预估耗时（分钟） | 实际耗时（分钟） |
| --- | --- | ---: | ---: |
| Planning | 计划 |  |  |
| · Estimate | · 估计这个任务需要多少时间 | 20 | 18 |
| Development | 开发 |  |  |
| · Analysis | · 需求分析（包括学习新技术） | 40 | 45 |
| · Design Spec | · 生成设计文档 | 30 | 35 |
| · Design Review | · 设计复审 | 20 | 20 |
| · Coding Standard | · 代码规范（为目前的开发制定合适的规范） | 20 | 20 |
| · Design | · 具体设计 | 40 | 40 |
| · Coding | · 具体编码 | 120 | 150 |
| · Code Review | · 代码复审 | 30 | 35 |
| · Test | · 测试（自我测试，修改代码，提交修改） | 70 | 85 |
| Reporting | 报告 |  |  |
| · Test Report | · 测试报告 | 40 | 35 |
| · Size Measurement | · 计算工作量 | 15 | 15 |
| · Postmortem & Process Improvement Plan | · 事后总结，并提出过程改进计划 | 30 | 25 |
| **合计** | **合计** | **475** | **523** |

实际耗时比估算多 48 分钟，主要花在处理 HTML 样例兼容和补充边界测试。
总体而言，性能优化和测试阶段节省的时间抵消了编码阶段的偏差。

## 八、Git 提交记录

项目按照“基础功能 → 性能优化 → 测试 → 质量分析 → 报告”的节奏提交：

1. 初始化项目并记录 PSP 估算。
2. 增加可运行的 `difflib` 基线版本。
3. 用字符 n-gram 余弦替换基线。
4. 增加 44 个单元测试和覆盖率配置。
5. 通过 Ruff 静态检查并统一格式。
6. 增加性能分析、图表、设计文档和博客材料。

## 九、总结

这次实现让我认识到，查重程序的关键不只是“能算出一个数”，而是要在
中文、增删改、语序变化、异常输入和性能限制之间取得平衡。最终版本在
课程样例上给出了可解释的 0.80、0.81、0.96、0.84、0.63。44 个功能
与异常测试全部通过，分支覆盖率达到 100%，且 Ruff 静态检查零警告。

后续如果继续改进，可以考虑：

1. 使用双数组 Trie 或滚动哈希减少 n-gram 字符串分配。
2. 对较长文本增加分段并行统计。
3. 引入可选的语义相似度模型，但保持标准库版本为默认实现。
