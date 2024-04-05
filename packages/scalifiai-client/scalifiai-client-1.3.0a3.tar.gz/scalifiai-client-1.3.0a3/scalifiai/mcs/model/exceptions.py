from scalifiai.exceptions import (
    raise_general_exception,
    GeneralException,
    BackendNotAvailableException,
    InstanceDeletedException,
)
from scalifiai.mcs.model_version.exceptions import (
    ModelVersionCreateException as ModelVariationCreateException,
    ModelVersionNotFoundException as ModelVariationNotFoundException,
)
from scalifiai.mcs.metadata.exceptions import (
    MetadataCreateException,
    MetadataNotFoundException,
    MetadataAlreadyExistsException,
    MetadataUpdateException,
    MetadataDeleteException,
    MetadataGenerateDownloadURLException,
    MetadataGeneratePreviewURLException,
)


class ModelException(GeneralException):
    default_message = """
{h1}
----ModelException-------------------------------------------------------------------------------
{end}
There's an error with a model in the Scalifi Ai Model Catalog Service (MCS).

This error indicates an issue occurred while processing a request related to models within the MCS. As this is a general exception, the specific cause might vary.

{h2}What can I do?{end}

1. {bold}Review the error message:{end} Sometimes, the error message might contain additional details about the specific issue encountered. This information can help you diagnose the problem further.
2. {bold}Check the Scalifi Ai status page:{end} The Scalifi Ai status page provides real-time information about service disruptions or ongoing maintenance. This can help determine if the issue is widespread or specific to your request. 
3. {bold}Refer to Scalifi Ai documentation:{end} The Scalifi Ai documentation might offer troubleshooting steps or specific information about model-related errors. You can visit documentation at {docs_url_base}

{correct}Need more help?{end}-> Contact Scalifi Ai support: {support_email}

{bold}For developers:{end} If you're encountering this error within your code, consider enabling more verbose logging within the MCS client library to gather additional details about the specific error.
"""


class ModelNotFoundException(ModelException):
    default_message = """
{h1}
----ModelNotFoundException-----------------------------------------------------------------------
{end}
The specified model could not be found.

This error indicates that the model you're trying to access or perform an action on does not exist in the Scalifi Ai's Model Catalog Service (MCS). There are two possible reasons for this:

* {bold}Non-existent model:{end} The model ID or name you provided might be incorrect, or the model you're referencing may have never been created.
* {bold}Deleted model:{end} It's also possible that the model you were previously working with has been deleted.

{h2}What can I do?{end}

1. {bold}Verify your model ID or name:{end} Double-check the model ID or name you're using to ensure it's accurate and matches an existing model in your MCS.
2. {bold}Check for deleted models:{end} If you suspect the model might have been deleted, consult with your team or organization's MCS administrator to confirm its status.

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelCreateException(ModelException):
    default_message = """
{h1}
----ModelCreateException-----------------------------------------------------------------------
{end}
An error occurred while creating a model.

This error indicates that there was a problem during the process of creating a new model instance in Scalifi Ai's Model Catalog Service (MCS). The specific cause might vary depending on the nature of the issue.

{h2}What can I do?{end}

1. {bold}Review the error message:{end} Sometimes, the error message might contain details about the specific reason for the failure. This information can help you diagnose the problem further.
2. {bold}Check your model definition:{end} Ensure your model definition adheres to the required format and specifications for the MCS. Refer to the Scalifi Ai documentation for guidance on creating valid model definitions.
3. {bold}Contact Scalifi Ai support:{end} If you've reviewed the error message and checked your model definition but the issue persists, consider contacting Scalifi Ai support for further assistance at {support_email}

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelTagAttachException(ModelException):
    default_message = """
{h1}
----ModelTagAttachException--------------------------------------------------------------------
{end}
An error occurred while attaching tags to a model.

This error indicates that there was a problem during the process of attaching one or more tags to a model in the Scalifi Ai's Model Catalog Service (MCS). The specific cause might vary depending on the nature of the issue.

{h2}What can I do?{end}

1. {bold}Review the error message:{end} Sometimes, the error message might contain details about the specific reason for the failure. This information can help you diagnose the problem further.
2. {bold}Verify your tags:{end} Ensure the tags you're trying to attach are valid and follow the MCS tagging specifications. Refer to the Scalifi Ai documentation for guidance on proper tag formats and usage.
3. {bold}Try attaching tags through the Scalifi Ai platform:{end} You can also attach tags directly to models within the Scalifi Ai platform user interface. This alternative approach might bypass any issues encountered with the programmatic tagging attempt.

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelTagRemoveException(ModelException):
    default_message = """
{h1}
----ModelTagRemoveException-------------------------------------------------------------------
{end}
An error occurred while removing a tag from a model.

This error indicates that there was a problem during the process of detaching a tag from a model in the Scalifi Ai's Model Catalog Service (MCS). The specific cause might vary depending on the nature of the issue.

{h2}What can I do?{end}

