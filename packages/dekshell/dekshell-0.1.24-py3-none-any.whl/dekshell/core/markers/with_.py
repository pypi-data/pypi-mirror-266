from ...core.redirect import redirect_shell_by_path_tree
from .base import MarkerBase
from ..contexts.properties import make_shell_properties


class WithMarker(MarkerBase):
    tag_head = "@with"

    def exec(self, env, command, marker_node, marker_set):
        path_dir = self.split_raw(command, 1)[1]
        path_shell = redirect_shell_by_path_tree(path_dir)
        for k, v in make_shell_properties(path_shell).items():
            self.set_var(env, [k], 0, v)
