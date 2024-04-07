#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright by: P.J. Grochowski

try:
    import yaml
except ImportError:
    from tunit import __package__ as packageName
    raise ImportError(f"YAML support is an extra feature! Please install: '{packageName}[yaml]'")

from typing import List, Type, Union, cast

from yaml import Dumper, FullLoader, Loader, Node, ScalarNode, UnsafeLoader, YAMLObject

from tunit.core import TimeUnit, TimeUnitTypeError

_DEFAULT_STRING_TAG = 'tag:yaml.org,2002:str'


class _TUnitYaml(YAMLObject):

    @classmethod
    def from_yaml(cls, loader: Union[Loader, FullLoader, UnsafeLoader], node: Node) -> Union[bool, int, float, str, None]:
        node.value = cls._tryDeserialize(node.value)
        return loader.construct_scalar(cast(ScalarNode, node))

    @classmethod
    def to_yaml(cls, dumper: Dumper, data: TimeUnit) -> ScalarNode:
        return dumper.represent_str(data.serialize())

    @staticmethod
    def _tryDeserialize(valueStr: str) -> Union[TimeUnit, str]:
        for timeUnit in TimeUnit.__subclasses__():
            try:
                return timeUnit.deserialize(valueStr=valueStr)
            except TimeUnitTypeError:
                pass

        return valueStr


class _TUnitYamlConfig:

    _DUMPERS: List[Type[Dumper]] = [
        Dumper,
    ]
    _LOADERS: List[Type[Loader]] = [
        Loader,
    ]

    @classmethod
    def registerYamlHandler(cls) -> None:
        for dumper in cls._DUMPERS:
            cls._registerOnDumper(dumper=dumper)
        for loader in cls._LOADERS:
            cls._registerOnLoader(loader=loader)

    @classmethod
    def unregisterYamlHandler(cls) -> None:
        for dumper in cls._DUMPERS:
            cls._unregisterFromDumper(dumper=dumper)
        for loader in cls._LOADERS:
            cls._unregisterFromLoader(loader=loader)

    @staticmethod
    def _registerOnDumper(dumper: Type[Dumper]) -> None:
        for timeUnit in cast(List[Type[TimeUnit]], TimeUnit.__subclasses__()):
            dumper.add_representer(timeUnit, _TUnitYaml.to_yaml)

    @staticmethod
    def _registerOnLoader(loader: Type[Loader]) -> None:
        loader.add_constructor(_DEFAULT_STRING_TAG, _TUnitYaml.from_yaml)

    @staticmethod
    def _unregisterFromDumper(dumper: Type[Dumper]) -> None:
        for timeUnit in cast(List[Type[TimeUnit]], TimeUnit.__subclasses__()):
            dumper.yaml_representers.pop(timeUnit, None)

    @staticmethod
    def _unregisterFromLoader(loader: Type[Loader]) -> None:
        loader.yaml_constructors.pop(_DEFAULT_STRING_TAG, None)
