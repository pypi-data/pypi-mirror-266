from scalifiai.exceptions import (
    GeneralException,
    BackendNotAvailableException,
    InstanceDeletedException,
    raise_general_exception,
)


class MetadataException(GeneralException):
    default_message = """
{h1}
----MetadataException----------------------------------------------------------------------
{end}
An error occurred while working with model or model variation metadata.

This error indicates a problem encountered when interacting with metadata associated with models or model variations within the library. Metadata allows for attaching additional information to these models, providing context and facilitating management.

{bold}Types of metadata:{end}

The library supports two primary types of metadata:

* {bold}Simple metadata:{end} Comprises basic data types like strings, floats, and integers. This is suitable for capturing key-value information related to the model or variation.
* {bold}Storage metadata:{end} Enables attaching files or other data structures to the model or variation. This can be useful for storing additional resources, configuration files, or supplementary data relevant to the model.

{bold}Understanding this exception:{end}

This exception serves as the base class for more specific errors related to metadata operations. Child exception classes will provide more details about the exact issue encountered.

{h2}What can I do?{end}

1. {bold}Review specific error message:{end} The accompanying error message (if available) should provide further details about the cause of the exception. Look for child exception class information or specific error codes.
2. {bold}Consult library documentation:{end} Refer to the library documentation for guidance on working with model and model variation metadata. This documentation should explain supported data types, usage guidelines, and potential limitations.
3. {bold}Contact Scalifi Ai support (if necessary):{end} For complex issues or if the provided information isn't sufficient, consider contacting Scalifi Ai support for further assistance specific to your metadata operation at {support_email}

{correct}Need more help?{end}-> {docs_url_base}
"""


class MetadataNotFoundException(MetadataException):
    default_message = """
{h1}
----MetadataNotFoundException------------------------------------------------------------------
{end}
The requested model or model variation metadata cannot be found.

This error indicates that the specific piece of metadata you're trying to access for a model or model variation is unavailable. There are two main reasons why this might occur:

* {bold}Non-existent metadata:{end} The metadata you're referencing might not have been added to the model or variation in the first place.
* {bold}Deleted metadata:{end} If the metadata previously existed, it's possible that it was intentionally deleted.

{bold}Understanding metadata:{end}

The library allows attaching additional information to models and model variations using metadata. This metadata can be either simple (basic data types) or storage-based (files or other data structures).

{h2}What can I do?{end}

1. {bold}Verify metadata key:{end} Double-check the key or identifier you're using to reference the specific piece of metadata. Ensure you're using the correct key associated with the model or variation.
2. {bold}Review model or variation information:{end} Confirm that the model or model variation you're working with actually has the metadata you're expecting. It's possible the metadata was never added.
3. {bold}Consult library documentation:{end} Refer to the library documentation for details on how to access and manage model and model variation metadata.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MetadataInvalidSimpleValueException(MetadataException):
    default_message = """
{h1}
----MetadataInvalidSimpleValueException--------------------------------------------------------
{end}
The provided value for simple metadata is invalid.

This error indicates that the value you're trying to add as simple metadata for a model or model variation is not supported. Simple metadata allows attaching basic data types like strings (str), floats, or integers (int) to models or variations for contextual information.

{bold}Supported data types:{end}

The library only accepts the following data types for simple metadata:

* String (str)
* Float (float)
* Integer (int)

{bold}Understanding the error:{end}

This exception is raised when you attempt to set a metadata value using a data type other than these supported types. For example, trying to add a list, dictionary, or custom object would trigger this error.

{h2}What can I do?{end}

