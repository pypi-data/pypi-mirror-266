import platform


UNIX_STYLES = {
    "h1": "\033[95m",
    "h2": "\033[94m",
    "blue": "\033[94m",
    "python": "\033[96m",
    "bash": "\033[95m",
    "warning": "\033[93m",
    "correct": "\033[92m",
    "fail": "\033[91m",
    "bold": "\033[1m",
    "underline": "\033[4m",
    "end": "\033[0m",
    "docs_url_base": "https://scalifiai.com/docs",
    "support_email": "helpdesk@scalifiai.com",
}

WINDOWS_STYLES = {
    "h1": "",
    "h2": "",
    "blue": "",
    "python": "",
    "bash": "",
    "warning": "",
    "correct": "",
    "fail": "",
    "bold": "",
    "underline": "",
    "end": "",
    "docs_url_base": "https://scalifiai.com/docs",
    "support_email": "helpdesk@scalifiai.com",
}

EMPTY_STYLES = {
    "h1": "",
    "h2": "",
    "blue": "",
    "python": "",
    "bash": "",
    "warning": "",
    "correct": "",
    "fail": "",
    "bold": "",
    "underline": "",
    "end": "",
    "docs_url_base": "https://scalifiai.com/docs",
    "support_email": "helpdesk@scalifiai.com",
}

if platform.system() in ["Linux", "Darwin"]:
    STYLES = UNIX_STYLES
elif platform.system() == "Windows":
    STYLES = WINDOWS_STYLES
else:
    STYLES = EMPTY_STYLES


class GeneralException(Exception):
    # TODO[VIMPORTANT] ADD PROPER MESSAGE WITH INSTRUCTIONS
    default_message = "General error: Unknown"

    def __init__(self, *, message=None, internal_data=None, extra_info=None):
        if message == None:
            self.message = self.default_message
        else:
            self.message = message

        self.internal_data = internal_data

        if extra_info != None:
            self.message += """
-----------------------------------------------------------------------------------------
{h1}Extra information{end}

{extra_info}
-----------------------------------------------------------------------------------------
"""

        super().__init__(self.message.format(**STYLES, extra_info=extra_info))


class NotImplementedException(GeneralException):
    default_message = """
{h1}
----NotImplementedException-----------------------------------------------------------------------
{end}
The functionality you're trying to use is not currently implemented.

This exception is a generic placeholder for parts of the code that haven't been implemented yet, 
or the functionality is intentionally not provided.

{h2}What does this mean?{end}

This error indicates a gap in functionality that needs to be addressed in future development. 
In some cases, it might be a placeholder for a feature that's planned but not yet completed.

{h2}What can I do?{end}

{bold}If you encountered this error while using a library or framework:{end}

  - Check the documentation for known limitations or upcoming features. 
    The documentation might mention if a specific functionality is not yet implemented 
    and might provide alternative approaches or workarounds.
  - Consider searching for open issues or feature requests related to this functionality 
    in the project's repository.

{correct}Need more help?{end}-> {docs_url_base}
"""


class BackendNotAvailableException(GeneralException):
    default_message = """
{h1}
----BackendNotAvailableException-----------------------------------------------------------------------
{end}
We're currently experiencing technical difficulties.

We apologize for the inconvenience. Our team is working on resolving the issue as quickly as possible.

{h2}What does this mean?{end}

This error indicates that the backend server responsible for processing your request is temporarily unavailable. 
This could be due to several reasons, such as high server load, maintenance, or unexpected issues.

{h2}What can I do?{end}

1. {bold}Try again later:{end} The issue might be resolved within a short period. We recommend waiting a few minutes and then trying your request again.
2. {bold}Check the status page:{end} Some services might have a status page that provides real-time information about outages or ongoing maintenance. This page can help you determine if the issue is widespread and when you can expect a resolution.

{correct}Need more help?{end}-> Contact our support team: {support_email}
"""


