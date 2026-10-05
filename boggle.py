#!/usr/bin/env python3
"""boggle - 终端 Boggle 单词查找器: 随机 4x4 棋盘, DFS 找出所有可组成单词并计分。纯标准库。"""
import argparse
import random
import secrets
import sys

# 内置常用词表(3-8 字母, 全小写)
WORDS = """cat cats dog dogs sun moon star art rat bat hat cap map tap
pen red bed log fog jog sit hit bit kit lit pit win fan man ran pan
game play word time love life hand land water fire earth heart light
stone bread cheese apple table chair house mouse horse sheep goat
tiger lion bear wolf eagle shark snake frog bird fish tree flower
grass road car bus train ship plane bike boat book pen paper
write read play sing dance jump run walk swim climb laugh smile
happy lucky quick brown fox jumps lazy never ever every under over
above below inside outside after before while since until about
again once twice three four five six seven eight nine ten
boggle finds words adjacents diagonal puzzle letter board dice
qu letters score player timer second minute hour day night
morning evening noon week month year spring summer autumn winter
cold hot warm cool rain snow wind cloud storm sunny rainy
code data file text word list set map tree graph node edge
hello world python quick brown fox lazy dog jumps over fence
great small large big tiny huge giant short long tall wide
deep shallow high low fast slow early late new old young
good bad best worst first last next final clear dark bright
black white gray color green blue yellow orange purple pink
one two six eight seven dozen score point win lose draw game
play clue hint solve guess find seek hide search quest task
job work rest sleep wake eat drink cook bake boil fry roast
dance music song sing band drum guitar piano flute violin
tennis swim golf ball bat club racket court field track
apple peach pear plum grape melon lemon lime kiwi mango
bread butter cheese egg milk cake pie soup salad rice
north south east west left right up down high low
one two three four five six seven eight""".split()
WORDS = sorted({w for w in WORDS if w.isalpha() and 3 <= len(w) <= 8})
WORD_SET = set(WORDS)
PREFIXES = set()
for _w in WORDS:
    for _i in range(1, len(_w) + 1):
        PREFIXES.add(_w[:_i])

SIZE = 4


def score_word(word):
    """Boggle 计分: 3-4 字母 1 分, 5->2, 6->3, 7->5, 8+->11。"""
    n = len(word)
    if n <= 4:
        return 1
    if n == 5:
        return 2
    if n == 6:
        return 3
    if n == 7:
        return 5
    return 11


def neighbors(r, c, size=SIZE):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size:
                yield nr, nc


def find_words(board, size=SIZE, min_len=3):
    """DFS 找出棋盘上所有可组成单词(含对角线相邻, 不重复用格)。"""
    found = set()

    def dfs(r, c, path, used):
        ch = board[r][c]
        # Q 骰面按 Qu 处理
        letters = "qu" if ch == "q" else ch
        cur = path + letters
        if cur not in PREFIXES:
            return
        if len(cur) >= min_len and cur in WORD_SET:
            found.add(cur)
        if len(cur) >= 8:
            return
        for nr, nc in neighbors(r, c, size):
            if (nr, nc) not in used:
                used.add((nr, nc))
                dfs(nr, nc, cur, used)
                used.remove((nr, nc))

    for r in range(size):
        for c in range(size):
            dfs(r, c, "", {(r, c)})
    return found


def random_board(rng):
    letters = "abcdefghijklmnopqrstuvwxyz"
    return [[rng.choice(letters) for _ in range(SIZE)] for _ in range(SIZE)]


def parse_board(text):
    t = text.lower().replace(" ", "")
    if len(t) != 16 or not t.isalpha():
        raise ValueError("棋盘必须是 16 个字母(如 CATS...)")
    return [list(t[i * 4:(i + 1) * 4]) for i in range(4)]


def render(board):
    return "\n".join(" ".join(row).upper() for row in board)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="boggle", description="Boggle 单词查找器: 找 4x4 棋盘上所有单词并计分")
    ap.add_argument("--board", help="固定棋盘, 16 个字母")
    ap.add_argument("--min", type=int, default=3, help="最短单词长度(默认 3)")
    ap.add_argument("--seed", type=int, help="随机种子(可复现棋盘)")
    args = ap.parse_args(argv)

    if args.min < 1:
        ap.error("--min 必须 >= 1")
    if args.board:
        try:
            board = parse_board(args.board)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
    else:
        rng = random.Random(args.seed) if args.seed is not None else secrets.SystemRandom()
        board = random_board(rng)

    print("棋盘:")
    print(render(board))
    words = find_words(board, SIZE, args.min)
    total = sum(score_word(w) for w in words)
    print(f"\n找到 {len(words)} 个单词, 总分 {total}:")
    for w in sorted(words, key=lambda x: (-score_word(x), x)):
        print(f"  {w} ({score_word(w)} 分)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
