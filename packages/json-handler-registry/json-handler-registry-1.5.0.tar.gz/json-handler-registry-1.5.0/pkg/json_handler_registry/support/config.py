#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright by: P.J. Grochowski

from abc import ABC, abstractmethod


class PackageSupportConfig(ABC):
    @staticmethod
    @abstractmethod
    def isEnabled() -> bool: ...
    @staticmethod
    @abstractmethod
    def enable() -> None: ...
    @staticmethod
    @abstractmethod
    def disable() -> None: ...
