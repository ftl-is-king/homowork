"""
@FileName：   test.py
@Description：C语言/Python作业自动化评测主程序
@Version:     V2.0
@Software：   Python 3

功能特性：
- 支持指定目录或自动发现待测程序
- 支持 C 语言编译运行与 Python 解释运行
- 自动评估代码耗时与内存消耗 (Linux /usr/bin/time -v 支持，并具备跨平台回退兼容)
- 结合正确率与时空开销综合评分
- 学生身份白名单核验 (DB.csv)
- 自动更新成绩表 (test.csv) 并支持推送到远程 GitHub 仓库
"""

import os
import sys
import re
import time
import math
import argparse
import json
import shutil
import statistics
import subprocess
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 兼容 Windows 控制台 UTF-8 输出
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import config

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class Student:
    """
    学生实体类，负责代码编译、执行评测、性能打分以及成绩归档
    """

    def __init__(self, student_id: int, name: str, email: str = "", csv_path: str = "test.csv"):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.csv_path = csv_path
        self.execution_time = None  # 毫秒 (ms)
        self.memory_usage = None    # 千字节 (KB)
        self.score = 0              # 百分制综合得分
        self.right = ""             # 测试点通过比 (如 5/5)
        self.right_count = 0
        self.total_count = 0
        self.details = []

    def run_program(
        self,
        command_prefix: list,
        input_count: int,
        gcc_cmd: list,
        exec_file: str,
        test_type: str = ".c",
        input_list: list = config.USER_INPUT,
        answer_list: list = config.ANSWER,
    ) -> bool:
        """
        编译并运行学生代码，遍历所有测试用例打分
        """
        print("\n" + "—" * 12 + f" 开始测试第 {input_count} 题 " + "—" * 12 + "\n")

        # 1. 编译 (仅 C 语言)
        if test_type == ".c":
            try:
                gcc_result = subprocess.run(gcc_cmd, capture_output=True, text=True)
                if gcc_result.returncode != 0 or not os.path.exists(exec_file):
                    print(f"❌ 编译失败，编译器输出：\n{gcc_result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ 编译异常: {e}")
                return False

        time_list = []
        memory_list = []
        right_count = 0

        if input_count - 1 >= len(input_list):
            print(f"⚠️ 题目编号 {input_count} 超出配置题库范围")
            return False

        cases = input_list[input_count - 1]
        expected_answers = answer_list[input_count - 1]
        input_len = len(cases)
        has_time_cmd = shutil.which("time") is not None or os.path.exists("/usr/bin/time")

        # 2. 遍历测试用例
        for i in range(input_len):
            case_input = cases[i]
            expected = expected_answers[i]
            run_cmd = list(command_prefix) + [exec_file] if command_prefix else [exec_file]

            start_time = time.perf_counter()
            try:
                result = subprocess.run(
                    run_cmd,
                    input=case_input,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            except subprocess.TimeoutExpired:
                print(f"⚠️ 第 {i + 1} 个测试用例运行超时 (5s)")
                return False
            except Exception as e:
                print(f"❌ 运行异常: {e}")
                return False
            end_time = time.perf_counter()

            elapsed_ms = (end_time - start_time) * 1000
            time_list.append(elapsed_ms)

            # 3. 提取内存信息
            max_resident_size = 1024  # 默认基准值
            if has_time_cmd and result.stderr:
                match = re.search(r"Maximum resident set size \(kbytes\): (\d+)", result.stderr)
                if match:
                    max_resident_size = int(match.group(1))
            memory_list.append(max_resident_size)

            # 4. 验证标准输出
            # 兼容 Windows \r\n 和 Linux \n，清理首尾空白
            normalized_output = result.stdout.replace("\r\n", "\n").strip()
            # 搜索完整答案
            pattern = rf"(?<!\d){re.escape(expected)}(?!\d)"
            if re.search(pattern, normalized_output):
                print(f"  [测试点 {i + 1}/{input_len}] >> ✅ 通过")
                right_count += 1
            else:
                # 再次做宽容的空白切分匹配
                output_tokens = normalized_output.split()
                expected_tokens = expected.split()
                if output_tokens == expected_tokens:
                    print(f"  [测试点 {i + 1}/{input_len}] >> ✅ 通过")
                    right_count += 1
                else:
                    print(f"  [测试点 {i + 1}/{input_len}] >> ❌ 错误 (期望: '{expected}', 实际输出: '{normalized_output}')")

        self.right_count = right_count
        self.total_count = input_len
        self.right = f"{right_count}/{input_len}"

        if right_count == input_len:
            print(f"\n🎉 恭喜你通过了全部测试点！({self.right})")
        elif right_count > 0:
            print(f"\n⚠️ 通过了部分测试点：({self.right})")
        else:
            print("\n❌ 未通过任何测试点，请检查逻辑并重新提交。")

        # 5. 计算去除极值后的平均耗时与内存
        if len(time_list) > 2:
            avg_time = statistics.mean(sorted(time_list)[1:-1])
            avg_memory = statistics.mean(sorted(memory_list)[1:-1])
        else:
            avg_time = statistics.mean(time_list)
            avg_memory = statistics.mean(memory_list)

        self.execution_time = avg_time
        self.memory_usage = avg_memory
        self.score = right_count * (config.CORRECTNESS_WEIGHT / input_len)
        return True

    def get_perf_score(self) -> float:
        """
        计算性能分 (时间、内存各满分 20 分，采用指数衰减曲线)
        """
        if self.execution_time is None or self.memory_usage is None:
            return 0.0

        max_score = config.MAX_PERF_SCORE
        t_full = config.TIME_FULL_MARKS_MS
        t_zero = config.TIME_ZERO_MS
        m_full = config.MEMORY_FULL_MARKS_KB
        m_zero = config.MEMORY_ZERO_KB

        # 时间分
        if self.execution_time <= t_full:
            time_score = max_score
        elif self.execution_time >= t_zero:
            time_score = 0.0
        else:
            time_score = max_score * math.exp(-10 * (self.execution_time - t_full) / (t_zero - t_full))

        # 内存分
        if self.memory_usage <= m_full:
            mem_score = max_score
        elif self.memory_usage >= m_zero:
            mem_score = 0.0
        else:
            mem_score = max_score * math.exp(-1.5 * (self.memory_usage - m_full) / (m_zero - m_full))

        return time_score + mem_score

    def log_results(self, count: int) -> bool:
        """
        登记成绩到 CSV 文件
        """
        current_time = datetime.now() + timedelta(hours=8)  # UTC+8
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        if self.execution_time is None or self.memory_usage is None:
            print("未记录结果：程序未成功运行。")
            return False

        # 计算总分 (正确率分 + 性能分)
        if self.score > 0:
            self.score += self.get_perf_score()
        else:
            self.execution_time = 0
            self.memory_usage = 0

        result_data = {
            "学号": self.student_id,
            "姓名": self.name,
            f"第{count}题运行时间(ms)": round(self.execution_time, 2),
            f"第{count}题运行内存(kb)": round(self.memory_usage, 2),
            f"第{count}题成绩": round(self.score, 2),
            f"第{count}题测试点通过数": self.right,
        }

        print(f"提交时间 (UTC+8): {formatted_time}")
        print(
            f"第 {count} 题结果: 运行时间 {result_data[f'第{count}题运行时间(ms)']} ms, "
            f"内存 {result_data[f'第{count}题运行内存(kb)']} KB, "
            f"测试点: {result_data[f'第{count}题测试点通过数']}"
        )
        print(f"第 {count} 题总得分: {result_data[f'第{count}题成绩']} / 100\n")

        if current_time > config.DEADLINE:
            print(f"⚠️ 提交已超过截止时间 ({config.DEADLINE})，本次成绩不计入成绩表。")
            return False

        # 确保 CSV 保存目录存在
        csv_dir = os.path.dirname(os.path.abspath(self.csv_path))
        if csv_dir:
            os.makedirs(csv_dir, exist_ok=True)

        # 维护 CSV 文件
        if os.path.exists(self.csv_path):
            try:
                df = pd.read_csv(self.csv_path, dtype={"学号": int})
            except Exception:
                df = pd.DataFrame(columns=["学号", "姓名"])
        else:
            df = pd.DataFrame(columns=["学号", "姓名"])

        # 动态添加缺失列
        for col in result_data.keys():
            if col not in df.columns:
                df[col] = np.nan

        # 更新或新增学生记录
        if self.student_id in df["学号"].values:
            score_col = f"第{count}题成绩"
            existing_score = df.loc[df["学号"] == self.student_id, score_col].values[0]
            if pd.isna(existing_score) or result_data[score_col] > float(existing_score):
                df.loc[
                    df["学号"] == self.student_id,
                    [
                        f"第{count}题运行时间(ms)",
                        f"第{count}题运行内存(kb)",
                        f"第{count}题成绩",
                        f"第{count}题测试点通过数",
                    ],
                ] = (
                    result_data[f"第{count}题运行时间(ms)"],
                    result_data[f"第{count}题运行内存(kb)"],
                    result_data[f"第{count}题成绩"],
                    result_data[f"第{count}题测试点通过数"],
                )
                print("✅ 成绩更新成功（高于历史记录）")
            else:
                print(f"ℹ️ 当前成绩 ({result_data[score_col]}) 未超过已有成绩 ({existing_score})，保留历史最高分。")
                return False
        else:
            df = pd.concat([df, pd.DataFrame([result_data])], ignore_index=True)
            print("✅ 成绩添加成功（首次记录）")

        df.to_csv(self.csv_path, index=False, encoding="utf-8-sig")

        # 同时同步一份到根目录 test.csv（保证双向兼容）
        root_csv = os.path.join(SCRIPT_DIR, "test.csv")
        if os.path.abspath(self.csv_path) != os.path.abspath(root_csv):
            try:
                df.to_csv(root_csv, index=False, encoding="utf-8-sig")
            except Exception:
                pass

        return True

    def push_to_github(self, repo_url: str = config.DEFAULT_REPO_URL):
        """
        使用 MY_URL 凭证推送更新后的成绩表到远程仓库
        """
        my_url = os.environ.get("MY_URL")
        if not my_url:
            print("ℹ️ 未检测到 MY_URL 凭证，跳过自动 Git 推送。")
            return False

        # 规范化目标 Git 仓库地址
        # 若以 https:// 开头，注入凭证：https://<TOKEN>@github.com/...
        clean_url = repo_url
        if "://" in repo_url:
            clean_url = repo_url.split("://", 1)[1]
        remote_target = f"https://{my_url}@{clean_url}"

        subprocess.run(["git", "config", "--local", "user.email", self.email or "actions@github.com"], check=False)
        subprocess.run(["git", "config", "--local", "user.name", self.name or "GitHub Actions"], check=False)

        # 带有 rebase 与重试的 push
        for attempt in range(1, 4):
            try:
                subprocess.run(["git", "remote", "set-url", "origin", remote_target], check=False)
                subprocess.run(["git", "add", self.csv_path], check=False)
                subprocess.run(["git", "commit", "-m", f"feat: {self.name}({self.student_id}) 更新测试成绩 [skip ci]"], check=False)
                # 先拉取最新主干防止冲突
                subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=False)
                push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
                if push_res.returncode == 0:
                    print("🚀 成绩表已成功同步推送至 GitHub 仓库！")
                    return True
                else:
                    print(f"⚠️ Git 推送第 {attempt} 次失败: {push_res.stderr}，尝试重试...")
                    time.sleep(2)
            except Exception as e:
                print(f"⚠️ Git 操作异常: {e}")
                time.sleep(2)

        print("❌ Git 同步失败，请检查网络或 MY_URL 权限。")
        return False


