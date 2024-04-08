import secrets
import requests
import datetime
from urllib.parse import urlencode
from flask import request, redirect, jsonify

def google_login_handler(config):
    """
    Handles the initiation of the Google OAuth login flow.

    :param config: The configuration settings for Flask Social Login package.
    :type config: Config

    :return: The view function for the Google OAuth login handler.
    :rtype: function
    """

    def google_login():
        """
        Initializes the Google OAuth login flow.

        :return: The redirect response to the Google OAuth login page.
        :rtype: Response
        """

        # Base URL for Google OAuth authentication
        base_google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"

        # Generate a unique state for this authentication request
        google_auth_request_state = secrets.token_urlsafe(128)

        # Parameters for Google OAuth URL
        google_auth_url_parameters = {
            "client_id": config.GOOGLE_AUTH_CLIENT_ID,
            "redirect_uri": f"{config.APPLICATION_ROOT_URL}{config.GOOGLE_AUTH_CALLBACK_HANDLER_URI}",
            "response_type": "code",
            "scope": config.GOOGLE_AUTH_SCOPE,
            "state": google_auth_request_state,
        }

        # Redirect the user to the Google OAuth login page
        response = redirect(
            f"{base_google_auth_url}?{urlencode(google_auth_url_parameters)}"
        )

        # Store the authentication state in a cookie
        response.set_cookie(
            "google_auth_request_state",
            google_auth_request_state,
            httponly=True,
            expires=datetime.datetime.now() + datetime.timedelta(minutes=5),
        )

        return response

    return google_login


def google_callback_handler(config, session):
    """
    Handles the Google OAuth callback flow.

    :param config: The configuration settings for Flask Social Login package.
    :type config: Config

    :param user: The user object for storing user information.
    :type user: User

    :return: The view function for the Google OAuth callback handler.
    :rtype: function
    """

    def google_callback():
        """
        Handles the Google OAuth callback flow.

        :return: The response to the Google OAuth callback.
        :rtype: Response
        """

        # Retrieve the stored authentication state from the cookie
        google_auth_request_state = request.cookies.get("google_auth_request_state")

        # Validate that the state parameter matches the stored authentication state
        if google_auth_request_state != request.args.get("state"):
            return jsonify(
                {
                    "status": "error",
                    "message": "The state parameter of the Google OAuth callback does not match the state parameter of the Google OAuth login request, this is most likely due to the OAuth flow being tampered with or taking more than 5 minutes to complete",
                }
            )

        # Retrieve the OAuth code from the callback
        google_auth_code = request.args.get("code")

        # Check if the OAuth code is present
        if not google_auth_code:
            return jsonify(
                {
                    "status": "error",
                    "message": "The Google OAuth code is missing from the callback, this is most likely due to a user canceling the OAuth flow or an error in the OAuth flow",
                }
            )

        # URL for exchanging the authorization code for an access token
        google_auth_token_url = "https://oauth2.googleapis.com/token"

        # Payload for exchanging the authorization code for an access token
        google_auth_token_payload = {
            "code": google_auth_code,
            "client_id": config.GOOGLE_AUTH_CLIENT_ID,
            "client_secret": config.GOOGLE_AUTH_CLIENT_SECRET,
            "redirect_uri": f"{config.APPLICATION_ROOT_URL}{config.GOOGLE_AUTH_CALLBACK_HANDLER_URI}",
            "grant_type": "authorization_code",
        }

        try:
            # Exchange the authorization code for an access token
            google_auth_token_response = requests.post(
                google_auth_token_url, data=google_auth_token_payload, timeout=5
            )
        except requests.exceptions.RequestException as e:
            return jsonify(
                {
                    "status": "error",
                    "message": f"The Google OAuth token request failed with the following error: {e}",
                }
            )

        # Parse the response from the token endpoint
        google_auth_token_response_data = google_auth_token_response.json()

        # Check for errors in the token response
        if "error" in google_auth_token_response_data:
            return jsonify(
                {
                    "status": "error",
                    "message": f"The Google OAuth token request failed with the following error: {google_auth_token_response_data['error']}",
                }
            )

        # Retrieve the access token from the token response
        google_auth_access_token = google_auth_token_response_data["access_token"]

        # URL for retrieving user information
        google_auth_user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"

        try:
            # Retrieve user information using the access token
            google_auth_user_info_response = requests.get(
                google_auth_user_info_url,
                headers={"Authorization": f"Bearer {google_auth_access_token}"},
                params={"alt": "json"},
                timeout=5,
            )
        except requests.exceptions.RequestException as e:
            return jsonify(
                {
                    "status": "error",
                    "message": f"The Google OAuth user info request failed with the following error: {e}",
                }
            )

        # Parse the response containing user information
        google_auth_user_info = google_auth_user_info_response.json()

        # Store the user information in the global context
        session["user"] = google_auth_user_info

        # Redirect the user to the success page
        response = redirect(config.GOOGLE_AUTH_SUCCESS_REDIRECT_URI)

        # Clear the authentication state cookie
        response.set_cookie("google_auth_request_state", "", expires=0)

        return response

    return google_callback


