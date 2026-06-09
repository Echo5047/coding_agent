# N皇后问题：回溯搜索实现

def is_valid(board, row, col):
    """
    检查在 (row, col) 放置皇后是否合法。
    注意：我们是一行一行往下放的，所以只需要检查 0 到 row-1 行的皇后是否与当前位置冲突。
    
    参数:
    board: list，当前的棋盘状态，board[i] 表示第 i 行皇后的列号
    row: int，当前准备放置皇后的行号
    col: int，当前准备放置皇后的列号
    
    返回:
    bool: 如果合法返回 True，否则返回 False
    """
    for prev_row in range(row):
        prev_col = board[prev_row]
        if prev_col == col or abs(prev_col - col) == abs(prev_row - row):
            return False
    return True


def backtrack(board, row, n, solutions):
    """
    使用回溯法求解N皇后问题。
    
    参数:
    board: list，当前的棋盘状态，初始时可以全为 -1
    row: int，当前正在处理的行号
    n: int，棋盘大小（N）
    solutions: list，用于保存所有找到的合法解
    """
    if row == n:
        solutions.append(board.copy())
        return

    for col in range(n):
        if is_valid(board, row, col):
            board[row] = col
            backtrack(board, row + 1, n, solutions)
            board[row] = -1

if __name__ == "__main__":
    N = 8
    board = [-1] * N
    solutions = []
    backtrack(board, 0, N, solutions)
    print(f"{N}皇后问题共有 {len(solutions)} 个解。")
    if solutions:
        print("其中一个解为:", solutions[0])