1. {bold}Verify data type:{end} Ensure the value you're trying to set as metadata is of type string, float, or integer. Use the `type(your_value).__name__` function to confirm the data type of your value.
2. {bold}Convert data if possible:{end} If your data can be reasonably converted to one of the supported types (e.g., converting a boolean to an integer), consider performing the conversion before setting the metadata.
3. {bold}Consider storage metadata:{end} If your data is more complex and cannot be converted to a simple type, explore using storage metadata instead. Storage metadata allows attaching files or other data structures to models or variations.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MetadataAlreadyExistsException(MetadataException):
    default_message = """
{h1}
----MetadataAlreadyExistsException------------------------------------------------------------
{end}
The metadata you're attempting to add already exists.

This error indicates that you're trying to create metadata for a model or model variation with a key that is already in use. Metadata keys serve as unique identifiers for accessing associated values.

{bold}Understanding metadata keys:{end}

- Metadata keys allow you to organize and retrieve specific pieces of information attached to models or variations.
- Each key must be unique within a model or variation to prevent conflicts and ensure clarity in data management.

{h2}What can you do?{end}

1. {bold}Choose a unique key:{end} Use a different key to store the new metadata. Ensure the key is not already in use within that model or variation.
2. {bold}Review existing metadata:{end} If you're unsure of existing keys, inspect the currently associated metadata for the model or variation to identify available keys.
3. {bold}Consider updating metadata:{end} If you intended to replace the existing value with a new one, explicitly update the existing metadata using its key, rather than trying to create a new one with the same key.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MetadataUploadException(MetadataException):
    default_message = """
{h1}
----MetadataUploadException------------------------------------------------------------------
{end}
An error occurred while uploading storage metadata for a model or model variation.

This error indicates that the library encountered an issue during the upload process when you attempted to add storage metadata to a model or model variation. Storage metadata allows attaching files or other data structures to provide additional resources or information.

{bold}Potential causes of upload failure:{end}

- {bold}Network issues:{end} Problems with your internet connection or network stability might hinder the upload process.
- {bold}File size limitations:{end} The library might have restrictions on the maximum size of files allowed for storage metadata.
- {bold}Server-side errors:{end} In rare cases, temporary issues on the server side could prevent successful uploads.

{h2}What can I do?{end}

1. {bold}Check internet connection:{end} Ensure you have a stable network connection to facilitate the upload.
2. {bold}Verify file size:{end} If you're uploading a large file, consult the library documentation to confirm supported file size limitations for storage metadata.
3. {bold}Retry upload:{end} Try uploading the storage metadata again. Sometimes, network hiccups can cause temporary failures.
4. {bold}Contact Scalifi Ai support (if necessary):{end} If the upload consistently fails and the previous steps don't resolve the issue, consider contacting Scalifi Ai support for further assistance at {support_email}. They can help investigate potential server-side issues or provide alternative solutions.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MetadataCreateException(MetadataException):
    default_message = """
{h1}
----MetadataCreateException------------------------------------------------------------------
{end}
An error occurred while creating metadata for a model or model variation.

This error indicates that the library encountered an issue during the creation process when you attempted to add metadata to a model or model variation. Metadata allows attaching additional information to these models, providing context and facilitating management.

{bold}Understanding metadata creation:**

The library offers functionalities to add metadata to models and variations. This metadata can be either simple (basic data types) or storage-based (files or other data structures).

{bold}Potential causes of creation failure:{end}

- {bold}Library restrictions:{end} In certain scenarios, the library might have restrictions on metadata creation based on model type, variation status, or other factors.
- {bold}Server-side errors:{end} Occasionally, temporary issues on the server side could prevent successful metadata creation.

{h2}What can I do?{end}

1. {bold}Review library documentation:{end} Refer to the library documentation for any potential limitations or restrictions on metadata creation that might apply in your situation.
2. {bold}Retry creation:{end} Try creating the metadata again. Sometimes, temporary issues can cause unexpected failures.
3. {bold}Contact Scalifi Ai support (if necessary):{end} If the issue persists after following these steps, consider contacting Scalifi Ai support for further assistance at {support_email}. They can investigate potential server-side issues or guide you on alternative approaches if restrictions prevent creation.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MetadataUpdateException(MetadataException):
    default_message = """
{h1}
----MetadataUpdateException---------------------------------------------------------------------
{end}
The attempt to update metadata has failed.

This error indicates that the library was unable to successfully process the metadata modification you requested. Metadata is used to store additional information about models or model variations, such as accuracy scores, model versions, or descriptive tags.

{bold}Potential causes:{end}

- {bold}Invalid metadata values:{end} Attempting to update metadata with invalid data types or exceeding allowed limits might trigger this error.
- {bold}Backend service errors:{end} Transient issues on the Scalifi Ai backend service itself can occasionally lead to temporary update failures.

{h2}What can I do?{end}

