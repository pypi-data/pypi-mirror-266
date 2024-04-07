#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright by: P.J. Grochowski

import json
from collections import OrderedDict
from functools import partial
from typing import Any, List, Type, Union, cast

from json_handler_registry import __logger as logger
from json_handler_registry.decoder import DecoderRegistryDict, IJsonDecoder, _JsonDecoderRegistryProxy
from json_handler_registry.encoder import EncoderRegistryDict, IJsonEncoder, _JsonEncoderRegistryProxy
from json_handler_registry.support.manager import PackageSupportManager

JsonEncoder = Union[Type[IJsonEncoder], IJsonEncoder]
JsonDecoder = Union[Type[IJsonDecoder], IJsonDecoder]


class _RegistryGuardPartial(partial):

    __REGISTRY_KEYWORD = 'cls'

    def __call__(__self, *args: Any, **kwargs: Any) -> Any:
        __self.__adjustKwargs(kwargs=kwargs)

        return super().__call__(*args, **kwargs)

    def __adjustKwargs(__self, kwargs: dict) -> None:
        if __self.__REGISTRY_KEYWORD in kwargs:
            offendingObject = kwargs[__self.__REGISTRY_KEYWORD]
            kwargs.update(__self.keywords)

            logger.warning(f"Detected attempt to replace registry! offendingObject='{offendingObject}'")


class JsonHandlerRegistry:

    _ENCODER_REGISTRY: EncoderRegistryDict = OrderedDict()
    _DECODER_REGISTRY: DecoderRegistryDict = OrderedDict()

    autoEnable: bool = True
    autoDisable: bool = True

    packageSupportManager: Type[PackageSupportManager] = PackageSupportManager

    @classmethod
    def isEmpty(cls) -> bool:
        return (
            len(cls._ENCODER_REGISTRY) <= 0 and
            len(cls._DECODER_REGISTRY) <= 0
        )

    @staticmethod
    def isEnabled() -> bool:
        return (
            isinstance(json.dumps, partial) and
            isinstance(json.loads, partial)
        )

    @classmethod
    def enable(cls) -> None:
        if cls.isEnabled():
            return

        json.dumps = _RegistryGuardPartial(
            json.dumps,
            cls=partial(
                _JsonEncoderRegistryProxy,
                registry=cls._ENCODER_REGISTRY
            )
        )
        json.loads = _RegistryGuardPartial(
            json.loads,
            cls=partial(
                _JsonDecoderRegistryProxy,
                registry=cls._DECODER_REGISTRY
            )
        )

    @classmethod
    def disable(cls) -> None:
        if cls.isEnabled():
            json.dumps = cast(partial, json.dumps).func
            json.loads = cast(partial, json.loads).func

    @classmethod
    def getRegisteredEncoderTypes(cls) -> List[Type[IJsonEncoder]]:
        return list(cls._ENCODER_REGISTRY.keys())

    @classmethod
    def getRegisteredDecoderTypes(cls) -> List[Type[IJsonDecoder]]:
        return list(cls._DECODER_REGISTRY.keys())

    @classmethod
    def registerEncoder(cls, jsonEncoder: JsonEncoder) -> None:
        encoderInstance = cls._getEncoderInstance(jsonEncoder=jsonEncoder)
        cls._ENCODER_REGISTRY[type(encoderInstance)] = encoderInstance
        cls._autoToggle()

    @classmethod
    def unregisterEncoder(cls, jsonEncoder: JsonEncoder) -> None:
        encoderType = cls._getEncoderType(jsonEncoder=jsonEncoder)
        cls._ENCODER_REGISTRY.pop(encoderType, None)
        cls._autoToggle()

    @classmethod
    def registerDecoder(cls, jsonDecoder: JsonDecoder) -> None:
        decoderInstance = cls._getDecoderInstance(jsonDecoder=jsonDecoder)
        cls._DECODER_REGISTRY[type(decoderInstance)] = decoderInstance
        cls._autoToggle()

    @classmethod
    def unregisterDecoder(cls, jsonDecoder: JsonDecoder) -> None:
        decoderType = cls._getDecoderType(jsonDecoder=jsonDecoder)
        cls._DECODER_REGISTRY.pop(decoderType, None)
        cls._autoToggle()

    @classmethod
    def _getEncoderType(cls, jsonEncoder: JsonEncoder) -> Type[IJsonEncoder]:
        return type(jsonEncoder) if isinstance(jsonEncoder, IJsonEncoder) else jsonEncoder

    @classmethod
    def _getEncoderInstance(cls, jsonEncoder: JsonEncoder) -> IJsonEncoder:
        return jsonEncoder if isinstance(jsonEncoder, IJsonEncoder) else jsonEncoder()

    @classmethod
    def _getDecoderType(cls, jsonDecoder: JsonDecoder) -> Type[IJsonDecoder]:
        return type(jsonDecoder) if isinstance(jsonDecoder, IJsonDecoder) else jsonDecoder

    @classmethod
    def _getDecoderInstance(cls, jsonDecoder: JsonDecoder) -> IJsonDecoder:
        return jsonDecoder if isinstance(jsonDecoder, IJsonDecoder) else jsonDecoder()

    @classmethod
    def _autoToggle(cls) -> None:
        isEmpty = cls.isEmpty()
        if cls.autoEnable and not isEmpty:
            cls.enable()
        elif cls.autoDisable and isEmpty:
            cls.disable()
