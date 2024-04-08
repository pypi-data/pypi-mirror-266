import builtins
import inspect
import os
import re
import sys
import traceback
from abc import ABC, abstractmethod
from collections import OrderedDict
from contextlib import contextmanager
from copy import copy, deepcopy
from dataclasses import dataclass, field, is_dataclass
from functools import wraps
from pathlib import Path
from threading import Lock, Thread
from time import sleep
from types import FrameType, MethodType, ModuleType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

import envium
from envium import computed_env_var, env_var
from rhei import Stopwatch

from envo import logger, utils
from envo.environ import environ
from envo.exceptions import user_code
from envo.logs import Logger
from envo.status import Status
from envo.utils import (
    Callback,
    import_env_from_file,
    import_from_file,
)

__all__ = [
    "Env",
    "command",
    "shell_context",
    "precmd",
    "postcmd",
    "onstdout",
    "onstderr",
    "oncreate",
    "onload",
    "onunload",
    "ondestroy",
    "boot_code",
    "Source",
]

T = TypeVar("T")

from envo.exceptions import UserError
from envo.shell import Shell

if TYPE_CHECKING:
    from envo import Plugin
    from envo.scripts import Status


class MagicFunctionData:
    type: str
    namespace: str
    expected_fun_args: List[str]


# magic function data
mfd_field = "mfd"


@dataclass
class MagicFunction:
    type: str
    expected_fun_args = None

    original_caller: Optional[Callable] = None

    def __new__(cls, *args, **kwargs) -> Callable:
        if args and callable(args[0]):
            fun = cast(Callable[..., Any], args[0])

            args = args[1:]

            cls._inject_data(fun, *args, **kwargs)
            return fun
        else:
            def decor(fun):
                cls._inject_data(fun, *args, **kwargs)
                return fun

            return decor

    @classmethod
    def _wrap_fun(cls, fun: Callable) -> Callable:
        return fun

    @classmethod
    def _inject_data(cls, wrapped: Callable, *args, **kwargs) -> None:
        wrapped.mfd = MagicFunctionData()
        wrapped.mfd.type = cls.type
        wrapped.mfd.expected_fun_args = cls.expected_fun_args

    @contextmanager
    def _context(self, *args, **kwargs) -> None:
        yield


@dataclass
class command(MagicFunction):
    type = "command"

    def __new__(cls, *args, in_root: Optional[bool] = True, cd_back: Optional[bool] = True) -> Callable:
        if args and callable(args[0]):
            fun = cast(Callable[..., Any], args[0])
            args = args[1:]

            @wraps(fun)
            def wrapped(*fun_args, **fun_kwargs):
                return cls._call(fun, fun_args, fun_kwargs, in_root, cd_back)

            cls._inject_data(wrapped, *args)
            return wrapped
        else:

            def decor(fun):
                @wraps(fun)
                def wrapped(*fun_args, **fun_kwargs):
                    return cls._call(fun, fun_args, fun_kwargs, in_root, cd_back)

                cls._inject_data(wrapped, in_root, cd_back)
                return wrapped

            return decor

    @classmethod
    def _call(cls, fun: Callable, fun_args, fun_kwargs, in_root: Optional[bool] = True, cd_back: Optional[bool] = True):
        if not cls.original_caller:
            cls.original_caller = fun

        if not fun_args or not isinstance(fun_args[0], Env):
            if fun_args and fun_args[0] == "__env__":
                fun_args = (builtins.__env__, *fun_args[1:])
            else:
                fun_args = (builtins.__env__, *fun_args)
        try:
            with cls._context(fun_args[0], in_root, cd_back):
                ret = fun(*fun_args, **fun_kwargs)
            return ret
        except Exception as e:
            if cls.original_caller is fun:
                logger.traceback()
                sys.exit(1)
            else:
                raise e
        finally:
            if cls.original_caller is fun:
                cls.original_caller = None

    @classmethod
    @contextmanager
    def _context(cls, env: "Env", in_root: Optional[bool] = True, cd_back: Optional[bool] = True) -> None:
        cwd = Path(".").absolute()

        if in_root:
            os.chdir(str(env.meta.root))

        try:
            yield
        finally:
            if cd_back:
                os.chdir(str(cwd))


class boot_code(MagicFunction):  # noqa: N801
    type: str = "boot_code"


class Event(MagicFunction):  # noqa: N801
    pass


class onload(Event):  # noqa: N801
    type: str = "onload"


class oncreate(Event):  # noqa: N801
    type: str = "oncreate"


class ondestroy(Event):  # noqa: N801
    type: str = "ondestroy"


class onunload(Event):  # noqa: N801
    type: str = "onunload"


