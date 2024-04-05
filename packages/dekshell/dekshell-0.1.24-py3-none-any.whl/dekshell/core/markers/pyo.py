from .base import MarkerBase


class PyOutMarker(MarkerBase):
    tag_head = "@pyo"

    def exec(self, env, command, marker_node, marker_set):
        args = self.split_raw(command, 2)
        self.set_var(env, args, 1, self.eval(env, args[2]))
