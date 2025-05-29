
import cryptography.hazmat
import cryptography.hazmat.backends
import cryptography.hazmat.primitives
import cryptography.hazmat.primitives.asymmetric
import cryptography.hazmat.primitives.asymmetric.ec
import automatey.OS.FileUtils as FileUtils

import hashlib
import ecdsa
import cryptography

class INTERNAL_CryptoEngines:
    
    class cryptography:
        
        @staticmethod
        def privateKeyFromBytes(curve, privateKey:bytes):
            privateKeyInt = int.from_bytes(privateKey)
            return cryptography.hazmat.primitives.asymmetric.ec.derive_private_key(privateKeyInt, curve.INTERNAL_cryptography_curve())
        
        @staticmethod
        def publicKeyFromBytes(curve, publicKey:bytes):
            NLength = len(publicKey) // 2
            x_bytes = publicKey[:NLength]
            y_bytes = publicKey[NLength:]
            x_int = int.from_bytes(x_bytes, "big")
            y_int = int.from_bytes(y_bytes, "big")
            public_numbers = cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicNumbers(x_int, y_int, curve.INTERNAL_cryptography_curve())
            return public_numbers.public_key()

class Feed:
    '''
    A feed encapsulates bytes, behind a `feed` call.
    
    Note that,
    - `feed` MUST be called, until it returns `None`.
    '''
    
    def __init__(self, bytesPerRead=1024):
        self.bytesPerRead = bytesPerRead
        
    def feed(self):
        '''
        (Interface) Returns `None` if feed is empty.
        '''
        pass

    def feedAll(self):
        pass

class Feeds:
    
    class FileFeed(Feed):
        '''
        Encapsulates bytes of a file.
        '''
        
        def __init__(self, f:FileUtils.File, bytesPerRead=1024):
            super().__init__(bytesPerRead=bytesPerRead)
            self.f = f
            self.f.openFile('rb')
        
        def feed(self):
            '''
            Returns `None` if feed is empty.
            '''
            readBytes = self.f.readAny(self.bytesPerRead)
            if len(readBytes) == 0:
                readBytes = None
                self.f.closeFile()
            return readBytes
        
        def feedAll(self):
            readBytes = self.f.readAny()
            self.f.closeFile()
            return readBytes
    
    class BytesFeed(Feed):
        '''
        Encapsulates bytes.
        '''
        def __init__(self, data:bytes, bytesPerRead=1024):
            super().__init__(bytesPerRead=bytesPerRead)
            self.data = data
            self.dataLength = len(self.data)
            self.idx = 0
        
        def feed(self):
            '''
            Returns `None` if feed is empty.
            '''
            readBytes = None
            if self.idx != self.dataLength:
                endIdx = min(self.idx + self.bytesPerRead, self.dataLength)
                readBytes = self.data[self.idx:endIdx]
                self.idx = endIdx
            return readBytes
        
        def feedAll(self):
            return self.data

class Hash:
    
    class Algorithms:
        
        SHA1 = 0
        SHA256 = 1
        SHA384 = 2
        SHA512 = 3
    
    INTERNAL_Algorithm2HashObject = {
        Algorithms.SHA1: hashlib.sha1,
        Algorithms.SHA256: hashlib.sha256,
        Algorithms.SHA384: hashlib.sha384,
        Algorithms.SHA512: hashlib.sha512,
    }
    
    @staticmethod
    def generate(feed:Feed, algorithm=Algorithms.SHA256) -> bytes:
        '''
        Generate a hash, based on a feed.
        '''
        hashObject = Hash.INTERNAL_Algorithm2HashObject[algorithm]()
        while (feedBytes := feed.feed()):
            hashObject.update(feedBytes)
        return bytes.fromhex(hashObject.hexdigest())

class ECC:
    
    class Curve:
        
        class SECP256R1:
            INTERNAL_ecdsa_curve = ecdsa.NIST256p
            INTERNAL_cryptography_curve = cryptography.hazmat.primitives.asymmetric.ec.SECP256R1
            
        class SECP384R1:
            INTERNAL_ecdsa_curve = ecdsa.NIST384p
            INTERNAL_cryptography_curve = cryptography.hazmat.primitives.asymmetric.ec.SECP384R1
    
    @staticmethod
    def generatePrivateKey(curve) -> bytes:
        return ecdsa.SigningKey.generate(curve=curve.INTERNAL_ecdsa_curve).to_string()
    
    @staticmethod
    def derivePublicKey(curve, privateKey:bytes) -> bytes:
        ecdsa_privateKey = ecdsa.SigningKey.from_string(privateKey, curve=curve.INTERNAL_ecdsa_curve)
        return ecdsa_privateKey.verifying_key.to_string()

    @staticmethod
    def deriveSharedSecret(curve, privateKey:bytes, publicKey:bytes) -> bytes:
        privateKey_cryptography = INTERNAL_CryptoEngines.cryptography.privateKeyFromBytes(curve, privateKey)
        publicKey_cryptography = INTERNAL_CryptoEngines.cryptography.publicKeyFromBytes(curve, publicKey)
        sharedSecret:bytes = privateKey_cryptography.exchange(cryptography.hazmat.primitives.asymmetric.ec.ECDH(), publicKey_cryptography)
        return sharedSecret

    class Signature:
        
        @staticmethod
        def generate(curve, privateKey:bytes, message:Feed, hashAlgorithm) -> bytes:
            hashFcn = Hash.INTERNAL_Algorithm2HashObject[hashAlgorithm]
            ecdsa_privateKey = ecdsa.SigningKey.from_string(privateKey, curve=curve.INTERNAL_ecdsa_curve, hashfunc=hashFcn)
            return ecdsa_privateKey.sign(message.feedAll())
        
        @staticmethod
        def verify(curve, publicKey:bytes, message:Feed, signature:bytes, hashAlgorithm) -> bool:
            '''
            Returns `True` if verification succeeds, `False` otherwise.
            '''
            hashFcn = Hash.INTERNAL_Algorithm2HashObject[hashAlgorithm]
            ecdsa_publicKey = ecdsa.VerifyingKey.from_string(publicKey, curve=curve.INTERNAL_ecdsa_curve, hashfunc=hashFcn)
            isVerified = True
            try:
                ecdsa_publicKey.verify(signature, message.feedAll())
            except:
                isVerified = False
            return isVerified
