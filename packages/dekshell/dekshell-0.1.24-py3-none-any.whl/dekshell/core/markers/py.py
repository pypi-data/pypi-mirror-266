from .base import MarkerBase


class PyMarker(MarkerBase):
    tag_head = "@py"

    def exec(self, env, command, marker_node, marker_set):
        argv = self.split_raw(command, 1)
        self.set_var(env, None, 0, self.eval(env, argv[1]))
