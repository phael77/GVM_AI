import os
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import GMP
from gvm.transforms import EtreeCheckCommandTransform
from dotenv import load_dotenv

class ConnectionManager:
    def __init__(self, path):
        self.__path = path
        
    def connect(self):
        connection = UnixSocketConnection(self.__path)
        transform = EtreeCheckCommandTransform()
        return GMP(connection=connection, transform=transform)
    
class AuthencationManager:
    def __init__(self, username, password):
        self.__username = username
        self.__password = password
        
    def authenticate(self, gmp):
        gmp.authenticate(self.__username, self.__password)