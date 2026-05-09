title = "Coding Basics Test"
description = """Please complete the following coding basics test within 5 minutes."""

questions = {
    "Coding Basics Test": [
        {
            "text": "What is the role of loops in programming?",
            "type": "single_choice",
            "options": [
                "Store multiple variables",
                "Connect to a database",
                "Output data",
                "Repeat the same code"
            ]
        },
        {
            "text": "What is the main purpose of functions in programming?",
            "type": "single_choice",
            "options": [
                "Reuse code and avoid writing the same code repeatedly",
                "Increase code execution speed",
                "Connect to the Internet",
                "Reduce program memory usage"
            ]
        },
        {
            "text": "Which of the following is a constant?",
            "type": "single_choice",
            "options": [
                "A value entered by a user",
                "A counter updated each loop iteration",
                "A defined value of pi in the program (e.g., 3.14159)",
                "A variable storing database query results"
            ]
        },
        {
            "text": "Which case is most suitable for using an array (list)?",
            "type": "single_choice",
            "options": [
                "Store one user's name",
                "Store names of 100 users",
                "Compute the sum of two numbers",
                "Print a message"
            ]
        },
        {
            "text": """Read the pseudocode below and answer:
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

What does this function check?""",
            "type": "single_choice",
            "options": [
                "Whether it is positive",
                "Whether it is even",
                "Whether it is prime",
                "Whether it is composite"
            ]
        },
        {
            "text": """Which pseudocode correctly computes the absolute difference between x and y?
            
```
A)
X, Y = input two values
ABS_VALUE = X - Y
RETURN ABS_VALUE


B)
X, Y = input two values
IF X - Y < 0 THEN
    ABS_VALUE = Y - X
ELSE
    ABS_VALUE = X - Y
RETURN ABS_VALUE

C)
X, Y = input two values
ABS_VALUE = X + Y
RETURN ABS_VALUE


D)
X, Y = input two values
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
            "text": """Which pseudocode correctly reverses an integer x (e.g., 12345 -> 54321)?

```
A)
X = input integer
REVERSE = 0
WHILE X != 0:
    REVERSE = REVERSE * 10 + X % 10
    X = X / 10
RETURN REVERSE

B)
X = input integer
REVERSE = -X
RETURN REVERSE

C)
X = input integer
REVERSE = 0
WHILE X != 0:
    REVERSE = REVERSE + (X % 10) * (X % 10)
    X = X / 10
RETURN REVERSE

D)
X = input integer
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
            "text": """Which pseudocode correctly computes the sum of the first N Fibonacci numbers?

```
A)
N = input number of terms
SUM = 0
FOR I FROM 1 TO N:
    SUM = SUM + I
RETURN SUM


B)
N = input number of terms
SUM = 1
FOR I FROM 2 TO N:
    SUM = SUM * I
RETURN SUM

C)
N = input number of terms
A = 0, B = 1, SUM = 0
FOR I FROM 1 TO N:
    SUM = SUM + A
    NEXT = A + B
    A = B
    B = NEXT
RETURN SUM

D)
N = input number of terms
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
            "text": """Read the pseudocode below and choose the possible logic error:

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
                "If array is empty, accessing array[LENGTH(array) - 1] will cause an error",
                "Value is always appended to the end, regardless of correct order",
                "The function does not update the array length after insertion, which may cause errors",
                "Value will be inserted multiple times"
            ]
        },
        {
            "text": """Read the pseudocode below and answer:

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

What is the purpose of this recursive function?""",
            "type": "single_choice",
            "options": [
                "Sort the array",
                "Find the maximum value in the array",
                "Split the array into two equal parts",
                "Compute the sum of all elements in the array"
            ]
        }
    ]
}

