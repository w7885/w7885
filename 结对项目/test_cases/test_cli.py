# test_cases/test_cli.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import subprocess
import os

def test_cli_n_zero():
    """-n 0：n不能为0，输出错误提示"""
    ret = subprocess.run(["python", "Myapp.py", "-n", "0", "-r", "10"], capture_output=True, text=True)
    assert "错误：-n 必须为正整数。" in ret.stdout


def test_cli_n_negative():
    """-n -5：n负数，输出错误提示"""
    ret = subprocess.run(["python", "Myapp.py", "-n", "-5", "-r", "10"], capture_output=True, text=True)
    assert "错误：-n 必须为正整数。" in ret.stdout


def test_cli_r_less_than_2():
    """-r 1：r必须大于1，输出错误提示"""
    ret = subprocess.run(["python", "Myapp.py", "-n", "10", "-r", "1"], capture_output=True, text=True)
    assert "错误：-r 必须大于 1。" in ret.stdout


def test_cli_only_n_no_r():
    """只传-n，缺少-r参数，输出错误提示"""
    ret = subprocess.run(["python", "Myapp.py", "-n", "10"], capture_output=True, text=True)
    assert "错误：生成题目时必须同时指定 -n 和 -r 参数。" in ret.stdout


def test_cli_only_r_no_n():
    """只传-r，缺少-n参数，输出错误提示"""
    ret = subprocess.run(["python", "Myapp.py", "-r", "10"], capture_output=True, text=True)
    assert "错误：生成题目时必须同时指定 -n 和 -r 参数。" in ret.stdout



if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
