"""Who is the current user?

v1 is single-user, so this always returns "default". The paid multi-user edition
replaces this one function with a lookup from the OAuth token. Everything that
touches data goes through here, so tenancy later is a code change, not a rewrite.
"""

DEFAULT_USER = "default"


def current_user() -> str:
    return DEFAULT_USER
