import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import os
from Myapp import grade

def test_grade_mixed_correct_wrong():
    """混合正确、错误答案批改"""
    exer_txt = "Exer_tmp.txt"
    ans_txt = "Ans_tmp.txt"
    grade_txt = "Grade.txt"  # 固定为Myapp输出的文件名
    with open(exer_txt, "w", encoding="utf-8") as f:
        f.write("1. 1+1\n2. 2+2\n3. 3+3\n")
    with open(ans_txt, "w", encoding="utf-8") as f:
        f.write("1. 2\n2. 5\n3. 6\n")
    grade(exer_txt, ans_txt)  # 去掉第三个参数
    with open(grade_txt, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Correct: 2 (1, 3)" in content
    assert "Wrong: 1 (2)" in content
    os.remove(exer_txt)
    os.remove(ans_txt)
    os.remove(grade_txt)

def test_grade_answer_with_space():
    """答案前后带多余空格，正常识别"""
    exer_txt = "Exer_tmp2.txt"
    ans_txt = "Ans_tmp2.txt"
    grade_txt = "Grade.txt"
    with open(exer_txt, "w", encoding="utf-8") as f:
        f.write("1. 1/6 + 1/8\n")
    with open(ans_txt, "w", encoding="utf-8") as f:
        f.write("1.  7/24  \n")
    grade(exer_txt, ans_txt)
    with open(grade_txt, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Correct: 1 (1)" in content
    os.remove(exer_txt)
    os.remove(ans_txt)
    os.remove(grade_txt)

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