class cmd_hook(MagicFunction):  # noqa: N801
    def __new__(cls, cmd_regex: str = ".*") -> Callable:
        ret = super().__new__(cls, cmd_regex)
        return ret

    @classmethod
    def _inject_data(cls, wrapped: Callable, cmd_regex: str = ".*") -> None:
        super()._inject_data(wrapped, cmd_regex)
        wrapped.mfd.cmd_regex = cmd_regex


class precmd(cmd_hook):  # noqa: N801
    type: str = "precmd"
    expected_fun_args = ["command", "out"]


class onstdout(cmd_hook):  # noqa: N801
    type: str = "onstdout"
    expected_fun_args = ["command", "out"]


class onstderr(cmd_hook):  # noqa: N801
    type: str = "onstderr"
    expected_fun_args = ["command", "out"]


class postcmd(cmd_hook):  # noqa: N801
    type: str = "postcmd"
    expected_fun_args = ["command", "stdout", "stderr"]


class shell_context(MagicFunction):  # noqa: N801
    type: str = "shell_context"

    def __init__(self) -> None:
        super().__init__()


PathLike = Union[Path, str]

magic_functions = {
    "command": command,
    "shell_context": shell_context,
    "boot_code": boot_code,
    "onload": onload,
    "onunload": onunload,
    "oncreate": oncreate,
    "ondestroy": ondestroy,
    "precmd": precmd,
    "onstdout": onstdout,
    "onstderr": onstderr,
}


@dataclass
class Source:
    root: Path
    watch_files: List[str] = field(default_factory=list)
    ignore_files: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.root = self.root.resolve()


class BaseEnv(ABC):
    class Meta:
        pass

    @abstractmethod
    def init(self) -> None:
        pass

    @abstractmethod
    def post_init(self) -> None:
        pass


class Env(BaseEnv):
    class Meta:
        """
        Environment metadata.
        """

        root: Path
        name: Optional[str] = None
        version: str = "0.1.0"
        parents: List[str] = []
        plugins: List["Plugin"] = []
        sources: List[Source] = []
        emoji: str = ""
        stage: str = "comm"
        watch_files: List[str] = []
        ignore_files: List[str] = []
        verbose_run: bool = True
        load_env_vars: bool = False

    class Environ(envium.Environ):
        pythonpath: Optional[List[PathLike]] = env_var(raw=True, default_factory=list)
        path: Optional[List[PathLike]] = env_var(raw=True, default_factory=list)
        root: Optional[Path] = env_var()
        stage: Optional[str] = env_var()
        envo_stage: Optional[str] = env_var(raw=True)
        envo_name: Optional[str] = env_var(raw=True)

    class Ctx(envium.Ctx):
        pass

    class Secrets(envium.Secrets):
        pass

    ctx: Ctx
    secrets: Secrets
    meta: Meta

    _environ_before: Optional[Dict[str, str]]

    env_id_to_secrets: ClassVar[Dict[str, Secrets]] = {}
    _shell: "Shell"

    def __init__(self):
        self._environ_before = os.environ.copy()
        self.meta = self.Meta()

        self.e = self.Environ(name=self.meta.name, load=self.meta.load_env_vars)
        self.e.envo_name = self.meta.name

        self.e.root = self.meta.root
        self.e.stage = self.meta.stage
        self.e.envo_stage = self.meta.stage

        self.e.path = self._path_str_to_list(os.environ["PATH"])

        if "PYTHONPATH" not in os.environ:
            self.e.pythonpath = []
        else:
            self.e.pythonpath = self._path_str_to_list(os.environ["PYTHONPATH"])

        self.ctx = self.Ctx(self.meta.name)

        secrets = Env.env_id_to_secrets.get(self.id, self.Secrets(self.meta.name))
        self.secrets = Env.env_id_to_secrets[self.id] = secrets

        self.init()

        self.validate()
        self.activate()

        self.post_init()

    def _get_path_delimiter(self) -> str:
        if utils.is_linux() or utils.is_darwin():
            return ":"
        elif utils.is_windows():
            return ";"
        else:
            raise NotImplementedError

    def _path_str_to_list(self, path: str) -> List[Path]:
        paths_str = path.split(self._get_path_delimiter())
        ret = [Path(s) for s in paths_str]
        return ret

    @classmethod
    def instantiate(cls, stage: Optional[str] = None) -> "Env":
        if not stage:
            stage = environ.stage

        env_class = import_from_file(cls.Meta.root / f"env_{stage}.py").ThisEnv
        return env_class()

    def init(self) -> None:
        super().init()
        pass

    def post_init(self) -> None:
        pass

    @property
    def id(self) -> str:
        return f"{self.__class__.__module__}:{self.__class__.__name__}"

    def validate(self) -> None:
        """
        Validate env
        """

        msgs = []
        if self.ctx.errors:
            msgs.append(f"Context errors in {self.meta.root}:\n" + f"\n".join([str(e) for e in self.ctx.errors]))

        if self.e.errors:
            msgs.append(f"Environ errors in {self.meta.root}:\n" + f"\n".join([str(e) for e in self.e.errors]))

        if self.secrets.errors:
            msgs.append(f"Secrets errors  in {self.meta.root}:\n" + f"\n".join([str(e) for e in self.e.errors]))

        msg = "\n".join(msgs)

        if msg:
            raise UserError(msg)

    def get_env_vars(self) -> Dict[str, str]:
        ret = self.e.get_env_vars()
        return ret

    def get_user_envs(self) -> List[Type["Env"]]:
        ret = []
        for c in self.__class__.__mro__:
            if not issubclass(c, Env) or c is Env:
                continue
            ret.append(c)

        return ret

    def get_env(self, directory: Union[Path, str], stage: Optional[str] = None) -> "Env":
        stage = stage or self.meta.stage
        directory = Path(directory)
        env_file = directory / f"env_{stage}.py"

        if not env_file.exists():
            with user_code():
                logger.traceback()
            raise UserError(f"{env_file} does not exit")

        env = import_env_from_file(env_file).ThisEnv()
        return env

    @classmethod
    def get_env_path(cls) -> Path:
        return cls.Meta.root / f"env_{cls.Meta.stage}.py"

    def dump_dot_env(self) -> Path:
        """
        Dump .env file for the current environment.

        File name follows env_{env_name} format.
        """
        path = Path(f".env_{self.meta.stage}")
        content = "\n".join([f'{key}="{value}"' for key, value in self.e.get_env_vars().items()])
        path.write_text(content, "utf-8")
        return path

    def activate(self) -> None:
        if not self._environ_before:
            self._environ_before = os.environ.copy()

        os.environ.update(**self.get_env_vars())

    def deactivate(self) -> None:
        if self._environ_before:
            os.environ = self._environ_before.copy()