1. {bold}Retry the operation:{end} Sometimes, transient server-side errors can cause sporadic failures. Trying the update again might succeed.
2. {bold}Review metadata values:{end} Carefully inspect any values you're attempting to update for validity and compatibility with expected data types and size restrictions.
3. {bold}Contact Scalifi Ai support (if necessary):{end} If the update consistently fails or you're encountering persistent issues, consider contacting Scalifi Ai support for further assistance at {support_email}. They can investigate potential backend problems or provide guidance on specific metadata operations.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MetadataDeleteException(MetadataException):
    default_message = """
{h1}
----MetadataDeleteException--------------------------------------------------------------------
{end}
The attempt to delete metadata has failed.

This error indicates that the library was unable to successfully remove the specified metadata from the model or model variation. Metadata provides additional information about models, such as accuracy scores, model versions, or descriptive tags.

{bold}Potential causes:{end}

- {bold}Network connectivity issues:{end} Disruptions in your internet connection can prevent communication with the Scalifi Ai backend service, hindering metadata deletion.
- {bold}Backend service errors:{end} Temporary problems on the Scalifi Ai backend service itself can occasionally cause deletion failures.
- {bold}Storage metadata dependencies:{end} Deleting storage metadata (files or data structures) might have additional dependencies or constraints.

{h2}What can I do?{end}

1. {bold}Check internet connection:{end} Ensure a stable internet connection to communicate with the backend service.
2. {bold}Retry the operation:{end} Temporary server-side issues might resolve themselves on a retry.
3. {bold}Contact Scalifi Ai support (if necessary):{end} Seek assistance from Scalifi Ai support({support_email}) for persistent issues or if you suspect backend problems.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MetadataGenerateDownloadURLException(MetadataException):
    default_message = """
{h1}
----MetadataGenerateDownloadURLException-------------------------------------------------------
{end}
An error occurred while attempting to generate a download URL for storage metadata.

This error indicates that the library encountered an issue when trying to create a downloadable link for storage metadata associated with a model or model variation. Storage metadata enables attaching files or other data structures to models or variations.

{bold}Understanding download URLs:{end}

The library typically provides functionality to generate temporary download URLs for accessing storage metadata. These URLs grant temporary permission to download the attached files or data structures.

{bold}Potential causes of this error:{end}

- {bold}Network connectivity issues:{end} Interruptions in your internet connection might prevent communication with the Scalifi Ai backend service, hindering URL generation.
- {bold}Invalid metadata type:{end} Attempting to generate a download URL for metadata that isn't of the storage type might trigger this error.

{h2}What can I do?{end}

1. {bold}Check internet connection:{end} Ensure a stable internet connection to communicate with the backend service.
2. {bold}Retry the operation:{end} Temporary server-side issues might resolve themselves on a retry.
3. {bold}Verify metadata type:{end} Confirm you're requesting a download URL for a valid storage metadata key (associated with a file or data structure).
4. {bold}Contact Scalifi Ai support (if necessary):{end} Seek assistance from Scalifi Ai support({support_email}) for persistent issues or if you suspect backend problems.

{bold}Alternative approach: Scalifi Ai platform{end}

