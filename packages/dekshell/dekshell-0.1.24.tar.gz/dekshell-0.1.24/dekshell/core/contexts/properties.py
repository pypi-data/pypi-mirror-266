import os
import sys
import shutil
from sysconfig import get_paths
from dektools.module import ModuleProxy
from ..redirect import shell_name

current_shell = shutil.which(shell_name, path=get_paths()['scripts'])


def make_shell_properties(shell):
    return {
        'shell': shell,
        'shr': f'{shell} r',
        'shrf': f'{shell} rf',
        'shrfc': f'{shell} rfc',
        'shrs': f'{shell} rs',
    }


default_properties = {
    'python': sys.executable,
    **make_shell_properties(current_shell),
    'pid': os.getpid(),
    'pname': os.path.basename(sys.executable),

    'os_name': os.name,
    'os_win': os.name == "nt",
    'mp': ModuleProxy(),
}
