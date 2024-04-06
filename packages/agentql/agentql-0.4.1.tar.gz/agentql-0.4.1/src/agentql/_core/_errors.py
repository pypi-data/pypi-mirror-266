import json
import logging

# pylint: disable-all
AGENTQL_1000_API_KEY_ERROR = 1000
AGENTQL_1001_ATTRIBUTE_NOT_FOUND_ERROR = 1001
AGENTQL_1002_NO_OPEN_BROWSER_ERROR = 1002
AGENTQL_1003_NO_OPEN_PAGE_ERROR = 1003
AGENTQL_1004_PAGE_TIMEOUT_ERROR = 1004
AGENTQL_1005_ACCESSIBILITY_TREE_ERROR = 1005
AGENTQL_1006_ELEMENT_NOT_FOUND_ERROR = 1006
AGENTQL_1007_OPEN_URL_ERROR = 1007
AGENTQL_1008_CLICK_ERROR = 1008
AGENTQL_1009_INPUT_ERROR = 1009
AGENTQL_1010_QUERY_SYNTAX_ERROR = 1010
AGENTQL_1011_UNABLE_TO_CLOSE_POPUP_ERROR = 1011
AGENTQL_2000_SERVER_ERROR = 2000
AGENTQL_2001_SERVER_TIMEOUT_ERROR = 2001


class BaseAgentQLError(Exception):
    def __init__(self, error, error_code):
        self.error = error
        self.error_code = error_code

    def __str__(self):
        return f"{self.error_code} {self.__class__.__name__}: {self.error}"


class APIKeyError(BaseAgentQLError):
    def __init__(
        self,
        message="Invalid or missing API key. Please set the environment variable 'AGENTQL_API_KEY' with a valid API key.",
    ):
        super().__init__(message, AGENTQL_1000_API_KEY_ERROR)


class AttributeNotFoundError(BaseAgentQLError):
    def __init__(self, name, response_data):
        message = f"{name} not found in AgentQL response node: {json.dumps(response_data)[:300]}. If you are trying to perform an action on an element, make sure the element is the leaf node in your query."
        super().__init__(message, AGENTQL_1001_ATTRIBUTE_NOT_FOUND_ERROR)


class NoOpenBrowserError(BaseAgentQLError):
    def __init__(
        self,
        message='No open browser if detected. Make sure you call "start_browser()" first.',
    ):
        super().__init__(message, AGENTQL_1002_NO_OPEN_BROWSER_ERROR)


class NoOpenPageError(BaseAgentQLError):
    def __init__(self, message='No page is open. Make sure you call "open_url()" first.'):
        super().__init__(message, AGENTQL_1003_NO_OPEN_PAGE_ERROR)


class PageTimeoutError(BaseAgentQLError):
    def __init__(self, message="Page took too long to respond"):
        super().__init__(message, AGENTQL_1004_PAGE_TIMEOUT_ERROR)


class AccessibilityTreeError(BaseAgentQLError):
    def __init__(self, message="Error generating accessibility tree"):
        super().__init__(message, AGENTQL_1005_ACCESSIBILITY_TREE_ERROR)


class ElementNotFoundError(BaseAgentQLError):
    def __init__(self, element_id=None):
        if element_id:
            message = f"{element_id} not found in AgentQL response node."
        else:
            message = "Element not found in AgentQL response node."
        super().__init__(message, AGENTQL_1006_ELEMENT_NOT_FOUND_ERROR)


class OpenUrlError(BaseAgentQLError):
    def __init__(self, message="Unable to open url"):
        super().__init__(message, AGENTQL_1007_OPEN_URL_ERROR)


class ClickError(BaseAgentQLError):
    def __init__(self, message="Unable to click"):
        super().__init__(message, AGENTQL_1008_CLICK_ERROR)


class InputError(BaseAgentQLError):
    def __init__(self, message="Unable to input text"):
        super().__init__(message, AGENTQL_1009_INPUT_ERROR)


class QuerySyntaxError(BaseAgentQLError):
    def __init__(self, message=None, *, unexpected_token, row, column):
        if not message:
            message = f"Unexpected character {unexpected_token} at row {row}, column {column} in AgentQL query."
        super().__init__(message, AGENTQL_1010_QUERY_SYNTAX_ERROR)
        self.unexpected_token = unexpected_token
        self.row = row
        self.column = column


class UnableToClosePopupError(BaseAgentQLError):
    def __init__(
        self,
        message="""Failed to automatically close popup. By default, the close function will query AgentQL server and click the close button in popup with the following query:

        {
            popup_form {
                close_btn
            }
        }

        You could analyze the popup by invoking popup.accessibility_tree and close it manually by querying AgentQL server.
        """,
    ):
        super().__init__(message, AGENTQL_1011_UNABLE_TO_CLOSE_POPUP_ERROR)


class AgentQLServerError(BaseAgentQLError):
    def __init__(self, error=None, error_code=None):
        if error is None:
            error = (
                "AgentQL server error, please try again, if this persists, please reach out to us."
            )
        if error_code is None:
            error_code = AGENTQL_2000_SERVER_ERROR

        super().__init__(error, error_code)


class AgentQLServerTimeoutError(AgentQLServerError):
    def __init__(
        self,
        message="Agentql Server Timed Out, please try again, if this persists, please reach out to us.",
    ):
        super().__init__(message, AGENTQL_2001_SERVER_TIMEOUT_ERROR)