For a user-friendly experience and broader management options, consider the Scalifi Ai platform accessible through any web browser. The platform provides functionalities to directly generate download URLs and manage all aspects of your storage metadata associated with models and variations.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MetadataGeneratePreviewURLException(MetadataException):
    default_message = """
{h1}
----MetadataGeneratePreviewURLException--------------------------------------------------------
{end}
An error occurred while attempting to generate a preview URL for storage metadata.

This error indicates that the library encountered an issue when trying to create a previewable link for storage metadata associated with a model or model variation. Storage metadata enables attaching files or other data structures to models or variations.

{bold}Understanding preview URLs:{end}

The library typically provides functionality to generate temporary preview URLs for viewing storage metadata content directly in a web browser without full download. These URLs grant read-only access for convenient previewing.

{bold}Potential causes of this error:{end}

- {bold}Network connectivity issues:{end} Interruptions in your internet connection might prevent communication with the Scalifi Ai backend service, hindering URL generation.
- {bold}File format compatibility:{end} Previewing might not be supported for all file types or formats.
- {bold}Invalid metadata type:{end} Attempting to generate a preview URL for metadata that isn't of the storage type might trigger this error.

{h2}What can I do?{end}

1. {bold}Check internet connection:{end} Ensure a stable internet connection to communicate with the backend service.
2. {bold}Retry the operation:{end} Temporary server-side issues might resolve themselves on a retry.
3. {bold}Verify metadata type:{end} Confirm you're requesting a preview URL for a valid storage metadata key (associated with a file or data structure supported for previewing).
4. {bold}Consider file format compatibility:{end} If the file type is not typically previewable (e.g., raw data), consider downloading instead.
5. {bold}Contact Scalifi Ai support (if necessary):{end} Seek assistance from Scalifi Ai support({support_email}) for persistent issues or if you suspect backend problems.

{bold}Alternative approach: Scalifi Ai platform{end}

For a user-friendly experience and broader management options, consider the Scalifi Ai platform accessible through any web browser. The platform often provides built-in previewing capabilities for supported storage metadata types, eliminating the need for manual URL generation.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MetadataInstanceDeletedException(InstanceDeletedException):
    default_message = """
{h1}
----MetadataInstanceDeletedException---------------------------------------------------------
{end}
The metadata instance you're referencing has been deleted.

This error indicates that you're trying to access a variable associated with a metadata instance that has already been deleted. This prevents your code from relying on potentially outdated or invalid information.

{bold}Understanding metadata instances:{end}

The library might create and manage metadata instances internally. These instances represent the metadata attached to a specific model or model variation at a particular point in time.

{bold}Why this error occurs:{end}

This exception is raised to discourage the use of stale information. If the underlying metadata instance has been deleted, the associated variables likely no longer hold accurate data.

{bold}Avoiding this error:{end}

1. {bold}Refresh metadata:{end} Before accessing metadata, consider retrieving a fresh instance using the library's functionalities. This ensures you're working with the latest metadata information.
2. {bold}Handle potential deletions:{end} If your code involves long-running operations or relies on metadata for extended periods, implement mechanisms to handle potential deletions. This might involve periodically refreshing the metadata instance or checking for its validity before use.

{correct}Need more help?{end}-> {docs_url_base}
"""


# ---------------------------------------------------------------------------------------------


class MetadataProxyDictException(GeneralException):
    default_message = """
{h1}
----MetadataProxyDictException----------------------------------------------------------------
{end}
An error occurred while interacting with the metadata proxy dictionary.

This error indicates a problem encountered when working with the metadata dictionary interface provided by the library. This dictionary-like interface allows you to manage model or model variation metadata using familiar Python dictionary syntax (e.g., `model_1.metadata["accuracy"] = 91`).

{bold}Understanding the metadata proxy dictionary:{end}

The library offers a convenient way to access and manipulate metadata through a proxy dictionary. This dictionary provides methods and syntax similar to regular Python dictionaries for a more intuitive user experience.

{bold}Potential causes of this error:{end}

While the specific cause can vary depending on the underlying issue, this exception might be triggered by:

* {bold}Invalid operations:{end} Attempting unsupported operations on the metadata proxy dictionary, such as using methods not intended for this context.
* {bold}Data type issues:{end} Assigning incompatible data types to metadata keys. Remember that metadata supports basic data types (strings, floats, integers) for simple metadata and files/data structures for storage metadata.
* {bold}Internal errors:{end} In rare cases, the library might encounter internal issues while processing operations on the metadata proxy dictionary.

{h2}What can I do?{end}

