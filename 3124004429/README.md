# 3124004429 论文查重

GitHub 仓库：<https://github.com/LB-CC-summer/software-engineering-plagiarism-check>

## 作业信息

- 学号：3124004429
- 课程项目：软件工程个人项目——论文查重
- 语言：Python 3
- 入口：`main.py`
- 运行环境：Python 3.9 及以上

## 功能

程序接受三个命令行参数，计算原文和抄袭版论文之间的重复率，并将结果写入
答案文件。输出保留两位小数，取值范围为 `0.00` 到 `1.00`。

```text
python main.py <原文文件绝对路径> <抄袭版文件绝对路径> <答案文件绝对路径>
```

示例：

```powershell
python main.py samples/orig.txt samples/orig_0.8_add.txt answer.txt
```

## 算法

程序采用语言无关的多阶字符 n-gram 余弦相似度：

1. 读取文本，识别 UTF-8、UTF-16 或 GB18030 编码。
2. 自动提取被浏览器保存为 HTML 的 GitHub 文本页面正文。
3. 使用 Unicode NFKC、大小写折叠和标点过滤进行归一化。
4. 生成 1-gram、2-gram 和 3-gram 词频向量。
5. 按 `0.15 / 0.45 / 0.40` 的权重融合余弦相似度。

该方案对中文无需第三方分词器，增删改鲁棒，同时可以感知语序打乱。
详细设计见 [`docs/design.md`](docs/design.md)。

## 项目结构

```text
3124004429/
├── main.py
├── profile_checker.py
├── requirements.txt
├── pyproject.toml
├── PSP.md
├── README.md
├── plagiarism/
│   ├── cli.py
│   ├── errors.py
│   ├── io_utils.py
│   ├── normalization.py
│   └── similarity.py
├── tests/
├── samples/
├── scripts/
├── reports/
├── images/
└── docs/
```

## 安装与运行

程序运行时只使用 Python 标准库。测试、覆盖率和静态检查工具可通过
`requirements.txt` 安装：

```powershell
python -m pip install -r requirements.txt
```

## 测试与质量

```powershell
python -m pytest --cov=plagiarism --cov-branch --cov-report=term-missing
python -m ruff check .
python -m ruff format --check .
```

当前结果：44 个测试全部通过，分支覆盖率 100%，Ruff 零警告。

## 性能

课程样例的 42,465 字符输入上：

| 算法 | 耗时 |
| --- | ---: |
| 基线 `difflib.SequenceMatcher` | 10.5560 秒 |
| 优化 n-gram 余弦 | 0.1571 秒 |

优化后约加速 67 倍，并消除了平方级复杂度带来的超时风险。

## 文档

- [设计说明](docs/design.md)
- [单元测试与异常报告](docs/test_report.md)
- [PSP 表](docs/psp.md)
- [博客园博文草稿](docs/blog.md)
