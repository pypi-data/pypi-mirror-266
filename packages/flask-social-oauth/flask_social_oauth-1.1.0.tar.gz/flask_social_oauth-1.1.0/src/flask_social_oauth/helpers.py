def sanitize_provider_name(provider_name):
    """
    Sanitize the provider name by removing spaces, dashes, and underscores and converting it to lowercase

    :param provider_name: The name of the social login provider
    :type provider_name: str

    :return: The sanitized provider name
    :rtype: str
    """
    if type(provider_name) != str:
        raise ValueError(
            f"Error in social login provider name `{provider_name}`: provider name must be a string"
        )
    return (
        provider_name.lower().replace(" ", "").replace("-", "").replace("_", "").strip()
    )


def validate_auth_config(config, provider_name):
    """
    Validate the OAuth configuration for a given provider

    :param config: The configuration settings for Flask Social Login package
    :type config: Config

    :param provider_name: The name of the social login provider
    :type provider_name: str
    """
    if not hasattr(config, f"{provider_name.upper()}_AUTH_CLIENT_ID"):
        raise ValueError(
            f"Error in OAuth configuration for `{provider_name}`: client ID is missing"
        )

    if not hasattr(config, f"{provider_name.upper()}_AUTH_CLIENT_SECRET"):
        raise ValueError(
            f"Error in OAuth configuration for `{provider_name}`: client secret is missing"
        )
