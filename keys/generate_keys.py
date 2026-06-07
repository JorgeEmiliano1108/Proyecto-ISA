from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

private_key = key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
).decode()

public_key = key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode()

with open('/app/keys/private.pem', 'w') as f:
    f.write(private_key)

with open('/app/keys/public.pem', 'w') as f:
    f.write(public_key)

private_single = private_key.replace('\n', '\\n')
public_single = public_key.replace('\n', '\\n')

with open('/app/keys/private_single.txt', 'w') as f:
    f.write(private_single)

with open('/app/keys/public_single.txt', 'w') as f:
    f.write(public_single)

print('OK: Llaves generadas')
print()
print('PUBLIC KEY SINGLE-LINE:')
print(public_single)
print()
print('PRIVATE KEY SINGLE-LINE:')
print(private_single)
