# 作业评测系统使用指南 (use.md)

欢迎使用 C 语言作业自动化评测系统！

---

## 提交方式一：通过 GitHub 仓库 URL 提交（推荐）

该方式无需配置任何 Secret，只需提供包含作业代码的公开 GitHub 仓库 URL 即可。

### 步骤说明：
1. **准备代码**：
   - 建立你的 GitHub 代码仓库（如 `c-homework`）。
   - 将作业代码文件命名为 `1_main.c`、`2_main.c` 等（以题目序号开头）。
   - 代码前三行格式必须为：
     ```c
     // 学号 (例如: 202401010001)
     // 邮箱 (例如: student@example.com)
     // 姓名 (例如: 张三)
     ```
2. **在评测仓库提交 Issue**：
   - 进入 [ftl-is-king/homowork/issues](https://github.com/ftl-is-king/homowork/issues)。
   - 点击 **New Issue**，选择 **作业 URL 提交与自动评测**。
   - 填入学号、姓名以及你的仓库地址（例如 `https://github.com/ftl-is-king/my-homework`）。
   - 点击提交。
3. **等待系统自动审批**：
   - GitHub Actions 会在后台自动克隆并运行测试。
   - 评测完成后会在 Issue 下方自动回复详细的成绩单（包含各用例耗时、内存、得分与总分）。
   - 成绩自动合并并计入主仓库的 `test.csv`。

---

## 提交方式二：使用学生模板与 GitHub Actions 自动回传

若你使用了 `student_template` 目录构建模板仓库，可以通过设置 `MY_URL` 实现推送即自动评测并同步成绩。

### 步骤说明：
1. **基于模板创建仓库**：
   - 使用包含 `student_template` 结构的仓库。
2. **配置 Secret**：
   - 在个人作业仓库中点击 **Settings** -> **Secrets and variables** -> **Actions**。
   - 点击 **New repository secret**。
   - Secret 名称设置为：`MY_URL`。
   - Secret 内容设置为群文件中分发的访问凭据。
3. **提交代码**：
   - 修改 `1_main.c` 并提交（Commit & Push）。
   - 触发个人仓库的 GitHub Actions。
   - Action 会拉取评测脚本执行测试，并将最新成绩回传推送到主仓库 `test.csv`。
