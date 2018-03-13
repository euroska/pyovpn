import uuid
import datetime
import os
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, dh
from cryptography.x509.oid import NameOID

ONE_DAY = datetime.timedelta(days=1)


class CA(object):

    def __init__(self, config={}):
        CA.normalizeConfig(config)
        self.config = config

        self.ca = None
        with open(config['CACERT_PATH'], "rb") as f:
            self.ca = x509.load_pem_x509_certificate(
                f.read(),
                backend=default_backend(),
            )

        self.key = None
        with open(config['CAKEY_PATH'], "rb") as f:
            self.key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend(),
            )

    @staticmethod
    def normalizeConfig(config):
        config['CACERT_PATH'] = config.get('CACERT_PATH', '')
        config['CAKEY_PATH'] = config.get('CAKEY_PATH', '')
        config['CAKEY_PASSWORD'] = config.get('CAKEY_PASSWORD', '')
        config['DH_PATH'] = config.get('DH_PATH', '')

        config['SEQUENCE_PATH'] = config.get('SEQUENCE_PATH', '')

    @staticmethod
    def normalizeNames(names):
        names['COMMON_NAME'] = names.get('COMMON_NAME', 'Test CA')
        names['ORGANIZATION_NAME'] = names.get('ORGANIZATION_NAME', 'Test organization')
        names['ORGANIZATIONAL_UNIT_NAME'] = names.get('ORGANIZATIONAL_UNIT_NAME', 'Test unit')

    @staticmethod
    def create(config={}, names={}, valid_from=None, valid_to=None):
        # normalize config
        CA.normalizeConfig(config)
        CA.normalizeNames(names)

        if valid_from is None:
            valid_from = datetime.datetime.now() - ONE_DAY

        if valid_to is None:
            valid_to = valid_from + datetime.timedelta(days=3650)

        # first create private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # get public key
        public_key = private_key.public_key()
        builder = x509.CertificateBuilder()
        name = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, names['COMMON_NAME']),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, names['ORGANIZATION_NAME']),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, names['ORGANIZATIONAL_UNIT_NAME']),
        ])

        # fill certificate
        builder = builder.subject_name(name)
        builder = builder.issuer_name(name)
        builder = builder.not_valid_before(valid_from)
        builder = builder.not_valid_after(valid_to)
        builder = builder.serial_number(int(uuid.uuid4()))
        builder = builder.public_key(public_key)
        builder = builder.add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        ca = builder.sign(
            private_key=private_key, algorithm=hashes.SHA256(),
            backend=default_backend()
        )

        with open(config['CACERT_PATH'], "wb") as f:
            f.write(
                ca.public_bytes(
                    encoding=serialization.Encoding.PEM,
                )
            )

        with open(config['CAKEY_PATH'], "wb") as f:
            encryption = serialization.NoEncryption()
            #if config['CAKEY_PASSWORD']:
                #encryption = serialization.BestAvailableEncryption(config['CAKEY_PASSWORD'])

            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=encryption,
            ))

        return CA(config=config)

    def nextSequence(self):
        '''
        '''
        with open(self.config['SEQUENCE_PATH'], "r") as f:
            number = int(f.read())

        number += 1

        with open(self.config['SEQUENCE_PATH'], "w") as f:
            f.write(str(number))

        return number


    def sign(self, csr, server=False, valid_from=None, valid_to=None):

        if valid_from is None:
            valid_from = datetime.datetime.now() - ONE_DAY

        if valid_to is None:
            valid_to = datetime.datetime.now() + datetime.timedelta(days=365)

        if valid_to > self.ca.not_valid_after:
            valid_to = self.ca.not_valid_after

        cert = x509.CertificateBuilder()
        cert = cert.subject_name(csr.subject)
        cert = cert.serial_number(self.nextSequence())
        cert = cert.not_valid_before(valid_from)
        cert = cert.not_valid_after(valid_to)
        cert = cert.issuer_name(self.ca.subject)
        cert = cert.public_key(csr.public_key())
        if server:
            cert = cert.add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            cert = cert.add_extension(
                x509.ExtendedKeyUsage(
                    [x509.ExtendedKeyUsageOID.SERVER_AUTH]
                ),
                critical=False,
            )
        else:
            cert = cert.add_extension(
                x509.ExtendedKeyUsage(
                    [x509.ExtendedKeyUsageOID.CLIENT_AUTH]
                ),
                critical=False,
            )

        cert = cert.sign(
            self.key,
            hashes.SHA256(),
            default_backend()
        )

        return cert

    def genCsr(self, names={}, extends=[]):
        '''
        '''
        CA.normalizeNames(names)

        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        csr = x509.CertificateSigningRequestBuilder().subject_name(
            x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, names['COMMON_NAME']),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, names['ORGANIZATION_NAME']),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, names['ORGANIZATIONAL_UNIT_NAME']),
            ])
        ).sign(
            key, hashes.SHA256(), default_backend()
        )

        return csr, key

    def genDH(self, size=2048):
        return dh.generate_parameters(
            generator=2, key_size=2048,
            backend=default_backend()
        )


    def revoke(self, crt):
        '''
        '''
        builder = x509.CertificateRevocationListBuilder()
        builder = builder.issuer_name(self.ca.subject)
        builder = builder.last_update(datetime.datetime.today())
        builder = builder.next_update(datetime.datetime.today() + datetime.timedelta(days=1))

        revoked_cert = x509.RevokedCertificateBuilder().serial_number(
            crt.serial_number
        ).revocation_date(
            datetime.datetime.today()
        ).build(default_backend())

        builder = builder.add_revoked_certificate(revoked_cert)

        return builder.sign(
            private_key=self.key, algorithm=hashes.SHA256(),
            backend=default_backend()
        )