def extract_student_info(file_path: str, db_path: str = "DB.csv", test_type: str = ".c") -> Student | None:
    """
    从代码前两行（或前三行）提取学生学号与姓名，并与白名单数据库 DB.csv 校验
    规则：
    - 第 1 行：学号 (// 202401010001)
    - 第 2 行：姓名 (// 张三) [若包含邮箱注释亦可智能识别提取姓名]
    """
    if not os.path.exists(file_path):
        print(f"❌ 找不到文件: {file_path}")
        return None

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [f.readline() for _ in range(5)]

        comment_prefix = "//" if test_type == ".c" else "#"

        student_id = None
        name = None
        email = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if not line.startswith(comment_prefix):
                continue
            body = line[len(comment_prefix):].strip()

            # 提取学号（纯数字连续 7~15 位）
            if not student_id:
                id_match = re.match(r"^(\d{7,15})$", body)
                if id_match:
                    student_id = int(id_match.group(1))
                    continue

            # 匹配邮箱（可选，不作强制要求）
            if not email and re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", body):
                email = body
                continue

            # 提取姓名（非空字符串，排除纯符号或注释块开始）
            if not name and body and not body.startswith("/*") and not body.startswith("*"):
                name = body
                continue

        if not student_id:
            print(f"❌ [{file_path}] 学号提取失败，请确保代码前两行包含: {comment_prefix} 学号")
            return None
        if not name:
            print(f"❌ [{file_path}] 姓名提取失败，请确保代码前两行包含: {comment_prefix} 姓名")
            return None

        # 白名单数据库核验（仅核对学号与姓名）
        if os.path.exists(db_path):
            try:
                db_df = pd.read_csv(db_path, dtype={"id": int, "学号": int})
                # 支持表头为 id 或 学号
                id_col = "id" if "id" in db_df.columns else "学号"
                name_col = "name" if "name" in db_df.columns else "姓名"

                stu_match = db_df[db_df[id_col] == student_id]
                if stu_match.empty:
                    print(f"⚠️ 数据库 ({db_path}) 中未找到学号 {student_id}，请确认是否具备提交资格。")
                    return None

                db_name = str(stu_match.iloc[0][name_col]).strip()
                if db_name != name:
                    print(f"⚠️ 学号 {student_id} 与姓名 '{name}' 不匹配 (数据库记录为: '{db_name}')！")
                    return None
            except Exception as e:
                print(f"⚠️ 读取数据库异常: {e}，跳过白名单强校验")
        else:
            print(f"ℹ️ 未检测到学生数据库 {db_path}，跳过白名单强校验。")

        return Student(student_id=student_id, name=name, email=email)

    except Exception as e:
        print(f"❌ 提取学生信息失败: {e}")
        return None


