from dektools.shell import shell_wrapper
from ...core.redirect import redirect_shell_by_path_tree
from ..contexts.properties import make_shell_properties
from .base import MarkerBase


class RedirectMarker(MarkerBase):
    tag_head = "@redirect"

    def exec(self, env, command, marker_node, marker_set):
        path_dir = self.split_raw(command, 1)[1]
        path_shell = redirect_shell_by_path_tree(path_dir)
        if path_shell:
            shell_properties = make_shell_properties(path_shell)
            if shell_properties['shell'] != path_shell:
                shrf = shell_properties['shrf']
                shell_wrapper(f'{shrf} {env.context["fp"]}')
                self.exit()
