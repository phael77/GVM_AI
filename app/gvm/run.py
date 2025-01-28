import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import GMP
from gvm.transforms import EtreeCheckCommandTransform
from typing import Annotated
from typing_extensions import TypedDict

# Carregar variáveis de ambiente
load_dotenv()

# Configurar o chatbot
api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
    max_tokens=None,
    api_key=api_key,
 
)

# Configurar o grafo de estados
class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()

# Função para criar tarefa no OpenVAS
def create_openvas_task(prompt: str) -> str:
    path = os.getenv('GVMD_SOCKET_PATH')
    username = os.getenv('GVMD_USERNAME')
    password = os.getenv('GVMD_PASSWORD')
    host = os.getenv('GVMD_HOST')
    port_list_name = os.getenv('GVMD_PORT_LIST_NAME', 'All IANA assigned TCP and UDP')

    try:
        connection = UnixSocketConnection(path=path)
        transform = EtreeCheckCommandTransform()

        with GMP(connection=connection, transform=transform) as gmp:
            gmp.authenticate(username, password)

            # Obter lista de portas
            port_lists = gmp.get_port_lists()
            port_list_id = next(
                (pl.get('id') for pl in port_lists.findall('port_list') if pl.findtext('name') == port_list_name),
                None
            )
            if not port_list_id:
                return "Port list not found."

            # Verificar ou criar alvo
            targets = gmp.get_targets()
            target_id = next(
                (t.get('id') for t in targets.findall('target') if t.findtext('name') == "My Target" or t.findtext('hosts') == host),
                None
            )
            if not target_id:
                target = gmp.create_target(
                    name="My Target",
                    hosts=[host],
                    comment="My Target",
                    port_list_id=port_list_id,
                )
                target_id = target.get("id")

            # Obter configuração de scan
            configs = gmp.get_scan_configs()
            config_id = next(
                (cfg.get('id') for cfg in configs.findall('config') if cfg.findtext('name') == 'Full and fast'),
                None
            )
            if not config_id:
                return "Scan configuration not found."

            # Obter scanner
            scanners = gmp.get_scanners()
            scanner_id = next(
                (sc.get('id') for sc in scanners.findall('scanner') if sc.findtext('name') == 'OpenVAS Default'),
                None
            )
            if not scanner_id:
                return "Scanner not found."

            # Criar tarefa
            task = gmp.create_task(
                name="New Task",
                config_id=config_id,
                target_id=target_id,
                scanner_id=scanner_id,
            )
            return f"Task created successfully: {task}"
    except Exception as e:
        return f"Error creating task: {e}"

# Integração com o chatbot
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            assistant_response = value["messages"][-1].content
            print("Assistant:", assistant_response)

            # Detectar intenção e criar tarefa no OpenVAS
            if "create a task" in assistant_response.lower():
                result = create_openvas_task(user_input)
                print("Task Status:", result)

# Loop de interação
while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except Exception as e:
        print(f"Error: {e}")
        break
