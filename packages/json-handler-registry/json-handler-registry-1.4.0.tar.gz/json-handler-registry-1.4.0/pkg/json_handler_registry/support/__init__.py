#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright by: P.J. Grochowski

from typing import Dict, List, Type

from json_handler_registry.support.impl.common import PackageSupportConfig
from json_handler_registry.support.impl.dataclasses_json import DataClassJsonSupport


class PackageSupportException(Exception):
    pass


class PackageSupportManager:

    _PACKAGE_SUPPORT_CONFIGS: Dict[str, Type[PackageSupportConfig]] = {
        'dataclasses-json': DataClassJsonSupport,
    }

    @classmethod
    def getSupportedPackages(cls) -> List[str]:
        return list(cls._PACKAGE_SUPPORT_CONFIGS.keys())

    @classmethod
    def getPackageSupportConfig(cls, package: str) -> Type[PackageSupportConfig]:
        packageSupportConfigOpt = cls._PACKAGE_SUPPORT_CONFIGS.get(package, None)
        if packageSupportConfigOpt is None:
            raise PackageSupportException(f"There is no builtin support for package: '{package}'")

        return packageSupportConfigOpt