1. {bold}Review the error message:{end} Sometimes, the error message might contain details about the specific reason for the failure. This information can help you diagnose the problem further.
2. {bold}Verify the tag name:{end} Ensure the name of the tag you're trying to remove is spelled correctly and exists on the model.
3. {bold}Try removing the tag through the Scalifi Ai platform:{end} You can also remove tags directly from models within the Scalifi Ai platform user interface. This alternative approach might bypass any issues encountered with the programmatic tag removal attempt.

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelVersionNotFoundException(ModelException):
    default_message = """
{h1}
----ModelVersionNotFoundException----------------------------------------------------------------
{end}
The specified model version could not be found.

This error indicates that the specific version of a model you're trying to access or perform an action on does not exist in the Scalifi Ai's Model Catalog Service (MCS). There are two possible reasons for this:

* {bold}Non-existent version:{end} The version number you provided might be incorrect, or the specific version you're referencing may have never been created.
* {bold}Deleted version:{end} It's also possible that the version of the model you were previously working with has been deleted.

{h2}What can I do?{end}

1. {bold}Verify your model version:{end} Double-check the version number you're using to ensure it's accurate and matches an existing version for the model in your MCS.
2. {bold}Check for deleted versions:{end} If you suspect the version might have been deleted, consult with your team or organization's MCS administrator to confirm its status.
3. {bold}Manage versions through the Scalifi Ai platform:{end} You can also manage model versions, including managing available variations directly within the Scalifi Ai platform.

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelVersionDeleteException(ModelException):
    default_message = """
{h1}
----ModelVersionDeleteException---------------------------------------------------------------
{end}
An error occurred while deleting a model version.

This error indicates that the MCS was unable to complete the deletion of a specific model version you requested. The exact cause might vary, but here are some possible reasons:

* {bold}Version in use:{end} The version might be actively used by a deployment or another process, preventing its immediate deletion.
* {bold}Permissions issue:{end} You might not have the necessary permissions to delete this version.

{h2}What can I do?{end}

1. {bold}Review the error message:{end} Check for any specific details about the failure.
2. {bold}Check for dependencies:{end} Verify if the version is currently used by any deployments or processes. If so, consider terminating those dependencies first.
3. {bold}Verify permissions:{end} Ensure you have the appropriate permissions to delete model versions. If you're unsure, consult your team or organization's MCS administrator.
4. {bold}Try deleting through the Scalifi Ai platform:{end} You can try deleting the version directly within the Scalifi Ai platform's user interface. This might provide more specific error messages or guidance.
5. {bold}Contact Scalifi Ai support:{end} If the issue persists despite these steps, reach out to Scalifi Ai support for further assistance at {support_email}

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelDeleteException(ModelException):
    default_message = """
{h1}
----ModelDeleteException---------------------------------------------------------------------
{end}
An error occurred while deleting a model.

This error indicates that the MCS was unable to complete the deletion of a specific model you requested. The exact cause might vary, but here are some possible reasons:

* {bold}Model in use:{end} The model might be referenced by versions, deployments, or other processes, preventing its immediate deletion.
* {bold}Permissions issue:{end} You might not have the necessary permissions to delete this model.

{h2}What can I do?{end}

1. {bold}Review the error message:{end} Check for any specific details about the failure reason.
2. {bold}Identify dependencies:{end} Investigate if the model is used by any model versions, deployments, or other entities within the MCS. These dependencies need to be addressed before deletion.
3. {bold}Verify permissions:{end} Ensure you have the appropriate permissions to delete models. If you're unsure, consult your team or organization's MCS administrator.
4. {bold}Manage models through the Scalifi Ai platform:{end} You can also manage models, including viewing dependencies and potentially initiating deletion (subject to permissions), directly within the Scalifi Ai platform's user interface.

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelInstanceDeletedException(InstanceDeletedException):
    default_message = """
{h1}
----ModelInstanceDeletedException--------------------------------------------------------------
{end}
The model instance you're trying to access has been deleted.

This error indicates that you're attempting to use a variable referencing a model instance that has already been deleted from the Scalifi Ai Model Catalog Service (MCS). This could happen due to various reasons, such as deletion from the platform or expiration of the instance's lifecycle.

{h2}What can I do?{end}

1. {bold}Review your code:{end} Double-check the code section where you're using the variable pointing to the deleted model instance.
2. {bold}Obtain a fresh instance:{end} If the model itself still exists, consider fetching a new instance of the model from the MCS using the appropriate methods provided by the library. This ensures you're working with up-to-date information.
3. {bold}Handle the exception:{end} Depending on your code's logic, you might need to implement exception handling for this specific error. This could involve gracefully exiting the code block, logging the error, or retrying the operation if applicable.

