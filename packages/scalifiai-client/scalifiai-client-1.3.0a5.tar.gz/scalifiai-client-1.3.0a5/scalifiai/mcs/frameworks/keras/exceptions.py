from scalifiai.exceptions import GeneralException


class KerasModelWrapperException(GeneralException):
    default_message = """
{h1}
----KerasModelWrapperException---------------------------------------------------------------
{end}
An error occurred with the Keras model wrapper.

This error indicates a problem encountered while working with the Keras model wrapper class within the library. The wrapper class simplifies interaction specifically with Keras models.

{bold}Keras model wrapper:{end}

The library provides a wrapper class for Keras models to streamline their integration and usage within the framework. This wrapper translates common operations for Keras models, providing a consistent user experience.

{bold}Potential causes of this error:{end}

While the specific cause can vary depending on the underlying issue, this exception might be triggered by:

* Errors originating from specific Keras functionalities within the wrapper.
* Issues with Keras model structure or data format incompatibilities.
* Unexpected behavior during model loading, training, or prediction using the wrapper.

{h2}What can I do?{end}

1. {bold}Review Keras documentation:{end} If the error message provides clues about the specific Keras operation involved, consult the official Keras documentation to understand potential error scenarios.
2. {bold}Verify model structure:{end} Ensure your Keras model is well-defined and adheres to expected structure for the task you're trying to accomplish.
3. {bold}Examine library documentation:{end} The library documentation might offer troubleshooting tips or best practices related to using the Keras model wrapper.
4. {bold}Inspect error message:{end} The specific error message accompanying this exception might provide more details about the underlying issue.
5. {bold}Contact Scalifi Ai support (if necessary):{end} For complex issues or if the provided information isn't sufficient, consider contacting Scalifi Ai support for further assistance at {support_email}

{correct}Need more help?{end}-> {docs_url_base}
"""


class KerasInvalidDataTypeModelException(KerasModelWrapperException):
    default_message = """
{h1}
----KerasInvalidDataTypeModelException------------------------------------------------------
{end}
An invalid data type was encountered while working with a Keras model.

This error indicates that the library cannot create signatures for the model's inputs or outputs due to an unsupported data type. This issue arises during model registration with the Model Catalog Service (MCS), which relies on signatures to manage model interactions.

{bold}Specific context for Keras models:{end}

- The encountered data type is not currently supported by the Keras model wrapper in this library.
- This might involve model input layers, output layers, or intermediate data structures.

{h2}What can I do?{end}

1. {bold}Review supported data types:{end} Consult the library documentation to determine the list of supported data types for Keras models. Check if your model's inputs and outputs align with these types.
2. {bold}Consider data type conversions:{end} If feasible, explore converting your data to a supported type using preprocessing techniques or Keras layers.
3. {bold}Contact Scalifi Ai support (if necessary):{end} If the unsupported data type is crucial for your workflow, consider reaching out to Scalifi Ai support to inquire about potential future support or alternative workarounds at {support_email}

{correct}Need more help?{end}-> {docs_url_base}
"""


class KerasInvalidModelException(KerasModelWrapperException):
    default_message = """
{h1}
----KerasInvalidModelException--------------------------------------------------------------
{end}
The provided Keras model is invalid for registration or retrieval from the Model Catalog Service (MCS).

This error indicates that the Keras model you're trying to register or fetch using the model wrapper class has failed essential checks within the library. These checks ensure model validity for storage and interaction within MCS.

{bold}Potential reasons for model rejection:{end}

* {bold}Incomplete model structure:{end} The model might be missing crucial components like layers or activation functions, leading to invalid architecture.
* {bold}Incompatibility issues:{end} The model's structure or configuration might not be compatible with the library's requirements or limitations for Keras models in MCS.
* {bold}Corrupted model file:{end} If fetching a model, the model file itself might be corrupted or damaged, hindering retrieval.
* {bold}Version mismatch:{end} Incompatibility between the model's Keras version and the library's supported versions might cause issues.

{h2}What can I do?{end}

1. {bold}Validate model structure:{end} Ensure your Keras model is well-defined and adheres to expected structure for the task you're trying to accomplish. Verify that all necessary components are present for a functional model.
2. {bold}Review library limitations:{end} Consult the library documentation to understand any restrictions or specific requirements for Keras models registered in MCS.
3. {bold}Check Keras version:{end} If applicable, verify that the model's Keras version is compatible with the version supported by the library.
4. {bold}Contact Scalifi Ai support (if necessary):{end} For complex issues or if the provided information isn't sufficient, consider contacting Scalifi Ai support for further assistance and potential troubleshooting specific to your model at {support_email}

{correct}Need more help?{end}-> {docs_url_base}
"""
