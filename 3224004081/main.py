# -*- coding: utf-8 -*-
"""
论文查重程序（兼容纯文本 / GitHub HTML 页面）
用法: python main.py [原文文件] [抄袭版论文文件] [答案文件]
"""
import sys
import os
import math
import re
from collections import Counter
from html.parser import HTMLParser

try:
    import jieba
except ImportError:
    jieba = None


# ---------- HTML 清洗 ----------
class _GitHubBlobParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_blob_code = False
        self.lines = []
        self._buf = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        cls = attrs.get('class', '')
        if tag == 'td' and 'blob-code' in cls:
            self.in_blob_code = True
            self._buf = []

    def handle_endtag(self, tag):
        if tag == 'td' and self.in_blob_code:
            self.lines.append(''.join(self._buf))
            self.in_blob_code = False

    def handle_data(self, data):
        if self.in_blob_code:
            self._buf.append(data)


def clean_html(text):
    """若是 HTML 则提取正文；否则原样返回"""
    if '<html' not in text.lower() and '<!doctype' not in text.lower():
        return text

    # 优先尝试提取 GitHub blob 正文
    parser = _GitHubBlobParser()
    parser.feed(text)
    if parser.lines:
        return '\n'.join(parser.lines)

    # 退化方案：粗暴去标签
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', text, flags=re.S | re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.S | re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = (text.replace('&nbsp;', ' ').replace('&amp;', '&')
                .replace('&lt;', '<').replace('&gt;', '>')
                .replace('&quot;', '"'))
    return re.sub(r'\s+', ' ', text)


# ---------- 文件读取 ----------
def read_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"文件不存在: {path}")
    for enc in ('utf-8', 'gbk', 'gb18030'):
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"无法解码文件: {path}")


# ---------- 分词与相似度 ----------
def tokenize(text):
    if not text:
        return []
    words = jieba.lcut(text) if jieba is not None else list(text)
    return [w.strip() for w in words
            if w.strip() and not re.match(r'^\W+$', w)]


def cosine_similarity(text1, text2):
    words1, words2 = tokenize(text1), tokenize(text2)
    if not words1 or not words2:
        return 0.0
    v1, v2 = Counter(words1), Counter(words2)
    vocab = set(v1) | set(v2)
    dot = sum(v1.get(w, 0) * v2.get(w, 0) for w in vocab)
    n1 = math.sqrt(sum(v * v for v in v1.values()))
    n2 = math.sqrt(sum(v * v for v in v2.values()))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)


def write_answer(path, value):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"{value:.2f}")


# ---------- 主流程 ----------
def main():
    if len(sys.argv) != 4:
        print("用法: python main.py [原文文件] [抄袭版论文文件] [答案文件]")
        sys.exit(1)

    orig_path, copy_path, ans_path = sys.argv[1], sys.argv[2], sys.argv[3]

    try:
        orig_text = clean_html(read_file(orig_path))
        copy_text = clean_html(read_file(copy_path))
    except (FileNotFoundError, ValueError) as e:
        print(f"读取文件失败: {e}")
        sys.exit(1)

    sim = cosine_similarity(orig_text, copy_text)
    write_answer(ans_path, sim)
    print(f"重复率: {sim:.2f}")


if __name__ == '__main__':
    main()