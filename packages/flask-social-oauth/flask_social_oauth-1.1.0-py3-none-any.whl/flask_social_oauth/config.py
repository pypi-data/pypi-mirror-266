class Config:
    """
    Defines the configuration settings for Flask Social Login package.
    """

    def __init__(
        self,
        social_auth_providers: list = [],
        application_root_url: str = "http://127.0.0.1:5000",
    ):
        """
        Initializes the configuration settings for Flask Social Login package.

        :param social_auth_providers: The list of social login providers, defaults to an empty list. (optional)
        :type social_auth_providers: list

        :param application_root_url: The root URL of the Flask application, defaults to "http://127.0.0.1:5000". (optional)
        :type application_root_url: str
        """
        self.SOCIAL_AUTH_PROVIDERS = social_auth_providers
        self.APPLICATION_ROOT_URL = application_root_url
        self.supported_providers = ["google", "github", "discord"]

    def google_auth(
        self,
        google_auth_client_id: str,
        google_auth_client_secret: str,
        google_auth_scope: str = "email profile openid",
        google_auth_success_redirect_uri: str = "/",
        google_auth_initialization_handler_uri: str = "/google/login",
        google_auth_callback_handler_uri: str = "/google/callback",
        google_auth_initialization_handler_wrapper=None,
        google_auth_callback_handler_wrapper=None,
    ):
        """
        Configures Google authentication parameters.

        :param google_auth_client_id: The client ID for Google authentication. (required)
        :type google_auth_client_id: str

        :param google_auth_client_secret: The client secret for Google authentication. (required)
        :type google_auth_client_secret: str

        :param google_auth_scope: The scope of Google authentication, defaults to "email profile openid". (optional)
        :type google_auth_scope: str

        :param google_oauth_success_redirect_uri: The URI to redirect after successful Google authentication, defaults to "/". (optional)
        :type google_oauth_success_redirect_uri: str

        :param google_auth_initialization_handler_uri: The URI for initiating Google authentication, defaults to "/google/login". (optional)
        :type google_auth_initialization_handler_uri: str

        :param google_auth_callback_handler_uri: The URI for Google authentication callback, defaults to "/google/callback". (optional)
        :type google_auth_callback_handler_uri: str

        :param google_auth_initialization_handler_wrapper: The wrapper function for Google authentication initialization handler, defaults to None. (optional)

        :param google_auth_callback_handler_wrapper: The wrapper function for Google authentication callback handler, defaults to None. (optional)
        """
        self.GOOGLE_AUTH_CLIENT_ID = google_auth_client_id
        self.GOOGLE_AUTH_CLIENT_SECRET = google_auth_client_secret
        self.GOOGLE_AUTH_SCOPE = google_auth_scope
        self.GOOGLE_AUTH_SUCCESS_REDIRECT_URI = google_auth_success_redirect_uri
        self.GOOGLE_AUTH_INITIALIZATION_HANDLER_URI = (
            google_auth_initialization_handler_uri
        )
        self.GOOGLE_AUTH_CALLBACK_HANDLER_URI = google_auth_callback_handler_uri
        self.GOOGLE_AUTH_INITIALIZATION_HANDLER_WRAPPER = (
            google_auth_initialization_handler_wrapper
        )
        self.GOOGLE_AUTH_CALLBACK_HANDLER_WRAPPER = google_auth_callback_handler_wrapper

    def github_auth(
        self,
        github_auth_client_id: str,
        github_auth_client_secret: str,
        github_auth_scope: str = "user:email",
        github_auth_success_redirect_uri: str = "/",
        github_auth_initialization_handler_uri: str = "/github/login",
        github_auth_callback_handler_uri: str = "/github/callback",
        github_auth_initialization_handler_wrapper=None,
        github_auth_callback_handler_wrapper=None,
    ):
        """
        Configures GitHub authentication parameters.

        :param github_auth_client_id: The client ID for GitHub authentication. (required)
        :type github_auth_client_id: str

        :param github_auth_client_secret: The client secret for GitHub authentication. (required)
        :type github_auth_client_secret: str

        :param github_auth_scope: The scope of GitHub authentication, defaults to None. (optional)
        :type github_auth_scope: str

        :param github_auth_initialization_handler_uri: The URI for initiating GitHub authentication, defaults to "/github/login". (optional)
        :type github_auth_initialization_handler_uri: str

        :param github_auth_callback_handler_uri: The URI for GitHub authentication callback, defaults to "/github/callback". (optional)
        :type github_auth_callback_handler_uri: str

        :param github_auth_initialization_handler_wrapper: The wrapper function for GitHub authentication initialization handler, defaults to None. (optional)

        :param github_auth_callback_handler_wrapper: The wrapper function for GitHub authentication callback handler, defaults to None. (optional)
        """
        self.GITHUB_AUTH_CLIENT_ID = github_auth_client_id
        self.GITHUB_AUTH_CLIENT_SECRET = github_auth_client_secret
        self.GITHUB_AUTH_SCOPE = github_auth_scope
        self.GITHUB_AUTH_SUCCESS_REDIRECT_URI = github_auth_success_redirect_uri
        self.GITHUB_AUTH_INITIALIZATION_HANDLER_URI = (
            github_auth_initialization_handler_uri
        )
        self.GITHUB_AUTH_CALLBACK_HANDLER_URI = github_auth_callback_handler_uri
        self.GITHUB_AUTH_INITIALIZATION_HANDLER_WRAPPER = (
            github_auth_initialization_handler_wrapper
        )
        self.GITHUB_AUTH_CALLBACK_HANDLER_WRAPPER = github_auth_callback_handler_wrapper

    def discord_auth(
        self,
        discord_auth_client_id: str,
        discord_auth_client_secret: str,
        discord_auth_scope: str = "identify email",
        discord_auth_success_redirect_uri: str = "/",
        discord_auth_initialization_handler_uri: str = "/discord/login",
        discord_auth_callback_handler_uri: str = "/discord/callback",
        discord_auth_initialization_handler_wrapper=None,
        discord_auth_callback_handler_wrapper=None,
    ):
        """
        Configures Discord authentication parameters.

        :param discord_auth_client_id: The client ID for Discord authentication. (required)
        :type discord_auth_client_id: str

        :param discord_auth_client_secret: The client secret for Discord authentication. (required)
        :type discord_auth_client_secret: str

        :param discord_auth_scope: The scope of Discord authentication, defaults to None. (optional)
        :type discord_auth_scope: str

        :param discord_auth_initialization_handler_uri: The URI for initiating Discord authentication, defaults to "/discord/login". (optional)
        :type discord_auth_initialization_handler_uri: str

        :param discord_auth_callback_handler_uri: The URI for Discord authentication callback, defaults to "/discord/callback". (optional)
        :type discord_auth_callback_handler_uri: str

        :param discord_auth_initialization_handler_wrapper: The wrapper function for Discord authentication initialization handler, defaults to None. (optional)

        :param discord_auth_callback_handler_wrapper: The wrapper function for Discord authentication callback handler, defaults to None. (optional)
        """
        self.DISCORD_AUTH_CLIENT_ID = discord_auth_client_id
        self.DISCORD_AUTH_CLIENT_SECRET = discord_auth_client_secret
        self.DISCORD_AUTH_SCOPE = discord_auth_scope
        self.DISCORD_AUTH_SUCCESS_REDIRECT_URI = discord_auth_success_redirect_uri
        self.DISCORD_AUTH_INITIALIZATION_HANDLER_URI = (
            discord_auth_initialization_handler_uri
        )
        self.DISCORD_AUTH_CALLBACK_HANDLER_URI = discord_auth_callback_handler_uri
        self.DISCORD_AUTH_INITIALIZATION_HANDLER_WRAPPER = (
            discord_auth_initialization_handler_wrapper
        )
        self.DISCORD_AUTH_CALLBACK_HANDLER_WRAPPER = (
            discord_auth_callback_handler_wrapper
        )