def github_login_handler(config):
    """
    Handles the initiation of the GitHub OAuth login flow.

    :param config: The configuration settings for Flask Social Login package.
    :type config: Config

    :return: The view function for the GitHub OAuth login handler.
    :rtype: function
    """

    def github_login():
        """
        Initializes the GitHub OAuth login flow.

        :return: The redirect response to the GitHub OAuth login page.
        :rtype: Response
        """

        # Base URL for GitHub OAuth authentication
        base_github_auth_url = "https://github.com/login/oauth/authorize"

        # Generate a unique state for this authentication request
        github_auth_request_state = secrets.token_urlsafe(128)

        # Parameters for GitHub OAuth URL
        github_auth_url_parameters = {
            "client_id": config.GITHUB_AUTH_CLIENT_ID,
            "redirect_uri": f"{config.APPLICATION_ROOT_URL}{config.GITHUB_AUTH_CALLBACK_HANDLER_URI}",
            "scope": config.GITHUB_AUTH_SCOPE,
            "state": github_auth_request_state,
            "allow_signup": "true",
        }

        # Redirect the user to the GitHub OAuth login page
        response = redirect(
            f"{base_github_auth_url}?{urlencode(github_auth_url_parameters)}"
        )

        # Store the authentication state in a cookie
        response.set_cookie(
            "github_auth_request_state",
            github_auth_request_state,
            httponly=True,
            expires=datetime.datetime.now() + datetime.timedelta(minutes=5),
        )

        return response

    return github_login


