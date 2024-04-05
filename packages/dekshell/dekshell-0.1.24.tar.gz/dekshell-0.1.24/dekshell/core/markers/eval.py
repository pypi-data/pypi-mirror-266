from .base import MarkerWithEnd


class EvalMarker(MarkerWithEnd):
    tag_head = "@eval"

    def exec(self, env, command, marker_node, marker_set):
        commands = []
        marker_node.walk(lambda node, depth: commands.extend([] if depth == 0 else [node.command]))
        text = '\n'.join(commands)
        code = self.translate(env, text)

        codes = []
        for line in code.split('\n'):
            if line.strip():
                codes.append(' ' * 4 + line)
        codes[-1] = f'    return {codes[-1]}'
        code = f'def inner_temp_func():\n' + "\n".join(codes)

        locals_ = self.eval_multi(env, code)
        result = locals_['inner_temp_func']()
        if not isinstance(result, (list, tuple)):
            result = [result]

        argv = self.split_raw(command)[1:]
        for i in range(len(argv)):
            self.set_var(env, argv, i, self.get_item(result, i, None))

        return []
