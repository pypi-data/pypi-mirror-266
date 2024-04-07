from scalifiai.exceptions import GeneralException

# TODO[VIMPORTANT] Instead of directly raising errors implement raise_custom_exceptions here also


class ModelFrameworkException(GeneralException):
    default_message = """
{h1}
----ModelFrameworkException----------------------------------------------------------------
{end}
An error occurred related to the model framework.

This error indicates a problem encountered while working with a specific model framework. The Model Catalog Service (MCS) supports various frameworks for managing models. This exception serves as the base class for more specific errors related to framework functionalities.

{bold}Common scenarios:{end}

* Registering a new model variation for a specific framework.
* Fetching a model and returning the model instance using a particular framework.

The exact cause might vary depending on the framework involved and the specific operation you're performing.

{h2}What can I do?{end}

1. {bold}Review framework documentation:{end} Refer to the documentation specific to the model framework you're using. This documentation might provide details on supported functionalities, limitations, and potential error scenarios.
2. {bold}Consult library documentation:{end} The library documentation might also offer troubleshooting steps or best practices related to framework usage within the library.
3. {bold}Contact Scalifi Ai support (if necessary):{end} For complex issues or if the provided information isn't sufficient, consider contacting Scalifi Ai support for further assistance at {support_email}

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelFrameworkNoModelException(ModelFrameworkException):
    default_message = """
{h1}
----ModelFrameworkNoModelException---------------------------------------------------------
{end}
A valid model framework key is required.

This error indicates that a required model framework key was missing when performing a model-specific operation. The Model Catalog Service (MCS) uses frameworks to represent different ways of deploying models.

This exception is raised in scenarios where a model framework key is expected but not provided.

{bold}Common examples:{end}

* Registering a new model variation: You might need to specify the framework key when registering a new variation for a specific model.
* Fetching a model instance: Depending on the library function, a framework key might be required to retrieve a model instance.

{h2}What can I do?{end}

1. {bold}Review function arguments:{end} Double-check the function or method you're using and ensure it includes the required model framework key as an argument.
2. {bold}Verify model information:{end} If registering a new variation, confirm you have the correct framework key associated with the model you're working with.
3. {bold}Consult library documentation:{end} Refer to the library documentation for details on specific function arguments and their expected values, including the model framework key.

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelFrameworkNotSupportedException(ModelFrameworkException):
    default_message = """
{h1}
----ModelFrameworkNotSupportedException-----------------------------------------------------
{end}
The provided model framework is not currently supported.

This error indicates that the model you're trying to use has a framework that is not yet supported by this library. The Model Catalog Service (MCS) supports various frameworks, but this library might have limitations in terms of compatible frameworks.

{h2}What can I do?{end}

1. {bold}Review supported frameworks:{end} Refer to the library documentation for a list of currently supported model frameworks. You might need to use a different model with a supported framework or wait for future library updates that might include additional framework support.
2. {bold}Consider alternatives:{end} Depending on your needs, you might be able to convert the model to a supported framework using external tools. However, converting frameworks might introduce compatibility issues or require additional expertise.
3. {bold}Contact Scalifi Ai support:{end} If you have a specific use case for an unsupported framework, consider contacting Scalifi Ai support to discuss potential solutions or workarounds at {support_email}

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelFrameworkNoKeyException(ModelFrameworkException):
    default_message = """
{h1}
----ModelFrameworkNoKeyException-----------------------------------------------------------
{end}
An invalid or missing model framework key was provided.

This error indicates that a problem occurred with the model framework key you provided when performing a model-specific operation. The Model Catalog Service (MCS) uses frameworks to represent different ways of managing models.

This exception is raised in two scenarios:

* {bold}Missing key:{end} You might have omitted the model framework key entirely when it was required for the operation.
* {bold}Invalid key:{end} The framework key you provided might be incorrect or not recognized by the library.

{h2}What can I do?{end}

1. {bold}Verify key presence:{end} Double-check that you've included the model framework key as an argument in the function or method you're using.
2. {bold}Review key format:{end} Ensure the provided framework key is formatted correctly according to the library's requirements. Refer to the documentation for specific key format guidelines.
3. {bold}Consult model information:{end} If registering a new variation, confirm you have the correct framework key associated with the model you're working with.

{correct}Need more help?{end}-> {docs_url_base}
"""


# ---------------------------------------------------------------------------------------------


class ModelWrapperException(GeneralException):
    default_message = """
{h1}
----ModelWrapperException-------------------------------------------------------------------
{end}
An error occurred within the model wrapper.

This error indicates a problem encountered while interacting with the model wrapper class within the library. This wrapper class serves as an intermediate layer for various supported Machine Learning (ML) frameworks. 

{bold}Understanding the model wrapper:{end}

The library provides a model wrapper class that simplifies interaction with different ML frameworks. This wrapper translates common operations across various frameworks, providing a consistent user experience.

{bold}Potential causes of this error:{end}

While the specific cause can vary depending on the underlying issue, this exception might be triggered by:

* Errors originating from specific framework implementations within the wrapper.
* Issues with model data or format incompatibilities.
* Unexpected behavior during model loading or execution.

{h2}What can I do?{end}

1. {bold}Review framework documentation:{end} If the error message provides clues about the specific framework involved, consult the documentation for that framework to understand potential error scenarios.
2. {bold}Verify model data:{end} Ensure your model data is formatted correctly and adheres to the expected format for the chosen framework.
3. {bold}Examine library documentation:{end} The library documentation might offer troubleshooting tips or best practices related to using the model wrapper class.
4. {bold}Inspect error message:{end} The specific error message accompanying this exception might provide more details about the underlying issue.
5. {bold}Contact Scalifi Ai support (if necessary):{end} For complex issues or if the provided information isn't sufficient, consider contacting Scalifi Ai support for further assistance at {support_email}

{correct}Need more help?{end}-> {docs_url_base}
"""


class ModelWrapperInvalidModelException(ModelWrapperException):
    default_message = """
{h1}
----ModelWrapperInvalidModelException------------------------------------------------------
{end}
The provided model is invalid and cannot be saved in the Model Catalog Service (MCS).

This error indicates that the model you're attempting to register using the model wrapper class has failed pre-registration checks. While the model's framework is supported, its structure or content does not meet the requirements for saving within MCS.

{bold}Potential causes:{end}

- {bold}Missing components:{end} The model might lack essential components or files for loading and execution.
- {bold}Incorrect formatting:{end} The model's structure or data might not adhere to the expected format for its framework.
- {bold}Compatibility issues:{end} Specific versions or configurations of the framework might not be compatible with MCS.
- {bold}Corrupted model:{end} The model itself might be corrupted or damaged.

{h2}What can I do?{end}

1. {bold}Review model integrity:{end} Ensure the model is complete and structurally sound. Verify its compatibility with the specified framework and MCS requirements.
2. {bold}Consult framework documentation:{end} Refer to the documentation for the model's framework to understand its structure, expected components, and formatting rules.
3. {bold}Check model saving guidelines:{end} The MCS documentation might provide specific guidelines or restrictions for supported model formats and frameworks.
4. {bold}Consider model conversion:{end} If feasible, explore converting the model to a more compatible format or version using external tools.
5. {bold}Contact Scalifi Ai support (if necessary):{end} If further assistance is required, provide details about the model framework, version, structure, and the specific error message to Scalifi Ai support for investigation at {support_email}

{correct}Need more help?{end}-> {docs_url_base}
"""


# ---------------------------------------------------------------------------------------------
