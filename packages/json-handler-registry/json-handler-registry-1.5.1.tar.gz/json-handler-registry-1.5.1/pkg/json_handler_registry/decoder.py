#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright by: P.J. Grochowski

from abc import ABC
from collections import deque
from json import JSONDecoder
from typing import Any, Callable, Deque, Optional, OrderedDict, Type, Union

_Node = Union[dict, list]


class IJsonDecoder(ABC):
    def decodeDict(self, dct: dict) -> Optional[object]:
        """Convert dictionary to your type instance.
        Or return ``None`` instead.
        """
    def decodeStr(self, valueStr: str) -> Optional[object]:
        """Convert string value to your type instance.
        Or return ``None`` instead.
        """


DecoderRegistryDict = OrderedDict[Type[IJsonDecoder], IJsonDecoder]


class _JsonDecoderRegistryProxy(JSONDecoder):

    def __init__(
        self,
        registry: DecoderRegistryDict,
        *args: Any,
        **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs, object_hook=self.__tryDecodeDict)

        self.__registry: DecoderRegistryDict = registry

    def decode(self, s: str, _w: Callable[..., Any] = lambda *args, **kwargs: None) -> Any:
        decodedObj = super().decode(s)
        if isinstance(decodedObj, str):
            return self.__tryDecodeStr(valueStr=decodedObj)

        if isinstance(decodedObj, (list, dict)):
            self.__deepUpdate(rootNode=decodedObj)

        return decodedObj

    def __tryDecodeDict(self, dct: dict) -> Union[object, dict]:
        for decoder in self.__registry.values():
            resultOpt = decoder.decodeDict(dct=dct)
            if resultOpt is not None:
                return resultOpt

        return dct

    def __tryDecodeStr(self, valueStr: str) -> Union[object, str]:
        for decoder in self.__registry.values():
            resultOpt = decoder.decodeStr(valueStr=valueStr)
            if resultOpt is not None:
                return resultOpt

        return valueStr

    def __deepUpdate(self, rootNode: _Node) -> None:
        nodesToWalk: Deque[_Node] = deque([rootNode])
        while len(nodesToWalk) > 0:
            node = nodesToWalk.popleft()
            nodeIterator = node.items() if isinstance(node, dict) else enumerate(node)
            for key, value in nodeIterator:
                if isinstance(value, (list, dict)):
                    nodesToWalk.append(value)
                    continue

                if not isinstance(value, str):
                    continue

                node[key] = self.__tryDecodeStr(valueStr=value)
