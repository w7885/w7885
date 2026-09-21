import argparse
import random
import re
from fractions import Fraction


# ----------------------------
# 分数格式化与解析
# ----------------------------

def format_fraction(fr: Fraction) -> str:
    """将 Fraction 转为题目要求的格式：真分数 a/b，带分数 a’b/c"""
    if fr.denominator == 1:
        return str(fr.numerator)
    if abs(fr.numerator) < fr.denominator:
        return f"{fr.numerator}/{fr.denominator}"
    whole = fr.numerator // fr.denominator
    rem = fr.numerator % fr.denominator
    if rem == 0:
        return str(whole)
    return f"{whole}’{rem}/{fr.denominator}"


def parse_fraction(s: str) -> Fraction:
    """解析题目中的分数格式，如 3/5、2’3/8"""
    s = s.strip()
    if "’" in s:
        whole, frac = s.split("’")
        a, b = frac.split("/")
        return Fraction(int(whole) * int(b) + int(a), int(b))
    if "/" in s:
        a, b = s.split("/")
        return Fraction(int(a), int(b))
    return Fraction(int(s), 1)


def safe_eval(expr: str) -> Fraction:
    """计算表达式，将 ÷ 转为 /，× 转为 *，并支持带分数"""
    expr = expr.replace("×", "*").replace("÷", "/")
    # 把带分数 a’b/c 替换为 (a + b/c)
    def repl(m):
        whole, a, b = m.group(1), m.group(2), m.group(3)
        return f"({whole}+{a}/{b})"
    expr = re.sub(r"(\d+)’(\d+)/(\d+)", repl, expr)
    # 为安全，只允许数字和运算符
    if not re.fullmatch(r"[0-9+\-*/(). ]+", expr):
        raise ValueError("非法表达式")
    return Fraction(eval(expr, {"__builtins__": None}, {}))


# ----------------------------
# 表达式树节点
# ----------------------------

class Node:
    def __init__(self, op=None, left=None, right=None, value=None, text=None):
        self.op = op          # 运算符或 None
        self.left = left
        self.right = right
        self.value = value    # Fraction
        self.text = text      # 叶子文本

    def to_expr(self):
        if self.op is None:
            return self.text
        left = self.left.to_expr()
        right = self.right.to_expr()
        return f"{left} {self.op} {right}"

    def signature(self):
        """用于去重：+ 和 × 交换左右后签名相同"""
        if self.op is None:
            return ("num", str(self.value))
        if self.op in ("+", "×"):
            s1 = self.left.signature()
            s2 = self.right.signature()
            return (self.op, tuple(sorted([s1, s2])))
        else:
            return (self.op, self.left.signature(), self.right.signature())


def make_number_node(r: int) -> Node:
    """生成 0 ~ r-1 的自然数或真分数"""
    if random.random() < 0.5:
        n = random.randint(0, r - 1)
        return Node(value=Fraction(n, 1), text=str(n))
    else:
        den = random.randint(2, max(2, r - 1))
        num = random.randint(1, den - 1)
        fr = Fraction(num, den)
        return Node(value=fr, text=format_fraction(fr))


def combine_node(op: str, left: Node, right: Node):
    """根据运算符合并两个节点，不合法返回 None"""
    if op == "+":
        val = left.value + right.value
        return Node(op="+", left=left, right=right, value=val)
    if op == "−":
        if left.value < right.value:
            return None
        val = left.value - right.value
        return Node(op="−", left=left, right=right, value=val)
    if op == "×":
        val = left.value * right.value
        return Node(op="×", left=left, right=right, value=val)
    if op == "÷":
        if right.value == 0:
            return None
        val = left.value / right.value
        return Node(op="÷", left=left, right=right, value=val)
    return None


def gen_expr_node(r: int, max_ops: int = 3):
    """随机生成一个合法表达式，运算符个数 1~max_ops"""
    num_ops = random.randint(1, max_ops)
    ops = [random.choice(["+", "−", "×", "÷"]) for _ in range(num_ops)]
    leaves = [make_number_node(r) for _ in range(num_ops + 1)]

    def build(nodes, op_list):
        if len(nodes) == 1:
            return nodes[0]
        i = random.randint(0, len(nodes) - 2)
        op = op_list[0]
        merged = combine_node(op, nodes[i], nodes[i + 1])
        if merged is None:
            return None
        new_nodes = nodes[:i] + [merged] + nodes[i + 2:]
        return build(new_nodes, op_list[1:])

    for _ in range(100):
        random.shuffle(leaves)
        node = build(leaves[:], ops[:])
        if node is not None:
            return node
    return None


# ----------------------------
# 生成题目
# ----------------------------

def generate_exercises(n: int, r: int):
    exercises = []
    answers = []
    signatures = set()

    attempts = 0
    while len(exercises) < n and attempts < n * 200:
        attempts += 1
        node = gen_expr_node(r, max_ops=3)
        if node is None:
            continue
        sig = node.signature()
        if sig in signatures:
            continue
        signatures.add(sig)
        expr_text = node.to_expr()
        exercises.append(f"{expr_text} =")
        answers.append(format_fraction(node.value))

    if len(exercises) < n:
        print(f"警告：仅生成了 {len(exercises)} 道不重复题目（目标 {n} 道）。")

    with open("Exercises.txt", "w", encoding="utf-8") as f:
        for e in exercises:
            f.write(e + "\n")

    with open("Answers.txt", "w", encoding="utf-8") as f:
        for a in answers:
            f.write(a + "\n")

    print(f"已生成 {len(exercises)} 道题目，保存到 Exercises.txt 和 Answers.txt。")


# ----------------------------
# 批改
# ----------------------------

def grade(exercise_file: str, answer_file: str):
    with open(exercise_file, "r", encoding="utf-8") as f:
        exercises = [line.strip() for line in f if line.strip()]
    with open(answer_file, "r", encoding="utf-8") as f:
        answers = [line.strip() for line in f if line.strip()]

    if len(exercises) != len(answers):
        print("题目数与答案数不一致！")
        return

    correct = []
    wrong = []

    for i, (ex, ans) in enumerate(zip(exercises, answers), start=1):
        expr = ex.rstrip("=").strip()
        try:
            val = safe_eval(expr)
            user_ans = parse_fraction(ans)
            if val == user_ans:
                correct.append(i)
            else:
                wrong.append(i)
        except Exception:
            wrong.append(i)

    with open("Grade.txt", "w", encoding="utf-8") as f:
        f.write(f"Correct: {len(correct)} ({', '.join(map(str, correct))})\n")
        f.write(f"Wrong: {len(wrong)} ({', '.join(map(str, wrong))})\n")

    print("批改完成，结果保存到 Grade.txt。")


# ----------------------------
# 主入口
# ----------------------------

def main():
    parser = argparse.ArgumentParser(description="小学四则运算题目生成与批改程序")
    parser.add_argument("-n", type=int, help="生成题目个数")
    parser.add_argument("-r", type=int, help="数值范围（自然数、真分数分母的上限，不含该值）")
    parser.add_argument("-e", type=str, help="题目文件")
    parser.add_argument("-a", type=str, help="答案文件")

    args = parser.parse_args()

    if args.e and args.a:
        grade(args.e, args.a)
        return

    if args.n is None or args.r is None:
        parser.print_help()
        print("\n错误：生成题目时必须同时指定 -n 和 -r 参数。")
        return

    if args.r <= 1:
        print("错误：-r 必须大于 1。")
        return

    generate_exercises(args.n, args.r)


if __name__ == "__main__":
    main()