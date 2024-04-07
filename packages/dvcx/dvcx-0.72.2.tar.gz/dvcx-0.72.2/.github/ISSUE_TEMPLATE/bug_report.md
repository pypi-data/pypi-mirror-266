---
name: Bug Report
about: Template to help gather minimal debugging/reproducing info
labels: bug
---

<!--
Common problems to check:
- old virtualenv
    Especially if any dependencies have changed or if you've installed additional packages, you might try creating a fresh virtualenv
      python -m venv ~/.virtualenvs/dvcx-new
      source ~/.virtualenvs/dvcx-new/bin/activate
      pip install -U pip
      pip install -e '.[dev]'

- re-install dvcx needed
    If using a PyPI release, try
      pip install -U dvcx

    If installing from a repo, try
      pip install -e '.[dev]'

- remove .dvcx if using a new dvcx version
    rm -rf .dvcx
-->

## Version info

```sh
dvcx -V; python -V
```
The command above prints:
```

```
<!--
Please share the dvcx and python version above between the backticks (```).
The output might look like this:

  0.19.1.dev1+g350df47.d20230503
  Python 3.8.12

-->


## Description

<!--
A clear and concise description of what the bug is.

If possible, reproduce CLI bugs with the verbose option:
  dvcx command -v
-->

### Reproduce

<!--
Step list of how to reproduce the bug

Example:
```
dvcx ls s3://bkt/dir1 s3://bkt/dir2
dvcx cp s3://bkt/dir3 ./abc
...
```
-->
