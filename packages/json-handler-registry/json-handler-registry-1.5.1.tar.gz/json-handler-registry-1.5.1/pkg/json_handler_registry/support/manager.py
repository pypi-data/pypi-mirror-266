#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright by: P.J. Grochowski

from typing import List, Type

from json_handler_registry.support.config import PackageSupportConfig


class PackageSupportException(Exception):
    pass


class PackageSupportManager:

    @classmethod
    def getSupportedPackages(cls) -> List[str]:
        from .impl import PACKAGE_SUPPORT_CONFIGS
        return list(PACKAGE_SUPPORT_CONFIGS.keys())

    @classmethod
    def getPackageSupportConfig(cls, package: str) -> Type[PackageSupportConfig]:
        from .impl import PACKAGE_SUPPORT_CONFIGS
        packageSupportConfigOpt = PACKAGE_SUPPORT_CONFIGS.get(package, None)
        if packageSupportConfigOpt is None:
            raise PackageSupportException(f"There is no builtin support for package: '{package}'")

        return packageSupportConfigOpt
