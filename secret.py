import secrets
import string

# Generate a secure random secret key with letters and digits (e.g., 16 characters long)
secret_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
print(secret_key)
