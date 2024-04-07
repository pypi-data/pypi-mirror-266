import os
from pydantic import ValidationError
from IPython.display import HTML
import requests
import pandas as pd
from datetime import datetime
import humanize

from scalifiai.base import BaseSubModule, Table
from scalifiai.mcs.main import MCS, MCSSubModuleTagsProxyDict
from scalifiai.mcs.frameworks.utils import get_framework_from_model
from scalifiai.mcs.metadata.main import Metadata, MetadataProxyDict
from scalifiai.mcs.metadata.schemas import CreateMetadataSimple, CreateMetadataStorage
from scalifiai.mcs.metadata.constants import OPERATION_ADDITION_AUTO_UPDATE_ENV_KEY
from scalifiai.mcs.metadata.exceptions import (
    raise_custom_exception as raise_custom_exception__metadata,
)
from scalifiai.mcs.model_version.main import ModelVersion
from .constants import (
    URL_SLUG,
    ADD_MODEL_VERSION_URL_SLUG,
    ADD_METADATA_URL_SLUG,
    LIST_METADATA_URL_SLUG,
    LIST_DISTINCT_MODEL_VERSIONS_URL_SLUG,
    LIST_MODEL_VARIATIONS_URL_SLUG,
    COMPLETE_METADATA_UPLOAD_URL_SLUG,
    UPDATE_METADATA_URL_SLUG,
    DELETE_METADATA_URL_SLUG,
    COMPLETE_MODEL_VERSION_CREATION_URL_SLUG,
    ATTACH_TAGS_URL_SLUG,
    LIST_TAGS_URL_SLUG,
    REMOVE_TAG_URL_SLUG,
    REMOVE_ALL_TAGS_URL_SLUG,
    DELETE_VERSION_URL_SLUG,
    GENERATE_METADATA_DOWNLOAD_URL_URL_SLUG,
    GENERATE_METADATA_PREVIEW_URL_URL_SLUG,
)
from .exceptions import ModelInstanceDeletedException, raise_custom_exception
from .schemas import (
    CreateModel,
    DeleteVersion,
    CreateModelTags,
    GenerateMetadataDownloadURL,
    GenerateMetadataPreviewURL,
)


