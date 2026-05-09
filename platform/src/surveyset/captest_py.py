title = "代码基础能力测试"
description = """请同学在5分钟内完成以下的代码能力测试题"""

questions = {
    "代码基础能力测试": [
        {
            "text": "什么是循环结构在编程中的作用?",
            "type": "single_choice",
            "options": [
                "存储多个变量",
                "连接数据库",
                "输出数据",
                "重复执行相同的代码"
            ]
        },
        {
            "text": "函数在编程中的主要目的是什么?",
            "type": "single_choice",
            "options": [
                "重复利用代码，避免重复编写相同的代码",
                "提高代码运行速度",
                "连接到互联网",
                "减小程序的内存消耗"
            ]
        },
        {
            "text": "以下哪个是常量?",
            "type": "single_choice",
            "options": [
                "用户输入的数值",
                "每次循环迭代时更新的计数器",
                "程序中定义的π值（如 3.14159）",
                "存储数据库查询结果的变量"
            ]
        },
        {
            "text": "以下哪种情况最适合使用数组（列表）？",
            "type": "single_choice",
            "options": [
                "存储一个用户的姓名",
                "存储100个用户的姓名",
                "计算两个数的和",
                "打印一条消息"
            ]
        },
        {
            "text": """阅读以下伪代码，回答问题：
```
FUNCTION MyFunc(n)
    IF n <= 1
        RETURN FALSE
    END IF
    FOR i FROM 2 TO sqrt(n)
        IF n MOD i == 0
            RETURN FALSE
        END IF
    END FOR
    RETURN TRUE
END FUNCTION
```

这个函数是用来判断什么的？""",
            "type": "single_choice",
            "options": [
                "是否为正数",
                "是否为偶数",
                "是否为质数",
                "是否为合数"
            ]
        },
        {
            "text": """以下哪个伪代码正确计算两个数值x和y的差的绝对值？
            
```
A)
X, Y = 输入两个数值
ABS_VALUE = X - Y
RETURN ABS_VALUE


B)
X, Y = 输入两个数值
IF X - Y < 0 THEN
    ABS_VALUE = Y - X
ELSE
    ABS_VALUE = X - Y
RETURN ABS_VALUE

C)
X, Y = 输入两个数值
ABS_VALUE = X + Y
RETURN ABS_VALUE


D)
X, Y = 输入两个数值
ABS_VALUE = (X - Y) * (X - Y)
RETURN ABS_VALUE
```
""",
            "type": "single_choice",
            "options": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
                {
            "text": """以下哪个伪代码正确实现了整数x的反转（如 12345->54321）？

```
A)
X = 输入整数
REVERSE = 0
WHILE X != 0:
    REVERSE = REVERSE * 10 + X % 10
    X = X / 10
RETURN REVERSE

B)
X = 输入整数
REVERSE = -X
RETURN REVERSE

C)
X = 输入整数
REVERSE = 0
WHILE X != 0:
    REVERSE = REVERSE + (X % 10) * (X % 10)
    X = X / 10
RETURN REVERSE

D)
X = 输入整数
REVERSE = 0
WHILE X != 0:
    REVERSE = REVERSE + X % 10
    X = X / 10
RETURN REVERSE
```
""",
            "type": "single_choice",
            "options": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        {
            "text": """以下哪个伪代码正确实现了计算斐波那契序列前N项的和？

```
A)
N = 输入项数
SUM = 0
FOR I FROM 1 TO N:
    SUM = SUM + I
RETURN SUM


B)
N = 输入项数
SUM = 1
FOR I FROM 2 TO N:
    SUM = SUM * I
RETURN SUM

C)
N = 输入项数
A = 0, B = 1, SUM = 0
FOR I FROM 1 TO N:
    SUM = SUM + A
    NEXT = A + B
    A = B
    B = NEXT
RETURN SUM

D)
N = 输入项数
FUNCTION FIB_SUM(N):
    IF N <= 1:
        RETURN N
    ELSE:
        RETURN FIB_SUM(N-1) + FIB_SUM(N-2)
RETURN FIB_SUM(N)
```
""",
            "type": "single_choice",
            "options": [
                "A",
                "B",
                "C",
                "D"
            ]
        },
        {
            "text": """阅读以下伪代码并选择可能的逻辑错误：

```
FUNCTION InsertSorted(array, value)
    FOR i FROM 0 TO LENGTH(array) - 1
        IF value < array[i]
            INSERT value AT POSITION i IN array
            BREAK
        END IF
    END FOR
    IF value >= array[LENGTH(array) - 1]
        APPEND value TO array
    END IF
    RETURN array
END FUNCTION
```
""",
            "type": "single_choice",
            "options": [
                "如果array为空，则访问array[LENGTH(array) - 1]将引发错误",
                "value始终被添加到数组末尾，而不考虑其正确的顺序位置",
                "函数在插入value后没有更新数组长度，可能导致后续操作错误",
                "value将重复插入多次到数组中"
            ]
        },
        {
            "text": """阅读以下伪代码并回答问题：

```
FUNCTION MyFunc(arr, left, right)
    IF left == right
        RETURN arr[left]
    ELSE
        mid = (left + right) / 2
        leftMax = MyFunc(arr, left, mid)
        rightMax = MyFunc(arr, mid + 1, right)
        IF leftMax > rightMax
            RETURN leftMax
        ELSE
            RETURN rightMax
        END IF
    END IF
END FUNCTION
```

这个递归函数的目的是什么？""",
            "type": "single_choice",
            "options": [
                "对数组进行排序",
                "找出数组中的最大值",
                "分割数组为两个相等的部分",
                "计算数组中所有元素的和"
            ]
        }
    ]
}

