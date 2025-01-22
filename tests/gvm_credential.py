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

# Validar variáveis de ambiente
if not all([path, username, password]):
    raise Exception("Algumas variáveis de ambiente não foram configuradas corretamente.")

# Estabelecer conexão com o Unix Socket
connection = UnixSocketConnection(path=path)
transform = EtreeCheckCommandTransform()

# Criar uma instância do GMP e iniciar uma sessão
with GMP(connection=connection, transform=transform) as gmp:
    try:
        # Autenticar com as credenciais fornecidas
        gmp.authenticate(username, password)

        # Criar uma credencial do tipo 'client certificate'
        new_credential = gmp.create_credential(
            name="My Client Certificate Credential",
            certificate="/home/phael77/client.crt",
            private_key="/home/phael77/client.key",  
            credential_type="cc",  
            comment="Credencial para autenticação via certificado cliente"
        )

        # Exibir o ID da credencial criada
        print(f"Credential created: {new_credential.get('id')}")

    except Exception as e:
        print(f"Erro: {e}")
