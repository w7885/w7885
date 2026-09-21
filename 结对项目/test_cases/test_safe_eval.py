# test_cases/test_safe_eval.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
from fractions import Fraction
from Myapp import safe_eval

def test_safe_eval_add():
    """加法"""
    assert safe_eval("1/6 + 1/8") == Fraction(7,24)

def test_safe_eval_sub():
    """减法，全角减号 −"""
    assert safe_eval("5 − 2") == Fraction(3,1)

def test_safe_eval_mul():
    """乘法 ×"""
    assert safe_eval("2 × 3") == Fraction(6,1)

def test_safe_eval_div():
    """除法 ÷"""
    assert safe_eval("1/4 ÷ 1/2") == Fraction(1,2)

def test_safe_eval_mixed_number():
    """带分数运算"""
    assert safe_eval("2’3/8 + 1") == Fraction(27,8)

def test_safe_eval_bracket():
    """括号表达式"""
    assert safe_eval("(2 + 3) × 4") == Fraction(20,1)

def test_safe_eval_zero_div():
    """除零抛出异常"""
    with pytest.raises(ZeroDivisionError):
        safe_eval("3 ÷ 0")

def test_safe_eval_invalid_expr():
    """非法表达式抛出异常"""
    with pytest.raises(ValueError):
        safe_eval("2 + abc")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
