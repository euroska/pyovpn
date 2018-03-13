from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import datetime
import uuid
one_day = datetime.timedelta(1, 0, 0)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()
builder = x509.CertificateBuilder()
name = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, u'OpenVPN CA'),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u'openstack-ansible'),
    x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u'Default CA Deployment'),
])
builder = builder.subject_name(name)
builder = builder.issuer_name(name)
builder = builder.not_valid_before(datetime.datetime.today() - one_day)
builder = builder.not_valid_after(datetime.datetime(2018, 8, 2))
builder = builder.serial_number(int(uuid.uuid4()))
builder = builder.public_key(public_key)
builder = builder.add_extension(
    x509.BasicConstraints(ca=True, path_length=None),
    critical=True,
)
certificate = builder.sign(
    private_key=private_key, algorithm=hashes.SHA256(),
    backend=default_backend()
)
print(isinstance(certificate, x509.Certificate))

with open("ca.key", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

data = certificate.public_bytes(
    encoding=serialization.Encoding.PEM,
)
with open("ca.crt", "wb") as f:
    f.write(data)

ca = x509.load_pem_x509_certificate(data, backend=default_backend())
# Generate our key
key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
# Write our key to disk for safe keeping
with open("cert.key", "wb") as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ))

#csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([

    # Provide various details about who we are.
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
    #x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"CA"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"mysite.com"),
])).add_extension(
    x509.SubjectAlternativeName([
        # Describe what sites we want this certificate for.
        x509.DNSName(u"mysite.com"),
        x509.DNSName(u"www.mysite.com"),
        x509.DNSName(u"subdomain.mysite.com"),
    ]),
    critical=False,
# Sign the CSR with our private key.
).sign(key, hashes.SHA256(), default_backend())
# Write our CSR out to disk.
with open("cert.csr", "wb") as f:
    f.write(csr.public_bytes(serialization.Encoding.PEM))


#crt = csr.sign(private_key, hashes.SHA256(), default_backend())
#with open("cert.pem", "wb") as f:
    #f.write(csr.public_bytes(serialization.Encoding.PEM))

cert = x509.CertificateBuilder()
cert = cert.subject_name(csr.subject)
cert = cert.serial_number(1)
cert = cert.not_valid_before(datetime.datetime.today() - one_day)
cert = cert.not_valid_after(datetime.datetime(2018, 8, 2))
cert = cert.issuer_name(ca.subject)
cert = cert.public_key(csr.public_key())
cert = cert.sign(private_key, hashes.SHA256(), default_backend())

with open("cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))
