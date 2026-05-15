"""
Day 4 · NumPy 基础练习
=====================

完成下面的题目（直接修改本文件）。
完成后运行：python3 day4_练习.py

今天最重要：题 3（切片）、题 4（矩阵运算）、题 6（广播）。
"""

import numpy as np  # pyright: ignore[reportMissingImports]

print("=" * 50)
print("Day 4 NumPy 练习")
print("=" * 50)

# 固定随机种子（保证每次跑结果一样）
np.random.seed(42)


# ----------------------------------------------------------------------
# 题 1：创建 ndarray（10 分钟）
# ----------------------------------------------------------------------
# 1.1 创建一个 1D 数组：包含 1 到 10
# 1.2 创建一个 3x3 全 0 矩阵
# 1.3 创建一个 5x5 单位矩阵
# 1.4 创建一个 0 到 1 之间均匀分布的 (3, 4) 矩阵
# 1.5 创建一个 0 到 1 之间步长 0.1 的等差数列
print("\n--- 题 1：创建 ndarray ---")
print(np.array([i + 1 for i in range(10)]))
print(np.zeros((3,3)))
print(np.ones((5,5)))
print(np.random.rand(3,4))
print(np.linspace(0,1,11))

print("orthes")
print(np.random.randint(0,100,10))
print(np.eye(3))
print(np.arange(0,1,0.1))
print(np.random.randn(5, 6))


# ----------------------------------------------------------------------
# 题 2：shape 与 reshape（15 分钟）⭐
# ----------------------------------------------------------------------
# 给定 a = np.arange(24)
# 完成：
#   2.1 打印 a.shape
#   2.2 reshape 为 (4, 6) 矩阵
#   2.3 reshape 为 (2, 3, 4) 三维数组
#   2.4 用 -1 自动算：reshape 为 (?, 6)（应该是 (4, 6)）
#   2.5 用 .T 转置一个 (3, 4) 矩阵，打印新 shape
print("\n--- 题 2：shape 与 reshape ---")
a = np.arange(24)
print(a.shape)
print(a.reshape(4,6))
print(a.reshape(2,3,4))
print(a.reshape(-1,6).shape)
b = np.random.randint(1,100,(3,4))
print(b.T.shape)
print(b)
print(b.flatten())
# ----------------------------------------------------------------------
# 题 3：索引与切片（25 分钟）⭐⭐
# ----------------------------------------------------------------------
# 假设有一个 5x5 的矩阵
print("\n--- 题 3：索引与切片 ---")
M = np.arange(25).reshape(5, 5)
print("原矩阵:")
print(M)
# 期望：
# [[ 0  1  2  3  4]
#  [ 5  6  7  8  9]
#  [10 11 12 13 14]
#  [15 16 17 18 19]
#  [20 21 22 23 24]]

# 用切片完成（每题尽量一行）：
#   3.1 取第 0 行
#   3.2 取最后一行
#   3.3 取第 2 列
#   3.4 取最后一列
#   3.5 取右下角 2x2 子矩阵：[[18, 19], [23, 24]]
#   3.6 取中心 3x3 子矩阵
#   3.7 取所有偶数行（0, 2, 4 行）
#   3.8 取对角线（提示：np.diag(M)）
print("====取第 0 行=====")
print(M[0])
print("====取最后一行=====")
print(M[-1])
print("====取第 2 列=====")
print(M[:,1])
print("====取最后一列=====")
print(M[:,-1])
print("===取右下角 2x2 子矩阵======")
print(M[-2:,-2:])
print("====取中心 3x3 子矩阵=====")
print(M[1:4,1:4])
print("===取所有偶数行======")
print(M[::2])
print("====取对角线=====")
print(np.diag(M))


# ----------------------------------------------------------------------
# 题 4：矩阵运算（20 分钟）⭐⭐⭐
# ----------------------------------------------------------------------
# 4.1 创建两个 3x3 矩阵：
A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 10]])
B = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

# 完成：
#   4.1 计算 A + B
#   4.2 计算 A * B（逐元素乘）
#   4.3 计算 A @ B（矩阵乘）
#   4.4 计算 A 的转置
#   4.5 计算 A 的元素和（用 .sum()）
#   4.6 计算 A 每行的和（axis=1）
#   4.7 计算 A 每列的和（axis=0）
#   4.8 找到 A 中最大值的位置（提示：np.argmax + np.unravel_index）

print("\n--- 题 4：矩阵运算 ---")
print("4.1")
print(A + B)
print("4.2")
print(A * B)
print("4.3")
print(A @ B)
print("4.4")
print(A.T)
print("4.5")
print(A.sum())
print("4.6")
print(A.sum(axis = 1))
print("4.7")
print(A.sum(axis = 0))
print("4.8")
print(np.unravel_index(np.argmax(A),A.shape))

# ----------------------------------------------------------------------
# 题 5：布尔索引（10 分钟）
# ----------------------------------------------------------------------
print("\n--- 题 5：布尔索引 ---")
scores = np.array([85, 60, 92, 45, 78, 88, 55, 95, 72, 65])

# 完成：
#   5.1 找出所有 >= 60 的分数
#   5.2 把所有 < 60 的分数都改成 0
#   5.3 计算 >= 80 分的占比（百分比）
#   5.4 把 90 分以上的标记为 'A'，其他为 'B'（用 np.where）

