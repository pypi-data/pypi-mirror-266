"""
基于动态规划的最小编辑距离
"""


def edit_distance(list1: list, list2: list, insertion_cost=1, deletion_cost=1, substitution_cost=1):
    # 计算两个列表的长度
    len1, len2 = len(list1), len(list2)

    # 初始化一个二维数组 dp 用于存储编辑距离中间结果
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    # 初始化第一列，表示将 list1 的前 i 个元素全部删除所需的代价
    for i in range(len1 + 1):
        dp[i][0] = i * deletion_cost

    # 初始化第一行，表示将 list2 的前 j 个元素全部插入到 list1 中所需的代价
    for j in range(len2 + 1):
        dp[0][j] = j * insertion_cost

    # 使用动态规划填充 dp 数组
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            # 如果 list1[i-1] 和 list2[j-1] 相等，不需要进行替换操作，cost 设置为 0
            if list1[i - 1] == list2[j - 1]:
                cost = 0
            else:
                # 如果 list1[i-1] 和 list2[j-1] 不相等，需要进行替换操作，使用 substitution_cost
                cost = substitution_cost
            # 计算将 list1 的前 i 个元素转换为 list2 的前 j 个元素的最小编辑距离
            dp[i][j] = min(dp[i - 1][j] + deletion_cost,  # 删除 list1[i-1]
                           dp[i][j - 1] + insertion_cost,  # 插入 list2[j-1] 到 list1 中
                           dp[i - 1][j - 1] + cost)  # 替换 list1[i-1] 为 list2[j-1]

    # 返回将 list1 转换为 list2 所需的最小编辑距离
    return dp[len1][len2]
