#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright by: P.J. Grochowski

from abc import ABC
from json import JSONEncoder
from typing import Any, Optional, OrderedDict, Type, Union

EncodingResult = Union[int, float, str, tuple, list, dict]


class IJsonEncoder(ABC):
    def encodeObject(self, obj: object) -> Optional[EncodingResult]:
        """Convert object to a JSON serializable data.
        Or return ``None`` instead.
        """


EncoderRegistryDict = OrderedDict[Type[IJsonEncoder], IJsonEncoder]


class _JsonEncoderRegistryProxy(JSONEncoder):

    def __init__(
        self,
        registry: EncoderRegistryDict,
        *args: Any,
        **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

        self.__registry: EncoderRegistryDict = registry

    def default(self, o: Any) -> Any:
        if isinstance(o, object):
            resultOpt = self.__tryEncodeObject(obj=o)
            if resultOpt is not None:
                return resultOpt

        return super().default(o)

    def __tryEncodeObject(self, obj: object) -> Optional[EncodingResult]:
        for encoder in self.__registry.values():
            resultOpt = encoder.encodeObject(obj=obj)
            if resultOpt is not None:
                return resultOpt

        return None
