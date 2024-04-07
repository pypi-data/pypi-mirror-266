from enum import Enum
import os
from pathlib import Path

from .keras.main import KerasModelWrapper
from .pytorch.main import PytorchModelWrapper
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

    KERAS = (
        KerasModelWrapper.framework_key,
        "Keras - Tensorflow",
        KerasModelWrapper,
    )
    PYTORCH = (
        PytorchModelWrapper.framework_key,
        "Pytorch",
        PytorchModelWrapper,
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

def get_all_files_and_size(search_dir_path=None, base_path=None):
    files_relative_paths = []
    files_data = []
    total_size = 0
    for dirpath, _, filenames in os.walk(search_dir_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                file_relative_path = str(Path(file_path).relative_to(base_path))
                file_size = os.path.getsize(file_path)
                files_relative_paths.append(file_relative_path)
                files_data.append(
                    {
                        "file_relative_path": file_relative_path,
                        "file_full_path": Path(file_path).resolve(),
                        "file_size": file_size,
                    }
                )
                total_size += file_size
    return total_size, files_relative_paths, files_data
