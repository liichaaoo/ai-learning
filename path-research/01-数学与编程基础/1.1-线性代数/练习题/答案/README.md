# 答案区

> 做完题目再看！

---

## 组织方式

建议按章节组织答案文件：
```
答案/
├── 01-向量-答案.md
├── 02-矩阵基础-答案.md
├── ...
└── 08-综合项目-参考实现/
```

---

## 获取参考答案的几种方式

### 方式 1：自己先做，再找 AI 对答案
- 做完后让 AI 批改你的解答
- AI 可以解释为什么错、更优雅的写法

### 方式 2：经典教材答案
- **MIT 18.06 习题答案**：[课程网站](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/pages/assignments/) 有完整答案
- **Linear Algebra Done Right**：每章末有习题，Sheldon Axler 官网提供部分答案
- **《线性代数及其应用》David Lay**：中译本有习题解答

### 方式 3：编程题验证
- 所有编程题都可以用 `np.linalg.XXX` 对比结果
- 用 `np.allclose` 或 `np.testing.assert_allclose` 做数值比较

---

## 编程题标准对照表

| 你的实现 | NumPy 标准答案 |
|---------|---------------|
| `my_dot(u, v)` | `np.dot(u, v)` |
| `matmul_loop(A, B)` | `A @ B` |
| `gauss_elimination(A, b)` | `np.linalg.solve(A, b)` |
| `det_recursive(A)` | `np.linalg.det(A)` |
| `power_iteration(A)` | `np.linalg.eig(A)` 中最大特征值 |
| `MyPCA` | `sklearn.decomposition.PCA` |
| `svd_compress` | `np.linalg.svd` |

---

## 如果实在卡住

1. **先看 3B1B 对应集**，几何直觉先通
2. **看 MIT 18.06 对应 Lecture**
3. **在笔记里写下卡点**（`../../笔记/`），过几天回头看
4. **问 AI**：把题目和你的思路描述清楚，让 AI 引导（而不是直接给答案）

---

> 💡 **学习原则**：做错的题比做对的题学到更多。不要追求全对，而要追求"真正理解"。
