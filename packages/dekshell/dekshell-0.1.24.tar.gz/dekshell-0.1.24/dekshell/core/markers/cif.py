from .base import MarkerWithEnd


class MarkerWithJudge(MarkerWithEnd):
    def exec(self, env, command, marker_node, marker_set):
        result = self.get_condition_result(env, command)
        index = next((i for i, child in enumerate(marker_node.children) if child.is_type(*self.final_branch_set)), None)
        if result:
            return marker_node.children[:index]
        else:
            if index is None:
                return []
            else:
                return marker_node.children[index:]

    def get_condition_result(self, env, command):
        argv = self.split(command)
        args, kwargs = self.cmd2ak(argv[2:])
        return self.call_func(env, self.get_item(argv, 1, 'false'), *args, **kwargs)


class IfElseMarker(MarkerWithJudge):
    tag_head = "@else"


class IfElifMarker(MarkerWithJudge):
    tag_head = "@elif"
    branch_set = {None, IfElseMarker}


class IfMarker(MarkerWithJudge):
    tag_head = "@if"
    branch_set = {IfElifMarker, IfElseMarker}
