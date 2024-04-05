import simplycli
from simplycli.decorators import __annotated__
from simplycli.meta import CommandLike, AbstractFunctionCommandWrapper, forward_meta


class __BundleCommand__(AbstractFunctionCommandWrapper):
    def __init__(self, command_like: CommandLike, properties):
        self.command_like = command_like

        self.__bundle_properties__ = properties
        self.__bundle__ = None

        forward_meta(self.command_like, self)

    def signature(self) -> CommandLike:
        return self.command_like

    def invoke(self, *args, **kwargs):
        args = list(args)
        args.insert(0, self.__bundle__)
        return self.command_like(*args, **kwargs)


class Bundle:
    @staticmethod
    @__annotated__
    def command(f, **properties):
        return __BundleCommand__(f, properties)

    def __commands__(self) -> list[__BundleCommand__]:
        cmds = []
        for attr in dir(self):
            val = getattr(self, attr)
            if getattr(val, "__bundle_properties__", None) is not None:
                val.__bundle__ = self
                cmds.append(val)
        return cmds


class BundleManager:
    def __init__(self, cli: "simplycli.CLI"):
        self._bundle_map: dict[Bundle, list[__BundleCommand__]] = {}

        self.cli = cli

    def active(self) -> set[Bundle]:
        return self._bundle_map.keys()

    def apply(self, bundle: Bundle):
        if bundle in self._bundle_map:
            cmds = self._bundle_map[bundle]
            new_cmds = [c for c in bundle.__commands__() if c not in cmds]
            for cmd in new_cmds:
                self.cli.command(cmd, **cmd.__bundle_properties__)
                cmds.append(cmd)
            return

        cmds = bundle.__commands__()
        self._bundle_map[bundle] = cmds
        for command in cmds:
            self.cli.command(command, **command.__bundle_properties__)

    def remove(self, bundle: Bundle):
        if bundle in self._bundle_map:
            cmds = self._bundle_map.pop(bundle)
            for command in cmds:
                self.cli.unregister(command)
