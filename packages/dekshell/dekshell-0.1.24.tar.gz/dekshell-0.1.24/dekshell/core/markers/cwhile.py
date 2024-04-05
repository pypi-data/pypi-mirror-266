from .base import MarkerWithEnd, BreakMarker, ContinueMarker


class WhileMarker(MarkerWithEnd):
    tag_head = "@while"

    def bubble_continue(self, env, marker_node_self, marker_node_target):
        if marker_node_target.is_type(BreakMarker):
            return marker_node_self, []
        elif marker_node_target.is_type(ContinueMarker):
            return marker_node_self, [marker_node_self]
        return None

    def exec(self, env, command, marker_node, marker_set):
        result = self.get_condition_result(env, command)
        if result:
            return [*marker_node.children, marker_set.node_cls(ContinueMarker(), None, None, marker_node)]
        else:
            return []

    def get_condition_result(self, env, command):
        argv = self.split(command)
        args, kwargs = self.cmd2ak(argv[2:])
        return self.call_func(env, self.get_item(argv, 1, 'false'), *args, **kwargs)
