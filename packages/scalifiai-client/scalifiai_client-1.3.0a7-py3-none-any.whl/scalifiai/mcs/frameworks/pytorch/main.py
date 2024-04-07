import tempfile
from pathlib import Path

from scalifiai.mcs.frameworks.base import ModelWrapper
from scalifiai.mcs.frameworks.constants import MODEL_SAVE_FOLDER_NAME
from scalifiai.mcs.model.exceptions import (
    raise_custom_exception as raise_custom_exception__model,
)
from .exceptions import PytorchInvalidDataTypeModelException, PytorchInvalidModelException
from .constants import FRAMEWORK_KEY


# TODO[VIMPORTANT] SEGREGATE `ModelWrapper` class into deep learning and machine learning wrapper class and model following function to appropriate model class: [infer_data_type, infer_signature, serialize_signature]
class PytorchModelWrapper(ModelWrapper):

    framework_key = FRAMEWORK_KEY

    # TODO[VIMPORTANT] CHECK AND MAKE FUNCTIONS PRIVATE IF THEY SHOULD NOT BE ACCESSIBLE DIRECTLY

    def __init__(self, *, model=None) -> None:
        # TODO[VIMPORTANT] MAKE A FUNCTION FOR IMPORTING DEPENDENT LIBRARIES FOR EACH FRAMEWORK IN THEIR CLASS AND USE THAT FUNCTION OR ELSE RAISE ERROR WITH PROPER INSTALLATION MENTIONED VIA OUR LIBRARY ONLY VIA OTHER DEPENDENCIEZS IN project.toml FILE

        super().__init__(model=model)
        self.DATA_TYPE_CONVERSION = {} # TODO[VIMPORTANT] ONCE SIGNATURE CREATION IS COMPLETED, ADD ALL APPROPRIATE DATA TYPES. TAKE REFERENCE FROM KERAS DIR.

    @classmethod
    def check_model_instance(cls, *, model_instance):

        try:
            import torch
        except Exception:
            print("Skipping Pytorch check as Pytorch installation is not detected")
            return False
        
        return isinstance(model_instance, torch.nn.Module)

    def infer_data_type(self, *, dtype):

        data_type = self.DATA_TYPE_CONVERSION.get(dtype, None)

        if data_type == None:
            raise PytorchInvalidDataTypeModelException(
                extra_info=f"Invalid data type: {dtype} || Type(dtype): {type(dtype)}"
            )

        return data_type

    def infer_signature(self):
        # TODO[VIMPORTANT] COMPLETE SIGNATURE CREATION AND ADD ALL APPROPRIATE DATA TYPES. TAKE REFERENCE FROM KERAS DIR.

        inputs = None
        # if self.model.inputs != None:
        #     inputs = [
        #         TensorSpec(
        #             dtype=self.infer_data_type(dtype=input.dtype),
        #             shape=input.shape.as_list(),
        #             name=input.name,
        #         )
        #         for input in self.model.inputs
        #     ]

        outputs = None
        # if self.model.outputs != None:
        #     outputs = [
        #         TensorSpec(
        #             dtype=self.infer_data_type(dtype=output.dtype),
        #             shape=output.shape.as_list(),
        #             name=output.name,
        #         )
        #         for output in self.model.outputs
        #     ]

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

    def get_total_params(self):

        return {
            "trainable": {
                "verbose": "Trainable",
                "value": int(sum(p.numel() for p in self.model.parameters() if p.requires_grad)),
            },
            "non_trainable": {
                "verbose": "Non-trainable",
                "value": int(sum(p.numel() for p in self.model.parameters() if not p.requires_grad)),
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

        import torch
        from scalifiai.mcs.model_version.main import ModelVersion
        from scalifiai.mcs.frameworks.utils import get_all_files_and_size

        with tempfile.TemporaryDirectory(dir=base_dir_path) as temp_dir:

            temp_dir_path = Path(temp_dir)
            model_save_file_path = temp_dir_path / Path(MODEL_SAVE_FOLDER_NAME)

            if not model_save_file_path.exists():
                model_save_file_path.mkdir()

            try:
                torch.jit.script(self.model).save(f"{model_save_file_path.absolute()}/model.pt")
            except Exception as ex:
                print(f"type(ex): {type(ex)}")
                print(f"ex: {ex}")
                try:
                    raise PytorchInvalidModelException(extra_info=str(ex))
                except Exception as ex:
                    raise PytorchInvalidModelException()

            self.signature = self.infer_signature()

            total_files_size, files_relative_paths, files_data = (
                get_all_files_and_size(
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

    # TODO[VIMPORTANT] COMPLETE FUNCTION AFTER TESTING
    @classmethod
    def load_local_model(cls, *, model_path=None):
        # TODO[VIMPORTANT] MAKE A FUNCTION FOR IMPORTING DEPENDENT LIBRARIES FOR EACH FRAMEWORK IN THEIR CLASS AND USE THAT FUNCTION OR ELSE RAISE ERROR WITH PROPER INSTALLATION MENTIONED VIA OUR LIBRARY ONLY VIA OTHER DEPENDENCIEZS IN project.toml FILE
        import torch

        model_file = next((item for item in model_path.iterdir() if item.is_file()), None)

        if model_file == None:
            raise PytorchInvalidModelException(extra_info="No valid model file found")

        print(f"type(model_file.absolute()): {type(model_file.absolute())}")
        print(f"model_file.absolute(): {model_file.absolute()}")

        return torch.jit.load(model_file.absolute())

