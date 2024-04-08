# Flask Social OAuth

Flask Social OAuth is a Python package that simplifies the integration of social oauth functionality into Flask web applications. With support for popular social authentication providers like Google, GitHub, and Discord, Flask Social OAuth streamlines the authentication process for users and enables seamless access to your web application.

## Installation

You can install Flask Social OAuth via pip:

```bash
pip install flask-social-oauth
```

## Quick Start

```python
from flask import Flask, session
from flask_social_oauth import Config, initialize_social_login

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure social authentication providers
config = Config()
config.google_auth(
    google_auth_client_id="your_client_id",
    google_auth_client_secret="your_client_secret"
)
config.github_auth(
    github_auth_client_id="your_client_id",
    github_auth_client_secret="your_client_secret"
)
config.discord_auth(
    discord_auth_client_id="your_client_id",
    discord_auth_client_secret="your_client_secret"
)

# Initialize social login
initialize_social_login(session, app, config)

if __name__ == '__main__':
    app.run(debug=True)
```

## Supported Providers

- Google
- GitHub
- Discord

## Detailed Description

### Config Class

The `Config` class is used to define the configuration settings for Flask Social Login package. It provides methods to configure authentication parameters for different social providers.

#### Methods

- `google_auth()`: Configures Google authentication parameters.
- `github_auth()`: Configures GitHub authentication parameters.
- `discord_auth()`: Configures Discord authentication parameters.

### initialize_social_login Function

The `initialize_social_login()` function is used to initialize social login for the Flask app using the provided configuration settings. It registers URL routes and handlers for social authentication providers.

#### Parameters

- `session`: The Flask session object.
- `app`: The Flask app instance.
- `config`: The configuration settings for Flask Social Login package.

### Google Handlers

#### `google_login_handler()`

Handles the initiation of the Google OAuth login flow.

#### Parameters

- `config`: The configuration settings for Flask Social Login package.

#### `google_callback_handler()`

Handles the Google OAuth callback flow.

#### Parameters

- `config`: The configuration settings for Flask Social Login package.
- `session`: The Flask session object.

### GitHub Handlers

#### `github_login_handler()`

Handles the initiation of the GitHub OAuth login flow.

#### Parameters

- `config`: The configuration settings for Flask Social Login package.

#### `github_callback_handler()`

Handles the GitHub OAuth callback flow.

#### Parameters

- `config`: The configuration settings for Flask Social Login package.
- `session`: The Flask session object.

### Discord Handlers

#### `discord_login_handler()`

Handles the initiation of the Discord OAuth login flow.

#### Parameters

- `config`: The configuration settings for Flask Social Login package.

#### `discord_callback_handler()`

Handles the Discord OAuth callback flow.

#### Parameters

- `config`: The configuration settings for Flask Social Login package.
- `session`: The Flask session object.

## Documentation

For more detailed usage and configuration, please refer to the [documentation](https://docs.om-mishra.com/flask-social-oauth).

## Issues and Contributions

If you encounter any issues or have suggestions for improvements, feel free to open an issue on [GitHub](https://github.com/om-mishra7/flask-social-oauth/issues). Contributions are also welcome!

## License

Flask Social OAuth is released under the [MIT License](https://github.com/om-mishra7/flask-social-oauth/blob/main/LICENSE).
