from .cif import MarkerWithJudge


class MarkerWithJudgePy(MarkerWithJudge):
    def get_condition_result(self, env, command):
        argv = self.split_raw(command, 1)
        return self.eval(env, self.get_item(argv, 1, 'false()'))


class PyIfElseMarker(MarkerWithJudgePy):
    tag_head = "@pyelse"


class PyIfElifMarker(MarkerWithJudgePy):
    tag_head = "@pyelif"
    branch_set = {None, PyIfElseMarker}


class PyIfMarker(MarkerWithJudgePy):
    tag_head = "@pyif"
    branch_set = {PyIfElifMarker, PyIfElseMarker}
