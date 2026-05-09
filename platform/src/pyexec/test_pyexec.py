# %%
from pyexec import sandbox_run_python

# %%
rslt = sandbox_run_python("print('hello world')", timeout=10)

print(rslt)
# %%


rslt = sandbox_run_python("print('hello world\")", timeout=10)
print(rslt)
