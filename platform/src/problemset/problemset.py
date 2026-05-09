from pathlib import Path

PATH_THIS_FILE = Path(__file__).parent


def load_problem(pname, ptype="py"):
    # WARNING: this function is not secure, do not process untrusted arguments

    assert isinstance(pname, str)
    assert "." not in pname

    # check if problem exists
    ppath = Path(PATH_THIS_FILE, pname + ".py")
    if not ppath.exists():
        raise FileNotFoundError(f"Problem {ppath} not found.")

    # load problem
    exec_globals = {}
    exec_locals = {}

    exec(open(ppath).read(), exec_globals, exec_locals)

    # check if problem is valid
    if ptype == "py":
        required = [
            "description",
            "code_template",
            "code_entrypoint",
            "validcases",
            "testcases",
            "knowledge",
            "title",
            "answer",
            "score"
        ]
    elif ptype == "math":
        required = [
            "description",
            "math_template",
            "title",
            "knowledge",
            "answer",
            "score"
        ]
    else:
        raise ValueError(f"Unknown problem type {ptype}.")

    for r in required:
        if r not in exec_locals:
            raise ValueError(f"Problem {ppath} does not have required attribute {r}.")

    # return problem
    return {k: exec_locals[k] for k in required}


def load_problemset(pnames, ptype="py"):
    problem_titles, pname2title, problemset = [], {}, {}
    for pname in pnames:
        problem = load_problem(pname, ptype)
        problem_titles.append(problem["title"])
        pname2title[pname] = problem["title"]
        problemset[pname] = problem

    title2pname = {v: k for k, v in pname2title.items()}

    return problem_titles, pname2title, title2pname, problemset


if __name__ == "__main__":
    print(load_problem("py_hw1/p1"))
