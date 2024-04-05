from .base import MarkerWithEnd
from .cc import CmdCallMarker
from .empty import EmptyMarker


class CmdCallBlockMarker(MarkerWithEnd):
    tag_head = "@ccb"

    def exec(self, env, command, marker_node, marker_set):
        marker = marker_set.find_marker_by_cls(CmdCallMarker)
        result = []
        for child in marker_node.children:
            if child.is_type(EmptyMarker):
                node = marker_set.node_cls(marker,
                                           CmdCallMarker.tag_head + ' ' + child.command,
                                           child.index,
                                           marker_node,
                                           child.command
                                           )
                result.append(node)
            else:
                result.append(child)
        return result
