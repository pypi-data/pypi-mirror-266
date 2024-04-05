from enum import Enum

from .keras.main import KerasModelWrapper
from .exceptions import (
    ModelFrameworkNoModelException,
    ModelFrameworkNotSupportedException,
    ModelFrameworkNoKeyException,
)


class Framework(Enum):

    def __new__(cls, value, verbose_name, wrapper_class):
        obj = object.__new__(cls)

        obj._value_ = value
        obj.verbose_name = verbose_name
        obj.wrapper_class = wrapper_class

        return obj

    # KERAS = (
    #     [
    #         "keras.src.engine.sequential",
    #         "keras.src.engine.functional",
    #         "keras.src.models.sequential",
    #         "keras.src.models.functional",
    #         "tensorflow.python.keras.engine.sequential",
    #         "tensorflow.python.keras.engine.functional",
    #         "keras.engine.sequential",
    #         "keras.engine.functional",
    #     ],
    #     "Keras - Tensorflow",
    #     KerasModelWrapper,
    # )

    # @classmethod
    # def match_model(cls, model):
    #     for member in cls:
    #         if model.__class__.__module__ in member.value:
    #             return member
    #     return None

    KERAS = (
        "keras",
        "Keras - Tensorflow",
        KerasModelWrapper,
    )

    @classmethod
    def match_model(cls, model):
        for member in cls:
            if member.wrapper_class.check_model_instance(model_instance=model):
                return member
        return None

    @classmethod
    def match_key(cls, key):
        for member in cls:
            if key == member.wrapper_class.framework_key:
                return member
        return None


def get_framework_from_model(*, model=None):

    if model == None:
        raise ModelFrameworkNoModelException()

    framework = Framework.match_model(model)

    if framework == None:
        raise ModelFrameworkNotSupportedException()

    return framework


def get_framework_from_key(*, key=None):

    if key == None:
        raise ModelFrameworkNoKeyException()

    framework = Framework.match_key(key)

    if framework == None:
        raise ModelFrameworkNotSupportedException()

    return framework
