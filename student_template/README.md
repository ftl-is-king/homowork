# C 语言作业代码仓库模板

本仓库为学生作业提交模板工程。

## 文件命名规范
每个作业代码请按照题目编号命名：
- 第 1 题：`1_main.c` 或 `1_xxx.c`
- 第 2 题：`2_main.c` 或 `2_xxx.c`
- 第 3 题：`3_main.c` 或 `3_xxx.c`
- 其余题目以此类推...

## 代码头部注释规范（必须严格遵守）
每个 `.c` 文件的**前三行**必须按如下格式书写注释（以 `//` 开头），否则评测系统将无法识别身份并拒绝打分：

```c
// 202401010001
// your_email@example.com
// 张三
```

## 提交作业方式
你可以选择以下两种方式之一提交作业：
1. **方式一（最简单：URL 提交）**：在 [ftl-is-king/homowork/issues](https://github.com/ftl-is-king/homowork/issues) 点击新建 Issue，粘贴你本仓库的 URL，机器人将自动评测并回帖。
2. **方式二（自动同步）**：根据 [use.md](use.md) 在仓库设置中配置 `MY_URL` Secret，直接在网页或本地 commit push 代码，GitHub Actions 将自动运行并同步成绩。