def get_submission_files(directory: str, test_type: str = ".c") -> list:
    """
    检索指定目录下的作业代码文件（按文件名开头的题号排序）
    支持根目录直属文件，以及子目录（如 src/、student_template/）递归查找
    """
    if not os.path.isdir(directory):
        return []

    files = []
    # 1. 优先检索根目录
    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)
        if os.path.isfile(full_path) and filename.endswith(test_type):
            match = re.match(r"^(\d+)_.*", filename)
            if match:
                files.append((int(match.group(1)), filename))
            elif filename == f"main{test_type}":
                files.append((1, filename))

    # 2. 若根目录下未找到，检索一级子目录（如 src/ 或子文件夹）
    if not files:
        for root, dirs, filenames in os.walk(directory):
            # 忽略隐藏目录与 Git 目录
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            if root == directory:
                continue
            for filename in filenames:
                if filename.endswith(test_type):
                    rel_path = os.path.relpath(os.path.join(root, filename), directory)
                    match = re.match(r"^(\d+)_.*", filename)
                    if match:
                        files.append((int(match.group(1)), rel_path))
                    elif filename == f"main{test_type}":
                        files.append((1, rel_path))
            if files:
                break

    files.sort(key=lambda x: x[0])
    return files


def main():
    parser = argparse.ArgumentParser(description="作业自动批改与审批评测系统")
    parser.add_argument("--dir", default=None, help="待评测作业文件所在目录")
    parser.add_argument("--type", default=config.TEST_TYPE, help="评测文件类型 (.c 或 .py)")
    parser.add_argument("--db", default=os.path.join(SCRIPT_DIR, "DB.csv"), help="学生白名单数据库文件路径")
    parser.add_argument("--csv", default=os.path.join(SCRIPT_DIR, "test.csv"), help="成绩汇总 CSV 文件路径")
    parser.add_argument("--repo", default=config.DEFAULT_REPO_URL, help="目标远程 Git 仓库")
    parser.add_argument("--no-push", action="store_true", help="不推送 Git 结果")
    parser.add_argument("--json-output", default=None, help="输出评测结果 JSON 文件路径")
    args = parser.parse_args()

    # 智能确定作业目录：优先命令行参数；若未指定且上一级目录存在作业文件则选用 ..，否则用当前目录
    target_dir = args.dir
    if not target_dir:
        parent_files = get_submission_files("..", args.type)
        if parent_files:
            target_dir = ".."
        else:
            target_dir = "."

    files = get_submission_files(target_dir, args.type)
    if not files:
        print(f"⚠️ 在目录 '{target_dir}' 下未找到匹配的待评测文件 (格式如 1_xxx{args.type} 或 main{args.type})")
        sys.exit(0)

    print(f"📁 发现 {len(files)} 份作业文件，开始批量评测...")

    has_time_cmd = shutil.which("time") is not None or os.path.exists("/usr/bin/time")
    time_prefix = ["/usr/bin/time", "-v"] if has_time_cmd else []

    any_updated = False
    last_student = None
    summary_results = []

    for file_num, filename in files:
        file_path = os.path.join(target_dir, filename)
        student = extract_student_info(file_path, db_path=args.db, test_type=args.type)
        if not student:
            print(f"❌ [{filename}] 学生信息提取或校验失败，跳过本题评测。")
            summary_results.append({
                "problem": file_num,
                "file": filename,
                "success": False,
                "error": "学生信息提取或白名单校验失败",
            })
            continue

        student.csv_path = args.csv
        last_student = student
        exec_file = os.path.join(target_dir, f"{filename}.out")

        if args.type == ".c":
            # 兼容 Windows 可执行后缀
            if sys.platform == "win32":
                exec_file = os.path.join(target_dir, f"{filename}.exe")
            gcc_cmd = ["gcc", "-O2", file_path, "-o", exec_file, "-lm"]
            run_cmd_prefix = time_prefix
        else:
            gcc_cmd = []
            run_cmd_prefix = time_prefix + [sys.executable]
            exec_file = file_path

        # 清理旧可执行文件
        if args.type == ".c" and os.path.exists(exec_file):
            try:
                os.remove(exec_file)
            except OSError:
                pass

        success = student.run_program(
            command_prefix=run_cmd_prefix,
            input_count=file_num,
            gcc_cmd=gcc_cmd,
            exec_file=exec_file,
            test_type=args.type,
        )

        if success:
            updated = student.log_results(file_num)
            if updated:
                any_updated = True
            summary_results.append({
                "problem": file_num,
                "file": filename,
                "success": True,
                "student_id": student.student_id,
                "name": student.name,
                "score": round(student.score, 2),
                "right": student.right,
                "time_ms": round(student.execution_time, 2) if student.execution_time else 0,
                "memory_kb": round(student.memory_usage, 2) if student.memory_usage else 0,
            })
        else:
            summary_results.append({
                "problem": file_num,
                "file": filename,
                "success": False,
                "error": "评测未通过或运行超时",
            })

    # 输出统计 JSON 文件
    if args.json_output:
        with open(args.json_output, "w", encoding="utf-8") as jf:
            json.dump(summary_results, jf, ensure_ascii=False, indent=2)

    # 尝试 Git 推送
    if any_updated and not args.no_push and last_student:
        last_student.push_to_github(repo_url=args.repo)

    print(f"\n================ 评测完成，共测试 {len(files)} 题 ================")


if __name__ == "__main__":
    main()
