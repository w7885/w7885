# test_cases/test_fraction.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
from fractions import Fraction
from Myapp import format_fraction, parse_fraction

def test_format_fraction_integer():
    """整数格式化"""
    assert format_fraction(Fraction(5,1)) == "5"
    assert format_fraction(Fraction(0,1)) == "0"

def test_format_fraction_proper():
    """真分数格式化"""
    assert format_fraction(Fraction(3,5)) == "3/5"
    assert format_fraction(Fraction(1,8)) == "1/8"

def test_format_fraction_mixed():
    """带分数格式化"""
    assert format_fraction(Fraction(19,8)) == "2’3/8"
    assert format_fraction(Fraction(7,2)) == "3’1/2"

def test_parse_fraction_integer():
    """解析整数"""
    assert parse_fraction("6") == Fraction(6,1)

def test_parse_fraction_proper():
    """解析普通真分数"""
    assert parse_fraction("3/5") == Fraction(3,5)

def test_parse_fraction_mixed():
    """解析带分数"""
    assert parse_fraction("2’3/8") == Fraction(19,8)
    assert parse_fraction("1’1/2") == Fraction(3,2)

def test_parse_fraction_clean_punct():
    """解析时自动清理空格、中文标点"""
    assert parse_fraction("  2’3/8 。") == Fraction(19,8)

def test_parse_empty():
    """空字符串抛出异常"""
    with pytest.raises(ValueError):
        parse_fraction("")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