print(scores[scores>=60])
scores[scores < 60] = 0
print(scores)
print(f"{(len(scores[scores>=80])/len(scores)) * 100}%")
print(np.where(scores >= 90, 'A', 'B'))





# ----------------------------------------------------------------------
# 题 6：广播（Broadcasting）（15 分钟）⭐⭐
# ----------------------------------------------------------------------
print("\n--- 题 6：广播 ---")
# 6.1 给定一个 (3, 4) 矩阵和一个 (4,) 向量，相加（广播）
M2 = np.arange(12).reshape(3, 4)
v = np.array([10, 20, 30, 40])
print(M2 + v)


# 6.2 数据归一化
# 给定 100 个样本，每个样本 5 个特征
print("\n--- 题 6.2：数据归一化 ---")
data = np.random.randn(100, 5) * 10 + 5
# 用广播实现：每个特征都变成 (x - 均值) / 标准差
# 提示：用 axis=0 算每列的均值和 std
print((data - data.mean(axis=0))/data.std(axis=0))


# 6.3 余弦相似度
a = np.array([1, 2, 3])
b = np.array([2, 4, 6])  # b = 2 * a，方向相同，应该相似度 = 1
# 计算 a 和 b 的余弦相似度
# 提示：cos = dot(a, b) / (norm(a) * norm(b))
# 提示：np.linalg.norm(x)
cos = np.dot(a,b)/(np.linalg.norm(a) * np.linalg.norm(b))
print(cos)


# ----------------------------------------------------------------------
# 题 7：模拟 AI 场景（15 分钟）⭐
# ----------------------------------------------------------------------
print("\n--- 题 7：模拟 AI 场景 ---")

# 场景：模型对一批样本预测了 5 个类别的得分
batch_size = 8
n_classes = 5
np.random.seed(0)
logits = np.random.randn(batch_size, n_classes)
print(f"logits\n{logits}")
print("logits shape:", logits.shape)

# 7.1 找出每个样本预测得分最高的类别（argmax 沿 axis=1）
# 期望结果是一个 shape (8,) 的数组
p = np.argmax(logits,axis=1)
print(p)


# 7.2 模拟真实标签（也是 8 个样本的类别索引）
true_labels = np.array([0, 2, 1, 4, 3, 0, 2, 1])

# 计算预测准确率（预测对的占比）
# 提示：predictions == true_labels 然后 mean
print("预测准确率：")
print((p == true_labels).mean())


# 7.3 把 logits 变成概率（softmax）
# 公式：softmax(x_i) = exp(x_i) / sum(exp(x_j))
# 沿 axis=1（每行总和应该是 1）
# 提示：np.exp() 和 .sum(axis=1, keepdims=True)
print("logits 变成概率（softmax）")
x_i = np.exp(logits)
s = x_i / x_i.sum(axis=1, keepdims=True)
print(s.sum(axis = 1))
print(s)


# ----------------------------------------------------------------------
# 题 8：one-hot 编码（10 分钟）
# ----------------------------------------------------------------------
print("\n--- 题 8：one-hot 编码 ---")

labels = np.array([0, 2, 1, 4, 3, 0])
n_classes = 5

# 把 labels 转成 one-hot 矩阵
# 期望 shape (6, 5)：
#   [[1, 0, 0, 0, 0],
#    [0, 0, 1, 0, 0],
#    [0, 1, 0, 0, 0],
#    [0, 0, 0, 0, 1],
#    [0, 0, 0, 1, 0],
#    [1, 0, 0, 0, 0]]
# 提示：np.eye(n_classes)[labels] 一行搞定 ⭐

print(np.eye(n_classes)[labels])


# ----------------------------------------------------------------------
# 题 9：综合 - 简易 KNN 分类（20 分钟）⭐⭐
# ----------------------------------------------------------------------
# 实现一个简易的 1-NN（最近邻）分类
# 给定训练数据和待预测数据，找最近的训练样本作为预测结果
print("\n--- 题 9：1-NN 分类 ---")

np.random.seed(1)
# 训练集：100 个 4 维样本 + 标签
X_train = np.random.randn(100, 4)
y_train = np.random.randint(0, 3, 100)   # 3 类

# 测试集：5 个 4 维样本，找最近的训练样本预测类别
X_test = np.random.randn(5, 4)

print("X_train",X_train)
print("y_train",y_train.shape)
print("X_test",X_test)
# 步骤：
# 9.1 对每个测试样本，计算和所有训练样本的欧氏距离
#     提示：可以用广播 + .sum(axis=1)
#     dist[i, j] = ||X_test[i] - X_train[j]||
# 9.2 找最近的训练样本索引（argmin 沿 axis=1）
# 9.3 用对应的 y_train 作为预测结果

s = X_test[:,np.newaxis,:] - X_train[np.newaxis,:,:]
d = np.linalg.norm(s,axis = 2)
print("9.1 对每个测试样本，计算和所有训练样本的欧氏距离")
print(d)
y = np.argmin(d,axis=1)
print("9.2 找最近的训练样本索引（argmin 沿 axis=1）")
print(y)
p = y_train[y]
print("9.3 用对应的 y_train 作为预测结果")
print(p)


print("\n" + "=" * 50)
print("Day 4 练习完成！")
print("如果你能看懂 tensor[:, 0] 和 a @ b，今天达标 ✅")
print("=" * 50)