def github_callback_handler(config, session):
    """
    Handles the GitHub OAuth callback flow.

    :param config: The configuration settings for Flask Social Login package.
    :type config: Config

    :param user: The user object for storing user information.
    :type user: User

    :return: The view function for the GitHub OAuth callback handler.
    :rtype: function
    """

    def github_callback():
        """
        Handles the GitHub OAuth callback flow.

        :return: The response to the GitHub OAuth callback.
        :rtype: Response
        """

        # Retrieve the stored authentication state from the cookie
        github_auth_request_state = request.cookies.get("github_auth_request_state")

        # Validate that the state parameter matches the stored authentication state
        if github_auth_request_state != request.args.get("state"):
            return jsonify(
                {
                    "status": "error",
                    "message": "The state parameter of the GitHub OAuth callback does not match the state parameter of the GitHub OAuth login request, this is most likely due to the OAuth flow being tampered with or taking more than 5 minutes to complete",
                }
            )

        # Retrieve the OAuth code from the callback
        github_auth_code = request.args.get("code")

        # Check if the OAuth code is present
        if not github_auth_code:
            return jsonify(
                {
                    "status": "error",
                    "message": "The GitHub OAuth code is missing from the callback, this is most likely due to a user canceling the OAuth flow or an error in the OAuth flow",
                }
            )

        # URL for exchanging the authorization code for an access token
        github_auth_token_url = "https://github.com/login/oauth/access_token"

        # Payload for exchanging the authorization code for an access token
        github_auth_token_payload = {
            "client_id": config.GITHUB_AUTH_CLIENT_ID,
            "client_secret": config.GITHUB_AUTH_CLIENT_SECRET,
            "code": github_auth_code,
        }

        try:
            # Exchange the authorization code for an access token
            github_auth_token_response = requests.post(
                github_auth_token_url,
                headers={"Accept": "application/json"},
                data=github_auth_token_payload,
                timeout=5,
            )
        except requests.exceptions.RequestException as e:

            return jsonify(
                {
                    "status": "error",
                    "message": f"The GitHub OAuth token request failed with the following error: {e}",
                }
            )

        # Parse the response from the token endpoint
        github_auth_token_response_data = github_auth_token_response.json()

        # Check for errors in the token response
        if "error" in github_auth_token_response_data:
            return jsonify(
                {
                    "status": "error",
                    "message": f"The GitHub OAuth token request failed with the following error: {github_auth_token_response_data['error']}",
                }
            )

        # Retrieve the access token from the token response
        github_auth_access_token = github_auth_token_response_data["access_token"]

        # URL for retrieving user information
        github_auth_user_info_url = "https://api.github.com/user"

        try:
            # Retrieve user information using the access token
            github_auth_user_info_response = requests.get(
                github_auth_user_info_url,
                headers={"Authorization": f"token {github_auth_access_token}"},
                timeout=5,
            )
        except requests.exceptions.RequestException as e:
            return jsonify(
                {
                    "status": "error",
                    "message": f"The GitHub OAuth user info request failed with the following error: {e}",
                }
            )

        # Parse the response containing user information
        github_auth_user_info = github_auth_user_info_response.json()
        print(github_auth_user_info)

        # Check if scope has email and if email is present in the user info
        if "email" in config.GITHUB_AUTH_SCOPE and not github_auth_user_info.get(
            "email"
        ):

            github_auth_user_emails_url = "https://api.github.com/user/emails"

            try:
                # Retrieve user emails using the access token
                github_auth_user_emails_response = requests.get(
                    github_auth_user_emails_url,
                    headers={"Authorization": f"token {github_auth_access_token}"},
                    timeout=5,
                )
            except requests.exceptions.RequestException as e:
                return jsonify(
                    {
                        "status": "error",
                        "message": f"The GitHub OAuth user emails request failed with the following error: {e}",
                    }
                )

            # Parse the response containing user emails
            github_auth_user_emails = github_auth_user_emails_response.json()

            github_auth_user_info["email"] = github_auth_user_emails

        # Store the user information in the global context
        session["user"] = github_auth_user_info

        # Redirect the user to the success page
        response = redirect(config.GITHUB_AUTH_SUCCESS_REDIRECT_URI)

        # Clear the authentication state cookie
        response.set_cookie("github_auth_request_state", "", expires=0)

        return response

    return github_callback


def discord_login_handler(config):
    """
    Handles the initiation of the Discord OAuth login flow.

    :param config: The configuration settings for Flask Social Login package.
    :type config: Config

    :return: The view function for the Discord OAuth login handler.
    :rtype: function
    """

    def discord_login():
        """
        Initializes the Discord OAuth login flow.

        :return: The redirect response to the Discord OAuth login page.
        :rtype: Response
        """

        # Base URL for Discord OAuth authentication
        base_discord_auth_url = "https://discord.com/api/oauth2/authorize"

        # Generate a unique state for this authentication request
        discord_auth_request_state = secrets.token_urlsafe(128)

        # Parameters for Discord OAuth URL
        discord_auth_url_parameters = {
            "client_id": config.DISCORD_AUTH_CLIENT_ID,
            "redirect_uri": f"{config.APPLICATION_ROOT_URL}{config.DISCORD_AUTH_CALLBACK_HANDLER_URI}",
            "response_type": "code",
            "scope": config.DISCORD_AUTH_SCOPE,
            "state": discord_auth_request_state,
        }

        # Redirect the user to the Discord OAuth login page
        response = redirect(
            f"{base_discord_auth_url}?{urlencode(discord_auth_url_parameters)}"
        )

        # Store the authentication state in a cookie
        response.set_cookie(
            "discord_auth_request_state",
            discord_auth_request_state,
            httponly=True,
            expires=datetime.datetime.now() + datetime.timedelta(minutes=5),
        )

        return response

    return discord_login


