from .base import MarkerWithEnd, BreakMarker, ContinueMarker


class ForMarker(MarkerWithEnd):
    tag_head = "@for"

    def bubble_continue(self, env, marker_node_self, marker_node_target):
        if marker_node_target.is_type(BreakMarker):
            var_temp_iter = self._get_var_temp_iter(marker_node_self)
            self.set_var(env, [var_temp_iter], 0, self.value_unset)
            var_temp_list = self._get_var_temp_list(marker_node_self)
            self.set_var(env, [var_temp_list], 0, self.value_unset)
            return marker_node_self, []
        elif marker_node_target.is_type(ContinueMarker):
            return marker_node_self, [marker_node_self]
        return None

    def exec(self, env, command, marker_node, marker_set):
        argv = self.split(command)
        args = argv[1:]
        assert len(args) in (1, 2, 3)
        var_temp_list = self._get_var_temp_list(marker_node)
        array_total = self.get_var(env, var_temp_list)
        if array_total is self.value_unset:
            array_total = list(self.eval(env, args[-1]))
            self.set_var(env, [var_temp_list], 0, array_total)
        var_temp_iter = self._get_var_temp_iter(marker_node)
        array = self.get_var(env, var_temp_iter)
        if array is self.value_unset:
            array = array_total
        if array:
            self.set_var(env, [var_temp_iter], 0, array[1:])
            if len(args) == 2:
                self.set_var(env, [args[0]], 0, array[0])
            elif len(args) == 3:
                self.set_var(env, [args[0]], 0, len(array_total) - len(array))
                self.set_var(env, [args[1]], 0, array[0])
            return [*marker_node.children, marker_set.node_cls(ContinueMarker(), None, None, marker_node)]
        else:
            self.set_var(env, [var_temp_iter], 0, self.value_unset)
            self.set_var(env, [var_temp_list], 0, self.value_unset)
            return []

    def _get_var_temp_iter(self, node):
        return f'__shell_var_temp__for_iter__{node.index}'

    def _get_var_temp_list(self, node):
        return f'__shell_var_temp__for_list__{node.index}'
