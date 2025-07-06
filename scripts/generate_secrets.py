import secrets


def generate_secret_key(length: int = 64) -> str:
    raw = secrets.token_urlsafe(length)
    return raw[:length]


if __name__ == "__main__":
    print(generate_secret_key())
