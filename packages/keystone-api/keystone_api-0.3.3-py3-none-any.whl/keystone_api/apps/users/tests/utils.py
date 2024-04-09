"""Testing utilities specific to dealing with user accounts"""

from apps.users.models import User


def create_test_user(
    username: str,
    first_name: str = "foo",
    last_name: str = "bar",
    email: str = "foo@bar.com",
    password: str = "foobar123",
    **kwargs
) -> User:
    """Create a user account for testing purposes

    Args:
        username: The account username
        first_name: The user's first name
        last_name: The user's last name
        email: A valid email address
        password: The account password
        **kwargs: Any other values in the user model

    Return:
        The saved user account
    """

    return User.objects.create_user(username, first_name, last_name, email, password, **kwargs)
