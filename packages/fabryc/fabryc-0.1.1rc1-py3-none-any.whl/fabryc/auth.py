"""
Retrieve Azure credentials
"""

from azure.identity import DefaultAzureCredential

SCOPE = "https://analysis.windows.net/powerbi/api/.default"


def get_token(scope: str = SCOPE):
    """
    Retrieve Azure credentials
    """
    credentials = DefaultAzureCredential(
        exclude_visual_studio_code_credential=False,
        exclude_interactive_browser_credential=False,
    )
    access_token = credentials.get_token(scope)
    token = access_token.token
    return token


if __name__ == "__main__":
    print(get_token())
