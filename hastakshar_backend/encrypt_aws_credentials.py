from cryptography.fernet import Fernet

# Generate a key for encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Encrypt your AWS credentials
aws_access_key_id = b'AKIA2P56CA5N7CTQJOPQ'
aws_secret_access_key = b'JGGi1m4EQJ/8ZASyEK1Gr9+j4x9DEBlRBQeUCzul'

encrypted_aws_access_key_id = cipher_suite.encrypt(aws_access_key_id)
encrypted_aws_secret_access_key = cipher_suite.encrypt(aws_secret_access_key)

print(f"Key: {key.decode()}")
print(f"Encrypted AWS_ACCESS_KEY_ID: {encrypted_aws_access_key_id.decode()}")
print(f"Encrypted AWS_SECRET_ACCESS_KEY: {encrypted_aws_secret_access_key.decode()}")
