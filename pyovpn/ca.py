import uuid
import datetime
import os
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, dh
from cryptography.x509.oid import NameOID

ONE_DAY = datetime.timedelta(days=1)

#__all__ = []


def normalizeConfig(config):
    config['ca_cert_path'] = config.get('ca_cert_path', '')
    config['ca_key_path'] = config.get('ca_key_path', '')
    config['ca_key_password'] = config.get('ca_key_password', '')
    config['dh_path'] = config.get('dh_path', '')
    config['crl_path'] = config.get('crl_path', '')
    config['sequence_path'] = config.get('sequence_path', '')


def normalizeSubject(subject):
    subject['cn'] = subject.get('cn', 'Test CA')
    subject['o'] = subject.get('o', 'Test organization')
    subject['ou'] = subject.get('ou', 'Test unit')


def serializeKeyPem(key, password=None, str=False):
    encryption = serialization.NoEncryption()
    if password is not None:
        encryption = serialization.BestAvailableEncryption(password)

    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=encryption,
    )

    if str:
        return pem.decode('ascii')
    return pem


def serializePem(cert, str=False):
    pem = cert.public_bytes(
        encoding=serialization.Encoding.PEM,
    )
    if str:
        return pem.decode('ascii')
    return pem


def saveKeyPem(key, path, password=None):
    with open(path, "wb") as f:
        f.write(serializeKeyPem(key, password=password))


def savePem(cert, path):
    with open(path, "wb") as f:
        f.write(serializePem(cert))


def saveDHPem(dh, path):
    with open(path, 'wb') as f:
        f.write(
            dh.parameter_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.ParameterFormat.PKCS3,
            )
        )


def getKey(path, password=None, regenerate=False):
    try:
        if os.path.exists(path) and not regenerate:
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

        saveKeyPem(private_key, path, password=password)

        return private_key

    except Exception as e:
        return


def getCsr(path):
    try:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return x509.load_pem_x509_csr(
                    f.read(),
                    backend=default_backend()
                )
    except Exception as e:
        return


def genDH(path, size=2048, public_exponent=65537):
    #return True
    if not os.path.exists(path):
        parametres = dh.generate_parameters(
            generator=2, key_size=2048,
            backend=default_backend()
        )
        saveDHPem(parametres, path)

    return True


class CA(object):

    @staticmethod
    def inicialize(config={}, subject={}, valid_from=None, valid_to=None):
        # normalize config
        normalizeConfig(config)
        normalizeSubject(subject)

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
            x509.NameAttribute(NameOID.COMMON_NAME, 'ca'),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, subject['o']),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, subject['ou']),
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
        savePem(ca, config['ca_cert_path'])

        return CA(config=config)

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

    @staticmethod
    def genCsr(subject={}, key=None, extends=[]):
        '''
        '''
        normalizeSubject(subject)

        if key is None:
            key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )

        csr = x509.CertificateSigningRequestBuilder().subject_name(
            x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, subject['cn']),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, subject['o']),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, subject['ou']),
            ])
        ).sign(
            key, hashes.SHA256(), default_backend()
        )

        return csr, key

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
        savePem(self.cert, self.path)

    @property
    def not_valid_before(self):
        return self.cert.not_valid_before

    @property
    def not_valid_after(self):
        return self.cert.not_valid_after

    @property
    def serial_number(self):
        return self.cert.serial_number

    @property
    def subject(self):
        return self.cert.subject

    def parseSubject(self):
        subject = {}
        for name in self.cert.subject:
            if name.oid == x509.oid.NameOID.COMMON_NAME:
                subject['cn'] = name.value

            if name.oid == x509.oid.NameOID.ORGANIZATION_NAME:
                subject['o'] = name.value

            if name.oid == x509.oid.NameOID.ORGANIZATIONAL_UNIT_NAME:
                subject['ou'] = name.value

        return subject


class Crl(object):

    @staticmethod
    def build(ca, path):
        builder = x509.CertificateRevocationListBuilder()
        builder = builder.issuer_name(ca.cert.subject)
        builder = builder.last_update(datetime.datetime.today())
        builder = builder.next_update(datetime.datetime.today() + datetime.timedelta(days=1))
        return builder

    @staticmethod
    def create(ca, path):
        '''
        '''
        builder = Crl.build(ca, path)

        return builder.sign(
            private_key=ca.key,
            algorithm=hashes.SHA256(),
            backend=default_backend()
        )

    def __init__(self, ca, path):
        self.ca = ca
        self.path = path
        self.revoked_numbers = []
        self.builder = Crl.build(ca, path)

        try:
            with open(path, 'rb') as f:
                self.crl = x509.load_pem_x509_crl(
                    f.read(), default_backend()
                )

        except Exception as e:
            self.crl = Crl.create(ca, path)
            self.save()

        self.load()

    def load(self):
        for revoked in self.crl:
            self.builder = self.builder.add_revoked_certificate(revoked)
            self.revoked_numbers.append(revoked.serial_number)

    def revoke(self, cert, save=True):
        revoked_cert = x509.RevokedCertificateBuilder().serial_number(
            cert.serial_number
        ).revocation_date(
            datetime.datetime.today()
        ).build(default_backend())

        self.builder = self.builder.add_revoked_certificate(revoked_cert)

        if save:
            self.save()

    def normalize(self, active=[]):
        for i in range(1, self.ca.sequence_number):
            if i not in active and i not in self.revoked_numbers:
                self.revoked_numbers.append(i)
                revoked_cert = x509.RevokedCertificateBuilder().serial_number(
                    i
                ).revocation_date(
                    datetime.datetime.today()
                ).build(default_backend())
                self.builder = self.builder.add_revoked_certificate(revoked_cert)

        self.save()
        return [i for i in active if i not in self.revoked_numbers]

    def save(self):
        savePem(self.builder.sign(
            private_key=self.ca.key,
            algorithm=hashes.SHA256(),
            backend=default_backend()
        ), self.path)

