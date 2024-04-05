import os
from .base import MarkerBase


class InvokeMarker(MarkerBase):
    tag_head = "@invoke"

    def exec(self, env, command, marker_node, marker_set):
        argv = self.split(command)
        path_shell_file = os.path.normpath(os.path.abspath(argv[1]))
        cwd = os.getcwd()
        os.chdir(os.path.dirname(path_shell_file))
        env.shell_exec(path_shell_file, self.cmd2ak(argv[2:])[1])
        os.chdir(cwd)
