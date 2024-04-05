import os
import shutil
import sys
import codecs
import typer
from dektools.output import pprint
from dektools.str import str_escaped
from dektools.shell import shell_wrapper
from dektools.file import write_file, remove_path
from dektools.typer import command_mixin
from ..core import shell_command_batch, shell_command_file, shell_command_file_cd
from ..core.markers.base import MarkerBase
from ..core.contexts import get_all_context
from ..core.markers import generate_markers
from ..core.redirect import redirect_shell_by_path_tree
from ..core.plugin import find_plugins
from ..core.encode import decode_run_str

app = typer.Typer(add_completion=False)


def get_argv(index=None):
    if index is not None:
        return sys.argv[index]
    else:
        return sys.argv


def get_kwargs(begin):
    return MarkerBase.cmd2ak(get_argv()[begin:])[1]


def try_redirect_shell(filepath=None):
    filepath = filepath or os.getcwd()
    path_shell = redirect_shell_by_path_tree(filepath)
    if path_shell:
        shell_wrapper(path_shell + ' ' + ' '.join(sys.argv[1:]))
        return True
    else:
        return False


@app.command(
    context_settings=dict(resilient_parsing=True)
)
def rs():
    line = get_argv(2)
    if not try_redirect_shell():
        line = decode_run_str(line)
        shell_command_batch(str_escaped(line), context=get_kwargs(3))


@app.command(
    context_settings=dict(resilient_parsing=True)
)
def raw_rs():
    line = get_argv(2)
    line = decode_run_str(line)
    shell_command_batch(str_escaped(line), context=get_kwargs(3))


@command_mixin(app)
def rrs(args):
    if not try_redirect_shell():
        shell_command_batch(str_escaped(args))


@command_mixin(app)
def raw_rrs(args):
    shell_command_batch(str_escaped(args))


@app.command(
    context_settings=dict(resilient_parsing=True)
)
def rf():
    filepath = get_argv(2)
    if not try_redirect_shell(filepath):
        filepath = os.path.normpath(os.path.abspath(filepath))
        shell_command_file_cd(filepath, context=get_kwargs(3))


@app.command(
    context_settings=dict(resilient_parsing=True)
)
def raw_rf():
    filepath = get_argv(2)
    filepath = os.path.normpath(os.path.abspath(filepath))
    shell_command_file_cd(filepath, context=get_kwargs(3))


@app.command(
    context_settings=dict(resilient_parsing=True)
)
def rfc():
    filepath = get_argv(2)
    if not try_redirect_shell(filepath):
        shell_command_file(filepath, context=get_kwargs(3))


@app.command(
    context_settings=dict(resilient_parsing=True)
)
def raw_rfc():
    filepath = get_argv(2)
    shell_command_file(filepath, context=get_kwargs(3))


@app.command(
    context_settings=dict(resilient_parsing=True)
)
def r():
    s = get_argv(2)
    if os.path.isfile(s):
        rf()
    else:
        rs()


@app.command(
    context_settings=dict(resilient_parsing=True)
)
def raw_r():
    s = get_argv(2)
    if os.path.isfile(s):
        raw_rf()
    else:
        raw_rs()


@app.command()
def self():
    if not try_redirect_shell():
        pprint(dict(
            context=get_all_context(),
            marker=generate_markers(),
            plugin=find_plugins()
        ))


@app.command()
def reg():
    assert os.name == 'nt'
    path_ext_reg = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'res', 'windows',
                                'ext.reg.tpl')
    with codecs.open(path_ext_reg, 'r', encoding='utf-8') as f:
        content = f.read()
    path_dekshell = shutil.which(os.path.basename(sys.argv[0]))
    content_reg = content.format(
        dekshell_exe=os.path.basename(path_dekshell),
        dekshell_exe_full_path=path_dekshell.replace('\\', '\\\\'),
    )
    path_reg = write_file('ext.reg', s=content_reg, t=True)
    shell_wrapper(f'regedit {path_reg}')
    remove_path(path_reg)
