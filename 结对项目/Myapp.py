import argparse
import random
import re
from fractions import Fraction

# ----------------------------
# 常量
# ----------------------------

MAX_OPS = 3              # 每题最多运算符个数
MAX_ATTEMPTS_FACTOR = 300  # 生成题目时最大尝试次数 = n * 该系数
OPS = ["+", "−", "×", "÷"]


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
    """
    解析题目中的分数格式，如 3/5、2’3/8。
    会清洗中文标点、多余空格。
    """
    s = s.strip().replace("。", "").replace("，", "").replace(" ", "")
    if not s:
        raise ValueError("空答案")
    if "’" in s:
        whole, frac = s.split("’")
        a, b = frac.split("/")
        return Fraction(int(whole) * int(b) + int(a), int(b))
    if "/" in s:
        a, b = s.split("/")
        return Fraction(int(a), int(b))
    return Fraction(int(s), 1)


# ----------------------------
# 自己实现的分数表达式求值器（替代 eval）
# ----------------------------

class FractionEvaluator:
    """
    递归下降解析器，支持的文法：
        expr   := term (('+' | '-') term)*
        term   := factor (('*' | '/') factor)*
        factor := number | '(' expr ')'
        number := 整数 | 分数 a/b | 带分数 a’b/c
    """

    def __init__(self, text: str):
        # 统一符号
        text = text.replace("×", "*").replace("÷", "/").replace("−", "-")
        self.text = text
        self.pos = 0

    def parse(self) -> Fraction:
        result = self.expr()
        self.skip_ws()
        if self.pos != len(self.text):
            raise ValueError(f"表达式解析未完成: {self.text!r} at {self.pos}")
        return result

    def skip_ws(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def peek(self) -> str:
        self.skip_ws()
        if self.pos < len(self.text):
            return self.text[self.pos]
        return ""

    def expr(self) -> Fraction:
        value = self.term()
        while True:
            ch = self.peek()
            if ch == "+":
                self.pos += 1
                value += self.term()
            elif ch == "-":
                self.pos += 1
                value -= self.term()
            else:
                break
        return value

    def term(self) -> Fraction:
        value = self.factor()
        while True:
            ch = self.peek()
            if ch == "*":
                self.pos += 1
                value *= self.factor()
            elif ch == "/":
                self.pos += 1
                divisor = self.factor()
                if divisor == 0:
                    raise ZeroDivisionError("除数为 0")
                value /= divisor
            else:
                break
        return value

    def factor(self) -> Fraction:
        ch = self.peek()
        if ch == "(":
            self.pos += 1
            value = self.expr()
            if self.peek() != ")":
                raise ValueError("缺少右括号")
            self.pos += 1
            return value
        return self.number()

    def number(self) -> Fraction:
        self.skip_ws()
        start = self.pos
        # 带分数 a’b/c
        m = re.match(r"(\d+)’(\d+)/(\d+)", self.text[self.pos:])
        if m:
            self.pos += m.end()
            whole, a, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if b == 0:
                raise ZeroDivisionError("分母为 0")
            return Fraction(whole * b + a, b)
        # 普通分数 a/b
        m = re.match(r"(\d+)/(\d+)", self.text[self.pos:])
        if m:
            self.pos += m.end()
            a, b = int(m.group(1)), int(m.group(2))
            if b == 0:
                raise ZeroDivisionError("分母为 0")
            return Fraction(a, b)
        # 整数
        m = re.match(r"\d+", self.text[self.pos:])
        if m:
            self.pos += m.end()
            return Fraction(int(m.group(0)), 1)
        raise ValueError(f"无法解析数字: {self.text[start:]!r}")


def safe_eval(expr: str) -> Fraction:
    """用 FractionEvaluator 求值，替代 eval"""
    return FractionEvaluator(expr).parse()


# ----------------------------
# 表达式树节点
# ----------------------------

class Node:
    def __init__(self, op=None, left=None, right=None, value=None, text=None):
        self.op = op
        self.left = left
        self.right = right
        self.value = value
        self.text = text

    def to_expr(self) -> str:
        if self.op is None:
            return self.text
        return f"{self.left.to_expr()} {self.op} {self.right.to_expr()}"

    def _flatten(self, op):
        """把同一运算符的连续子节点扁平化，用于处理结合律"""
        if self.op == op:
            return self.left._flatten(op) + self.right._flatten(op)
        return [self]

    def signature(self):
        """
        去重签名：
        - + 和 × 满足交换律和结合律，扁平化后排序
        - − 和 ÷ 不满足，保持左右顺序
        """
        if self.op is None:
            return ("num", str(self.value))
        if self.op in ("+", "×"):
            parts = self._flatten(self.op)
            return (self.op, tuple(sorted(p.signature() for p in parts)))
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
        # 题目要求：除法结果应是真分数（分子 < 分母）
        if val.denominator == 1 or abs(val.numerator) >= val.denominator:
            return None
        return Node(op="÷", left=left, right=right, value=val)
    return None


def gen_expr_node(r: int, max_ops: int = MAX_OPS):
    """随机生成一个合法表达式，运算符个数 1~max_ops"""
    num_ops = random.randint(1, max_ops)
    ops = [random.choice(OPS) for _ in range(num_ops)]
    leaves = [make_number_node(r) for _ in range(num_ops + 1)]

    def build(nodes, op_list):
        if len(nodes) == 1:
            return nodes[0]
        i = random.randint(0, len(nodes) - 2)
        merged = combine_node(op_list[0], nodes[i], nodes[i + 1])
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
    max_attempts = n * MAX_ATTEMPTS_FACTOR
    while len(exercises) < n and attempts < max_attempts:
        attempts += 1
        node = gen_expr_node(r, max_ops=MAX_OPS)
        if node is None:
            continue
        sig = node.signature()
        if sig in signatures:
            continue
        signatures.add(sig)
        exercises.append(f"{node.to_expr()} =")
        answers.append(format_fraction(node.value))

    if len(exercises) < n:
        print(f"警告：目标 {n} 道，实际只生成了 {len(exercises)} 道不重复题目。")

    with open("Exercises.txt", "w", encoding="utf-8") as f:
        for i, e in enumerate(exercises, start=1):
            f.write(f"{i}.{e}\n")

    with open("Answers.txt", "w", encoding="utf-8") as f:
        for i, a in enumerate(answers, start=1):
            f.write(f"{i}.{a}\n")

    print(f"已生成 {len(exercises)} 道题目，保存到 Exercises.txt 和 Answers.txt。")


# ----------------------------
# 批改
# ----------------------------

def grade(exercise_file: str, answer_file: str):
    def strip_index(line: str) -> str:
        """去掉行首的 '1.'、'2.' 这样的序号"""
        return re.sub(r"^\s*\d+\.\s*", "", line).strip()

    with open(exercise_file, "r", encoding="utf-8") as f:
        exercises = [strip_index(line) for line in f if line.strip()]
    with open(answer_file, "r", encoding="utf-8") as f:
        answers = [strip_index(line) for line in f if line.strip()]

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
        except Exception as e:
            print(f"第 {i} 题解析失败: {e}")
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

    if args.n <= 0:
        print("错误：-n 必须为正整数。")
        return

    if args.r <= 1:
        print("错误：-r 必须大于 1。")
        return

    generate_exercises(args.n, args.r)


if __name__ == "__main__":
    main()