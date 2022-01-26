import os
import shlex
import sys

from invoke import task, util


in_ci = os.environ.get("CI", "false") == "true"
if in_ci:
    pty = False
else:
    pty = util.isatty(sys.stdout) and util.isatty(sys.stderr)

in_pkg = os.environ.get("PACKAGING") == "true"


@task
def reformat(c):
    c.run("isort --skip grammar.py cuddle tests tasks.py", pty=pty)
    c.run("black --exclude grammar.py cuddle tests tasks.py", pty=pty)


@task
def lint(c):
    c.run("flake8 --show-source --statistics cuddle tests", pty=pty)


@task
def test(c, verbose=False, onefile=""):
    pytest_args = ["pytest", "--strict-config"]

    if in_ci or in_pkg:
        pytest_args.append("--strict-markers")

    if not in_pkg:
        pytest_args.extend(("--cov=cuddle", "--cov-report=term-missing"))
        if in_ci:
            pytest_args.append("--cov-report=xml")
        else:
            pytest_args.append("--cov-report=html")

    if verbose:
        pytest_args.append("-vv")
    elif in_pkg:
        pytest_args.append("-q")
    else:
        pytest_args.append("-v")

    if onefile:
        pytest_args.append(shlex.quote(onefile))

    c.run(" ".join(pytest_args), pty=pty)


@task
def type_check(c):
    c.run("mypy cuddle tests", pty=pty)


@task
def gen_parser(c):
    c.run("tatsu --generate-parser cuddle/grammar.tatsu --outfile cuddle/grammar.py")