{correct}Need more help?{end}-> {docs_url_base}
"""


def raise_custom_exception(*, response=None, action=None, internal_data=None):

    data, error_code = raise_general_exception(
        response=response, internal_data=internal_data
    )

    if action == None:
        raise Exception("No action value provided")

    if action in [
        "RETRIEVE",
        "DELETE",
        "add_model_version",
        "complete_model_version_creation",
        "add_metadata",
        "complete_metadata_upload",
        "list_metadata",
        "update_metadata",
        "list_model_variations",
        "list_distinct_model_versions",
        "delete_metadata",
        "attach_tags",
        "list_tags",
        "remove_tag",
        "remove_all_tags",
        "delete_version",
        "generate_metadata_download_url",
        "generate_metadata_preview_url",
    ]:
        if response.status_code == 404:
            raise ModelNotFoundException()

    if error_code != None and type(error_code) == dict and len(error_code) != 0:

        error_code_key = error_code.get("status", None)

        if action == "CREATE":

            if error_code_key != None and data.get("detail", None):
                raise ModelCreateException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise ModelCreateException(internal_data=internal_data)

                raise ModelCreateException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "add_model_version":

            if error_code_key != None and data.get("detail", None):
                raise ModelVariationCreateException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise ModelVariationCreateException(internal_data=internal_data)

                raise ModelVariationCreateException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "complete_model_version_creation":

            if error_code_key != None and data.get("detail", None):
                raise ModelVariationCreateException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                if "version_id" in error_code.keys():
                    if error_code["version_id"][0] == "not_found":
                        raise ModelVariationNotFoundException()

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise ModelVariationCreateException(internal_data=internal_data)

                raise ModelVariationCreateException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "add_metadata":

            if error_code_key != None and data.get("detail", None):
                raise MetadataCreateException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                if (
                    "metadata" in error_code.keys()
                    and "non_field_errors" in error_code["metadata"].keys()
                ):
                    if "unique" in error_code["metadata"]["non_field_errors"]:
                        raise MetadataAlreadyExistsException()

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise MetadataCreateException(internal_data=internal_data)

                raise MetadataCreateException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "complete_metadata_upload":

            if error_code_key != None and data.get("detail", None):
                raise MetadataCreateException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                if "metadata_id" in error_code.keys():
                    if error_code["metadata_id"][0] == "not_found":
                        raise MetadataNotFoundException()

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise MetadataCreateException(internal_data=internal_data)

                raise MetadataCreateException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "update_metadata":

            if error_code_key != None and data.get("detail", None):
                raise MetadataUpdateException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                if "metadata_id" in error_code.keys():
                    if error_code["metadata_id"][0] == "not_found":
                        raise MetadataNotFoundException()

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise MetadataUpdateException(internal_data=internal_data)

                raise MetadataUpdateException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "delete_metadata":

            if error_code_key != None and data.get("detail", None):
                raise MetadataDeleteException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                if "metadata_id" in error_code.keys():
                    if error_code["metadata_id"][0] == "not_found":
                        raise MetadataNotFoundException()

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise MetadataDeleteException(internal_data=internal_data)

                raise MetadataDeleteException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "attach_tags":

            if error_code_key != None and data.get("detail", None):
                raise ModelTagAttachException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise ModelTagAttachException(internal_data=internal_data)

                raise ModelTagAttachException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "remove_tag":

            if error_code_key != None and data.get("detail", None):
                raise ModelTagRemoveException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise ModelTagRemoveException(internal_data=internal_data)

                raise ModelTagRemoveException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "remove_all_tags":

            if error_code_key != None and data.get("detail", None):
                raise ModelTagRemoveException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise ModelTagRemoveException(internal_data=internal_data)

                raise ModelTagRemoveException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "delete_version":

            if error_code_key != None and data.get("detail", None):
                raise ModelVersionDeleteException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                if "version" in error_code.keys():
                    if error_code["version"][0] == "not_found":
                        raise ModelVersionNotFoundException()

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise ModelVersionDeleteException(internal_data=internal_data)

                raise ModelVersionDeleteException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "DELETE":

            if error_code_key != None and data.get("detail", None):
                raise ModelDeleteException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise ModelDeleteException(internal_data=internal_data)

                raise ModelDeleteException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "generate_metadata_download_url":

            if error_code_key != None and data.get("detail", None):
                raise MetadataGenerateDownloadURLException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                if "metadata_id" in error_code.keys():
                    if error_code["metadata_id"][0] == "not_found":
                        raise MetadataNotFoundException()

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise MetadataGenerateDownloadURLException(
                        internal_data=internal_data
                    )

                raise MetadataGenerateDownloadURLException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "generate_metadata_preview_url":

            if error_code_key != None and data.get("detail", None):
                raise MetadataGeneratePreviewURLException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                if "metadata_id" in error_code.keys():
                    if error_code["metadata_id"][0] == "not_found":
                        raise MetadataNotFoundException()

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise MetadataGeneratePreviewURLException(
                        internal_data=internal_data
                    )

                raise MetadataGeneratePreviewURLException(
                    extra_info=data_string, internal_data=internal_data
                )

    if error_code != None and len(error_code.keys()) != 0:

        data_string = ""
        for key, value in data.items():
            if key == "error_code":
                continue
            data_string += f"Field: {key} || Error: {value}\n"

        if len(data_string) != 0:
            BackendNotAvailableException(
                extra_info=data_string, internal_data=internal_data
            )

    raise BackendNotAvailableException(internal_data=internal_data)
