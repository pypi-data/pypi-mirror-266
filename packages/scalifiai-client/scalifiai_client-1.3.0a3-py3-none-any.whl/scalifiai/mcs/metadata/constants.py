from typing_extensions import Literal

URL_SLUG = "metadata"

# TODO[VIMPORTANT] KEEP BOTH IN SYNC
DATA_TYPES = ["str", "int", "float", "file"]
DATA_TYPES_SIMPLE = ["str", "int", "float"]
DATA_TYPES_STORAGE = ["file"]
DATA_TYPES_SIMPLE_LITERAL = Literal["str", "int", "float"]
DATA_TYPES_STORAGE_LITERAL = Literal["file"]

OPERATION_ADDITION_AUTO_UPDATE_ENV_KEY = "METADATA_ADDITION_AUTO_UPDATE"
