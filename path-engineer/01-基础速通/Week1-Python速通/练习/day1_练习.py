"""
Day 1 · Python 基础语法练习
=========================

完成下面的题目（直接修改本文件）。
完成后运行：python3 day1_练习.py
预期输出在每题最后的注释里。

提示：
  - 把每题的 # TODO 部分替换为你的代码
  - 不要复制粘贴别人的答案，自己写！
  - 卡住了回去看 Day1-基础语法.md 对应章节
"""

print("=" * 50)
print("Day 1 练习")
print("=" * 50)


# ----------------------------------------------------------------------
# 题 1：变量与类型（5 分钟）
# ----------------------------------------------------------------------
# 创建以下变量并打印它们的值和类型：
#   - name: 字符串"fletcher"
#   - age: 整数 30
#   - height: 浮点数 1.75
#   - is_student: 布尔值 False
# 用 f-string 输出，格式为：
#   name = fletcher (类型: <class 'str'>)
print("\n--- 题 1：变量与类型 ---")
name = 'fletcherli'
age = 30
height = 1.75
is_student = False

print(f"name = {name} (类型: {type(name)})")
print(f"age = {age} (类型:{type(age)})")
print(f"height = {height} (类型:{type(height)})")
print(f"is_student = {is_student} (类型: {type(is_student)})")


# ----------------------------------------------------------------------
# 题 2：f-string 格式化（5 分钟）
# ----------------------------------------------------------------------
# 给定下面的数据，用 f-string 输出：
#   "fletcher 的月薪是 ¥12,345.67，年薪 ¥148,148.04"
#   要求：千分位逗号、保留 2 位小数
print("\n--- 题 2：f-string 格式化 ---")
name = "fletcher"
monthly_salary = 12345.6711

print(f"{name}的月薪是 ¥{monthly_salary:,.2f} , 年薪 ¥{monthly_salary * 12:,.2f}")


# ----------------------------------------------------------------------
# 题 3：控制流 - FizzBuzz（10 分钟）
# ----------------------------------------------------------------------
# 打印 1 到 15 的数字，但是：
#   - 3 的倍数打印 "Fizz"
#   - 5 的倍数打印 "Buzz"
#   - 同时是 3 和 5 的倍数打印 "FizzBuzz"
#   - 其他打印数字本身
# 预期输出：1 2 Fizz 4 Buzz Fizz 7 8 Fizz Buzz 11 Fizz 13 14 FizzBuzz
print("\n--- 题 3：FizzBuzz ---")
for i in range(1,16):
	if i%3 == 0 and i%5 == 0:
		print(f"FizzBuzz")
	elif i%3 == 0:
		print(f"Fizz")
	elif i%5 == 0:
		print(f"Buzz")
	else:
		print(i)

# ----------------------------------------------------------------------
# 题 4：enumerate + zip 实战（10 分钟）
# ----------------------------------------------------------------------
# 给定两个列表：员工和工资，输出：
#   "1. Alice: ¥15000"
#   "2. Bob: ¥18000"
#   "3. Charlie: ¥22000"
# 提示：用 enumerate + zip
print("\n--- 题 4：enumerate + zip ---")
employees = ["Alice", "Bob", "Charlie"]
salaries = [15000, 18000, 22000]
for i,(employee ,salarie) in enumerate(zip(employees,salaries),1):
	print(f"{i}. {employee}:¥{salarie}")

# ----------------------------------------------------------------------
# 题 5：函数 + 默认参数（10 分钟）
# ----------------------------------------------------------------------
# 写一个函数 calculate_price(price, discount=0.0, tax=0.13)
#   - price: 原价
#   - discount: 折扣率（默认 0，0.1 表示 10% 折扣）
#   - tax: 税率（默认 13%）
# 返回最终价格 = price * (1 - discount) * (1 + tax)
# 测试：
#   calculate_price(100)              # 100 * 1.13 = 113
#   calculate_price(100, 0.1)         # 90 * 1.13 = 101.7
#   calculate_price(100, 0.1, 0.05)   # 90 * 1.05 = 94.5
print("\n--- 题 5：函数 + 默认参数 ---")
def calculate_price(price,discount=0.0, tax=0.13):
	return price * (1 - discount) * (1 + tax)

