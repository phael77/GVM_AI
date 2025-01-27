import os
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import GMP
from gvm.transforms import EtreeCheckCommandTransform
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Obter os valores das variáveis de ambiente
path = os.getenv('GVMD_SOCKET_PATH')
username = os.getenv('GVMD_USERNAME')
password = os.getenv('GVMD_PASSWORD')

# Estabelecer conexão com o Unix Socket
connection = UnixSocketConnection(path=path)
transform = EtreeCheckCommandTransform()

# Criar uma instância do GMP e iniciar uma sessão
with GMP(connection=connection, transform=transform) as gmp:
    try:
        # Autenticar com as credenciais fornecidas
        gmp.authenticate(username, password)

        # Obter e listar todas as listas de portas
        port_lists = gmp.get_port_lists()
        for port_list in port_lists.findall('port_list'):
            print(f"Port List Name: {port_list.findtext('name')}, ID: {port_list.get('id')}")

    except Exception as e:
        print(f"Erro: {e}")