class ShellEnv:
    """
    Defines environment.
    """

    @dataclass
    class _Links:
        shell: Optional["Shell"]
        env: Env
        status: "Status"

    @dataclass
    class _Sets:
        blocking: bool = False

    _sys_modules_snapshot: Dict[str, ModuleType] = OrderedDict()
    magic_functions: Dict[str, Any]
    env: Env

    def __init__(self, se: _Sets, li: _Links) -> None:
        self._se = se
        self._li = li
        self.env = self._li.env

        self.env._shell = self._li.shell

        self.magic_functions = {
            "shell_context": {},
            "precmd": {},
            "onstdout": {},
            "onstderr": {},
            "postcmd": {},
            "onload": {},
            "oncreate": {},
            "ondestroy": {},
            "onunload": {},
            "boot_code": {},
            "command": {},
        }

        if self.env.meta.verbose_run:
            os.environ["ENVO_VERBOSE_RUN"] = "True"
        elif os.environ.get("ENVO_VERBOSE_RUN"):
            os.environ.pop("ENVO_VERBOSE_RUN")

        self._exiting = False

        self._shell_environ_before = None

        self.logger: Logger = logger.create_child("envo", descriptor=self.env.meta.name)

        self._environ_before = None
        self._shell_environ_before = None
        self._collect_magic_functions()

        self.logger.debug("Starting env", metadata={"root": self.env.meta.root, "stage": self.env.meta.stage})

        self._li.shell.calls.pre_cmd = Callback(self._on_precmd)
        self._li.shell.calls.on_stdout = Callback(self._on_stdout)
        self._li.shell.calls.on_stderr = Callback(self._on_stderr)
        self._li.shell.calls.post_cmd = Callback(self._on_postcmd)
        self._li.shell.calls.on_exit = Callback(self._on_destroy)

        if "" in sys.path:
            sys.path.remove("")

        if not self._sys_modules_snapshot:
            self._sys_modules_snapshot = OrderedDict(sys.modules.copy())

        builtins.__env__ = self.env

    def get_name(self) -> str:
        """
        Return env name
        """
        return self.env.meta.name

    def redraw_prompt(self) -> None:
        self._li.shell.redraw()

    def load(self) -> None:
        """
        Called after creation.
        :return:
        """

        def thread(self: "ShellEnv") -> None:
            logger.debug("Starting onload thread")

            sw = Stopwatch()
            sw.start()

            onload_funs = self.magic_functions["onload"].values()

            try:
                for h in onload_funs:
                    h(self.env)
                self._run_boot_codes()
            except Exception as e:
                with user_code():
                    logger.traceback()
                self._exit()
                return

            # declare commands
            for name, c in self.magic_functions["command"].items():
                self._li.shell.set_variable(name, c)

            # set context
            self._li.shell.set_context(self._get_shell_context())
            while sw.value <= 0.5:
                sleep(0.1)

            logger.debug("Finished load context thread")
            self._li.status.shell_context_ready = True
            self.first_run = False

        if not self._se.blocking:
            Thread(target=thread, args=(self,)).start()
        else:
            thread(self)

    def on_shell_create(self) -> None:
        """
        Called only after creation.
        :return:
        """
        functions = self.magic_functions["oncreate"].values()
        for h in functions:
            h(self.env)

    def _get_namespace_and_function(self, name: str) -> Tuple[Optional[str], str]:
        if "__" in name and not name.endswith("__"):
            namespace = name.split("__")[0]
            f = "".join(name.split("__")[1:])
            return namespace, f
        else:
            return None, name

    def _collect_magic_functions(self) -> None:
        """
        Go through fields and transform decorated functions to commands.
        """

        def hasattr_static(obj: Any, field: str) -> bool:
            try:
                inspect.getattr_static(obj, field)
            except AttributeError:
                return False
            else:
                return True

        for c in reversed(self.env.__class__.__mro__):
            for f in dir(c):
                if hasattr_static(self.__class__, f) and inspect.isdatadescriptor(
                    inspect.getattr_static(self.__class__, f)
                ):
                    continue

                attr = inspect.getattr_static(c, f)

                if hasattr(attr, mfd_field):
                    namespace, f = self._get_namespace_and_function(f)
                    namespaced_name = f"{namespace}.{f}" if namespace else f
                    self.magic_functions[attr.mfd.type][namespaced_name] = attr

    def _get_shell_context(self) -> Dict[str, Any]:
        shell_context = {}
        for c in self.magic_functions["shell_context"].values():
            try:
                with user_code():
                    cont = c(self.env)
            except Exception as e:
                logger.traceback()
                continue
            for k, v in cont.items():
                namespace, f = self._get_namespace_and_function(k)

                namespaced_name = f"{namespace}.{f}" if namespace else k
                shell_context[namespaced_name] = v

        return shell_context

    def _on_destroy(self) -> None:
        functions = self.magic_functions["ondestroy"]
        for h in functions.values():
            h()

        self._exit()

    def _exit(self) -> None:
        self.logger.debug("Exiting env")

    def activate(self) -> None:
        """
        Validate env and send vars to os.environ

        :param owner_namespace:
        """
        if not self._shell_environ_before:
            self._shell_environ_before = dict(self._li.shell.environ.items())
        self._li.shell.environ.update(**self.env.get_env_vars())

    def _deactivate(self) -> None:
        """
        Validate env and send vars to os.environ

        :param owner_namespace:
        """
        if self._shell_environ_before:
            if self._li.shell:
                tmp_environ = copy(self._li.shell.environ)
                for i, v in tmp_environ.items():
                    self._li.shell.environ.pop(i)
                for k, v in self._shell_environ_before.items():
                    if v is None:
                        continue
                    self._li.shell.environ[k] = v

        self.env.deactivate()

    def _run_boot_codes(self) -> None:
        self._li.status.source_ready = False
        boot_codes_f = self.magic_functions["boot_code"]

        codes = []

        for f in boot_codes_f.values():
            with user_code():
                codes.extend(f(self.env))

        for c in codes:
            self._li.shell.run_code(c)

        self._li.status.source_ready = True

    def _on_precmd(self, command: str) -> Optional[str]:
        functions = self.magic_functions["precmd"]
        for f in functions.values():
            if re.match(f.mfd.cmd_regex, command):
                with user_code():
                    ret = f(self.env, command)  # type: ignore
                command = ret

        return command

    def _on_stdout(self, command: str, out: bytes) -> str:
        functions = self.magic_functions["onstdout"]
        for f in functions.values():
            if re.match(f.mfd.cmd_regex, command):
                with user_code():
                    ret = f(self.env, command, out)  # type: ignore
                if ret:
                    out = ret
        return out

    def _on_stderr(self, command: str, out: bytes) -> str:
        functions = self.magic_functions["onstderr"]
        for f in functions.values():
            if re.match(f.mfd.cmd_regex, command):
                with user_code():
                    ret = f(self.env, command, out)  # type: ignore
                if ret:
                    out = ret
        return out

    def _on_postcmd(self, command: str, stdout: str, stderr: str) -> None:
        functions = self.magic_functions["postcmd"]
        for f in functions.values():
            if re.match(f.mfd.cmd_regex, command):
                with user_code():
                    f(self.env, command, stdout, stderr)  # type: ignore

    def _unload(self) -> None:
        self._deactivate()
        functions = self.magic_functions["onunload"]
        for f in functions.values():
            f(self.env)
        self._li.shell.calls.reset()
