from flask_social_oauth.config import Config
from flask_social_oauth.helpers import sanitize_provider_name, validate_auth_config


def initialize_social_login(session, app, config):
    """
    Initialize social login for the Flask app using the provided configuration settings

    :param app: The Flask app
    :type app: Flask

    :param config: The configuration settings for Flask Social Login package
    :type config: Config
    """

    if app is None or config is None or session is None:
        raise ValueError(
            "Flask app, configuration settings, and global context must be provided to the `initialize_social_login` function"
        )

    for provider in config.SOCIAL_AUTH_PROVIDERS:

        sanitized_provider_name = sanitize_provider_name(provider)

        if sanitized_provider_name == "google":
            validate_auth_config(config, "google")

            from flask_social_auth.handlers import google_login_handler, google_callback_handler

            app.add_url_rule(
                config.GOOGLE_AUTH_INITIALIZATION_HANDLER_URI,
                view_func=google_login_handler(config)
                if config.GOOGLE_AUTH_INITIALIZATION_HANDLER_WRAPPER is None
                else config.GOOGLE_AUTH_INITIALIZATION_HANDLER_WRAPPER(google_login_handler(config)),
            )

            app.add_url_rule(
                config.GOOGLE_AUTH_CALLBACK_HANDLER_URI,
                view_func=google_callback_handler(config, session) if config.GOOGLE_AUTH_CALLBACK_HANDLER_WRAPPER is None else config.GOOGLE_AUTH_CALLBACK_HANDLER_WRAPPER(google_callback_handler(config, session)),
            )

        elif sanitized_provider_name == "github":
            validate_auth_config(config, "github")

            from flask_social_auth.handlers import github_login_handler, github_callback_handler

            app.add_url_rule(
                config.GITHUB_AUTH_INITIALIZATION_HANDLER_URI,
                view_func=github_login_handler(config)
                if config.GITHUB_AUTH_INITIALIZATION_HANDLER_WRAPPER is None
                else config.GITHUB_AUTH_INITIALIZATION_HANDLER_WRAPPER(github_login_handler(config)),
            )

            app.add_url_rule(
                config.GITHUB_AUTH_CALLBACK_HANDLER_URI,
                view_func=github_callback_handler(config, session) if config.GITHUB_AUTH_CALLBACK_HANDLER_WRAPPER is None else config.GITHUB_AUTH_CALLBACK_HANDLER_WRAPPER(github_callback_handler(config, session)),
            )

        elif sanitized_provider_name == "discord":
            validate_auth_config(config, "discord")

            from flask_social_auth.handlers import discord_login_handler, discord_callback_handler

            app.add_url_rule(
                config.DISCORD_AUTH_INITIALIZATION_HANDLER_URI,
                view_func=discord_login_handler(config)
                if config.DISCORD_AUTH_INITIALIZATION_HANDLER_WRAPPER is None
                else config.DISCORD_AUTH_INITIALIZATION_HANDLER_WRAPPER(discord_login_handler(config)),
            )

            app.add_url_rule(
                config.DISCORD_AUTH_CALLBACK_HANDLER_URI,
                view_func=discord_callback_handler(config, session) if config.DISCORD_AUTH_CALLBACK_HANDLER_WRAPPER is None else config.DISCORD_AUTH_CALLBACK_HANDLER_WRAPPER(discord_callback_handler(config, session)),
            )

        else:
            raise ValueError(
                f"Unsupported social login provider: `{provider}`, please choose from: {config.supported_providers}"
            )
        

