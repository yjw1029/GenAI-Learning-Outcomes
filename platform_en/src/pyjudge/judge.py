from .execution import sandbox_run, sandbox_run_async

judge_code_template = """
def check(fn):
    # Make the function available in the global scope so recursion works
    globals()[fn.__name__] = fn
    
    testcases = ## testcases ##

    results = []
    for testcase in testcases:
        input, expected = testcase
        try:
            if isinstance(input, list):
                output = fn(*input)
            else:
                output = fn(input)
            flag = output == expected
            results.append({
                "input": input,
                "output": repr(output),
                "expected": expected,
                "message": "passed" if flag else "failed",
                "passed": flag,
                "finished": True,
            })
        except Exception as e:
            results.append({
                "input": input,
                "output": None,
                "expected": expected,
                "message": f"Error: {type(e).__name__}: {e}",
                "passed": False,
                "finished": False,
            })

    return results
"""


def judge_code(taskcode, task_entrypoint, testcases, timeout=1):
    testcases_str = ",\n    ".join(
        [f"({repr(input)}, {repr(output)})" for input, output in testcases]
    )
    testcases_str = f"[\n    {testcases_str}\n]"
    judge_code = judge_code_template.replace("## testcases ##", testcases_str)
    whole_code = f"""{taskcode}
{judge_code}
return_me = check({task_entrypoint})
"""

    return sandbox_run(whole_code, timeout)


async def judge_code_async(taskcode, task_entrypoint, testcases, timeout=1):
    testcases_str = ",\n    ".join(
        [f"({repr(input)}, {repr(output)})" for input, output in testcases]
    )
    testcases_str = f"[\n    {testcases_str}\n]"
    judge_code = judge_code_template.replace("## testcases ##", testcases_str)
    whole_code = f"""{taskcode}
{judge_code}
return_me = check({task_entrypoint})
"""
    return await sandbox_run_async(whole_code, timeout)
