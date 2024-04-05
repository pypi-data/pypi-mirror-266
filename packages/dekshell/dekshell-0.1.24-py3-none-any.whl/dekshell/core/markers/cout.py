from dektools.shell import shell_output
from .base import MarkerBase


class CmdOutMarker(MarkerBase):
    tag_head = "@cout"

    def exec(self, env, command, marker_node, marker_set):
        argv = self.split_raw(command, 2)
        self.set_var(env, argv, 1, shell_output(argv[2]))
