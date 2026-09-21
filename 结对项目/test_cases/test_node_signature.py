# test_cases/test_node_signature.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from fractions import Fraction
from Myapp import Node

def test_add_commute_dup():
    """2+3 和3+2 重复"""
    n1 = Node(value=Fraction(2), text="2")
    n2 = Node(value=Fraction(3), text="3")
    expr_a = Node(op="+", left=n1, right=n2)
    expr_b = Node(op="+", left=n2, right=n1)
    assert expr_a.signature() == expr_b.signature()

def test_mul_commute_dup():
    """6×8 和8×6 重复"""
    n1 = Node(value=Fraction(6), text="6")
    n2 = Node(value=Fraction(8), text="8")
    expr_a = Node(op="×", left=n1, right=n2)
    expr_b = Node(op="×", left=n2, right=n1)
    assert expr_a.signature() == expr_b.signature()

def test_add_associate_not_dup():
    """(1+2)+3 和 1+(2+3) 不重复（只处理交换律）"""
    n1 = Node(value=Fraction(1), text="1")
    n2 = Node(value=Fraction(2), text="2")
    n3 = Node(value=Fraction(3), text="3")
    expr1 = Node(op="+", left=Node(op="+", left=n1, right=n2), right=n3)
    expr2 = Node(op="+", left=n1, right=Node(op="+", left=n2, right=n3))
    assert expr1.signature() != expr2.signature()

def test_chain_add_reverse_not_dup():
    """(1+2)+3 和(3+2)+1 不重复"""
    n1 = Node(value=Fraction(1), text="1")
    n2 = Node(value=Fraction(2), text="2")
    n3 = Node(value=Fraction(3), text="3")
    expr1 = Node(op="+", left=Node(op="+", left=n1, right=n2), right=n3)
    expr2 = Node(op="+", left=Node(op="+", left=n3, right=n2), right=n1)
    assert expr1.signature() != expr2.signature()



if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