class Model(BaseSubModule, MCS):
    # TODO[VIMPORTANT] CHECK AND MAKE FUNCTIONS PRIVATE IF THEY SHOULD NOT BE ACCESSIBLE DIRECTLY

    sub_module_url_slug = URL_SLUG
    is_deleted_error = ModelInstanceDeletedException

    add_model_version_url_slug = ADD_MODEL_VERSION_URL_SLUG
    add_metadata_url_slug = ADD_METADATA_URL_SLUG
    list_metadata_url_slug = LIST_METADATA_URL_SLUG
    list_distinct_model_versions_url_slug = LIST_DISTINCT_MODEL_VERSIONS_URL_SLUG
    list_model_variations_url_slug = LIST_MODEL_VARIATIONS_URL_SLUG
    complete_metadata_upload_url_slug = COMPLETE_METADATA_UPLOAD_URL_SLUG
    update_metadata_url_slug = UPDATE_METADATA_URL_SLUG
    delete_metadata_url_slug = DELETE_METADATA_URL_SLUG
    complete_model_version_creation_url_slug = COMPLETE_MODEL_VERSION_CREATION_URL_SLUG
    attach_tags_url_slug = ATTACH_TAGS_URL_SLUG
    list_tags_url_slug = LIST_TAGS_URL_SLUG
    remove_tag_url_slug = REMOVE_TAG_URL_SLUG
    remove_all_tags_url_slug = REMOVE_ALL_TAGS_URL_SLUG
    delete_version_url_slug = DELETE_VERSION_URL_SLUG
    generate_metadata_download_url_url_slug = GENERATE_METADATA_DOWNLOAD_URL_URL_SLUG
    generate_metadata_preview_url_url_slug = GENERATE_METADATA_PREVIEW_URL_URL_SLUG

    verbose_column_mapping = {
        "id": "ID",
        "created_at": "Created at",
        "updated_at": "Updated at",
        "uuid": "UUID",
        "delete_marker": "Marked for deletion",
        "verbose_name": "Name",
        "description": "Description",
        "tags": "Tags",
        "total_tag_count": "Total tags",
        "extra_params_base": "Extra parameters",
        "user": "Owner ID",
    }

    # Keep in sync with model_version.main.ModelVersion class
    tags_verbose_column_mapping = {
        "id": "ID",
        "created_at": "Created at",
        "updated_at": "Updated at",
        "uuid": "UUID",
        "delete_marker": "Marked for deletion",
        "key": "Name",
        "value": "Value",
    }

    instance_data = None

    def __init__(self, model_identifier=None, *, api_key=None) -> None:
        super().__init__(api_key=api_key)

        self.model_identifier = model_identifier

        data = self.retrieve()

        self.instance_data = data

        # TODO[IMPORTANT] THINK OF CONVERTING THIS INTO A PROPERTY
        self.metadata = MetadataProxyDict(
            parent_instance=self,
            addition_auto_update=os.environ.get(
                OPERATION_ADDITION_AUTO_UPDATE_ENV_KEY, True
            ),
        )  # TODO[VIMPORTANT] ADD A __SETATTR__ CHECK TO NOT CHANGE `metadata` to SOMETHING ELSE, ALSO UPDATE A __GETATTR__ FUNCTION FOR `.metadata` TO LIST METADATA AND RETURN A TABLE

        # TODO[IMPORTANT] THINK OF CONVERTING THIS INTO A PROPERTY
        self.tags = MCSSubModuleTagsProxyDict(
            parent_instance=self
        )  # TODO[VIMPORTANT] ADD A __SETATTR__ CHECK TO NOT CHANGE `tags` to SOMETHING ELSE, ALSO UPDATE A __GETATTR__ FUNCTION FOR `.tags` TO LIST METADATA AND RETURN A TABLE

    def __repr__(self):
        self.validate()

        return f"Model(ID={self.instance_data['id']}, Name=`{self.instance_data['verbose_name']}`)"

    # TODO[VIMPORTANT] ADD THIS PROPERTY TO ALL SUB-MODULES
    @property
    def info(self):
        self.validate()

        html_content = "<table>"
        for key, value in self.instance_data.items():
            final_key = (
                self.verbose_column_mapping.get(key, None)
                if self.verbose_column_mapping.get(key, None) != None
                else None
            )
            if final_key == None:
                continue

            final_value = value

            # TODO[VIMPORTANT] GENERALIZE THIS SO THAT WE CAN APPLY ANY FUNCTION TO ANY FIELDS BY SPECIFYINGIT IN THE VERBOSE COLUMNS CONFIG, CAN ALSO USE FUNCTIONS OF TABLE IN base.py
            if key in ["created_at", "updated_at"]:
                final_value = pd.to_datetime(final_value)
                if (datetime.now(self.local_timezone) - final_value).days > 0:
                    final_value = humanize.naturaldate(final_value)
                else:
                    final_value = humanize.naturaltime(
                        final_value, when=datetime.now(self.local_timezone)
                    )

            html_content += f"<tr><th>{final_key}</th><td>{final_value}</td></tr>"
        html_content += "</table>"
        return HTML(html_content)

    # TODO[VIMPORTANT] ADD THIS PROPERTY TO ALL SUB-MODULES
    @property
    def raw_info(self):
        self.validate()

        return self.instance_data

    @property
    def variations(self):
        self.validate()

        return self.list_variations()

    @property
    def versions(self):
        self.validate()

        return self.list_versions()

    @classmethod
    def _list(cls, *, extra_query_params=None, api_key=None):

        # TODO[VIMPORTANT] ADD CHECK HERE FOR CORRECT TYPE OF `extra_query_params`, THINK OF DOING IT VIA PYDANTIC AND ALSO FOR ALL OTHER FUNCTIONS
        if extra_query_params == None:
            extra_query_params = {}

        url = cls.generate_url(generic_action=True)

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        extra_query_params.update({"query_type": "SELF_CREATED"})
        request_manager = cls.get_request_manager(api_key=api_key)
        resp = request_manager.send_request(
            method="GET", url=url, query_params=extra_query_params
        )

        if resp.status_code == 200:
            return resp.json()["data"]
        else:
            raise_custom_exception(
                response=resp, action="LIST"
            )  # TODO[VIMPORTANT] SEE IF ANY SPECIFIC CASES NEED TO BE HANDLED FOR THIS

    # TODO[VIMPORTANT] ADD OPTION TO PASS FILTERS WITH PROPER DYNAMIC CHECK VIA PYDANTIC
    @classmethod
    def list(cls, *, api_key=None, data=None, columns=None, verbose_columns=True):
        # TODO[VIMPORTANT] ADD CHECK FOR KWARGS TO THIS METHOD

        if data == None:
            data = cls._list(api_key=api_key)

        table_instance = Table(data=data["results"], local_timezone=cls.local_timezone)

        return table_instance.to_representation(
            default_columns=data["default_visible_columns"]["cli"],
            columns=columns,
            column_mapping=cls.verbose_column_mapping,
            verbose_columns=verbose_columns,
        )

    @classmethod
    def create_model(
        cls, *, api_key=None, name=None, description="", sub_task=None, language=None
    ):

        # raise TempException() # TODO[VIMPORTANT] DELETE AFTER TESTING

        try:
            model_obj = CreateModel(
                name=name, description=description, sub_task=sub_task, language=language
            )
        except ValidationError as ex:
            errors = [f"`{error['loc'][0]}`: {error['msg']}" for error in ex.errors()]
            error_message = "\n".join(errors)
            raise Exception(
                error_message
            )  # TODO[VIMPORTANT] REPLACE WITH A CUSTOM EXCEPTION with proper custom, easier to understand error messages based on type of error given by pydantic

        url = cls.generate_url(generic_action=True)

        request_manager = cls.get_request_manager(api_key=api_key)

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        resp = request_manager.send_request(
            method="POST", url=url, data=model_obj.model_dump()
        )

        if resp.status_code == 201:
            data = resp.json()["data"]
        else:
            raise_custom_exception(response=resp, action="CREATE")

        return cls(data["id"], api_key=api_key)

    def retrieve(self):
        self.validate()

        url = self.generate_url(
            generic_action=True,
            resource_specific=True,
            resource_id=self.model_identifier,
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        resp = self.request_manager.send_request(
            method="GET", url=url, query_params={"query_type": "SELF_CREATED"}
        )

        if resp.status_code == 200:
            return resp.json()["data"]
        else:
            raise_custom_exception(response=resp, action="RETRIEVE")

    def refresh_instance(self):
        self.validate()

        data = self.retrieve()

        self.instance_data = data

    def register_model_version(self, *, model=None, variation=None):
        self.validate()

        framework = get_framework_from_model(model=model)
        wrapped_model = framework.wrapper_class(model=model)

        url = self.generate_url(
            generic_action=False,
            action_slug=self.add_model_version_url_slug,
            resource_specific=True,
            resource_id=self.model_identifier,
        )

        return wrapped_model.save_and_upload(
            base_dir_path=self.base_dir_path,
            variation=variation,
            request_manager=self.request_manager,
            upload_url=url,
            parent_action=self.add_model_version_url_slug,
            model_instance=self,
        )

    def add_metadata_simple(self, *, data_type=None, key=None, value=None):
        self.validate()

        try:
            metadata_obj = CreateMetadataSimple(
                key=key, data_type=data_type, value={"value": value}
            )
        except ValidationError as ex:
            errors = [f"`{error['loc'][0]}`: {error['msg']}" for error in ex.errors()]
            error_message = "\n".join(errors)
            raise Exception(
                error_message
            )  # TODO[VIMPORTANT] REPLACE WITH A CUSTOM EXCEPTION with proper custom, easier to understand error messages based on type of error given by pydantic

        url = self.generate_url(
            generic_action=False,
            action_slug=self.add_metadata_url_slug,
            resource_specific=True,
            resource_id=self.instance_data["id"],
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        resp = self.request_manager.send_request(
            method="POST",
            url=url,
            data={"metadata": metadata_obj.model_dump()},
            query_params={"query_type": "SELF_CREATED"},
        )

        if resp.status_code == 201:
            data = resp.json()["data"]
        else:
            raise_custom_exception(response=resp, action=self.add_metadata_url_slug)

        return Metadata(
            data["metadata_id"], api_key=self.request_manager.credential_manager.api_key
        )

    def add_metadata_storage(self, *, data_type=None, key=None, file_path=None):
        self.validate()

        # TODO[VIMPORTANT] ADD CHECK FOR KWARGS TO THIS METHOD, THINK OF DOING THIS BY PYDANTIC

        try:
            metadata_obj = CreateMetadataStorage(
                key=key, data_type=data_type, file_path=file_path
            )
        except ValidationError as ex:
            errors = [f"`{error['loc'][0]}`: {error['msg']}" for error in ex.errors()]
            error_message = "\n".join(errors)
            raise Exception(
                error_message
            )  # TODO[VIMPORTANT] REPLACE WITH A CUSTOM EXCEPTION with proper custom, easier to understand error messages based on type of error given by pydantic

        url = self.generate_url(
            generic_action=False,
            action_slug=self.add_metadata_url_slug,
            resource_specific=True,
            resource_id=self.instance_data["id"],
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS

        metadata_obj_data = metadata_obj.model_dump()

        file_size = os.path.getsize(metadata_obj_data["file_path"])

        resp = self.request_manager.send_request(
            method="POST",
            url=url,
            data={
                "metadata": {
                    "key": metadata_obj_data["key"],
                    "data_type": metadata_obj_data["data_type"],
                    "properties": {"file_size": file_size},
                }
            },
            query_params={"query_type": "SELF_CREATED"},
        )

        if resp.status_code == 201:
            data = resp.json()["data"]
        else:
            raise_custom_exception(response=resp, action=self.add_metadata_url_slug)

        try:
            metadata_instance = Metadata(
                data["metadata_id"],
                api_key=self.request_manager.credential_manager.api_key,
            )

            # TODO[VIMPORTANT] ADD A METHOD TO RETRY THIS UPLOAD ATLEAST 3 TIMES BEFORE RAISING AN EXCEPTION AND MOVE ALL S3 FILE UPLOAD AND DOWNLOAD TO `Metadata` CLASS
            with open(metadata_obj_data["file_path"], "rb") as fp:

                file_data = {"file": (metadata_obj_data["file_path"].name, fp)}

                resp = requests.post(
                    url=metadata_instance.instance_data["properties"]["upload_config"][
                        "presigned_post_data"
                    ]["url"],
                    data=metadata_instance.instance_data["properties"]["upload_config"][
                        "presigned_post_data"
                    ]["fields"],
                    files=file_data,
                )

                if resp.status_code != 204:
                    raise_custom_exception__metadata(response=resp, action="S3_UPLOAD")
        except Exception as ex:
            self.complete_metadata_upload(metadata_id=data["metadata_id"])

            raise ex

        self.complete_metadata_upload(metadata_id=metadata_instance.instance_data["id"])
        metadata_instance.refresh_instance()

        return metadata_instance

    def complete_metadata_upload(self, *, metadata_id=None):
        self.validate()

        # TODO[VIMPORTANT] ADD CHECK FOR KWARGS TO THIS METHOD, THINK OF DOING THIS BY PYDANTIC

        url = self.generate_url(
            generic_action=False,
            action_slug=self.complete_metadata_upload_url_slug,
            resource_specific=True,
            resource_id=self.model_identifier,
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        resp = self.request_manager.send_request(
            method="PATCH",
            url=url,
            query_params={"query_type": "SELF_CREATED"},
            data={"metadata_id": metadata_id},
        )

        if resp.status_code == 200:
            return resp.json()["data"]
        else:
            raise_custom_exception(
                response=resp, action=self.complete_metadata_upload_url_slug
            )

    def update_metadata(self, *, metadata_id=None, data_type=None, value=None):
        self.validate()

        # TODO[VIMPORTANT] ADD CHECK FOR KWARGS TO THIS METHOD, THINK OF DOING THIS BY PYDANTIC

        url = self.generate_url(
            generic_action=False,
            action_slug=self.update_metadata_url_slug,
            resource_specific=True,
            resource_id=self.model_identifier,
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        resp = self.request_manager.send_request(
            method="PATCH",
            url=url,
            query_params={"query_type": "SELF_CREATED", "confirm_update": "true"},
            data={
                "metadata_id": metadata_id,
                "metadata": {"data_type": data_type, "properties": {"value": value}},
            },
        )

        if resp.status_code == 200:
            return resp.json()["data"]
        else:
            raise_custom_exception(response=resp, action=self.update_metadata_url_slug)

    def _list_metadata(self, *, extra_query_params=None):
        self.validate()

        # TODO[VIMPORTANT] ADD CHECK HERE FOR CORRECT TYPE OF `extra_query_params`, THINK OF DOING IT VIA PYDANTIC AND ALSO FOR ALL OTHER FUNCTIONS
        if extra_query_params == None:
            extra_query_params = {}

        url = self.generate_url(
            generic_action=False,
            action_slug=self.list_metadata_url_slug,
            resource_specific=True,
            resource_id=self.instance_data["id"],
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        extra_query_params.update({"query_type": "SELF_CREATED"})
        resp = self.request_manager.send_request(
            method="GET", url=url, query_params=extra_query_params
        )

        if resp.status_code == 200:
            return resp.json()["data"]
        else:
            raise_custom_exception(response=resp, action=self.list_metadata_url_slug)

    # TODO[VIMPORTANT] ADD OPTION TO PASS FILTERS WITH PROPER DYNAMIC CHECK VIA PYDANTIC
    def list_metadata(self, *, api_key=None, columns=None, verbose_columns=True):
        self.validate()

        # TODO[VIMPORTANT] ADD CHECK FOR KWARGS TO THIS METHOD, THINK OF DOING THIS BY PYDANTIC

        data = self._list_metadata()

        table_instance = Table(
            data=data["results"], normalize=True, local_timezone=self.local_timezone
        )

        return table_instance.to_representation(
            default_columns=data["default_visible_columns"]["cli"],
            columns=columns,
            column_mapping=Metadata.verbose_column_mapping,
            verbose_columns=verbose_columns,
        )

    # TODO[VIMPORTANT] ADD OPTION TO PASS FILTERS WITH PROPER DYNAMIC CHECK VIA PYDANTIC
    def _list_model_variations(self, *, extra_query_params=None):
        self.validate()

        # TODO[VIMPORTANT] ADD CHECK HERE FOR CORRECT TYPE OF `extra_query_params`, THINK OF DOING IT VIA PYDANTIC AND ALSO FOR ALL OTHER FUNCTIONS
        if extra_query_params == None:
            extra_query_params = {}

        url = self.generate_url(
            generic_action=False,
            action_slug=self.list_model_variations_url_slug,
            resource_specific=True,
            resource_id=self.instance_data["id"],
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        extra_query_params.update({"query_type": "SELF_CREATED"})
        resp = self.request_manager.send_request(
            method="GET", url=url, query_params=extra_query_params
        )

        if resp.status_code == 200:
            return resp.json()["data"]
        else:
            raise_custom_exception(
                response=resp, action=self.list_model_variations_url_slug
            )

    # TODO[VIMPORTANT] ADD OPTION TO PASS FILTERS WITH PROPER DYNAMIC CHECK VIA PYDANTIC
    def list_variations(self, *, api_key=None, columns=None, verbose_columns=True):
        self.validate()

        # TODO[VIMPORTANT] ADD CHECK FOR KWARGS TO THIS METHOD

        data = self._list_model_variations()

        table_instance = Table(
            data=data["results"], normalize=True, local_timezone=self.local_timezone
        )

        return table_instance.to_representation(
            default_columns=data["default_visible_columns"]["cli"],
            columns=columns,
            column_mapping=ModelVersion.verbose_column_mapping,
            verbose_columns=verbose_columns,
        )

    def _list_distinct_model_versions(self, *, extra_query_params=None):
        self.validate()

        # TODO[VIMPORTANT] ADD CHECK HERE FOR CORRECT TYPE OF `extra_query_params`, THINK OF DOING IT VIA PYDANTIC AND ALSO FOR ALL OTHER FUNCTIONS
        if extra_query_params == None:
            extra_query_params = {}

        url = self.generate_url(
            generic_action=False,
            action_slug=self.list_distinct_model_versions_url_slug,
            resource_specific=True,
            resource_id=self.instance_data["id"],
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        extra_query_params.update({"query_type": "SELF_CREATED"})
        resp = self.request_manager.send_request(
            method="GET", url=url, query_params=extra_query_params
        )

        if resp.status_code == 200:
            return resp.json()["data"]
        else:
            raise_custom_exception(
                response=resp, action=self.list_distinct_model_versions_url_slug
            )

    # TODO[VIMPORTANT] ADD OPTION TO PASS FILTERS WITH PROPER DYNAMIC CHECK VIA PYDANTIC
    def list_versions(self, *, columns=None, verbose_columns=True):
        self.validate()

        # TODO[VIMPORTANT] ADD CHECK FOR KWARGS TO THIS METHOD

        data = self._list_distinct_model_versions()

        table_instance = Table(
            data=data["results"], normalize=True, local_timezone=self.local_timezone
        )

        return table_instance.to_representation(
            default_columns=data["default_visible_columns"]["cli"],
            columns=columns,
            column_mapping=ModelVersion.verbose_column_mapping,
            verbose_columns=verbose_columns,
        )

    def delete_metadata(self, *, metadata_id=None):
        self.validate()

        # TODO[VIMPORTANT] ADD CHECK FOR KWARGS TO THIS METHOD, THINK OF DOING THIS BY PYDANTIC

        url = self.generate_url(
            generic_action=False,
            action_slug=self.delete_metadata_url_slug,
            resource_specific=True,
            resource_id=self.model_identifier,
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        resp = self.request_manager.send_request(
            method="DELETE",
            url=url,
            query_params={"query_type": "SELF_CREATED", "confirm_delete": "true"},
            data={"metadata_id": metadata_id},
        )

        if resp.status_code == 200:
            return None
        else:
            raise_custom_exception(response=resp, action=self.delete_metadata_url_slug)

    def complete_model_version_creation(self, *, version_id=None):
        self.validate()

        # TODO[VIMPORTANT] ADD CHECK FOR KWARGS TO THIS METHOD, THINK OF DOING THIS BY PYDANTIC

        url = self.generate_url(
            generic_action=False,
            action_slug=self.complete_model_version_creation_url_slug,
            resource_specific=True,
            resource_id=self.model_identifier,
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        resp = self.request_manager.send_request(
            method="PATCH",
            url=url,
            query_params={"query_type": "SELF_CREATED"},
            data={"version_id": version_id},
        )

        if resp.status_code == 200:
            return None
        # TODO[VIMPORTANT] ADD CUSTOM EXCEPTIONS HERE TO HANDLE 400 RESPONSES
        else:
            raise_custom_exception(
                response=resp, action=self.complete_model_version_creation_url_slug
            )

    def attach_tags(self, *, tags=None):
        self.validate()

        try:
            model_tags = CreateModelTags(tags=tags)
        except ValidationError as ex:
            errors = [f"`{error['loc']}`: {error['msg']}" for error in ex.errors()]
            error_message = "\n".join(errors)
            raise Exception(
                error_message
            )  # TODO[VIMPORTANT] REPLACE WITH A CUSTOM EXCEPTION with proper custom, easier to understand error messages based on type of error given by pydantic

        url = self.generate_url(
            generic_action=False,
            action_slug=self.attach_tags_url_slug,
            resource_specific=True,
            resource_id=self.instance_data["id"],
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        resp = self.request_manager.send_request(
            method="PATCH",
            url=url,
            data=model_tags.model_dump(),
            query_params={"query_type": "SELF_CREATED"},
        )

        if resp.status_code != 200:
            raise_custom_exception(response=resp, action=self.attach_tags_url_slug)

        return None

    def _list_tags(self, *, extra_query_params=None):
        self.validate()

        # TODO[VIMPORTANT] ADD CHECK HERE FOR CORRECT TYPE OF `extra_query_params`, THINK OF DOING IT VIA PYDANTIC AND ALSO FOR ALL OTHER FUNCTIONS
        if extra_query_params == None:
            extra_query_params = {}

        url = self.generate_url(
            generic_action=False,
            action_slug=self.list_tags_url_slug,
            resource_specific=True,
            resource_id=self.instance_data["id"],
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        extra_query_params.update({"query_type": "SELF_CREATED"})
        resp = self.request_manager.send_request(
            method="GET", url=url, query_params=extra_query_params
        )

        if resp.status_code == 200:
            return resp.json()["data"]
        else:
            raise_custom_exception(response=resp, action=self.list_tags_url_slug)

    # TODO[VIMPORTANT] ADD OPTION TO PASS FILTERS WITH PROPER DYNAMIC CHECK VIA PYDANTIC
    def list_tags(self, *, api_key=None, columns=None, verbose_columns=True):
        self.validate()

        # TODO[VIMPORTANT] ADD CHECK FOR KWARGS TO THIS METHOD, THINK OF DOING THIS BY PYDANTIC

        data = self._list_tags()

        table_instance = Table(data=data["results"], local_timezone=self.local_timezone)

        return table_instance.to_representation(
            default_columns=data["default_visible_columns"]["cli"],
            columns=columns,
            column_mapping=self.tags_verbose_column_mapping,
            verbose_columns=verbose_columns,
        )

    def remove_tag(self, *, tag_id=None):
        self.validate()

        # TODO[VIMPORTANT] ADD CHECK FOR KWARGS TO THIS METHOD, THINK OF DOING THIS BY PYDANTIC

        url = self.generate_url(
            generic_action=False,
            action_slug=self.remove_tag_url_slug,
            resource_specific=True,
            resource_id=self.instance_data["id"],
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        resp = self.request_manager.send_request(
            method="PATCH",
            url=url,
            data={"tag_id": tag_id},
            query_params={"query_type": "SELF_CREATED"},
        )

        if resp.status_code != 200:
            raise_custom_exception(response=resp, action=self.remove_tag_url_slug)

        return None

    def remove_all_tags(self):
        self.validate()

        # TODO[VIMPORTANT] ADD CHECK FOR KWARGS TO THIS METHOD, THINK OF DOING THIS BY PYDANTIC

        url = self.generate_url(
            generic_action=False,
            action_slug=self.remove_all_tags_url_slug,
            resource_specific=True,
            resource_id=self.instance_data["id"],
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        resp = self.request_manager.send_request(
            method="PATCH",
            url=url,
            query_params={"query_type": "SELF_CREATED", "confirm_update": "true"},
        )

        if resp.status_code != 200:
            raise_custom_exception(response=resp, action=self.remove_all_tags_url_slug)

        return None

    def delete_version(self, *, version=None):
        self.validate()

        try:
            DeleteVersion(version=version)
        except ValidationError as ex:
            errors = [f"`{error['loc'][0]}`: {error['msg']}" for error in ex.errors()]
            error_message = "\n".join(errors)
            raise Exception(
                error_message
            )  # TODO[VIMPORTANT] REPLACE WITH A CUSTOM EXCEPTION with proper custom, easier to understand error messages based on type of error given by pydantic

        url = self.generate_url(
            generic_action=False,
            action_slug=self.delete_version_url_slug,
            resource_specific=True,
            resource_id=self.instance_data["id"],
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        resp = self.request_manager.send_request(
            method="DELETE",
            url=url,
            query_params={"query_type": "SELF_CREATED", "confirm_delete": "true"},
            data={"version": version},
        )

        if resp.status_code != 200:
            raise_custom_exception(response=resp, action=self.delete_version_url_slug)

        return None

    def delete(self):
        self.validate()

        url = self.generate_url(
            generic_action=True,
            resource_specific=True,
            resource_id=self.instance_data["id"],
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        resp = self.request_manager.send_request(
            method="DELETE",
            url=url,
            query_params={"query_type": "SELF_CREATED", "confirm_delete": "true"},
        )

        if resp.status_code != 200:
            raise_custom_exception(response=resp, action="DELETE")

        self.is_deleted = True

        return None

    def _generate_metadata_download_url(self, *, metadata_id=None):
        self.validate()

        try:
            metadata_data = GenerateMetadataDownloadURL(metadata_id=metadata_id)
        except ValidationError as ex:
            errors = [f"`{error['loc']}`: {error['msg']}" for error in ex.errors()]
            error_message = "\n".join(errors)
            raise Exception(
                error_message
            )  # TODO[VIMPORTANT] REPLACE WITH A CUSTOM EXCEPTION with proper custom, easier to understand error messages based on type of error given by pydantic

        url = self.generate_url(
            generic_action=False,
            action_slug=self.generate_metadata_download_url_url_slug,
            resource_specific=True,
            resource_id=self.instance_data["id"],
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        resp = self.request_manager.send_request(
            method="GET",
            url=url,
            query_params={
                "query_type": "SELF_CREATED",
                "metadata_id": metadata_data.model_dump()["metadata_id"],
            },
        )

        if resp.status_code == 200:
            return resp.json()["data"]
        else:
            raise_custom_exception(
                response=resp, action=self.generate_metadata_download_url_url_slug
            )

    def _generate_metadata_preview_url(self, *, metadata_id=None):
        self.validate()

        try:
            metadata_data = GenerateMetadataPreviewURL(metadata_id=metadata_id)
        except ValidationError as ex:
            errors = [f"`{error['loc']}`: {error['msg']}" for error in ex.errors()]
            error_message = "\n".join(errors)
            raise Exception(
                error_message
            )  # TODO[VIMPORTANT] REPLACE WITH A CUSTOM EXCEPTION with proper custom, easier to understand error messages based on type of error given by pydantic

        url = self.generate_url(
            generic_action=False,
            action_slug=self.generate_metadata_preview_url_url_slug,
            resource_specific=True,
            resource_id=self.instance_data["id"],
        )

        # TODO[VIMPORTANT] ADD OPTION TO SEARCH 'ORG_WIDE' OR 'SELF_CREATED', SHOULD BE ACCESSIBLE IN ALL FUNCTIONS
        resp = self.request_manager.send_request(
            method="GET",
            url=url,
            query_params={
                "query_type": "SELF_CREATED",
                "metadata_id": metadata_data.model_dump()["metadata_id"],
            },
        )

        if resp.status_code == 200:
            return resp.json()["data"]
        else:
            raise_custom_exception(
                response=resp, action=self.generate_metadata_preview_url_url_slug
            )
