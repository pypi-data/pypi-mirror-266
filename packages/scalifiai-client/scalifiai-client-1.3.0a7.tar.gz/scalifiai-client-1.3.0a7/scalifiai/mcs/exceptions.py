from scalifiai.exceptions import GeneralException


class MCSSubModuleTagsProxyDictException(GeneralException):
    default_message = """
{h1}
----MCSSubModuleTagsProxyDictException---------------------------------------------------------
{end}
An error occurred while using the tags proxy dictionary.

This error indicates an issue occurred while interacting with the tags attached to a model / model variation using the dictionary-like interface provided by our library (e.g., `model_1.tags["tag_1"] = "value_1"`). The specific cause might vary depending on the nature of the problem.

{h2}What can I do?{end}

1. {bold}Review the error message:{end} Sometimes, the error message might contain details about the specific reason for the failure. This information can help you diagnose the problem further.
2. {bold}Verify tag key and value:{end} Ensure the tag key (e.g., `"tag_1"`) is valid and the value you're assigning adheres to the supported data types for tags in the MCS.
3. {bold}Check for unsupported operations:{end} The tags proxy dictionary is intended for basic tag manipulation (e.g., get, set, delete). If you're attempting unsupported operations like iterating through all tags using dictionary methods, consider using the recommended methods provided by the library for those tasks.
4. {bold}Refer to library documentation:{end} Our library documentation has a dedicated section explaining the tags proxy dictionary and its supported operations. Refer to this documentation for detailed usage guidelines.

{correct}Need more help?{end}-> Contact Scalifi Ai support: {support_email}
"""


class MCSSubModuleTagsProxyDictInvalidOperationValueException(
    MCSSubModuleTagsProxyDictException
):
    default_message = """
{h1}
----MCSSubModuleTagsProxyDictInvalidOperationValueException----------------------------------
{end}
An error occurred due to an invalid value in the tags proxy dictionary.

This error indicates that you attempted to use an unsupported data type or invalid value while interacting with the tags attached to a model / model variation using the dictionary-like interface (e.g., `model_1.tags["tag_1"] = "value_1"`).

* {bold}Common causes:{end}
    * Assigning data types like lists, dictionaries, or custom objects as tag values.
    * Using unsupported characters or exceeding character limits for tags or values.

{h2}What can I do?{end}

1. {bold}Verify tag value:{end} Ensure the value you're assigning to a tag is a basic data type supported by the MCS for tags (e.g., strings, numbers, booleans).
2. {bold}Review tag validation rules:{end} Refer to the Scalifi Ai documentation or our library documentation for any specific rules or limitations regarding tag values in the MCS.
3. {bold}Use appropriate methods:{end} If you require storing complex data structures associated with models, consider using recommended methods provided by the library that are designed for that purpose (e.g., .attach_tags()).
4. {bold}Manage tags through the Scalifi Ai platform:{end} You can also manage tags directly on models within the Scalifi Ai platform user interface. This alternative approach might allow for validations or data entry methods that are not available through the library's dictionary proxy.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MCSSubModuleTagsProxyDictInvalidOperationException(
    MCSSubModuleTagsProxyDictException
):
    default_message = """
{h1}
----MCSSubModuleTagsProxyDictInvalidOperationException---------------------------------------
{end}
An error occurred due to an unsupported operation on the tags proxy dictionary.

This error indicates that you attempted to perform an operation on the tags attached to a model / model variation using the dictionary-like interface (e.g., `model_1.tags["tag_1"] = "value_1"`) that is not supported by the proxy dictionary.

* {bold}Unsupported operations:{end}
    * Methods like `.items()`, `.keys()`, `.values()`, or `.popitems()` are not designed for retrieving all tags at once.
    * Other dictionary methods that might modify the entire dictionary structure are also not supported.

{h2}What can I do?{end}

1. {bold}Iterate through tags individually:{end} If you require processing individual tags, you can iterate through them using a loop and accessing them by key (e.g., `for tag_name, value in model_1.tags: ...`).
2. {bold}Use recommended methods:{end} The library likely provides dedicated methods for retrieving or manipulating all tags associated with a model / model variation. Refer to the library documentation for these methods (e.g., `.list_tags()`, `.attach_tags()`, `.remove_tag()`). These methods offer a safer and more efficient way to interact with tags.
3. {bold}Manage tags through the Scalifi Ai platform:{end} You can also manage tags directly on models within the Scalifi Ai platform's user interface.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MCSSubModuleTagsProxyDictNotFoundException(MCSSubModuleTagsProxyDictException):
    default_message = """
{h1}
----MCSSubModuleTagsProxyDictNotFoundException------------------------------------------------
{end}
The tag you requested is not found on the model / model variation.

This error indicates that you tried to access a tag using a key (e.g., `model_1.tags["tag_1"]`) that does not exist within the tags associated with the model / model variation. There are a few reasons why this might happen:

* {bold}Non-existent tag:{end} The specific tag key you used might not have been assigned to the model / model variation in the first place.
* {bold}Typo in key:{end} It's also possible that there's a typo in the tag key you're using. Double-check the spelling for accuracy.

{h2}What can I do?{end}

1. {bold}Verify tag key:{end} Ensure the tag key you're using is correct and matches an existing tag assigned to the model / model variation.
2. {bold}List available tags:{end} If you're unsure about the exact tag keys, consider using recommended methods provided by the library to retrieve all tags associated with the model / model variation (e.g., `.list_tags()`). This can help you verify available tags and their spellings.
3. {bold}Manage tags through the Scalifi Ai platform:{end} You can also manage tags directly on models within the Scalifi Ai platform's user interface. This alternative approach provides a visual representation of the model / model variation tags allowing searching for specific tags.

{correct}Need more help?{end}-> {docs_url_base}
"""


class MCSSubModuleTagsProxyDictMultipleTagsDeleteExceptionException(
    MCSSubModuleTagsProxyDictException
):
    default_message = """
{h1}
----MCSSubModuleTagsProxyDictMultipleTagsDeleteExceptionException---------------------------
{end}
Deleting a tag using dictionary notation is not possible when multiple tags share the same key.

This error indicates that you attempted to delete a tag using its key within the model / model variation tags dictionary (e.g., `del model_1.tags["tag_1"]`) but the MCS identified that multiple tags exist with the same key. The library's dictionary proxy cannot perform this deletion using dictionary notation due to this ambiguity.

{h2}What can I do?{end}

1. {bold}Use recommended methods:{end} The library likely provides dedicated methods for deleting tags associated with a model / model variation. Refer to the library documentation for methods like `.remove_tag()` (to remove a specific tag by ID) or `.remove_all_tags()` (to remove all tags associated with the instance). These methods offer more control and handle scenarios with multiple tags under the same key.
2. {bold}List available tags:{end} Consider using methods like `.list_tags()` to retrieve all tags associated with the model / model variation. This can help you identify the specific tags you want to delete and their corresponding keys for targeted deletion using the recommended methods.
3. {bold}Manage tags through the Scalifi Ai platform:{end} You can also manage tags directly on models within the Scalifi Ai platform's user interface. This alternative approach might provide a clearer view of existing tags with the same key and allow for selecting specific tags for deletion.

{correct}Need more help?{end}-> {docs_url_base}
"""