def discord_callback_handler(config, session):
    """
    Handles the Discord OAuth callback flow.

    :param config: The configuration settings for Flask Social Login package.
    :type config: Config

    :param user: The user object for storing user information.
    :type user: User

    :return: The view function for the Discord OAuth callback handler.
    :rtype: function
    """

    def discord_callback():
        """
        Handles the Discord OAuth callback flow.

        :return: The response to the Discord OAuth callback.
        :rtype: Response
        """

        # Retrieve the stored authentication state from the cookie
        discord_auth_request_state = request.cookies.get("discord_auth_request_state")

        # Validate that the state parameter matches the stored authentication state
        if discord_auth_request_state != request.args.get("state"):
            return jsonify(
                {
                    "status": "error",
                    "message": "The state parameter of the Discord OAuth callback does not match the state parameter of the Discord OAuth login request, this is most likely due to the OAuth flow being tampered with or taking more than 5 minutes to complete",
                }
            )

        # Retrieve the OAuth code from the callback
        discord_auth_code = request.args.get("code")

        # Check if the OAuth code is present
        if not discord_auth_code:
            return jsonify(
                {
                    "status": "error",
                    "message": "The Discord OAuth code is missing from the callback, this is most likely due to a user canceling the OAuth flow or an error in the OAuth flow",
                }
            )

        # URL for exchanging the authorization code for an access token
        discord_auth_token_url = "https://discord.com/api/oauth2/token"

        # Payload for exchanging the authorization code for an access token
        discord_auth_token_payload = {
            "client_id": config.DISCORD_AUTH_CLIENT_ID,
            "client_secret": config.DISCORD_AUTH_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": discord_auth_code,
            "redirect_uri": f"{config.APPLICATION_ROOT_URL}{config.DISCORD_AUTH_CALLBACK_HANDLER_URI}",
            "scope": config.DISCORD_AUTH_SCOPE,
        }

        try:
            # Exchange the authorization code for an access token
            discord_auth_token_response = requests.post(
                discord_auth_token_url,
                data=discord_auth_token_payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=5,
            )
        except requests.exceptions.RequestException as e:
            return jsonify(
                {
                    "status": "error",
                    "message": f"The Discord OAuth token request failed with the following error: {e}",
                }
            )

        # Parse the response from the token endpoint
        discord_auth_token_response_data = discord_auth_token_response.json()

        # Check for errors in the token response
        if "error" in discord_auth_token_response_data:
            return jsonify(
                {
                    "status": "error",
                    "message": f"The Discord OAuth token request failed with the following error: {discord_auth_token_response_data['error']}",
                }
            )

        # Retrieve the access token from the token response
        discord_auth_access_token = discord_auth_token_response_data["access_token"]

        # URL for retrieving user information
        discord_auth_user_info_url = "https://discord.com/api/users/@me"

        try:
            # Retrieve user information using the access token
            discord_auth_user_info_response = requests.get(
                discord_auth_user_info_url,
                headers={"Authorization": f"Bearer {discord_auth_access_token}"},
                timeout=5,
            )
        except requests.exceptions.RequestException as e:
            return jsonify(
                {
                    "status": "error",
                    "message": f"The Discord OAuth user info request failed with the following error: {e}",
                }
            )

        # Parse the response containing user information
        discord_auth_user_info = discord_auth_user_info_response.json()

        # Store the user information in the global context
        session["user"] = discord_auth_user_info

        # Redirect the user to the success page
        response = redirect(config.DISCORD_AUTH_SUCCESS_REDIRECT_URI)

        # Clear the authentication state cookie
        response.set_cookie("discord_auth_request_state", "", expires=0)

        return response

    return discord_callback
