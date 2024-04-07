#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright by: P.J. Grochowski

from typing import Dict, Type

from json_handler_registry.support.config import PackageSupportConfig
from json_handler_registry.support.impl.dataclasses_json import DataClassJsonSupport

PACKAGE_SUPPORT_CONFIGS: Dict[str, Type[PackageSupportConfig]] = {
    'dataclasses-json': DataClassJsonSupport
}
