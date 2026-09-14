# -*- coding: utf-8 -*-
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import cosine_similarity, read_file, write_answer, tokenize, clean_html

passed = 0
failed = 0

def check(name, condition):
    global passed, failed
    if condition:
        print("[PASS] " + name)
        passed += 1
    else:
        print("[FAIL] " + name)
        failed += 1

# 1. 完全相同
check("完全相同文本相似度为1", abs(cosine_similarity("今天天气很好", "今天天气很好") - 1.0) < 1e-9)

# 2. 完全不同
check("完全不同文本相似度为0", cosine_similarity("今天天气很好", "苹果香蕉橘子") == 0.0)

# 3. 部分重叠
sim = cosine_similarity("今天是星期天天气晴", "今天是周天天气晴朗")
check("部分重叠相似度在0到1之间", 0 < sim < 1)

# 4. 一边为空
check("一边为空相似度为0", cosine_similarity("", "任何内容") == 0.0 and cosine_similarity("任何内容", "") == 0.0)

# 5. 两边都为空
check("两边都为空相似度为0", cosine_similarity("", "") == 0.0)

# 6. 分词过滤标点
check("分词过滤标点", tokenize("你好，世界！") == ["你好", "世界"])

# 7. 空字符串分词
check("空字符串分词为空列表", tokenize("") == [])

# 8. 读取不存在的文件
try:
    read_file("not_exist_file.txt")
    check("读取不存在文件抛异常", False)
except FileNotFoundError:
    check("读取不存在文件抛异常", True)

# 9. 正常读取文件
with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, encoding='utf-8') as f:
    f.write("测试内容")
    name = f.name
try:
    check("正常读取文件内容", read_file(name) == "测试内容")
finally:
    os.remove(name)

# 10. 答案保留两位小数
with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as f:
    name = f.name
try:
    write_answer(name, 0.123456)
    with open(name, encoding='utf-8') as f:
        check("答案保留两位小数", f.read() == "0.12")
finally:
    os.remove(name)

# 11. clean_html 对纯文本原样返回
check("纯文本clean_html原样返回", clean_html("普通文本") == "普通文本")

print("")
print("通过: %d, 失败: %d" % (passed, failed))
sys.exit(0 if failed == 0 else 1)