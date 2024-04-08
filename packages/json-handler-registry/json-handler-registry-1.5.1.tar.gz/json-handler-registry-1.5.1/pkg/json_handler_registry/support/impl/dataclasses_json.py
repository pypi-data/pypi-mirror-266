#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright by: P.J. Grochowski

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, cast
from uuid import UUID

from json_handler_registry.encoder import EncodingResult, IJsonEncoder
from json_handler_registry.registry import JsonHandlerRegistry
from json_handler_registry.support.config import PackageSupportConfig


class DataClassJsonEncoder(IJsonEncoder):
    def encodeObject(self, obj: object) -> Optional[EncodingResult]:
        if isinstance(obj, datetime):
            return obj.timestamp()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, Enum):
            return cast(EncodingResult, obj.value)
        if isinstance(obj, Decimal):
            return str(obj)
        return None


class DataClassJsonSupport(PackageSupportConfig):

    @staticmethod
    def isEnabled() -> bool:
        return DataClassJsonEncoder in JsonHandlerRegistry.getRegisteredEncoderTypes()

    @staticmethod
    def enable() -> None:
        JsonHandlerRegistry.registerEncoder(DataClassJsonEncoder)

    @staticmethod
    def disable() -> None:
        JsonHandlerRegistry.unregisterEncoder(DataClassJsonEncoder)