1. {bold}Review supported operations:{end} Refer to the library documentation to understand the valid operations and usage patterns for the metadata proxy dictionary.
2. {bold}Verify data types:{end} Ensure you're assigning data types compatible with the expected metadata types (simple or storage).
3. {bold}Consult library documentation:{end} The library documentation should provide guidance on using the metadata proxy dictionary effectively. Refer to it for detailed explanations and examples.
4. {bold}Retry operation:{end} If the error appears sporadic, try repeating the operation with the metadata proxy dictionary. Sometimes, temporary issues can cause unexpected failures.
5. {bold}Contact Scalifi Ai support (if necessary):{end} For complex issues or if the error persists, consider contacting Scalifi Ai support for further assistance at {support_email}. They can investigate potential internal errors or provide alternative solutions.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MetadataProxyDictInvalidOperationValueException(MetadataProxyDictException):
    default_message = """
{h1}
----MetadataProxyDictInvalidOperationValueException-------------------------------------------
{end}
The provided value is invalid for the attempted operation on the metadata proxy dictionary.

This error indicates that the value you're trying to assign or use with the metadata proxy dictionary is incompatible with the operation you're performing. The metadata proxy dictionary allows managing metadata using Python dictionary syntax, but it has limitations on data types and operations.

{bold}Understanding metadata operations:{end}

While the metadata proxy dictionary resembles regular Python dictionaries, it serves a specific purpose. It's designed for managing model or model variation metadata, which has specific data type requirements.

{bold}Supported data types:{end}

The library supports two primary types of metadata:

* {bold}Simple metadata:{end} Compatible with basic data types like strings (str), floats (float), and integers (int).
* {bold}Storage metadata:{end} Enables attaching files or other data structures to the model or variation.

{bold}Common causes of this error:{end}

This exception might be raised in scenarios like:

* {bold}Assigning unsupported data types:{end} Trying to set values like lists, dictionaries, or custom objects as metadata, which are not supported for simple metadata.
* {bold}Using inappropriate values for operations:{end} Attempting operations on the metadata proxy dictionary that are not intended for this context, such as using methods meant for regular dictionaries.

{h2}What can I do?{end}

1. {bold}Verify data type:{end} Ensure the value you're using is compatible with the intended operation. Refer to the supported data types for simple and storage metadata.
2. {bold}Consider alternative approaches:{end} If your data is complex and cannot be converted to a supported type, explore using storage metadata for attaching files or data structures.
3. {bold}Review supported operations:{end} Consult the library documentation to understand the valid operations and usage patterns for the metadata proxy dictionary.
4. {bold}Manage metadata through Scalifi Ai platform:{end} For advanced management or limitations with the proxy dictionary, visit the Scalifi Ai platform through any web browser to directly manage your model and variation metadata.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MetadataProxyDictFindInvalidResponseException(MetadataProxyDictException):
    default_message = """
{h1}
----MetadataProxyDictFindInvalidResponseException-------------------------------------------
{end}
An unexpected response was received while attempting to retrieve metadata using the proxy dictionary.

This error indicates that the library encountered an issue when trying to fetch specific metadata using the dictionary-like interface. The metadata proxy dictionary allows accessing model or model variation metadata with familiar Python syntax (e.g., `accuracy = model_1.metadata["accuracy"]`).

{bold}Understanding the error:{end}

In normal operation, the library interacts with the backend service to retrieve the requested metadata. However, in this case, the response received from the service was invalid or incompatible, preventing successful retrieval.

{bold}Potential causes:{end}

- {bold}Temporary server issues:{end} Occasional hiccups on the server side might result in unexpected responses.
- {bold}Library bugs (rare):{end} In rare cases, the library itself might encounter issues when processing the response.

{h2}What can I do?{end}

1. {bold}Retry the operation:{end} Sometimes, temporary issues can cause unexpected responses. Try retrieving the metadata again using the proxy dictionary.
2. {bold}Review your code:{end} Ensure you're using the correct key to access the desired metadata within the model or variation.
3. {bold}Contact Scalifi Ai support (if necessary):{end} If the issue persists after retrying, consider contacting Scalifi Ai support for further assistance at {support_email}. They can investigate potential server-side issues or library bugs, and provide guidance on troubleshooting further.

{bold}Alternative approach: Scalifi Ai platform:{end}

