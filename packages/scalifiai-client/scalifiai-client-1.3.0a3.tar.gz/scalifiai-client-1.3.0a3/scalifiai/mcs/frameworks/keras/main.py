import tempfile
from pathlib import Path
import os
import requests

from scalifiai.mcs.frameworks.base import ModelWrapper
from scalifiai.mcs.frameworks.schema import TensorSpec, DataType
from scalifiai.mcs.model.exceptions import (
    raise_custom_exception as raise_custom_exception__model,
)
from scalifiai.mcs.metadata.exceptions import (
    raise_custom_exception as raise_custom_exception__metadata,
)
from .exceptions import KerasInvalidDataTypeModelException, KerasInvalidModelException
from .constants import MODEL_SAVE_FOLDER_NAME, FRAMEWORK_KEY


# TODO[VIMPORTANT] SEGREGATE `ModelWrapper` class into deep learning and machine learning wrapper class and model following function to appropriate model class: [infer_data_type, infer_signature, serialize_signature]
class KerasModelWrapper(ModelWrapper):

    framework_key = FRAMEWORK_KEY

    # TODO[VIMPORTANT] CHECK AND MAKE FUNCTIONS PRIVATE IF THEY SHOULD NOT BE ACCESSIBLE DIRECTLY

    def __init__(self, *, model=None) -> None:
        # TODO[VIMPORTANT] MAKE A FUNCTION FOR IMPORTING DEPENDENT LIBRARIES FOR EACH FRAMEWORK IN THEIR CLASS AND USE THAT FUNCTION OR ELSE RAISE ERROR WITH PROPER INSTALLATION MENTIONED VIA OUR LIBRARY ONLY VIA OTHER DEPENDENCIEZS IN project.toml FILE
        import tensorflow as tf

        super().__init__(model=model)
        self.DATA_TYPE_CONVERSION = {
            tf.int8: DataType.INT8,
            tf.int16: DataType.INT16,
            tf.int32: DataType.INT32,
            tf.int64: DataType.INT64,
            tf.uint8: DataType.UINT8,
            tf.uint16: DataType.UINT16,
            tf.uint32: DataType.UINT32,
            tf.uint64: DataType.UINT64,
            tf.qint8: DataType.QINT8,
            tf.qint16: DataType.QINT16,
            tf.qint32: DataType.QINT32,
            tf.quint8: DataType.QUINT8,
            tf.quint16: DataType.QUINT16,
            tf.bfloat16: DataType.FLOAT16,
            tf.half: DataType.FLOAT16,
            tf.float32: DataType.FLOAT32,
            tf.float64: DataType.FLOAT64,
            tf.double: DataType.FLOAT64,
            tf.complex64: DataType.COMPLEX64,
            tf.complex128: DataType.COMPLEX128,
            tf.string: DataType.STRING,
            tf.bool: DataType.BOOL,
            tf.variant: DataType.VARIANT,
        }
    
    @classmethod
    def check_model_instance(cls, *, model_instance):

        try:
            import tensorflow as tf
        except Exception:
            print("Skipping Tensorflow check as Tensorflow installation is not detected")
            return False
        
        return isinstance(model_instance, tf.keras.Model)

    def infer_data_type(self, *, dtype):

        data_type = self.DATA_TYPE_CONVERSION.get(dtype, None)

        if data_type == None:
            raise KerasInvalidDataTypeModelException(
                extra_info=f"Invalid data type: {dtype} || Type(dtype): {type(dtype)}"
            )

        return data_type

    def infer_signature(self):

        inputs = None
        if self.model.inputs != None:
            inputs = [
                TensorSpec(
                    dtype=self.infer_data_type(dtype=input.dtype),
                    shape=input.shape.as_list(),
                    name=input.name,
                )
                for input in self.model.inputs
            ]

        outputs = None
        if self.model.outputs != None:
            outputs = [
                TensorSpec(
                    dtype=self.infer_data_type(dtype=output.dtype),
                    shape=output.shape.as_list(),
                    name=output.name,
                )
                for output in self.model.outputs
            ]

        return {"inputs": inputs, "outputs": outputs}

    def serialize_signature(self):

        signature = {}

        for key in self.signature.keys():
            if signature.get(key, None) == None:
                signature[key] = None
            if self.signature[key] != None:
                signature[key] = []
                for spec in self.signature[key]:
                    signature[key].append(spec.to_dict())

        return signature

    @classmethod
    def get_all_files_and_size(cls, *, search_dir_path=None, base_path=None):
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

    def get_total_params(self):
        # TODO[VIMPORTANT] MAKE A FUNCTION FOR IMPORTING DEPENDENT LIBRARIES FOR EACH FRAMEWORK IN THEIR CLASS AND USE THAT FUNCTION OR ELSE RAISE ERROR WITH PROPER INSTALLATION MENTIONED VIA OUR LIBRARY ONLY VIA OTHER DEPENDENCIEZS IN project.toml FILE
        import tensorflow as tf

        return {
            "trainable": {
                "verbose": "Trainable",
                "value": int(
                    sum([tf.size(w).numpy() for w in self.model.trainable_weights])
                ),
            },
            "non_trainable": {
                "verbose": "Non-trainable",
                "value": int(
                    sum([tf.size(w).numpy() for w in self.model.non_trainable_weights])
                ),
            },
        }

    def save_and_upload(
        self,
        *,
        base_dir_path=None,
        variation=None,
        request_manager=None,
        upload_url=None,
        parent_action=None,
        model_instance=None,
    ):

        from scalifiai.mcs.model_version.main import ModelVersion

        with tempfile.TemporaryDirectory(dir=base_dir_path) as temp_dir:

            temp_dir_path = Path(temp_dir)
            model_save_file_path = temp_dir_path / Path(MODEL_SAVE_FOLDER_NAME)

            try:
                self.model.save(model_save_file_path, save_format="tf")
            except Exception as ex:
                print(f"type(ex): {type(ex)}")
                print(f"ex: {ex}")
                try:
                    raise KerasInvalidModelException(extra_info=str(ex))
                except Exception as ex:
                    raise KerasInvalidModelException()

            self.signature = self.infer_signature()

            total_files_size, files_relative_paths, files_data = (
                self.get_all_files_and_size(
                    search_dir_path=model_save_file_path, base_path=model_save_file_path
                )
            )

            create_version_request_body = {
                "framework": self.framework_key,
                "variation_name": variation,
                "config": {
                    "total_files_size": total_files_size,
                    "all_file_keys": files_relative_paths,
                    "signature": self.serialize_signature(),
                    "total_params": self.get_total_params(),
                },
            }

            # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
            resp = request_manager.send_request(
                method="POST",
                url=upload_url,
                query_params={"query_type": "SELF_CREATED"},
                data=create_version_request_body,
            )

            if resp.status_code == 201:
                resp_data = resp.json()["data"]
            else:
                raise_custom_exception__model(response=resp, action=parent_action)

            model_version_instance = None

            try:
                model_version_instance = ModelVersion(
                    resp_data["id"], api_key=request_manager.credential_manager.api_key
                )

                for file in files_data:

                    model_version_instance.add_metadata_storage(
                        data_type="file",
                        key=file["file_relative_path"],
                        file_path=file["file_full_path"],
                        _model_core_file=True,
                    )

            except Exception as ex:
                model_instance.complete_model_version_creation(
                    version_id=resp_data["id"]
                )

                raise ex

            model_instance.complete_model_version_creation(
                version_id=model_version_instance.instance_data["id"]
            )
            model_version_instance.refresh_instance()

            return model_version_instance

    @classmethod
    def load_local_model(cls, *, model_path=None):
        # TODO[VIMPORTANT] MAKE A FUNCTION FOR IMPORTING DEPENDENT LIBRARIES FOR EACH FRAMEWORK IN THEIR CLASS AND USE THAT FUNCTION OR ELSE RAISE ERROR WITH PROPER INSTALLATION MENTIONED VIA OUR LIBRARY ONLY VIA OTHER DEPENDENCIEZS IN project.toml FILE
        import tensorflow as tf

        return tf.keras.models.load_model(model_path)
