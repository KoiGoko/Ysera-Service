def register_user(user: User):
    """Register a new user."""
    user.password = generate_password_hash(user.password)
    user.save()
    return user


def login_user(user: User):
    """Login a user."""
    user = User.objects.get(email=user.email)
    if not check_password_hash(user.password, user.password):
        raise Exception('Invalid password')
    return user


def edit_user(user: User):
    """Edit a user."""
    user.password = generate_password_hash(user.password)
    user.save()
    return user