For more comprehensive metadata management or if you encounter issues retrieving metadata through the proxy dictionary, consider using the Scalifi Ai platform directly through any web browser. The platform provides a user-friendly interface to view and access metadata associated with your models and variations.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MetadataProxyDictInvalidOperationException(MetadataProxyDictException):
    default_message = """
{h1}
----MetadataProxyDictInvalidOperationException------------------------------------------------
{end}
An invalid operation was attempted on the metadata proxy dictionary.

This error indicates that you're trying to perform an operation that is not supported by the metadata proxy dictionary. While this dictionary-like interface allows managing metadata using familiar Python syntax, it has limitations to ensure consistency and integrity with the underlying metadata system.

{bold}Understanding supported operations:{end}

- {bold}Creating or updating metadata:{end} Use direct assignment like `model_1.metadata["accuracy"] = 91`.
- {bold}Retrieving metadata:{end} Access values using their keys like `accuracy = model_1.metadata["accuracy"]`.

{bold}Unsupported operations:{end}

- {bold}Iterating over keys/values:{end} Methods like `.items()`, `.popitems()`, or `.keys()` are not supported.
- {bold}Direct structural modifications:{end} Attempting to add or remove keys directly using dictionary methods is not supported.

{bold}Alternative approaches:{end}

1. {bold}Model/Variation methods:{end} For more flexibility and control, use the specific methods provided on model or model variation instances for metadata management:
   - `.list_metadata()` to enumerate existing metadata.
   - `.add_metadata_simple()` to create simple metadata.
   - `.add_metadata_storage()` to create storage metadata.
   - `.delete_metadata()` to delete metadata.
2. {bold}Scalifi Ai platform:{end} For a user-friendly interface and advanced metadata management, access the Scalifi Ai platform through any web browser. It provides comprehensive tools for viewing, editing, and managing metadata associated with your models and variations.

{h2}What can I do?{end}

1. {bold}Review supported operations:{end} Consult the library documentation to understand the valid operations permitted within the metadata proxy dictionary.
2. {bold}Utilize explicit methods:{end} Use the model or variation instance methods for more control over metadata management.
3. {bold}Explore Scalifi Ai platform:{end} For a broader range of metadata management options, consider using the Scalifi Ai platform directly.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MetadataProxyDictInvalidValueException(MetadataProxyDictException):
    default_message = """
{h1}
----MetadataProxyDictInvalidValueException-------------------------------------------------
{end}
The provided value is invalid for the attempted operation on the metadata proxy dictionary.

This error indicates that you're trying to use the dictionary notation with an unsupported data type for metadata. The metadata proxy dictionary allows managing simple metadata using familiar Python syntax, but it has limitations regarding complex data types.

{bold}Understanding metadata types:{end}

The library supports two primary metadata types:

* {bold}Simple metadata:{end} Compatible with basic data types like strings (str), floats (float), and integers (int). This type is suitable for storing values like accuracy scores or model versions.
* {bold}Storage metadata:{end} Enables attaching files or other data structures to the model or variation. This type is ideal for storing larger or more complex information like configuration files or model artifacts.

{bold}Common cause of this error:{end}

This exception might be raised when you attempt to:

- {bold}Display or update storage metadata using dictionary notation:{end} The metadata proxy dictionary is not designed to directly display or manipulate complex data structures like files associated with storage metadata.

{bold}Alternative approaches:{end}

1. {bold}Model/Variation methods:{end} For managing storage metadata, use the dedicated methods provided on model or model variation instances:
   - `.list_metadata()` to list existing metadata, including storage types.
   - `.add_metadata_storage()` to attach files or data structures as storage metadata.
   - `.update_metadata()` (if supported type) to update existing metadata (check library documentation).
   - `.delete_metadata()` to delete metadata.
2. {bold}Scalifi Ai platform:{end} For a user-friendly interface and advanced metadata management, access the Scalifi Ai platform through any web browser. It provides tools for viewing, editing, and managing all metadata types associated with your models and variations.

{h2}What can I do?{end}

1. {bold}Review metadata types:{end} Ensure you're using the correct metadata type (simple or storage) for your data. Simple types are suitable for the dictionary notation, while storage types require dedicated methods.
2. {bold}Utilize explicit methods:{end} Use the appropriate model or variation methods for adding, updating, or deleting storage metadata.
3. {bold}Explore Scalifi Ai platform:{end} Consider the Scalifi Ai platform for a comprehensive solution to manage all your model and variation metadata needs.

{correct}Need more help?{end}-> {docs_url_base}
"""


# ---------------------------------------------------------------------------------------------


def raise_custom_exception(*, response=None, action=None, internal_data=None):

    data, error_code = raise_general_exception(
        response=response, internal_data=internal_data
    )

    if action == None:
        raise Exception("No action value provided")

    if action in ["RETRIEVE"]:
        if response.status_code == 404:
            raise MetadataNotFoundException()

    if action == "S3_UPLOAD":
        raise MetadataUploadException()

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
