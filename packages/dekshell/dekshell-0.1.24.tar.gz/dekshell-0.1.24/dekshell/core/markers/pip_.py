from dektools.file import write_file
from ...utils.pkg import get_installed_distributions_map, is_dist_installed
from .base import MarkerWithEnd


class PipMarker(MarkerWithEnd):
    tag_head = "@pip"

    def exec(self, env, command, marker_node, marker_set):
        def walk(node, depth):
            if depth != 0:
                for c in node.command.split('||'):
                    c = c.strip()
                    if c:
                        req_list.append(c)

        req_list = []
        marker_node.walk(walk)
        dist_map = get_installed_distributions_map()
        req_list = [req for req in req_list if not is_dist_installed(req, dist_map)]
        fp = write_file(None, t='\n'.join(req_list))
        env.shell(f'pip install -r {fp}')
        return []
