import re
import os
from Myapp import generate_exercises

def strip_index(s: str) -> str:
    """去除行首题号，如 1. 1+2 → 1+2"""
    return re.sub(r"^\d+\.\s*", "", s).strip()

def test_generate_op_count_no_more_than_3():
    """需求：每题运算符数量不超过3个，至少1个"""
    generate_exercises(n=30, r=10)
    op_pat = re.compile(r"[+−×÷]")
    with open("Exercises.txt", "r", encoding="utf-8") as f:
        for line in f:
            expr = strip_index(line)
            if not expr:
                continue
            ops = op_pat.findall(expr)
            assert 1 <= len(ops) <= 3, f"运算符数量违规：{expr}"
    os.remove("Exercises.txt")
    os.remove("Answers.txt")

def test_generate_all_numbers_less_than_r():
    """需求：r=10，生成所有数字不能包含10"""
    generate_exercises(n=30, r=10)
    num_pat = re.compile(r"\d+")
    with open("Exercises.txt", "r", encoding="utf-8") as f:
        for line in f:
            expr = strip_index(line)
            if not expr:
                continue
            nums = num_pat.findall(expr)
            for num_str in nums:
                num = int(num_str)
                assert num < 10, f"出现数字>=10：{expr}"
    os.remove("Exercises.txt")
    os.remove("Answers.txt")

def test_generate_10000_stress():
    """需求：支持一万道题目生成，语义上无重复（依据signature查重）"""
    # 接收generate返回的所有signature
    sig_list = generate_exercises(n=10000, r=10)
    sig_set = set(sig_list)
    # 校验：返回的signature数量=10000，语义无重复
    assert len(sig_set) == 10000
