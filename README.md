# ftl-is-king/homowork 作业自动审批与评测系统

[![Evaluate Homework](https://github.com/ftl-is-king/homowork/actions/workflows/eval_url.yml/badge.svg)](https://github.com/ftl-is-king/homowork/actions/workflows/eval_url.yml)

自动化 C 语言/Python 作业批改与管理平台。支持通过 **Issue 提交仓库 URL 自动审批** 或 **学生端 GitHub Actions 自动回传** 两种方式进行代码评估。

---

## 🌟 核心功能

1. **URL 提交自动审批**：学生只需在 Issue 中提供自己的作业代码仓库 URL，系统后台 Actions 自动克隆、编译、测试，并在 Issue 下生成精美的 Markdown 成绩报告。
2. **多维度评分体系**：
   - **正确率得分**（满分 60 分）：根据测试用例通过比例严格打分。
   - **运行时间得分**（满分 20 分）：基于执行耗时指数衰减打分，超时自动熔断（5 秒）。
   - **运行内存得分**（满分 20 分）：基于物理内存（RSS）占用指数衰减打分。
   - **历史最高分保护**：同一题目多次提交自动保留最高分记录。
3. **白名单准入校验**：内置 `DB.csv` 学籍校验机制，核实学号与姓名一致性方可入库。
4. **成绩自动归档**：评测通过后成绩自动沉淀至 `test.csv`，支持 Git 并发重试与自动推送。
5. **双向兼容**：完全兼容 [Ultra-auto_eval](https://github.com/NGC2237plus/Ultra-auto_eval) 及 `use.md` 模板同步方案。

---

## 📁 目录结构

```text
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── submit_homework.yml      # Issue URL 提交表单模板
│   └── workflows/
│       ├── eval_url.yml             # 核心：Issue URL 提交自动审批与回帖评测
│       └── manual_eval.yml          # 手动触发指定仓库评测工作流
├── config.py                        # 评测配置（题目用例、期望输出、截止日期、评分权重）
├── test.py                          # 核心评测与打分主程序
├── DB.csv                           # 学生白名单数据库 (id, name, email)
├── test.csv                         # 成绩汇总表 (自动更新)
├── requirements.txt                 # Python 依赖
├── student_template/                # 学生端模板工程目录
│   ├── .github/workflows/main.yml   # 学生端 Action (通过 MY_URL 拉取评测并回传)
│   ├── 1_main.c                     # 作业 C 语言代码示例
│   ├── README.md                    # 学生端说明
│   └── use.md                       # 学生端操作指南
├── use.md                           # 根目录作业提交指南
└── README.md                        # 本说明文档
```

---

## 🚀 教师与维护者指南

### 1. 录入学生白名单 (`DB.csv`)
在 `DB.csv` 中登记具备提交资格的学生学号、姓名与邮箱：
```csv
id,name,email
202401010001,测试学生,test@example.com
202401010002,张三,zhangsan@example.com
```

### 2. 配置作业题目与用例 (`config.py`)
在 `config.py` 中可自由修改：
- `USER_INPUT`: 每道题目的标准输入用例列表。
- `ANSWER`: 每道题目的标准预期输出列表。
- `DEADLINE`: 作业截止日期（超时将不记录成绩）。

### 3. 查看与导出成绩
学生所有评测成绩均实时保存在 `test.csv` 中，可直接在 GitHub 网页查看或下载为 Excel/CSV 分析。

---

## 👨‍💻 学生作业提交方式

详见 [使用指南 (use.md)](use.md)。简要说明如下：

### 方式一：URL 提交（最便捷，零配置）
1. 在个人 GitHub 账号中新建公开仓库，按 `1_main.c`、`2_main.c` 命名上传代码。
2. 代码**前三行**规范添加学号、邮箱与姓名注释：
   ```c
   // 202401010001
   // myemail@example.com
   // 张三
   ```
3. 在 [homowork Issues](https://github.com/ftl-is-king/homowork/issues) 发起 Issue 并填入仓库 URL，等待系统自动回复评测报告。

### 方式二：使用模板与 Actions 回传
在个人仓库设置中添加 `MY_URL` Secret，提交代码后个人 Actions 将自动拉取评测并在主仓库打分。

---

## 🛠️ 本地开发与测试

在本地测试评测脚本：
```bash
# 安装依赖
pip install -r requirements.txt

# 指定目录评测 C 代码
python test.py --dir ./student_template --no-push
```
