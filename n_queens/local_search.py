# N皇后问题：局部搜索（最小冲突启发式）实现

import random

def get_conflicts(board, row, col, n):
    """
    计算如果将第 row 行的皇后放在第 col 列，会与棋盘上其他行的皇后产生多少个冲突。
    
    参数:
    board: list，当前的棋盘状态
    row: int，当前要计算的行号
    col: int，当前要计算的列号
    n: int，棋盘大小
    
    返回:
    int: 冲突的数量
    """
    conflicts = 0
    for other_row in range(n):
        if other_row == row:
            continue

        other_col = board[other_row]
        if other_col == col or abs(other_col - col) == abs(other_row - row):
            conflicts += 1

    return conflicts

def min_conflicts(n, max_steps=1000):
    """
    使用最小冲突启发式算法求解N皇后问题。
    
    参数:
    n: int，棋盘大小
    max_steps: int，最大允许的局部搜索步数
    
    返回:
    list 或 None: 如果找到解则返回 board 状态，否则返回 None
    """
    if n <= 0:
        return []

    steps_used = 0
    restart_interval = max(10, n * 10)

    while steps_used < max_steps:
        # 随机初始化棋盘，每行随机分配一个列号；如果陷入局部最优，后续会重启。
        board = [random.randint(0, n - 1) for _ in range(n)]

        for _ in range(min(restart_interval, max_steps - steps_used)):
            steps_used += 1

            # 找出当前棋盘上所有存在冲突的行
            conflicted_rows = []
            for r in range(n):
                if get_conflicts(board, r, board[r], n) > 0:
                    conflicted_rows.append(r)

            if not conflicted_rows:
                return board

            row = random.choice(conflicted_rows)
            conflict_counts = [get_conflicts(board, row, col, n) for col in range(n)]
            min_conflict = min(conflict_counts)
            best_cols = [col for col, count in enumerate(conflict_counts) if count == min_conflict]
            board[row] = random.choice(best_cols)

    return None

if __name__ == "__main__":
    N = 8
    solution = min_conflicts(N, max_steps=5000)
    if solution:
        print(f"局部搜索成功找到 {N} 皇后问题的一个解:", solution)
    else:
        print("局部搜索未能在大步数内找到解。")