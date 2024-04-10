import configparser
import json
import re
from collections import ChainMap
from pathlib import Path
from typing import Any, Self, Optional, Tuple

from jinja2 import Template


class Config(ChainMap):
    """
    The Config class extends the ChainMap class to provide access to config files.

    From outside, a Config looks like a series of python dictionaries which get searched in
    order for a given configuation item,

    Jinja argument processing can be applied on a per item basis using the get_item function,
    Jinja processing is NOT applied as files are read in from the config file. Other items in the config
    can be referenced in jinja templates.

    The Config class maintains one special Config instance which contains secrets. These can be usernames,
    passwords, api keys, or anything else that should not normally be kept in publicly accessible
    configuration files. One file of secrets can be read from a secure location and referenced by items
    in the normal config files.

    """
    _secret_config: Self | None = None

    @classmethod
    def set_secrets(cls, *args: Self | ChainMap | dict[str, Any] | Path) -> None:
        """
        Sets the secret config held by this class.
        :param args: zero or more Config, ChainMap, dict[str, Any], Path
        :return: None
        """
        cls._secret_config = cls(*args)

    def __init__(self, *args: Self | ChainMap | dict[str, Any] | Path):
        """
        Constructs a new Config object.
        :param args: zero or more Config, ChainMap, dict[str, Any], Path
        """
        args2 = self.process_args(*args)
        super().__init__(*args2)

    @classmethod
    def process_args(cls, *args: Self | ChainMap | dict[str, Any] | Path) -> list[dict[str, Any]]:
        """
        Processes a mixed list of Config like inputs to a list of dictionaries.
        * Paths or str filenames are opened and loaded from disk.
        * Config or ChainMap inputs are split into their internal maps (preserving order)
        :param args: zero or more Config, ChainMap, dict[str, Any], Path
        :return: an ordered list of dict objects
        """
        pending: list[Any] = list(args)
        out: list[dict[str, Any]] = []
        while len(pending) > 0:
            candidate = pending.pop(0)

            # for ChainMap/Config inputs, add the individual maps
            if isinstance(candidate, ChainMap):
                maps = candidate.maps.copy()  # dont consume the source!
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
        """
        Converts a string into a dict. Content type is determined using a few heuristics.
        * convert from json if a line starting with "{" is found
        * convert from yaml if a line starting with "---" is found  TODO
        * convert from ini/configparser if a line starting with "[" is found
          * note first level in dict will be sections, not items
        * convert from env/bash name=value  otherwise
        :param text:
        :return: ict[str, Any]
        """
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
    def strip_comments(cls, text: str, markers: Tuple[str] = None) -> str:
        """
        Strips line comments starting with markers
        :param markers: tuple of line markers, defaults to ("#", ";", "//")
        :param text: input text
        :return: output text with line comments removed
        """
        if markers is None:
            markers = ("#", ";", "//")
        lines = text.split("\n")
        new_lines = [line for line in lines if not line.strip(" \t").startswith(markers)]
        return "\n".join(new_lines)

    def get_item(self, *item_names: str, default=None, allow_none=False,
                 secrets: bool = False, jinja=True) -> Any:
        """
        get an argument from self.merged_args
        :param item_names: one or more alternate names, first found used
        :param default: if none of the names are found return this value
        :param allow_none: set True to suppress KeyError if returning None
        :param jinja: enable jinja processing on item read from config
        :param secrets: enable secrets in config chaining
        :return: first item found or None if allow_none is set

        This getter is designed to support gradual switchover from legacy names to newer names.

        As a special case, if an Exception type is placed in the chain of adaption data, it will get raised.
        This is intended to facilitate marking required parameters in default config data.
        """
        val = default
        config = self
        if secrets and self._secret_config is not None:
            config = ChainMap(config, self._secret_config)
        for name in item_names:
            if name in config:
                val = config[name]
                break
        if val is None and not allow_none:
            raise KeyError(f"keys not found: {item_names}")
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
          * if data is a str, apply templates
          * if data is a list containing ONLY str, apply recursively for one level only
          * anything else returns unmodified
        :param data: data to be processed
        :param config: defaults to self, if caller has already appended secrets, that can be passed here
        :param secrets: append secrets before templates
        :return: result
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

    def set_item_if_missing(self, key: str, val: Any) -> None:
        """
        Convenience method for set_item which prevents overwriting existing item value
        :param key: name of item
        :param val: value of item
        :return: None
        """
        self.set_item(key, val, overwrite=False)

    def set_item(self, key: str, value: Any, overwrite=True, ) -> None:
        """
        Set one item in config
        :param key: item name
        :param value: item value
        :param overwrite: Allow overwriting existing item (defaults True)
        :return: None
        """
        if key not in self or overwrite:
            self[key] = value