class InstanceDeletedException(GeneralException):
    default_message = """
{h1}
----InstanceDeletedException-----------------------------------------------------------------------
{end}
The instance you're trying to access has been deleted.

{h2}What does this mean?{end}

It appears you've defined a variable that references a specific instance of a service. This instance has since been deleted, and attempting to access the variable now results in this error.

{h2}What can I do?{end}

1. {bold}Update your code:{end} 
  - Remove references to the deleted instance. 
  - If the instance is still needed, recreate it or use a different instance.
2. {bold}Review your instance management:{end} 
  - Consider implementing checks to ensure the referenced instance is still valid before accessing the variable.

{correct}Need more help?{end}-> {docs_url_base}
"""


class UnauthenticatedException(GeneralException):
    default_message = """
{h1}
----UnauthenticatedException-----------------------------------------------------------------------
{end}
You are not currently authenticated.

This error indicates that the system could not identify you and grant access to the requested resource.

{h2}What does this mean?{end}

There are two ways to authenticate with our system:

1. {bold}API Key:{end} You can provide your API key directly in the method call using a keyword argument like `Model.list(api_key="YOUR_API_KEY")`.
2. {bold}Environment Variable:{end} You can set an environment variable named `SCALIFI_AI_API_KEY` with your API key value. This variable will be used automatically for authentication.

{bold}Make sure you are using one of these methods to provide your API key.{end}

{h2}What can I do?{end}

1. {bold}Verify your API key:{end} Ensure you're using the correct API key associated with your account. You can find your API key in your account settings on the Scalifi Ai platform.
2. {bold}Check your method call:{end} If you're providing the API key directly in the method call, double-check for any typos or incorrect usage of the keyword argument.
3. {bold}Set the environment variable:{end} If you prefer using the environment variable, ensure you've set it correctly with the variable name `SCALIFI_AI_API_KEY` and your actual API key value. You can find instructions on setting environment variables specific to your operating system online.

{correct}Need more help?{end}-> {docs_url_base}
"""


class UnauthorizedException(GeneralException):
    default_message = """
{h1}
----UnauthorizedException-----------------------------------------------------------------------
{end}
You are not authorized to perform this action.

This error indicates that you do not have the necessary permissions to access the requested resource or perform the specific action.

{h2}What does this mean?{end}

Permissions are typically controlled by your organization's administrator(s) through Scalifi Ai's Identity and Access Management (IAM) service.

{h2}What can I do?{end}

1. {bold}Contact your organization administrator:{end} Explain the action you're trying to perform and request the necessary permissions. They can grant you the required access level within Scalifi Ai's IAM system.
2. {bold}Review your access level:{end} If unsure about your permissions, consult with your administrator to understand your current access level and if it aligns with your intended actions.

{bold}Note:{end} You cannot modify your own permissions within the Scalifi Ai platform. This requires intervention from an authorized administrator who has access to modify and attach permissions within your organization.

{correct}Need more help?{end}-> {docs_url_base}
"""


class QuotaException(GeneralException):
    default_message = """
{h1}
----QuotaException-----------------------------------------------------------------------
{end}
You've encountered a quota limitation.

This error indicates that your request cannot be processed due to limitations on your account's quotas. These quotas can be related to various aspects such as:

* {bold}Resource usage:{end} Limits on the amount of resources you can consume (e.g., storage, API calls).
* {bold}Service subscription:{end}  Trying to access a service your organization is not subscribed to.
* {bold}Rate limiting:{end}  Exceeding the allowed rate of requests within a specific timeframe. 

{h2}What does this mean?{end}

Depending on the specific quota that was exceeded, the meaning can vary. However, it generally indicates that you need to take some action to fulfill your request.

{h2}What can I do?{end}

1. {bold}Check your Scalifi Ai usage dashboard:{end} This dashboard provides insights into your current quota usage and helps identify which quota limitation you might have reached.
2. {bold}Contact your organization administrator:{end}  If your quotas are insufficient for your needs, your admin can adjust your quota limits or explore upgrading your subscription plan.
3. {bold}Review Scalifi Ai pricing and plans:{end}  The Scalifi Ai pricing page outlines different plans and their associated quota levels. This can help you understand your current limitations and explore options if needed.

{correct}Need more help?{end}-> {docs_url_base}
"""


