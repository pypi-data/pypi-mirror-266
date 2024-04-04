import subprocess
from typing import List


def run_command(command: str) -> str:
    return subprocess.check_output(command, shell=True).decode("utf-8")


def levenshtein_distance(A: str, B: str) -> int:
    N, M = len(A), len(B)
    dp: List[List[int]] = [[0 for i in range(M + 1)] for j in range(N + 1)]

    for j in range(M + 1):
        dp[0][j] = j
    for i in range(N + 1):
        dp[i][0] = i
    for i in range(1, N + 1):
        for j in range(1, M + 1):
            if A[i - 1] == B[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1])

    return dp[N][M]
