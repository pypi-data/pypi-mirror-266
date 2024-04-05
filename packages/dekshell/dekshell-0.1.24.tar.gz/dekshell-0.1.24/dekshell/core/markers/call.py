from .base import MarkerBase


class CallMarker(MarkerBase):
    tag_head = "@call"

    def exec(self, env, command, marker_node, marker_set):
        argv = self.split(command)
        env.shell_exec(argv[1], self.cmd2ak(argv[2:])[1])
