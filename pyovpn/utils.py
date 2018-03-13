from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization

def saveKeyPem(key, path, password=None):
    with open(path, "wb") as f:
        encryption = serialization.NoEncryption()
        if password is not None:
            encryption = serialization.BestAvailableEncryption(password)

        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=encryption,
        ))

def saveCertPem(cert, path):
    with open(path, "wb") as f:
        f.write(
            cert.public_bytes(
                encoding=serialization.Encoding.PEM,
            )
        )

def saveCRLPem(crl, path):
    with open(path, "wb") as f:
        f.write(
            crl.public_bytes(
                encoding=serialization.Encoding.PEM,
            )
        )

def saveDHPem(dh, path):
    with open(path, 'wb') as f:
        f.write(
            dh.parameter_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.ParameterFormat.PKCS3,
            )
        )
