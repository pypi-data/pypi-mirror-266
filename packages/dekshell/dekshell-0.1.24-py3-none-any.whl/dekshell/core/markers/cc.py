from .base import MarkerBase


class CmdCallMarker(MarkerBase):
    tag_head = "@cc"

    def exec(self, env, command, marker_node, marker_set):
        argv = self.split(command)
        args, kwargs = self.cmd2ak(argv[2:])
        self.set_var(env, None, 0, self.call_func(env, argv[1], *args, **kwargs))
