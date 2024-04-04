# JWT Authentication

A Python implementation of JSON Web Tokens (JWT) for authentication and authorization using a symmetric secret key and HMAC-SHA256.

## Features

- Generate JWT tokens with customizable expiration times
- Validate JWT tokens and verify their integrity using a symmetric secret key and HMAC-SHA256
- Extract user information (such as user ID) from JWT tokens

## Installation

You can install the package via pip:

```pip install my_jwt```

## Usage

```python
from my_jwt import JWT
```

# Create a JWT instance with your secret key
secret_key = 'your_secret_key'
jwt = JWT(secret_key)

# Generate a token for a user
user_id = 'user123'
token = jwt.createToken(user_id)

# Validate a token
is_valid, message = jwt.validateToken(token)
if is_valid:
    print('Token is valid')
else:
    print(f'Token is invalid: {message}')

# Get the user ID from a token
user_id = jwt.getUserId(token)
print(f'User ID: {user_id}')

# Contributing
Contributions are welcome! Please open an issue or submit a pull request.

# License
This project is licensed under the MIT License.