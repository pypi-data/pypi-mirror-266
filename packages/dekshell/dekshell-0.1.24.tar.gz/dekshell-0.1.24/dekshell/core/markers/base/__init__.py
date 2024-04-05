import os
import re
import shlex
import functools
from dektools.str import str_format_var
from dektools.common import classproperty
from dektools.shell import shell_output, shell_exitcode


class MarkerBase:
    tag_head = None
    tag_tail = None
    branch_set = set()

    var_name_anonymous = '_'

    trans_marker_command_rc = '>?'  # return code
    trans_marker_command = '>'
    trans_marker_eval = '='
    trans_marker_env = '$'
    trans_marker_ignore = '?'

    value_unset = object()

    def recognize(self, command):
        command = self.strip(command)
        return self.tag_head == '' or \
            command.startswith(self.tag_head) and \
            command[len(self.tag_head):len(self.tag_head) + 1] in ('', ' ')

    def bubble_continue(self, env, marker_node_self, marker_node_target):
        return None

    def exec(self, env, command, marker_node, marker_set):
        pass

    def exit(self):
        raise ExitException()

    def set_var(self, env, array, index, value):
        env.context[self.get_item(array, index, self.var_name_anonymous)] = value

    def call_func(self, env, func_name, *args, **kwargs):
        args, kwargs = self.var_map_batch(env, *args, **kwargs)
        func = env.context.get(func_name)
        if func is None:
            func = self.eval(env, func_name)
        return func(*args, **kwargs)

    def translate(self, env, s):
        def second(content):
            _begin, _end = '!', '!'
            _fx, _args = str_format_var(content, _begin, _end)
            return _fx(_args, env.eval_locals, lambda key: f'{_begin}{key}{_end}')

        def missing(key):
            if key.startswith(self.trans_marker_command_rc):
                return shell_exitcode(second(key[len(self.trans_marker_command_rc):]))
            elif key.startswith(self.trans_marker_command):
                return shell_output(second(key[len(self.trans_marker_command):]))
            elif key.startswith(self.trans_marker_eval):
                return self.eval(env, second(key[len(self.trans_marker_eval):]))
            elif key.startswith(self.trans_marker_env):
                return os.getenv(second(key[len(self.trans_marker_env):]))
            elif key.startswith(self.trans_marker_ignore):
                try:
                    return self.eval(env, second(key[len(self.trans_marker_ignore):]))
                except NameError:
                    return ''
            else:
                return f'{begin}{key}{end}'

        begin, end = '{', '}'
        fx, args = str_format_var(s, begin, end)
        return fx(args, env.eval_locals, missing)

    @classproperty
    @functools.lru_cache(None)
    def final_branch_set(cls):
        return {cls if x is None else x for x in cls.branch_set}

    @staticmethod
    def get_item(array, index, default=None):
        if array:
            try:
                return array[index]
            except IndexError:
                pass
        return default

    @staticmethod
    def strip(command):
        return command.strip()

    @staticmethod
    def split(command, posix=False):
        return shlex.split(command, posix=posix)

    @staticmethod
    def split_raw(command, maxsplit=-1):
        result = []
        for x in command.split(' '):
            x = x.strip()
            if x:
                result.append(x)
        return ' '.join(result).split(' ', maxsplit)

    @staticmethod
    def eval(env, s, v=None):
        return eval(s, env.eval_locals | (v or {}))

    def get_var(self, env, s, v=None):
        try:
            return self.eval(env, s, v)
        except NameError:
            return self.value_unset

    @staticmethod
    def eval_multi(env, s, v=None):
        locals_ = env.eval_locals | (v or {})
        exec(s, locals_)
        return locals_

    @staticmethod
    def var_map(env, s):
        if re.match(r'\$[0-9a-zA-Z_]+$', s):
            return env.eval_locals[s[1:]]
        else:
            return s.replace(r'\$', "$")

    @classmethod
    def var_map_batch(cls, env, *args, **kwargs):
        return [cls.var_map(env, x) for x in args], {k: cls.var_map(env, v) for k, v in kwargs.items()}

    @staticmethod
    def cmd2ak(argv):  # arg0 arg1 k0**kwarg0 k1**kwarg1
        args = []
        kwargs = {}
        for x in argv:
            if re.match(r'[0-9a-zA-Z_]+\*\*(?!\*)', x):
                k, v = x.split('**', 1)
                kwargs[k] = v
            else:
                args.append(x.replace(r'\*', "*"))
        return args, kwargs


class EndMarker(MarkerBase):
    tag_head = "@end"


class BreakMarker(MarkerBase):
    tag_head = "@break"


class ContinueMarker(MarkerBase):
    tag_head = "@continue"


class MarkerWithEnd(MarkerBase):
    tag_tail = EndMarker


class MarkerShell(MarkerBase):
    shell_cls = None

    def exec(self, env, command, marker_node, marker_set):
        command = self.strip(command)
        if command:
            kwargs = marker_node.payload or {}
            env.shell(command, self.shell_cls(kwargs))


class ExitException(Exception):
    pass
