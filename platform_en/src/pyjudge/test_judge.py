from judge import judge_code

example_task_code_1 = """
def rx(s):
    return s.replace("x", "")
"""

example_task_code_2 = """
def rx(s):
"""

example_task_code_3 = """
def rx(s):
    pass
"""

example_task_code_4 = """
def rx(s):
    if s == "xxx": return [""][2]
    return s.replace("x", "")
"""

example_entrypoint = "rx"

testcases = [
    ("hello", "hello"),
    ("world", "world"),
    ("xxx", ""),
    ("xxxhelloxxx", "hello"),
    ("xxxworldxxx", "world"),
]

if __name__ == "__main__":
    # all passed
    ret = judge_code(example_task_code_1, example_entrypoint, testcases)
    assert ret["exec_result"] == "finished"
    assert all([x["passed"] == True for x in ret["output"]])

    # syntax error
    ret = judge_code(example_task_code_2, example_entrypoint, testcases)
    assert "failed" in ret["exec_result"]

    # all not passed
    ret = judge_code(example_task_code_3, example_entrypoint, testcases)
    assert ret["exec_result"] == "finished"
    assert all([x["passed"] == False for x in ret["output"]])

    # index error sometimes
    ret = judge_code(example_task_code_4, example_entrypoint, testcases)
    assert ret["exec_result"] == "finished"
    assert ret["output"][0]["passed"] == True
    assert ret["output"][2]["passed"] == False
    assert "IndexError" in ret["output"][2]["message"]
