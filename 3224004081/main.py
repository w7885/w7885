import sys
import os


def read_file(file_path):
    """
    读取论文文件。
    使用 utf-8-sig，可以同时兼容普通 UTF-8 和带 BOM 的 UTF-8 文件。
    """
    with open(file_path, "r", encoding="utf-8-sig") as file:
        return file.read()


def preprocess(text):
    """
    对论文进行预处理。

    删除空格、换行、制表符等空白字符，
    保留正文中的中文、英文、数字和标点符号。
    """
    return "".join(text.split())


def calculate_lcs(text1, text2):
    """
    使用滚动数组计算两个文本的最长公共子序列（LCS）长度。

    时间复杂度：O(n * m)
    空间复杂度：O(min(n, m))
    """
    # 让 text2 成为较短的文本，减少内存使用
    if len(text1) < len(text2):
        text1, text2 = text2, text1

    m = len(text2)

    # dp[j] 表示当前计算到的位置的 LCS 长度
    dp = [0] * (m + 1)

    for char1 in text1:
        # prev 表示上一行、上一列的值
        prev = 0

        for j in range(1, m + 1):
            # 保存原来的 dp[j]
            temp = dp[j]

            if char1 == text2[j - 1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])

            prev = temp

    return dp[m]


def calculate_repetition_rate(original_text, plagiarized_text):
    """
    计算论文重复率。

    重复率 = 最长公共子序列长度 / 原文长度 × 100
    """
    if len(original_text) == 0:
        return 0.0

    lcs_length = calculate_lcs(original_text, plagiarized_text)

    return lcs_length / len(original_text) * 100


def write_result(file_path, repetition_rate):
    """
    将重复率写入答案文件，保留两位小数。
    """
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"{repetition_rate:.2f}")


def main():
    # 检查命令行参数数量
    if len(sys.argv) != 4:
        print(
            "用法：python main.py "
            "[原文文件绝对路径] "
            "[抄袭版论文文件绝对路径] "
            "[答案文件绝对路径]"
        )
        sys.exit(1)

    original_path = sys.argv[1]
    plagiarized_path = sys.argv[2]
    result_path = sys.argv[3]

    # 检查输入路径是否为绝对路径
    if not os.path.isabs(original_path):
        print("错误：原文文件路径必须是绝对路径")
        sys.exit(1)

    if not os.path.isabs(plagiarized_path):
        print("错误：抄袭版论文文件路径必须是绝对路径")
        sys.exit(1)

    if not os.path.isabs(result_path):
        print("错误：答案文件路径必须是绝对路径")
        sys.exit(1)

    try:
        # 检查输入文件是否存在
        if not os.path.isfile(original_path):
            raise FileNotFoundError(f"原文文件不存在：{original_path}")

        if not os.path.isfile(plagiarized_path):
            raise FileNotFoundError(f"抄袭版论文文件不存在：{plagiarized_path}")

        # 读取文件
        original_text = read_file(original_path)
        plagiarized_text = read_file(plagiarized_path)

        # 文本预处理
        original_text = preprocess(original_text)
        plagiarized_text = preprocess(plagiarized_text)

        # 计算重复率
        repetition_rate = calculate_repetition_rate(
            original_text,
            plagiarized_text
        )

        # 写入答案文件
        write_result(result_path, repetition_rate)

    except FileNotFoundError as e:
        print(f"错误：{e}")
        sys.exit(1)

    except PermissionError as e:
        print(f"错误：没有文件访问权限：{e}")
        sys.exit(1)

    except UnicodeDecodeError as e:
        print(f"错误：文件编码无法识别：{e}")
        sys.exit(1)

    except OSError as e:
        print(f"错误：文件读写失败：{e}")
        sys.exit(1)

    except Exception as e:
        print(f"错误：程序运行失败：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()