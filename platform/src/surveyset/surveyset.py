from pathlib import Path

PATH_THIS_FILE = Path(__file__).parent


def load_survey(sname):
    # WARNING: this function is not secure, do not process untrusted arguments

    assert isinstance(sname, str)
    assert "." not in sname

    # check if survey exists
    spath = Path(PATH_THIS_FILE, sname + ".py")
    if not spath.exists():
        raise FileNotFoundError(f"Survey {spath} not found.")

    # load survey
    exec_globals = {}
    exec_locals = {}

    exec(open(spath).read(), exec_globals, exec_locals)

    # check if survey is valid
    required = [
        "title",
        "description",
        "questions"
    ]

    for r in required:
        if r not in exec_locals:
            raise ValueError(f"Survey {spath} does not have required attribute {r}.")
    
    # Validate that questions is a dict {page_title: [question set]}
    if not isinstance(exec_locals["questions"], dict):
        raise ValueError(f"Survey {spath} 'questions' must be a dictionary with format {{page_title: [question set]}}.")
    
    for page_title, question_set in exec_locals["questions"].items():
        if not isinstance(question_set, list):
            raise ValueError(f"Survey {spath} page '{page_title}' must have a list of questions.")

    # return survey
    return {k: exec_locals[k] for k in required}


def load_surveyset(sname):
    # Change: accept only one survey name
    survey = load_survey(sname)
    
    # Extract page title list
    page_titles = list(survey["questions"].keys())
    
    # Create page index mapping
    page_index_map = {i: title for i, title in enumerate(page_titles)}
    title_index_map = {title: i for i, title in enumerate(page_titles)}
    
    return {
        "survey_title": survey["title"],
        "survey_description": survey["description"],
        "page_titles": page_titles,
        "page_index_map": page_index_map,
        "title_index_map": title_index_map,
        "total_pages": len(page_titles),
        "questions": survey["questions"]
    }


if __name__ == "__main__":
    print(load_survey("sample_survey"))
