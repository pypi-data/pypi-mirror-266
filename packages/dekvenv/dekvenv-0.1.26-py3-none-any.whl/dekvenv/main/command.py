import os
import sys
import typer
import virtualenv
from typing_extensions import Annotated
from dektools.file import remove_path, write_file
from dektools.shell import shell_wrapper
from dektools.sys import sys_paths_relative
from ..active import activate_venv
from ..constants import dir_name_venv
from ..utils.common import get_py_pkg_name, get_py_pkg_info
from .core import get_pkg_path

app = typer.Typer(add_completion=False)


@app.command()
def create(name=dir_name_venv, path='.', parent=''):
    path = os.path.normpath(os.path.abspath(path))
    path_venv = os.path.join(path, name)
    if not os.path.exists(path_venv):
        virtualenv.cli_run([path_venv])
    if parent:
        path_parent = os.path.normpath(os.path.abspath(parent))
        path_var = sys_paths_relative('', True)
        path_lib = path_var['platlib']
        pth = f"import site;site.addsitedir(r'{path_parent}{path_lib}')"
        write_file(os.path.join(path_venv + path_lib, 'aaa__parent.pth'), s=pth)


@app.command()
def active(name=dir_name_venv, ignore: Annotated[bool, typer.Option("--ignore/--no-ignore")] = True):
    path_venv = os.path.join(os.getcwd(), name)
    activate_venv(path_venv, ignore)


@app.command()
def build(path='.'):
    from ..pdm.core import is_pdm_project
    remove_path(os.path.join(path, '.pdm-build'))
    remove_path(os.path.join(path, 'build'))
    remove_path(os.path.join(path, 'dist'))
    if os.path.isdir(path):
        for fn in os.listdir(path):
            if fn.endswith('.egg-info'):
                remove_path(os.path.join(path, fn))

    if is_pdm_project(path):
        shell_wrapper(f'pdm build -p {path}')
    else:
        shell_wrapper(f'{sys.executable} -m build -s -w {path}')


@app.command()
def update(path_dir):
    from ..pdm.core import pdm_update_cache_pkg
    path_dir = os.path.normpath(os.path.abspath(path_dir))
    pdm_update_cache_pkg(path_dir, get_py_pkg_info(path_dir))


@app.command()
def push(server: str = '', path: str = '.', se: bool = True):
    from ..pdm.core import pdm_clear_cache_hash_pkg, pdm_clear_cache_pkg, pdm_clear_cache_metadata
    assert server
    build(path)
    path_pkg = get_pkg_path(path)
    pdm_clear_cache_hash_pkg(server, os.path.basename(path_pkg))
    pdm_clear_cache_pkg(get_py_pkg_name(path), path_pkg)
    pdm_clear_cache_metadata(path_pkg)
    shell_wrapper(f'twine upload {"--skip-existing" if se else ""} --repository {server} {path_pkg}')


@app.command()
def var(name):
    data = sys_paths_relative('', True)
    if name:
        v = data[name]
    else:
        v = data
    sys.stdout.write(str(v))
    sys.stdout.flush()
