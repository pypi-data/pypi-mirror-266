from scalifiai.exceptions import (
    raise_general_exception,
    GeneralException,
    BackendNotAvailableException,
    InstanceDeletedException,
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


class ModelVersionException(GeneralException):
    default_message = """
{h1}
----ModelVersionException---------------------------------------------------------------------
{end}
An error occurred while working with a model variation.

This error indicates an issue occurred during operations related to a specific variation of a model version in the Model Catalog Service (MCS). A model version can have multiple frameworks, and each framework can have variations. This exception class serves as the base for more specific errors related to these variations.

The exact cause might vary depending on the nature of the operation and the specific model variation involved.

{h2}What can I do?{end}

1. {bold}Review the error message:{end} Sometimes, the error message might contain details about the specific reason for the failure. This information can help you diagnose the problem further.
2. {bold}Consult library documentation:{end} Refer to the documentation for your MCS library to understand the supported operations for model variations and any potential limitations.
3. {bold}Check for specific error messages:{end} If possible, identify any child exception classes associated with this error. These child exceptions often provide more specific messages about the problem.
4. {bold}Contact Scalifi Ai support (if necessary):{end} For complex issues or if the provided information isn't sufficient, consider reaching out to Scalifi Ai support for further assistance at {support_email}

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelVersionNotFoundException(ModelVersionException):
    default_message = """
{h1}
----ModelVersionNotFoundException-------------------------------------------------------------
{end}
The specified model variation could not be found.

This error indicates that the model variation you're trying to access or operate on does not exist in the Model Catalog Service (MCS). There are a few possible reasons for this:

* {bold}Non-existent variation:{end} The specific combination of model version, framework, and variation you requested might not have been created in the MCS.
* {bold}Deleted variation:{end} It's also possible that the variation you're referencing was previously deleted.

{h2}What can I do?{end}

1. {bold}Verify details:{end} Double-check the model ID, name, version, framework, and variation details you're using to ensure they are accurate.
2. {bold}List available variations:{end} Consider using library methods to retrieve a list of available variations for a specific model version and framework. This can help you verify the existence of the desired variation.
3. {bold}Manage model variations through the Scalifi Ai platform:{end} You can also manage model variations directly on models within the Scalifi Ai platform's user interface. This alternative approach provides a visual representation of available variations and potentially allow for creating or deleting them (subject to permissions).

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelVersionModelFetchException(ModelVersionException):
    default_message = """
{h1}
----ModelVersionModelFetchException------------------------------------------------------------
{end}
An error occurred while fetching the model file.

This error indicates that there was a problem retrieving the model file associated with the requested model variation. This could happen due to various reasons related to the download process.

* {bold}Network issues:{end} Unstable internet connectivity or network restrictions might prevent the model file from downloading successfully.
* {bold}Server-side problems:{end} In rare cases, temporary issues on the MCS servers could hinder the download process.
* {bold}Insufficient storage space:{end} Your local device might not have enough storage space available to accommodate the model file size.

{h2}What can I do?{end}

1. {bold}Check your internet connection:{end} Ensure you have a stable internet connection and that there are no firewalls or network restrictions blocking the download.
2. {bold}Retry the download:{end} Sometimes, retrying the download can resolve temporary glitches.
3. {bold}Free up disk space:{end} Make sure your local device has sufficient storage space to store the downloaded model file. You might need to free up space by deleting unnecessary files or using an external storage device.
4. {bold}Contact Scalifi Ai support (if necessary):{end} If the issue persists after trying the above steps, consider contacting Scalifi Ai support for further assistance at {support_email}

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelVersionCreateException(ModelVersionException):
    default_message = """
{h1}
----ModelVersionCreateException-----------------------------------------------------------
{end}
An error occurred while creating a new variation or new version.

This error indicates that there was a problem when you attempted to create a new model variation or version within a specific model in the Model Catalog Service (MCS).

{h2}Possible causes of this error include:{end}

* {bold}Invalid inputs or formatting:{end} The data provided for creating the variation, such as its name, framework, or model file path, might contain errors or incorrect formatting.
* {bold}File path or access issues:{end} The model file might be inaccessible due to invalid paths, permissions, or storage problems.

{h2}What can I do?{end}

1. {bold}Review input details:{end} Double-check the information you provided for creating the variation, ensuring its accuracy and adherence to required formats. Pay close attention to variations in naming conventions, file paths, and framework compatibility.
2. {bold}Verify model file accessibility:{end} Ensure that the MCS can access the model file correctly. Check for valid file paths, permissions, storage availability, and potential network restrictions.
3. {bold}Consult documentation for restrictions:{end} Refer to the MCS documentation to understand any limitations regarding variation creation within model versions or specific model settings.
4. {bold}Retry the creation process:{end} Sometimes, temporary glitches can be resolved by retrying the creation.
5. {bold}Contact Scalifi Ai support:{end} If the issue persists, reach out to Scalifi Ai support for further guidance and assistance at {support_email}

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelVersionTagAttachException(ModelVersionException):
    default_message = """
{h1}
----ModelVersionTagAttachException---------------------------------------------------------
{end}
An error occurred while attaching tags to the model variation.

This error indicates that there was a problem adding tags to the specified model variation within the Model Catalog Service (MCS). Model variations can have tags associated with them for better organization and searchability.

{h2}Possible causes of this error include:{end}

* {bold}Invalid tag format or data type:{end} The tags you're trying to attach might be in an unsupported format or contain invalid data types not allowed for tags within MCS.

{h2}What can I do?{end}

1. {bold}Verify tag format and data type:{end} Ensure the tags you're attaching adhere to the supported format and data types allowed for MCS tags. Refer to the library documentation or MCS documentation for specific guidelines.
2. {bold}Retry the attachment process:{end} Sometimes, temporary glitches can be resolved by retrying the tag attachment.
3. {bold}Manage tags through the Scalifi Ai platform:{end} You can also manage tags directly on model variations within the Scalifi Ai platform's user interface. This alternative approach provides a user-friendly interface for attaching and editing tags.

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelVersionTagRemoveException(ModelVersionException):
    default_message = """
{h1}
----ModelVersionTagRemoveException---------------------------------------------------------
{end}
An error occurred while removing tags from the model variation.

This error indicates that there was a problem detaching tags from the specified model variation within the Model Catalog Service (MCS). Model variations can have tags associated with them for better organization and searchability.

{h2}Possible causes of this error include:{end}

* {bold}Invalid tag name or reference:{end} The tag names you're trying to remove might be misspelled, non-existent, or using an incorrect reference format.

{h2}What can I do?{end}

1. {bold}Verify tag names or references:{end} Double-check the spelling and accuracy of the tag names or references you're using for removal. Ensure they match existing tags associated with the variation.
2. {bold}Retry the removal process:{end} Sometimes, temporary glitches can be resolved by retrying the tag removal.
3. {bold}Manage tags through the Scalifi Ai platform:{end} You can also manage tags directly on model variations within the Scalifi Ai platform's user interface. This alternative approach provides a user-friendly interface for viewing and removing tags associated with the variation.

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelVersionDeleteException(ModelVersionException):
    default_message = """
{h1}
----ModelVersionDeleteException-------------------------------------------------------------
{end}
An error occurred while deleting the model variation.

This error indicates that there was a problem when you attempted to delete a specific variation of a model version within the Model Catalog Service (MCS). Models can have multiple versions, and each version can have variations. This exception is raised specifically when deleting a variation.

{h2}Possible causes of this error include:{end}

* {bold}Non-existent variation:{end} The variation you're trying to delete might not exist in the first place.
* {bold}Dependency issues:{end} The variation you're referencing might be used by other resources or models within MCS, preventing its deletion.

{h2}What can I do?{end}

1. {bold}Verify variation name:{end} Double-check the name or reference you're using to ensure it accurately identifies the target variation for deletion.
2. {bold}Review dependencies:{end} Consider if the variation is being used by other models or workflows within MCS. You might need to address these dependencies before deletion is possible.
3. {bold}Contact Scalifi Ai support (if necessary):{end} If the issue persists after trying the above steps, consider contacting Scalifi Ai support for further assistance at {support_email}

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelVersionInstanceDeletedException(InstanceDeletedException):
    default_message = """
{h1}
----ModelVersionInstanceDeletedException----------------------------------------------------
{end}
Attempted access of a deleted model variation instance.

This error indicates that you tried to access a variable associated with a model variation instance that has already been deleted. This exception helps prevent the use of stale information and variables within your code.

{bold}Context:{end}

- In the Model Catalog Service (MCS), models can have versions, and each version can have variations.
- You might create a variable referencing a specific model variation instance within your code using the MCS library.
- If the underlying model variation instance is subsequently deleted in MCS, this error is raised when you attempt to access the variable again.

{h2}What can I do?{end}

1. {bold}Handle the exception:{end}  Your code should handle this exception to gracefully recover from the situation. You can:
    - Check for the existence of the instance before accessing its associated variable.
    - Implement logic to refresh or retrieve a new instance if necessary.
2. {bold}Review instance management:{end} Consider how model variation instances are managed in your workflow. If instances are frequently deleted, you might need to adjust your code to handle potential deletions and retrieve new instances as needed.

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
        "complete_metadata_upload",
        "add_metadata",
        "list_metadata",
        "update_metadata",
        "delete_metadata",
        "attach_tags",
        "list_tags",
        "remove_tag",
        "remove_all_tags",
        "generate_metadata_download_url",
        "generate_metadata_preview_url",
    ]:
        if response.status_code == 404:
            raise ModelVersionNotFoundException()

    if error_code != None and type(error_code) == dict and len(error_code) != 0:

        error_code_key = error_code.get("status", None)

        if action == "complete_metadata_upload":
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
                raise ModelVersionTagAttachException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise ModelVersionTagAttachException(internal_data=internal_data)

                raise ModelVersionTagAttachException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "remove_tag":

            if error_code_key != None and data.get("detail", None):
                raise ModelVersionTagRemoveException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise ModelVersionTagRemoveException(internal_data=internal_data)

                raise ModelVersionTagRemoveException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "remove_all_tags":

            if error_code_key != None and data.get("detail", None):
                raise ModelVersionTagRemoveException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            elif error_code_key == None and len(error_code.keys()) != 0:

                data_string = ""
                for key, value in data.items():
                    if key == "error_code":
                        continue
                    data_string += f"Field: {key} || Error: {value}\n"

                if len(data_string) == 0:
                    raise ModelVersionTagRemoveException(internal_data=internal_data)

                raise ModelVersionTagRemoveException(
                    extra_info=data_string, internal_data=internal_data
                )
        elif action == "DELETE":

            if error_code_key != None and data.get("detail", None):
                raise ModelVersionDeleteException(
                    extra_info=data["detail"], internal_data=internal_data
                )

            if error_code_key == None and len(error_code.keys()) != 0:

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