class QuotaExceededException(QuotaException):
    default_message = """
{h1}
----QuotaExceededException-----------------------------------------------------------------------
{end}
You've exceeded your quota for a specific resource.

This error indicates that your request cannot be processed because you've reached the maximum limit for a particular resource quota. These quotas can be related to various aspects like storage space, API calls, or other resource usage.

{h2}What can I do?{end}

1. {bold}Check your Scalifi Ai usage dashboard:{end}  The dashboard provides detailed information on your current resource usage and quota limits. This will help you identify the specific resource that has exceeded its quota.
2. {bold}Optimize your resource usage:{end} If possible, consider ways to optimize your usage of the resource that reached its quota. This might involve reviewing your code or processes to reduce resource consumption.
3. {bold}Contact your organization administrator:{end} If quota limitations are hindering your work, your administrator might be able to adjust your quota limits or explore upgrading your subscription plan.

{correct}Need more help?{end}-> {docs_url_base}
"""


class QuotaExpiredException(QuotaException):
    default_message = """
{h1}
----QuotaExpiredException-----------------------------------------------------------------------
{end}
Your organization's quota has expired.

This error indicates that your organization's quota for Scalifi Ai platform has expired and is no longer active. Consequently, your requests cannot be processed until a new quota is assigned.

{h2}What can I do?{end}

1. {bold}Contact your organization administrator:{end}  They will be able to check the status of your organization's quota and take necessary actions. This might involve renewing the quota or upgrading the subscription plan.
2. {bold}Review Scalifi Ai pricing and plans:{end}  The Scalifi Ai pricing page outlines different plans and their associated quota levels. This can help your administrator understand options for renewing or upgrading the quota.

{correct}Need more help?{end}-> {docs_url_base}
"""


class QuotaAPIRateLimitExceededException(QuotaException):
    default_message = """
{h1}
----QuotaAPIRateLimitExceededException-----------------------------------------------------------------
{end}
You've exceeded the rate limit for a specific API action.

This error indicates that you've made too many requests for a particular API action within a short timeframe. Scalifi Ai enforces rate limits to ensure fair usage of resources and prevent overloading the system.

{h2}What can I do?{end}

1. {bold}Wait and retry:{end} The rate limit will automatically reset after a certain period. You can wait a few minutes and then try your request again.
2. {bold}Optimize your API calls:{end} Consider ways to optimize your code to reduce the number of API calls required for the same task. This might involve combining multiple requests or batching operations.
3. {bold}Contact your organization administrator:{end} If rate limits are a persistent issue for your workflows, your administrator might be able to explore options for upgrading your subscription plan to a tier with higher rate limits.

{correct}Need more help?{end}-> {docs_url_base}
"""


class QuotaServiceNotSubscribedException(QuotaException):
    default_message = """
{h1}
----QuotaServiceNotSubscribedException---------------------------------------------------------
{end}
Your organization is not subscribed to the requested service.

This error indicates that your organization's quota plan does not cover the specific service you're trying to access. Scalifi Ai offers various services, each with its own quota limitations and subscription requirements.

{h2}What can I do?{end}

1. {bold}Contact your organization administrator:{end}  They can review your organization's current subscription plan and determine if subscribing to the requested service is necessary. 
2. {bold}Review Scalifi Ai pricing and plans:{end}  The Scalifi Ai pricing page outlines different plans and the services they include. This can help your administrator understand options for adding the desired service to your quota.

{correct}Need more help?{end}-> {docs_url_base}
"""


# ---------------------------------------------------------------------------------------------


