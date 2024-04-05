import os
from .base import MarkerWithEnd
from .empty import EmptyMarker


class ShellMarker(MarkerWithEnd):
    tag_head = "@shell"

    def exec(self, env, command, marker_node, marker_set):
        argv = self.split_raw(command, 1)
        config = self.get_item(argv, 1, '').strip()
        if config:
            config = eval(f'dict({config})', {'environ': os.environ})
        else:
            config = None
        marker = marker_set.find_marker_by_cls(EmptyMarker)
        result = []
        for child in marker_node.children:
            if child.is_type(EmptyMarker):
                node = marker_set.node_cls(
                    marker,
                    child.command,
                    child.index,
                    marker_node,
                    payload=config
                )
                result.append(node)
            else:
                result.append(child)
        return result
