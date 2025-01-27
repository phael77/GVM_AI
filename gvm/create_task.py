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
        
class PortListManager:
    def __init__(self, port_list_name):
        self.__port_list_name = port_list_name
        
    def get_port_list_id(self, gmp):
        """Obtém o ID da lista de portas pelo nome."""
        port_lists = gmp.get_port_lists()
        for port_list in port_lists.findall('port_list'):
            if port_list.findtext('name') == self.port_list_name:
                return port_list.get('id')
        raise Exception(f"Port list '{self.__port_list_name}' not found.")
    
class TargetManager:
    def __init__(self, host, port_list_manager):
        self.__host = host
        self.__port_list_manager = port_list_manager
        
    def get_host(self):
        return self.__host
    
    def get_port_list_manager(self):
        return self.__port_list_manager
            
    def get_target_id(self, gmp):
        """Obtém o ID do alvo pelo nome do host."""
        targets = gmp.get_targets()
        for target in targets.findall('target'):
            if target.findtext('name') == "My Target" or target.findtext('hosts') == self.__host:
                return target.get('id')
        port_list_id = self.__port_list_manager.get_port_list_id(gmp)
        target = gmp.create_target(
            name="My Target",
            hosts=[self.__host],
            comment="My Target",
            port_list_id=port_list_id,  
        )
        return target.get("id")
    
class ConfigManager:
    def get_config_id(self, gmp):
        configs = gmp.get_configs()
        for config in configs('config'):
            if config.findtext('name') == "Full and fast":
                return config.get('id')
        raise Exception("Scan Configuration 'Full and fast' not found.")
            
class ScannerManager:
    def get_scanner_id(self, gmp):
        scanners = gmp.get_scanners()
        for scanner in scanners.findall('scanner'):
            if scanner.findtext('name') == "OpenVAS Default":
                return scanner.get('id')
        raise Exception("Scanner 'OpenVAS Default' not found.")
    
class TaskCreator:
    def __init__(self):
        pass
    
    def create_task(self, gmp, target_id, config_id, scanner_id):
        return gmp.create_task(
            name=name,
            target_id=target_id,
            config_id=config_id,
            scanner_id=scanner_id,
        )