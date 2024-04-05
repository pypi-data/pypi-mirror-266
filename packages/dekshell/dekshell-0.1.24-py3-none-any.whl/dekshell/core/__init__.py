import os
import time
import codecs
import datetime
from dektools.time import get_tz
from dektools.format import format_duration
from dektools.shell import shell_command, shell_wrapper
from .contexts import get_all_context
from .markers import generate_markers
from .markers.base.extra import MarkerSet
from ..utils.beep import sound_notify
from ..utils.shell import shell_bin


def shell_file(path):
    shell_wrapper(f'{shell_bin} rf {path}')


def shell_command_file_cd(filepath, **kwargs):
    cwd = os.getcwd()
    os.chdir(os.path.dirname(filepath))
    shell_command_file(filepath, **kwargs)
    os.chdir(cwd)


def shell_command_file(filepath, **kwargs):
    filepath = os.path.abspath(filepath).replace('\\', '/')
    with codecs.open(filepath, encoding='utf-8') as f:
        kwargs['source'] = dict(desc=filepath)
        kwargs['context'] = (kwargs.get('context') or {}) | dict(fp=filepath, fpp=os.path.dirname(filepath))
        shell_command_batch(f.read(), **kwargs)


default_configs = {
    'default': dict(),
    'beep': dict(beep_success=True, beep_failed=True),
    'deschead': dict(desc_begin=True, desc_took=True),
    'descper': dict(desc_begin_per=True, desc_took_per=True),
    'source': lambda src: dict(source=dict(desc=src))
}
default_configs |= {
    'notify': default_configs['beep'] | default_configs['deschead'],
    'notifyper': default_configs['beep'] | default_configs['deschead'] | default_configs['descper'],
}


def shell_command_batch(commands, **kwargs):
    tag = '# config #'
    if commands.startswith(tag):
        index = commands.find('\n')
        config_str = commands[len(tag):None if index == -1 else index]
        config_data = eval(config_str, default_configs)
        kwargs.update(config_data)
    shell_command_batch_core(commands, **kwargs)


def shell_command_batch_core(
        commands,
        context=None,
        marker=None,
        desc_begin=False,
        desc_begin_per=False,
        desc_took=False,
        desc_took_per=False,
        beep_success=False,
        beep_failed=False,
        tz=None,
        ms_names=None,
        marker_set_cls=None,
        plugin_kwargs=None,
        source=None
):
    def shell_exec(filepath, c=None):
        shell_command_file(
            filepath,
            context=(context or {}) | (c or {}),
            marker=marker,
            ms_names=ms_names,
            marker_set_cls=marker_set_cls,
            plugin_kwargs=plugin_kwargs,
        )

    def shell(cmd, execute=None, env=None):
        if desc_begin_per:
            _shell_desc_begin(cmd)
        ts_per_begin = time.time()
        err = (execute or shell_command)(cmd, env=env)
        if err:
            print()
            if beep_failed:
                sound_notify(False)
            raise err
        else:
            if desc_took_per:
                _shell_desc_took(cmd, int((time.time() - ts_per_begin) * 1000), ms_names, tz)

    marker_set = (marker_set_cls or MarkerSet)(generate_markers(*(marker or []), **(plugin_kwargs or {})))
    context_final = get_all_context() | (context or {})
    tz = get_tz(tz)
    ts_begin = time.time()
    commands = _get_commands(commands)
    commands_name = _get_commands_name(commands, source)
    if desc_begin:
        _shell_desc_begin(commands_name)

    marker_set.exec(commands, shell_exec, shell, context_final)

    if desc_took:
        _shell_desc_took(commands_name, int((time.time() - ts_begin) * 1000), ms_names, tz)
    if beep_success:
        sound_notify(True)


def _shell_desc_begin(desc):
    print(f'\n\n---------Running---------: {desc}\n\n', flush=True)


def _shell_desc_took(desc, ms, ms_names, tz):
    now = datetime.datetime.now(tz)
    print(f'\n\n---------Done------------: {desc}', flush=True)
    print(f'---------Took------------: {format_duration(ms, ms_names)} (now: {now})\n\n', flush=True)


def _get_commands(commands):
    return commands.split('\n')


def _get_commands_name(commands, source):
    if source:
        desc = source.get('desc')
        if desc:
            return desc
    if not commands:
        return ''
    elif len(commands) == 1:
        return commands[0]
    else:
        suffix = ' ···' if len(commands) > 2 else ''
        return f"{commands[0]} ···  {commands[1]}{suffix}"
