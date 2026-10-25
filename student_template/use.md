# 作业提交与使用指南 (use.md)

本指南指导你如何提交 C 语言作业并获取自动评测成绩。

---

## 方式一：通过仓库 URL 自动审批（推荐，零配置）

1. **创建你的作业仓库**：
   - 在 GitHub 新建公开（Public）仓库（例如 `my-c-homework`）。
   - 将你的作业代码按 `1_main.c`、`2_main.c` 上传至仓库。
   - 务必确保每个代码文件**前三行**包含学号、邮箱、姓名注释：
     ```c
     // 202401010001
     // myemail@example.com
     // 张三
     ```

2. **提交 URL 进行审批**：
   - 打开评测仓库：[ftl-is-king/homowork/issues](https://github.com/ftl-is-king/homowork/issues)
   - 点击 **New Issue**，选择 **作业 URL 提交与自动评测** 模板。
   - 填写学号、姓名以及你的作业仓库链接（例如 `https://github.com/your-username/my-c-homework`）。
   - 点击提交 Issue。

3. **查看评测结果**：
   - 提交后 1~2 分钟内，GitHub Actions 会自动运行评测。
   - 评测完成后，机器人会在你的 Issue 下自动回复测试点详情、运行耗时、内存占用以及最终得分，成绩自动登记入库！

---

## 方式二：模板仓库 + GitHub Actions 自动评测

若你使用本模板仓库，也可以配置 `MY_URL` 实现推送即自动测试并上传成绩。

### 1. 配置密钥 Secret
1. 打开你新建的作业仓库，点击 **Settings** >> **Secrets and variables** >> **Actions**。
2. 点击 **New repository secret** 按钮。
3. 填入名称：`MY_URL`。
4. 填入内容：向助教或群文件索取提供的 GitHub 访问凭证（Token）。
5. 点击 **Add secret** 保存。

### 2. 编写与提交代码
1. 点击项目中的 `1_main.c`。
2. 点击右上角的铅笔 ✏️ 图标编辑代码。
3. 确认前三行信息正确，编写并测试逻辑。
4. 点击右上角 **Commit changes...** 提交代码。

### 3. 查看 Actions 测试详情
1. 点击仓库上方的 **Actions** 标签页。
2. 点击列表中最新的评测工作流，进入查看详细编译与用例通过日志。
3. 评测成功后，成绩将自动回传至主评测仓库。
