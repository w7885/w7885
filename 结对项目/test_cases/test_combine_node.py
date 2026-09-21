# test_cases/test_combine_node.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
from fractions import Fraction
from Myapp import Node, combine_node

def test_combine_add():
    """加法合并正常"""
    a = Node(value=Fraction(2), text="2")
    b = Node(value=Fraction(3), text="3")
    res = combine_node("+", a, b)
    assert res is not None
    assert res.value == Fraction(5)

def test_combine_sub_valid():
    """合法减法：5−2，大数减小数"""
    a = Node(value=Fraction(5), text="5")
    b = Node(value=Fraction(2), text="2")
    res = combine_node("−", a, b)
    assert res.value == Fraction(3)

def test_combine_sub_invalid():
    """非法减法：2−5，左边小于右边返回None"""
    a = Node(value=Fraction(2), text="2")
    b = Node(value=Fraction(5), text="5")
    res = combine_node("−", a, b)
    assert res is None

def test_combine_div_valid():
    """合法除法，结果是真分数：1/4 ÷ 1/2 =1/2"""
    a = Node(value=Fraction(1,4), text="1/4")
    b = Node(value=Fraction(1,2), text="1/2")
    res = combine_node("÷", a, b)
    assert res is not None
    assert res.value == Fraction(1,2)

def test_combine_div_invalid_big():
    """非法除法，结果大于等于1，返回None。例如3 ÷ 1/2 =6"""
    a = Node(value=Fraction(3,1), text="3")
    b = Node(value=Fraction(1,2), text="1/2")
    res = combine_node("÷", a, b)
    assert res is None

def test_combine_div_zero():
    """除数为0返回None"""
    a = Node(value=Fraction(3), text="3")
    b = Node(value=Fraction(0), text="0")
    res = combine_node("÷", a, b)
    assert res is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
