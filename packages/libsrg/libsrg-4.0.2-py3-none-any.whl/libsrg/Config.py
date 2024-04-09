import configparser
import json
import re
from collections import ChainMap
from pathlib import Path
from typing import Any, Self, Optional

from jinja2 import Template


class Config(ChainMap):
    _secret_config: Self | None = None

    @classmethod
    def set_secrets(cls, *args: Self | ChainMap | dict[str, Any]) -> None:
        """Constructs a new Config object and installs it as secret_config """
        cls._secret_config = cls(*args)

    def __init__(self, *args: Self | ChainMap | dict[str, Any]):
        args2 = self.process_args(*args)
        super().__init__(*args2)

    @classmethod
    def process_args(cls, *args: Self | ChainMap | dict[str, Any]) -> list[dict[str, Any]]:
        pending: list[Any] = list(args)
        out: list[dict[str, Any]] = []
        while len(pending) > 0:
            candidate = pending.pop(0)

            # for ChainMap/Config inputs, add the individual maps
            if isinstance(candidate, ChainMap):
                maps = candidate.maps.copy() # dont consume the source!
                while len(maps) > 0:
                    map = maps.pop(-1)
                    pending.insert(0, map)
                continue

            # assume string argument is a pathname
            if isinstance(candidate, str):
                candidate = Path(candidate)

            # open path arguments
            if isinstance(candidate, Path):
                with open(candidate, "r") as f:
                    text = f.read()
                # noinspection PyBroadException
                candidate = cls.text_to_dict(text)

            # only valid choice is dict here
            if isinstance(candidate, dict):
                out.append(candidate)
            else:
                raise TypeError(f"{type(candidate)} unexpected at {candidate}")
        return out

    @classmethod
    def text_to_dict(cls, text: str) -> dict[str, Any]:
        text = cls.strip_comments(text)
        json_pat = re.compile(r"^\s*\{", re.MULTILINE)
        if json_pat.match(text):
            out = json.loads(text)
            return out
        ini_pat = re.compile(r"^\s*\[", re.MULTILINE)
        if ini_pat.match(text):
            cp = configparser.ConfigParser()
            cp.read_string(text)
            # reformat ini data as native dict of dicts
            out = {name: {k: v for k, v in cp[name].items()} for name in cp.sections()}
            return out
        # fallback to flat env like file w/o [inisection]
        cp = configparser.ConfigParser()
        cp.read_string("[qqq]\n" + text)
        out = {k: v for k, v in cp["qqq"].items()}
        return out

    @classmethod
    def strip_comments(cls, text: str) -> str:
        lines = text.split("\n")
        new_lines = [line for line in lines if not line.strip(" \t").startswith(("#", ";", "//"))]
        return "\n".join(new_lines)

    def get_config_item(self, *names: str, default=None, allow_none=False,
                        secrets: bool = False, jinja=True) -> Any:
        """
        get an argument from self.merged_args
        :param jinja: TODO
        :param secrets:
        :param config:
        :param names: one or more redundant names, first found used
        :param default: if none of the names are found return this value
        :param allow_none: set True to suppress KeyError if returning None
        :return: first parameter found or None if allow_none is set

        This getter is designed to support gradual switchover from legacy names to newer names.

        As a special case, if an Exception type is placed in the chain of adaption data, it will get raised.
        This is intended to facilitate marking required parameters in default config data.
        """
        val = default
        config = self
        if secrets and self._secret_config is not None:
            config = ChainMap(config, self._secret_config)
        for name in names:
            if name in config:
                val = config[name]
                break
        if val is None and not allow_none:
            raise KeyError(f"keys not found: {names}")
        if isinstance(val, Exception):
            raise val
        if jinja or secrets:
            # config already has secrets if enabled
            val = self.apply_templates_to_strings(val, config=config, secrets=False)
        return val

    def apply_templates_to_strings(self, data: Any, config: Optional[Self] = None,
                                   secrets: bool = False) -> Any:
        """
        apply templates to strings in data (applies to str or list of str, else return unchanged

        """
        if config is None:
            config = self
        if secrets:
            config = ChainMap(config, self._secret_config)
        if isinstance(data, str):
            template = Template(data)
            val = template.render(config)
            return val
        if isinstance(data, list):
            # only apply to list of str, not list of Any
            if all([isinstance(x, str) for x in data]):
                return [self.apply_templates_to_strings(x, config=config, secrets=False) for x in data]
        return data

    def set_config_if_missing(self, key: str, val: Any):
        self.set_config(key, val, overwrite=False)

    def set_config(self, key: str, value: Any, overwrite=True, ) -> None:
        if key not in self or overwrite:
            self[key] = value
