from .base import MarkerBase


class PyOutCmdMarker(MarkerBase):
    tag_head = "@pyoc"

    def exec(self, env, command, marker_node, marker_set):
        argv = self.split(command)
        args, kwargs = self.cmd2ak(argv[3:])
        self.set_var(env, argv, 1, self.call_func(env, argv[2], *args, **kwargs))
