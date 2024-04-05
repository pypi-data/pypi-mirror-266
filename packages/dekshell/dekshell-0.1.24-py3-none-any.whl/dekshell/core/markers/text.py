from .base import MarkerWithEnd


class TextMarker(MarkerWithEnd):
    tag_head = "@text"

    def exec(self, env, command, marker_node, marker_set):
        commands = []
        marker_node.walk(lambda node, depth: commands.extend([] if depth == 0 else [node.command]))
        args = self.split_raw(command, 2)
        text = '\n'.join(commands)
        self.set_var(env, args, 1, self.translate(env, text))
        return []
