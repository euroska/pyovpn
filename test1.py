from pyovpn.ca import CA
from pyovpn.utils import *

config = {
    'CACERT_PATH': './cacert.pem',
    'CAKEY_PATH': './cakey.pem',
    'CAKEY_PASSWORD': '',
    'CERT_PATH': './certs',
    'SEQUENCE_PATH': './serial',
    'CRL_PATH': './crl.pem',
    'DH_PATH': './dh.pem',
}

ca = CA.create(config=config)

server_csr, server_key = ca.genCsr(names={
    'COMMON_NAME': 'server',
})
server = ca.sign(server_csr, server=True)

client_csr, client_key = ca.genCsr(names={
    'COMMON_NAME': 'client',
})

client = ca.sign(client_csr, server=False)

cert_csr, cert_key = ca.genCsr(names={'COMMON_NAME': 'crl'})
cert = ca.sign(cert_csr, server=False)

crl = ca.revoke(client)

#dh = ca.genDH(size=2048)

saveCertPem(server, 'server.pem')
saveKeyPem(server_key, 'server.key')

saveCertPem(client, 'client.pem')
saveKeyPem(client_key, 'client.key')
#saveDHPem(dh, 'dh.pem')
saveCRLPem(crl, 'crl.pem')

#with open('crl.pem', "wb") as f:
    #f.write(
        #crl.public_bytes(
            #encoding=serialization.Encoding.PEM,
        #)
    #)
