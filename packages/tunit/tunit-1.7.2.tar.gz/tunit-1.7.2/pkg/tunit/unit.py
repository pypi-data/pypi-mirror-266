#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright by: P.J. Grochowski

from typing import Callable, cast

from tunit.core import ITimeUnit, TimeUnit


class Nanoseconds(TimeUnit):
    unitInfo = cast(Callable, staticmethod(lambda: ITimeUnit.UnitInfo(name='Nanoseconds', symbol='ns', conversionFactor=1)))


class Microseconds(TimeUnit):
    unitInfo = cast(Callable, staticmethod(lambda: ITimeUnit.UnitInfo(name='Microseconds', symbol='us', conversionFactor=(1_000 * Nanoseconds.conversionFactor))))


class Milliseconds(TimeUnit):
    unitInfo = cast(Callable, staticmethod(lambda: ITimeUnit.UnitInfo(name='Milliseconds', symbol='ms', conversionFactor=(1_000 * Microseconds.conversionFactor))))


class Seconds(TimeUnit):
    unitInfo = cast(Callable, staticmethod(lambda: ITimeUnit.UnitInfo(name='Seconds', symbol='s', conversionFactor=(1_000 * Milliseconds.conversionFactor))))


class Minutes(TimeUnit):
    unitInfo = cast(Callable, staticmethod(lambda: ITimeUnit.UnitInfo(name='Minutes', symbol='m', conversionFactor=(60 * Seconds.conversionFactor))))


class Hours(TimeUnit):
    unitInfo = cast(Callable, staticmethod(lambda: ITimeUnit.UnitInfo(name='Hours', symbol='h', conversionFactor=(60 * Minutes.conversionFactor))))


class Days(TimeUnit):
    unitInfo = cast(Callable, staticmethod(lambda: ITimeUnit.UnitInfo(name='Days', symbol='d', conversionFactor=(24 * Hours.conversionFactor))))


class Weeks(TimeUnit):
    unitInfo = cast(Callable, staticmethod(lambda: ITimeUnit.UnitInfo(name='Weeks', symbol='w', conversionFactor=(7 * Days.conversionFactor))))
