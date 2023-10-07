import bcrypt


def generate_password_hash(password):
    """Generate a password hash."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
