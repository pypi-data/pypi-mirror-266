from .base import MarkerBase


class EchoMarker(MarkerBase):
    tag_head = "@echo"

    def exec(self, env, command, marker_node, marker_set):
        argv = self.split_raw(command, 1)
        self.call_func(env, 'print', self.get_item(argv, 1, ''))
