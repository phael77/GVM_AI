Criei esses dois testes, vou falar primeiro sobre o teste 1

O primeiro conecta-se a um serviço Greenbone Vulnerability Manager (GVM) usando um socket Unix. 

E o segundo conecta-se via unix socket ao serviço GVM e envia uma requisição para listar as tasks de acordo com o filtro de string que colocarmos.

Aí eu fiz os testes usando variáveis de ambiente para definir o caminho do socket, username e password para maior segurança á esses dados.