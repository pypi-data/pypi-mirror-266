from pathlib import Path
import pandas as pd
import tzlocal
from datetime import datetime
import humanize
import os

from .credentials import Credentials
from .constants import PLATFORM_URL_BASE_SLUG, LIBRARY_BASE_DIR_NAME, PLATFORM_URL_NAME
from .request_manager import RequestManager
from .exceptions import InstanceDeletedException


class BaseModule:
    # TODO[VIMPORTANT] CHECK AND MAKE FUNCTIONS PRIVATE IF THEY SHOULD NOT BE ACCESSIBLE DIRECTLY

    module_url_slug = None
    base_dir_path = None
    local_timezone = tzlocal.get_localzone()
    platform_url = None

    def __init__(self, *, api_key=None) -> None:

        self.api_key = api_key

        self.credential_manager = Credentials(api_key=self.api_key)
        self.request_manager = RequestManager(
            credential_manager=self.credential_manager
        )

        self.base_dir_path = self.check_or_create_base_dir()

    def check_or_create_base_dir(self):
        current_dir = Path.cwd()

        base_dir = current_dir / LIBRARY_BASE_DIR_NAME

        if not base_dir.exists():
            base_dir.mkdir()

        full_path = base_dir.resolve()

        return full_path

    @classmethod
    def get_request_manager(cls, *, api_key=None):

        credential_manager = Credentials(api_key=api_key)
        request_manager = RequestManager(credential_manager=credential_manager)

        return request_manager


class BaseSubModule(BaseModule):
    # TODO[VIMPORTANT] CHECK AND MAKE FUNCTIONS PRIVATE IF THEY SHOULD NOT BE ACCESSIBLE DIRECTLY

    sub_module_url_slug = None
    is_deleted_error = InstanceDeletedException

    def __init__(self, *, api_key=None) -> None:
        super().__init__(api_key=api_key)
        self.is_deleted = False

    @classmethod
    def generate_url(
        cls,
        *,
        generic_action=True,
        action_slug=None,
        resource_specific=False,
        resource_id=None,
    ):

        cls.platform_url = os.environ.get(PLATFORM_URL_NAME, None)
        if cls.platform_url == None:
            cls.platform_url = PLATFORM_URL_BASE_SLUG

        if generic_action == True:
            url = f"{cls.module_url_slug}/{cls.sub_module_url_slug}/{cls.sub_module_url_slug}"
        else:
            url = f"{cls.module_url_slug}/{cls.sub_module_url_slug}/{action_slug}"

        if resource_specific == True:
            url += f"/{resource_id}"

        url = f"{cls.platform_url}/{url}/"

        return url

    def validate(self):

        if self.is_deleted == True:
            raise self.is_deleted_error()


class Table:

    def __init__(
        self,
        data=None,
        normalize=False,
        normalize_sep="__",
        normalize_level=1,
        local_timezone=None,
    ) -> None:
        self.data = data
        self.normalize = normalize
        self.normalize_sep = normalize_sep
        self.normalize_level = normalize_level
        self.local_timezone = local_timezone
        # TODO[VIMPORTANT] ADD PYDANTIC VALIDATION HERE

    def convert_datetime(self, value):

        if pd.isna(value) == False:
            value = pd.to_datetime(value)
            if (datetime.now(self.local_timezone) - value).days > 0:
                value = humanize.naturaldate(value)
            else:
                value = humanize.naturaltime(
                    value, when=datetime.now(self.local_timezone)
                )

        return value

    def convert_size(self, value):

        if pd.isna(value) == False:
            value = humanize.naturalsize(value)

        return value

    def to_representation(
        self,
        default_columns=None,
        columns=None,
        column_mapping=None,
        verbose_columns=True,
    ):
        # TODO[VIMPORTANT] ADD CHECK FOR KWARGS TO THIS METHOD

        if self.normalize == False:
            df = pd.DataFrame(self.data)
        else:
            df = pd.json_normalize(
                self.data, sep=self.normalize_sep, max_level=self.normalize_level
            )

        visible_columns = None
        visible_columns_verbose = None
        if columns == None:
            visible_columns = set(default_columns).intersection(set(df.columns))
            if verbose_columns == True:
                visible_columns_verbose = visible_columns
                visible_columns = [
                    (
                        column_mapping[col]
                        if column_mapping.get(col, None) != None
                        else col
                    )
                    for col in visible_columns
                ]
        elif columns == "*":
            visible_columns = df.columns
            if verbose_columns == True:
                visible_columns = list(
                    set(visible_columns).intersection(set(column_mapping.keys()))
                )
                visible_columns_verbose = visible_columns
                visible_columns = [
                    (
                        column_mapping[col]
                        if column_mapping.get(col, None) != None
                        else col
                    )
                    for col in visible_columns
                ]
        else:
            visible_columns = columns
            visible_columns_verbose = visible_columns

        if verbose_columns == True:

            # TODO[VIMPORTANT] GENERALIZE THIS SO THAT WE CAN APPLY ANY FUNCTION TO ANY FIELDS BY SPECIFYINGIT IN THE VERBOSE COLUMNS CONFIG, CAN ALSO USE FUNCTIONS OF TABLE IN base.py
            if "created_at" in visible_columns_verbose:
                df["created_at"] = df["created_at"].map(self.convert_datetime)

            # TODO[VIMPORTANT] GENERALIZE THIS SO THAT WE CAN APPLY ANY FUNCTION TO ANY FIELDS BY SPECIFYINGIT IN THE VERBOSE COLUMNS CONFIG, CAN ALSO USE FUNCTIONS OF TABLE IN base.py
            if "updated_at" in visible_columns_verbose:
                df["updated_at"] = df["updated_at"].map(self.convert_datetime)

            # TODO[VIMPORTANT] GENERALIZE THIS SO THAT WE CAN APPLY ANY FUNCTION TO ANY FIELDS BY SPECIFYINGIT IN THE VERBOSE COLUMNS CONFIG, CAN ALSO USE FUNCTIONS OF TABLE IN base.py
            if "properties__file_size" in visible_columns_verbose:
                df["properties__file_size"] = df["properties__file_size"].map(
                    self.convert_size
                )
            df.rename(columns=column_mapping, inplace=True)
        return df.reindex(columns=visible_columns)
