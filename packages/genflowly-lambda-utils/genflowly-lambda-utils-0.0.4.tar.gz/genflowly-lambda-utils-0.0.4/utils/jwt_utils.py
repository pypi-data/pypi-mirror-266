import base64
import json


def extract_field_from_jwt(jwt: str, field: str) -> str:
    """
    Extracts a specified field from a JWT

    Parameters:
    - jwt (str): The JWT by OAUTH provider to extract the information.
    - field (str): The field to extract from the token's payload.

    Returns:
    - str: The extracted field value if available; raises ValueError otherwise.

    Raises:
    - ValueError: If the JWT is invalid or the specified field is not present.
    """
    try:
        parts = jwt.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid ID token format: JWT should have three parts.")

        payload = parts[1]
        padding_needed = 4 - len(payload) % 4
        if padding_needed:
            payload += "=" * padding_needed
        decoded_payload = base64.urlsafe_b64decode(payload)
        parsed_payload = json.loads(decoded_payload)

        if field not in parsed_payload:
            raise ValueError(f"{field} not found in JWT payload.")

        return parsed_payload[field]
    except Exception as e:
        raise ValueError(f"Failed to extract {field}: {str(e)}")


# Functions specifically for 'profile' and 'name'
def extract_profile(jwt: str) -> str:
    """
    Extracts the profile picture URL from a JWT

    Parameters:
    - jwt (str): The JWT ID token from OAUTH provider

    Returns:
    - str: The extracted profile picture URL if available.

    Raises:
    - ValueError: If the JWT is invalid or the profile picture URL is not present.
    """
    return extract_field_from_jwt(jwt, 'picture')


def extract_name(jwt: str) -> str:
    """
    Extracts the name from a JWT

    Parameters:
    - jwt (str): The JWT ID token from OAUTH provider

    Returns:
    - str: The extracted name if available.

    Raises:
    - ValueError: If the JWT is invalid or the name is not present.
    """
    return extract_field_from_jwt(jwt, 'name')


def extract_email(jwt: str) -> str:
    """
    Extracts the email from a JWT

    Parameters:
    - jwt (str): The JWT ID token from OAUTH provider

    Returns:
    - str: The extracted email if available.

    Raises:
    - ValueError: If the JWT is invalid or the email is not present.
    """
    return extract_field_from_jwt(jwt, 'email')
