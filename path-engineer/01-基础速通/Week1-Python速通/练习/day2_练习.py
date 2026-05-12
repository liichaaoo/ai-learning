"""
Day 2 · Python 数据结构练习
==========================

完成下面的题目（直接修改本文件）。
完成后运行：python3 day2_练习.py

提示：本日重点是【列表推导式】和【字典遍历】，多用它们。
"""

print("=" * 50)
print("Day 2 练习")
print("=" * 50)

from collections import Counter
# ----------------------------------------------------------------------
# 题 1：列表基础（5 分钟）
# ----------------------------------------------------------------------
# 给定 nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
# 完成：
#   1.1 打印长度
#   1.2 打印第一个和最后一个元素（用负索引）
#   1.3 打印排序后的列表（升序）
#   1.4 打印去重后的元素个数（提示：set）
#   1.5 打印反转后的列表（用切片 [::-1]）
print("\n--- 题 1：列表基础 ---")
nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
print(len(nums))
print(nums[0],nums[-1])
print(sorted(nums))
print(len(set(nums)))
print(nums[::-1])


# ----------------------------------------------------------------------
# 题 2：切片实战（10 分钟）
# ----------------------------------------------------------------------
# 给定一个学生分数列表（10 个学生）
# 用切片完成：
#   2.1 前 3 个学生
#   2.2 后 3 个学生
#   2.3 中间 4 个（索引 3 到 6）
#   2.4 每隔一个取一个
#   2.5 反转列表
print("\n--- 题 2：切片实战 ---")
scores = [85, 92, 78, 90, 65, 88, 75, 95, 80, 70]
print(scores[:3])
print(scores[-3:])
print(scores[3:7])
print(scores[::2])
print(scores[::-1])


# ----------------------------------------------------------------------
# 题 3：列表推导式（15 分钟）⭐ 重点
# ----------------------------------------------------------------------
# 用【一行】列表推导式完成：
#   3.1 生成 1 到 20 的平方数列表
#   3.2 从 nums 中筛出所有偶数
#   3.3 把字符串列表都转大写
#   3.4 生成两个列表的笛卡尔积（每对组合）
#   3.5 综合：从分数列表挑出 >= 80 的，并标记为 "优秀"，否则 "良好"，结果是字符串列表
print("\n--- 题 3：列表推导式 ---")
nums_for_3 = list(range(1, 21))
words = ["hello", "world", "python", "rocks"]
sizes = ["S", "M", "L"]
colors = ["red", "blue"]
test_scores = [85, 60, 92, 70, 88, 50, 95]
print([i * i for i in nums_for_3])
print([i for i in nums_for_3 if i % 2 == 0])
print([word.upper() for word in words])
print([(size,color) for size in sizes for color in colors])
print([f"{s}:优秀" if s >= 80 else f"{s}:良好" for s in test_scores])
# ----------------------------------------------------------------------
# 题 4：字典基础（10 分钟）
# ----------------------------------------------------------------------
# 给定一个学生成绩字典：
student_scores = {
    "Alice": 85,
    "Bob": 60,
    "Charlie": 92,
    "David": 45,
    "Eve": 78,
}
# 完成：
#   4.1 用 .get() 安全访问 "Frank"，不存在时返回 0
#   4.2 添加一个新学生 "Grace": 88
#   4.3 计算平均分
#   4.4 找出最高分的学生姓名（提示：max(d, key=d.get)）
#   4.5 用 for + .items() 遍历，打印 "Alice 得了 85 分" 这样的格式
print("\n--- 题 4：字典基础 ---")

print(student_scores.get("Frank",0))
student_scores["Grace"]=88
print(student_scores)
print(sum(student_scores.values())/len(student_scores.values()))
# print(max(student_scores,key=lambda name:student_scores[name]))
print(max(student_scores, key = student_scores.get))
for name,score in student_scores.items():
	print(f"{name} 得了 {score} 分")


# ----------------------------------------------------------------------
# 题 5：字典推导式（10 分钟）⭐
# ----------------------------------------------------------------------
# 基于上面的 student_scores，用【一行】字典推导式完成：
#   5.1 创建一个新字典，只保留分数 >= 60 的学生
#   5.2 创建一个新字典，所有分数 +5（鼓励）
#   5.3 创建一个反向字典：分数 -> 学生名（假设分数不重复）
print("\n--- 题 5：字典推导式 ---")
print({name:score for name,score in student_scores.items() if score >= 60})
print({name:(score+5) for name,score in student_scores.items()})
print({score:name for name,score in student_scores.items()})