class CredentialException(GeneralException):
    default_message = """
{h1}
----CredentialException-----------------------------------------------------------------------
{end}
There's a problem with your credentials.

This error indicates an issue with the credentials used to authenticate with Scalifi Ai. Common reasons for this error include:

* {bold}Missing API key:{end} You haven't provided your API key when making a request.
* {bold}Incorrect API key:{end} You've provided an invalid or incorrect API key.
* {bold}Credential manager issue:{end} There might be an internal problem with the credential management system.

{h2}What can I do?{end}

1. {bold}Verify your API key:{end} Ensure you're using the correct API key associated with your account. You can find your API key in your account settings on the Scalifi Ai platform. 
2. {bold}Check your method call:{end} If providing the API key directly in the method call, double-check for any typos or incorrect usage of the keyword argument.
3. {bold}Set the environment variable:{end} If your system uses an environment variable to store the API key, make sure the variable name and value are set correctly (e.g., `SCALIFI_AI_API_KEY` with your actual API key).

{bold}If you've verified your credentials and the issue persists, please contact Scalifi Ai support for further assistance{end}

{correct}Need more help?{end}-> Contact Scalifi Ai support: {support_email}
"""


class CredentialAPIKeyMissingException(CredentialException):
    default_message = """
{h1}
----CredentialAPIKeyMissingException---------------------------------------------------------
{end}
Your API key is missing.

Scalifi Ai requires an API key to authenticate your requests and grant access to its services. You haven't provided your API key in either of the supported methods:

* {bold}Method call argument:{end} You can include your API key directly in the method call using a keyword argument like `Model.list(api_key="YOUR_API_KEY")`.
* {bold}Environment variable:{end} You can set an environment variable named `SCALIFI_AI_API_KEY` with your API key value. 

{h2}What can I do?{end}

1. {bold}Provide your API key:{end} Locate your API key in your account settings on the Scalifi Ai platform. Then, choose one of the following methods to provide it:
    * {bold}Method call argument:{end} Include the `api_key` argument with your actual API key value when calling the method (replace `"YOUR_API_KEY"` with your actual key).
    * {bold}Environment variable:{end} Set the environment variable `SCALIFI_AI_API_KEY` with your actual API key value. You can find instructions on setting environment variables specific to your operating system online.

{correct}Need more help?{end}-> {docs_url_base}
"""


# ---------------------------------------------------------------------------------------------


def raise_general_exception(*, response=None, internal_data=None):

    try:
        data = response.json()
    except Exception as ex:
        try:
            raise BackendNotAvailableException(
                extra_info=str(ex), internal_data=internal_data
            )
        except Exception:
            raise BackendNotAvailableException(internal_data=internal_data)

    error_code = data.get("error_code", None)

    if error_code != None and type(error_code) == dict and len(error_code) != 0:
        error_code_key = error_code.get("status", None)
        if error_code_key == None and error_code.get("non_field_errors", None) != None:
            error_code_key = error_code["non_field_errors"][0]

        if error_code_key == "quota_exceeded":
            if data.get("detail", None) != None:
                raise QuotaExceededException(
                    extra_info=data["detail"], internal_data=internal_data
                )
            raise QuotaExceededException(internal_data=internal_data)
        elif error_code_key == "qutoa_expired":
            if data.get("detail", None) != None:
                raise QuotaExpiredException(
                    extra_info=data["detail"], internal_data=internal_data
                )
            raise QuotaExpiredException(internal_data=internal_data)
        elif error_code_key == "quota_rate_limit_exceeded":
            if data.get("detail", None) != None:
                raise QuotaAPIRateLimitExceededException(
                    extra_info=data["detail"], internal_data=internal_data
                )
            raise QuotaAPIRateLimitExceededException(internal_data=internal_data)
        elif error_code_key == "quota_service_not_subscribed":
            if data.get("detail", None) != None:
                raise QuotaServiceNotSubscribedException(
                    extra_info=data["detail"], internal_data=internal_data
                )
            raise QuotaServiceNotSubscribedException(internal_data=internal_data)
        elif error_code_key == "unauthenticated":
            if data.get("detail", None) != None:
                raise UnauthenticatedException(
                    extra_info=data["detail"], internal_data=internal_data
                )
            raise UnauthenticatedException(internal_data=internal_data)
        elif error_code_key == "unauthorized":
            if data.get("detail", None) != None:
                raise UnauthorizedException(
                    extra_info=data["detail"], internal_data=internal_data
                )
            raise UnauthorizedException(internal_data=internal_data)

    return data, error_code
