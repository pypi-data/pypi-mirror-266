import os
import shutil
from subprocess import check_output

import pytest
import virtualenv
from dulwich.porcelain import clone
from packaging import version


@pytest.fixture
def bucket():
    return "s3://noaa-bathymetry-pds/"


def pytest_generate_tests(metafunc):
    str_revs = metafunc.config.getoption("--dvcx-revs")
    revs = str_revs.split(",") if str_revs else [None]
    if "dvcx_rev" in metafunc.fixturenames:
        metafunc.parametrize("dvcx_rev", revs, scope="session")


class VirtualEnv:
    def __init__(self, path) -> None:
        self.path = path
        self.bin = self.path / ("Scripts" if os.name == "nt" else "bin")

    def create(self) -> None:
        virtualenv.cli_run([os.fspath(self.path)])

    def run(self, cmd: str, *args: str, env=None) -> None:
        exe = self.which(cmd)
        check_output([exe, *args], env=env)  # noqa: S603

    def which(self, cmd: str) -> str:
        assert self.bin.exists()
        return shutil.which(cmd, path=self.bin) or cmd


@pytest.fixture(scope="session", name="make_dvcx_venv")
def fixture_make_dvcx_venv(tmp_path_factory):
    def _make_dvcx_venv(name):
        venv_dir = tmp_path_factory.mktemp(f"dvcx-venv-{name}")
        venv = VirtualEnv(venv_dir)
        venv.create()
        return venv

    return _make_dvcx_venv


@pytest.fixture(scope="session", name="dvcx_venvs")
def fixture_dvcx_venvs():
    return {}


@pytest.fixture(scope="session", name="dvcx_git_repo")
def fixture_dvcx_git_repo(tmp_path_factory, test_config):
    url = test_config.dvcx_git_repo

    if os.path.isdir(url):
        return url

    tmp_path = os.fspath(tmp_path_factory.mktemp("dvcx-git-repo"))
    clone(url, tmp_path)

    return tmp_path


@pytest.fixture(scope="session", name="dvcx_bin")
def fixture_dvcx_bin(
    dvcx_rev,
    dvcx_venvs,
    make_dvcx_venv,
    dvcx_git_repo,
    test_config,
):
    if dvcx_rev:
        venv = dvcx_venvs.get(dvcx_rev)
        if not venv:
            venv = make_dvcx_venv(dvcx_rev)
            venv.run("pip", "install", "-U", "pip")
            venv.run("pip", "install", f"git+file://{dvcx_git_repo}@{dvcx_rev}")
            dvcx_venvs[dvcx_rev] = venv
        dvcx_bin = venv.which("dvcx")
    else:
        dvcx_bin = test_config.dvcx_bin

    def _dvcx_bin(*args):
        return check_output([dvcx_bin, *args], text=True)  # noqa: S603

    actual = version.parse(_dvcx_bin("--version"))
    _dvcx_bin.version = (actual.major, actual.minor, actual.micro)

    return _dvcx_bin


@pytest.fixture(scope="function", name="make_bench")
def fixture_make_bench(request):
    def _make_bench(name):
        import pytest_benchmark.plugin

        # hack from https://github.com/ionelmc/pytest-benchmark/issues/166
        bench = pytest_benchmark.plugin.benchmark.__pytest_wrapped__.obj(request)

        suffix = f"-{name}"

        def add_suffix(_name):
            start, sep, end = _name.partition("[")
            return start + suffix + sep + end

        bench.name = add_suffix(bench.name)
        bench.fullname = add_suffix(bench.fullname)

        return bench

    return _make_bench


@pytest.fixture(
    scope="function", params=[pytest.param(None, marks=pytest.mark.benchmark)]
)
def bench_dvcx(dvcx_bin, make_bench):
    def _bench_dvcx(*args, **kwargs):
        name = kwargs.pop("name", None)
        name = f"-{name}" if name else ""
        bench = make_bench(args[0] + name)
        return bench.pedantic(dvcx_bin, args=args, **kwargs)

    return _bench_dvcx