# ----------------------------------------------------------------------
# 题 6：用 Counter 统计单词频率（10 分钟）
# ----------------------------------------------------------------------
# 给定一段文字，统计每个单词出现的次数
text = """
the quick brown fox jumps over the lazy dog
the lazy dog sleeps all day
the fox is quick and clever
"""
# 6.1 把文字拆成单词（提示：text.split()）
# 6.2 用 collections.Counter 统计频率
# 6.3 打印出现次数最多的 3 个单词及次数（提示：counter.most_common(3)）
print("\n--- 题 6：单词频率 ---")
counter = Counter(text.split())
print(counter)
print(counter.most_common(3))


# ----------------------------------------------------------------------
# 题 7：集合运算（10 分钟）
# ----------------------------------------------------------------------
# 模拟用户技能匹配
fletcher_skills = {"java", "spring", "mysql", "redis", "kafka", "docker", "k8s"}
job_required = {"java", "spring", "kafka", "kubernetes", "ai", "rag"}

# 完成：
#   7.1 fletcher 已掌握的、岗位需要的技能（交集）
#   7.2 fletcher 还不会的、岗位需要的技能（差集）
#   7.3 fletcher 会但岗位没要求的（差集，反向）
#   7.4 计算技能匹配度：交集大小 / 岗位需要数量（百分比）
#   7.5 用 f-string 格式化输出，保留 1 位小数（如 "匹配度: 50.0%"）
print("\n--- 题 7：集合运算 ---")

print(fletcher_skills & job_required) # 交集
print(fletcher_skills - job_required) # 差集
print(job_required - fletcher_skills) # 反向差集
print(f"{len(fletcher_skills & job_required)/len(job_required)*100:.1f}%")
print(f"匹配度：{len(fletcher_skills & job_required)/len(job_required)*100:.1f}%")


# ----------------------------------------------------------------------
# 题 8：解包（unpacking）（10 分钟）⭐
# ----------------------------------------------------------------------
# 8.1 多变量赋值：交换两个变量的值
print("\n--- 题 8：解包 ---")
a, b = 100, 200
a, b = b, a
print(a, b)
# print(a, b)  # 应该输出 200 100

# 8.2 列表解包
data = [1, 2, 3, 4, 5]
first, *middle, last = data
print(first,last,middle)
# 期望：first=1, last=5, middle=[2, 3, 4]

# 8.3 字典解包合并
default_config = {"lr": 0.01, "batch_size": 32, "epochs": 10}
user_config = {"batch_size": 64, "device": "cuda"}
print({**default_config,**user_config})
# 期望：{'lr': 0.01, 'batch_size': 64, 'epochs': 10, 'device': 'cuda'}


# ----------------------------------------------------------------------
# 题 9：综合实战 - 简易学生管理（15 分钟）⭐⭐
# ----------------------------------------------------------------------
# 给定学生数据列表（每个是 dict）
print("\n--- 题 9：综合实战 ---")
students = [
    {"name": "Alice", "age": 20, "scores": {"math": 90, "english": 85}},
    {"name": "Bob", "age": 21, "scores": {"math": 75, "english": 92}},
    {"name": "Charlie", "age": 19, "scores": {"math": 88, "english": 70}},
    {"name": "David", "age": 22, "scores": {"math": 60, "english": 65}},
]

# 完成（每题尽量一行解决）：
#   9.1 提取所有学生的姓名列表
#   9.2 找出年龄 >= 20 的学生姓名
#   9.3 计算每个学生的总分（math + english），结果是 {name: total} 字典
#   9.4 找出总分最高的学生姓名
#   9.5 计算所有学生数学的平均分

print([student["name"] for student in students])
print([student["name"] for student in students if student["age"] >=20])
print({student["name"]:sum(student["scores"].values()) for student in students})
# print(max({student["name"]:sum(student["scores"].values()) for student in students},key = {student["name"]:sum(student["scores"].values()) for student in students}.get))
print(max(students, key=lambda s: sum(s["scores"].values()))["name"])
# print({student["name"]:(sum(student["scores"].values())/len(student["scores"].values())) for student in students})
print(sum(s["scores"]["math"] for s in students)/len(students))
print("\n" + "=" * 50)
print("Day 2 练习完成！")
print("=" * 50)
