import uuid
import datetime
import os
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, dh
from cryptography.x509.oid import NameOID

ONE_DAY = datetime.timedelta(days=1)


def normalizeConfig(config):
    config['ca_cert_path'] = config.get('ca_cert_path', '')
    config['ca_key_path'] = config.get('ca_key_path', '')
    config['ca_key_password'] = config.get('ca_key_password', '')
    config['dh_path'] = config.get('dh_path', '')
    config['crl_path'] = config.get('crl_path', '')
    config['sequence_path'] = config.get('sequence_path', '')


def normalizeNames(names):
    names['cn'] = names.get('cn', 'Test CA')
    names['o'] = names.get('o', 'Test organization')
    names['ou'] = names.get('ou', 'Test unit')


def getKey(path, password=None):
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return serialization.load_pem_private_key(
                f.read(),
                password=password,
                backend=default_backend(),
            )

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    with open(path, 'wb') as f:
        encryption = serialization.NoEncryption()
        if password:
            encryption = serialization.BestAvailableEncryption(password)

            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=encryption,
            ))

    return private_key

def genDH(path, size=2048, public_exponent=65537):
    if not os.path.exists(path):
        parametres = dh.generate_parameters(
            generator=2, key_size=2048,
            backend=default_backend()
        )

    with open(path, 'wb') as f:
        f.write(parametres.parameter_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.ParameterFormat.PKCS3
        ))
    return True


class CA(object):

    def __init__(self, config={}):
        normalizeConfig(config)
        genDH(config['dh_path'])

        self.config = config
        self.sequence_number = self.loadSequence()

        self.key = getKey(
            config['ca_key_path'],
            self.config['ca_key_password']
        )
        self.cert = Cert(config['ca_cert_path'], key=self.key)
        self.crl = Crl(self, config['crl_path'])


    @staticmethod
    def create(config={}, names={}, valid_from=None, valid_to=None):
        # normalize config
        normalizeConfig(config)
        normalizeNames(names)

        if valid_from is None:
            valid_from = datetime.datetime.now() - ONE_DAY

        if valid_to is None:
            valid_to = valid_from + datetime.timedelta(days=3650)

        # first create private key
        private_key = getKey(config['ca_key_path'])

        # get public key
        public_key = private_key.public_key()
        builder = x509.CertificateBuilder()
        name = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, names['cn']),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, names['o']),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, names['ou']),
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

        # save ca cert
        with open(config['ca_cert_path'], "wb") as f:
            f.write(
                ca.public_bytes(
                    encoding=serialization.Encoding.PEM,
                )
            )

        return CA(config=config)

    def loadSequence(self):
        '''
        '''
        if os.path.exists(self.config['sequence_path']):
            with open(self.config['sequence_path'], "r") as f:
                return int(f.read())
        return 1

    def nextSequence(self):
        '''
        '''
        self.sequence_number += 1

        with open(self.config['sequence_path'], "w") as f:
            f.write(str(self.sequence_number))

        return self.sequence_number

    def signCert(self, csr, server=False, valid_from=None, valid_to=None):

        if valid_from is None:
            valid_from = datetime.datetime.now() - ONE_DAY

        if valid_to is None:
            valid_to = datetime.datetime.now() + datetime.timedelta(days=365)

        if valid_to > self.cert.not_valid_after:
            valid_to = self.cert.not_valid_after

        cert = x509.CertificateBuilder() \
            .subject_name(csr.subject) \
            .serial_number(self.nextSequence()) \
            .not_valid_before(valid_from) \
            .not_valid_after(valid_to) \
            .issuer_name(self.cert.subject) \
            .public_key(csr.public_key())

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

        return self.sign(cert)

    def sign(self, request):
        return request.sign(
            self.key,
            hashes.SHA256(),
            default_backend()
        )



class Cert(object):

    def __init__(self, cert_path, key, csr=None):
        self.path = cert_path
        with open(cert_path, 'rb') as f:
            self.cert = x509.load_pem_x509_certificate(
                f.read(),
                default_backend()
            )

        self.key = key
        self.csr = csr

    def save(self):
        with open(self.path, 'wb') as f:
            f.write(
                self.cert.public_bytes(
                    encoding=serialization.Encoding.PEM
                )
            )

    @staticmethod
    def genCsr(self, names={}, key=None, extends=[]):
        '''
        '''
        normalizeNames(names)

        if key is None:
            key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )

        csr = x509.CertificateSigningRequestBuilder().subject_name(
            x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, names['cn']),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, names['o']),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, names['ou']),
            ])
        ).sign(
            key, hashes.SHA256(), default_backend()
        )

        return csr, key


class Crl(object):

    def __init__(self, ca, crl_path):
        self.ca = ca
        self.crl_path = crl_path

        with open(crl_path, 'wb') as f:
            self.crl = x509.load_pem_x509_crl(
                f.read(), default_backend()
            )


    @staticmethod
    def create(self, path):
        '''
        '''
        builder = x509.CertificateRevocationListBuilder()
        builder = builder.issuer_name(self.cert.subject)
        builder = builder.last_update(datetime.datetime.today())
        builder = builder.next_update(datetime.datetime.today() + datetime.timedelta(days=1))

        return builder.sign(
            private_key=self.key,
            algorithm=hashes.SHA256(),
            backend=default_backend()
        )

    def addNumber(self, number):
        revoked_cert = x509.RevokedCertificateBuilder().serial_number(
            number
        ).revocation_date(
            datetime.datetime.today()
        ).build(default_backend())

        builder = builder.add_revoked_certificate(revoked_cert)

    def addCert(self, cert):
        revoked_cert = x509.RevokedCertificateBuilder().serial_number(
            cert.serial_number
        ).revocation_date(
            datetime.datetime.today()
        ).build(default_backend())

        builder = builder.add_revoked_certificate(revoked_cert)

    def normalize(self, active=[]):
        return active

    def save(self):
        pass