# 调用测试（不要修改下面）
print(calculate_price(100))
print(calculate_price(100, 0.1))
print(calculate_price(100, 0.1, 0.05))


# ----------------------------------------------------------------------
# 题 6：多返回值（5 分钟）
# ----------------------------------------------------------------------
# 写一个函数 get_min_max(numbers) 返回列表的最小值和最大值
# 测试：
#   small, big = get_min_max([3, 1, 4, 1, 5, 9, 2, 6])
#   print(small, big)  # 1 9
# 提示：可以直接用内置 min() 和 max()
print("\n--- 题 6：多返回值 ---")
def get_min_max(numbers):
	return min(numbers),max(numbers)

# 调用测试（不要修改下面）
small, big = get_min_max([3, 1, 4, 1, 5, 9, 2, 6])
print(f"最小值: {small}, 最大值: {big}")


# ----------------------------------------------------------------------
# 题 7：类与对象（15 分钟）
# ----------------------------------------------------------------------
# 定义一个类 BankAccount，有：
#   属性：owner（用户名）、balance（余额）
#   构造方法：__init__(self, owner, initial_balance=0)
#   方法：
#     - deposit(amount): 存钱
#     - withdraw(amount): 取钱（如果余额不足，print "余额不足" 并不修改）
#     - __str__(self): 返回字符串 "BankAccount(owner=Alice, balance=1000)"
# 测试见下方
print("\n--- 题 7：类与对象 ---")
class BankAccount:
	def __init__(self,owner,initial_balance = 0):
		self.owner = owner
		self.balance = initial_balance

	def deposit(self,amount):
		self.balance += amount

	def withdraw(self,amount):
		if self.balance < amount:
			print("余额不足")
		else:
			self.balance -= amount
	
	def __str__(self):
		return f"BankAccount(owner={self.owner},balance={self.balance})"

# 调用测试（不要修改下面）
account = BankAccount("Alice", 1000)
print(account)              # BankAccount(owner=Alice, balance=1000)
account.deposit(500)
print(account)              # BankAccount(owner=Alice, balance=1500)
account.withdraw(2000)      # 余额不足
print(account)              # BankAccount(owner=Alice, balance=1500)
account.withdraw(500)
print(account)              # BankAccount(owner=Alice, balance=1000)


# ----------------------------------------------------------------------
# 题 8：综合运用（10 分钟）
# ----------------------------------------------------------------------
# 写一个函数 analyze_scores(scores: dict) -> dict
# 接收一个字典：{"Alice": 85, "Bob": 60, "Charlie": 90}
# 返回一个字典：
#   {
#       "average": 平均分,
#       "max_student": 最高分学生姓名,
#       "passed": 及格的学生列表（>= 60）
#   }
# 提示：
#   - sum(scores.values()) / len(scores) 算平均
#   - max(scores, key=scores.get) 拿最大值的 key
#   - [name for name, score in scores.items() if score >= 60]  ← 列表推导式（明天会学）
print("\n--- 题 8：综合运用 ---")
def analyze_scores(scores):
	return dict(average = sum(scores.values())/len(scores),max_student = max(scores, key = scores.get),passed = [name for name, score in scores.items() if score >= 60])
# 调用测试
result = analyze_scores({"Alice": 85, "Bob": 60, "Charlie": 90, "David": 45})
print(result)
# 预期：{'average': 70.0, 'max_student': 'Charlie', 'passed': ['Alice', 'Bob', 'Charlie']}


print("\n" + "=" * 50)
print("Day 1 练习完成！记得在 README 里打勾 ✅")
print("=" * 50)


# ----------------------------------------------------------------------
# 入口
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # 这个 if 是 Python 主程序入口（相当于 Java 的 main 方法）
    # 当你 import 这个文件时，下面的代码不会执行
    # 直接 python3 day1_练习.py 时才执行
    pass  # 上面已经直接打印了，这里不用再做什么
