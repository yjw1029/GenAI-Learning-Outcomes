def get_syntax_error(source):
    unknown_error = False
    syntax_error = False

    msg = ""

    try:
        compiled = compile(source, filename="main.py", mode="exec")
    except SyntaxError as e:
        syntax_error = True
        msg = str(e)
    except Exception:
        unknown_error = True
        msg = "Unknown error"
    return {"unknown_error": unknown_error, "syntax_error": syntax_error, "msg": msg}
