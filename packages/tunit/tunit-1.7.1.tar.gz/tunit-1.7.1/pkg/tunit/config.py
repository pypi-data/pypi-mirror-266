#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright by: P.J. Grochowski

from tunit.core import _TUnitSerializationConfig


class TUnitConfig(_TUnitSerializationConfig):

    @staticmethod
    def registerJsonHandler(enableRegistry: bool = True) -> None:
        from .markup.json import _TUnitJsonConfig
        _TUnitJsonConfig.registerJsonHandler(enableRegistry=enableRegistry)

    @staticmethod
    def unregisterJsonHandler(disableRegistry: bool = False) -> None:
        from .markup.json import _TUnitJsonConfig
        _TUnitJsonConfig.unregisterJsonHandler(disableRegistry=disableRegistry)

    @staticmethod
    def registerYamlHandler() -> None:
        from .markup.yaml import _TUnitYamlConfig
        _TUnitYamlConfig.registerYamlHandler()

    @staticmethod
    def unregisterYamlHandler() -> None:
        from .markup.yaml import _TUnitYamlConfig
        _TUnitYamlConfig.unregisterYamlHandler()
