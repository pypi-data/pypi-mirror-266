import os
from .base import MarkerBase


class EnvMarker(MarkerBase):
    tag_head = "@env"

    def exec(self, env, command, marker_node, marker_set):
        argv = self.split(command, True)
        args, _ = self.cmd2ak(argv[1:3])
        args, _ = self.var_map_batch(env, *args)
        os.environ[args[0]] = args[1]
