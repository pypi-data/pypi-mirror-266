#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright by: P.J. Grochowski

try:
    import json_handler_registry
except ImportError:
    from tunit import __package__ as packageName
    raise ImportError(f"JSON support is an extra feature! Please install: '{packageName}[json]'")

from typing import Optional

from json_handler_registry.decoder import IJsonDecoder
from json_handler_registry.encoder import EncodingResult, IJsonEncoder
from json_handler_registry.registry import JsonHandlerRegistry

from tunit.core import TimeUnit, TimeUnitTypeError


class _TUnitJsonEncoder(IJsonEncoder):

    def encodeObject(self, obj: object) -> Optional[EncodingResult]:
        return obj.serialize() if isinstance(obj, TimeUnit)\
            else None


class _TUnitJsonDecoder(IJsonDecoder):

    def decodeDict(self, dct: dict) -> Optional[object]:
        return None

    def decodeStr(self, valueStr: str) -> Optional[object]:
        for timeUnit in TimeUnit.__subclasses__():
            try:
                return timeUnit.deserialize(valueStr=valueStr)
            except TimeUnitTypeError:
                pass

        return None


class _TUnitJsonConfig:

    @staticmethod
    def registerJsonHandler(enableRegistry: bool = True) -> None:
        if enableRegistry:
            JsonHandlerRegistry.enable()
        JsonHandlerRegistry.registerEncoder(_TUnitJsonEncoder)
        JsonHandlerRegistry.registerDecoder(_TUnitJsonDecoder)

    @staticmethod
    def unregisterJsonHandler(disableRegistry: bool = False) -> None:
        if disableRegistry:
            JsonHandlerRegistry.disable()
        JsonHandlerRegistry.unregisterEncoder(_TUnitJsonEncoder)
        JsonHandlerRegistry.unregisterDecoder(_TUnitJsonDecoder)
