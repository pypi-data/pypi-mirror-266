"""
安全模块工具
"""
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from bcrypt import checkpw,gensalt,hashpw
from base64 import b64decode
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
from cryptography.fernet import Fernet
from jose import jwt

class FernetAPI:
    def __init__(self,key:str) -> None:
        """key可通过 Fernet.generate_key() 生成
        """
        self.__fernet = Fernet(key)
    
    @property
    def fernet(self):
        return self.__fernet
    
    def encrypt(self,plain_text:str)->str:
        """加密
        """
        return self.fernet.encrypt(plain_text.encode()).decode()
        
    def decrypt(self,encrypted_text: str)->str:
        """解密
        """
        return self.fernet.decrypt(encrypted_text).decode()

        
class HashAPI:
    def __init__(self,key:str) -> None:
       """Hash对象
       
       Args:
        key:str,加密密钥
       """
       self.__key = key

    @property
    def key(self):
       return self.__key
    
    def hash_text(self,plain_text:str)->str:
        """将明文哈希加密
        """
        return hashpw(plain_text.encode(),gensalt()).decode()

    def decrypt(self,hash_text:str)->str:
        """解密哈希文本
        """
        cipher = AES.new(self.key.encode(),AES.MODE_ECB)
        enc_text = b64decode(hash_text)
        dec_text = unpad(cipher.decrypt(enc_text),AES.block_size).decode()
        return dec_text

    def verifty(self,plain_text:str,hash_text:str)->bool:
        """验证明文文本和哈希加密文本内容是否一致
        """
        return checkpw(plain_text.encode(),hash_text.encode())


class JWTAPI:
    def __init__(self,key:str,expire_min:int,algorithm:str='HS256') -> None:
        """JWT对象

        Args:
            key:str,密钥
            expire_min:int,token的有效期(分钟)
            algorithm:str,加密算法

        """
        self.__key = key
        self.__algorithm = algorithm
        self.expire = expire_min

    @property
    def key(self):
        return self.__key
    
    @property
    def algorithm(self):
        return self.__algorithm
    
    def encode(self,**kw)-> str:
        """编码JWT的token
        """
        # expire = datetime.utcnow() + timedelta(minutes=self.expire)
        expire = datetime.now(ZoneInfo("UTC")) + timedelta(minutes=self.expire)
        payload = dict(**kw,exp=expire)
        return jwt.encode(payload,key=self.key,algorithm=self.algorithm)

    def decode(self,token:str)->dict:
        """解码JWT的token
        """
        return jwt.decode(token=token,key=self.key,algorithms=self.algorithm)
