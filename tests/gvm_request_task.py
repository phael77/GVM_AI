import sys
import os

from gvm.connections import UnixSocketConnection
from gvm.errors import GvmError
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeCheckCommandTransform

from dotenv import load_dotenv

load_dotenv()

path = os.getenv('GVMD_SOCKET_PATH')
connection = UnixSocketConnection(path=path)
transform = EtreeCheckCommandTransform()

username = os.getenv('GVMD_USERNAME')
password = os.getenv('GVMD_PASSWORD')

try:
    tasks = []

    with Gmp(connection=connection, transform=transform) as gmp:
        gmp.authenticate(username, password)

        tasks = gmp.get_tasks(filter_string='scan')

        for task in tasks.xpath('task'):
            print(task.find('name').text)

except GvmError as e:
    print('An error occurred', e, file=sys.stderr)