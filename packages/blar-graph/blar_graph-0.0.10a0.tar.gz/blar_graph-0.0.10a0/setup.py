# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['blar_graph',
 'blar_graph.agents_tools.agents_examples',
 'blar_graph.agents_tools.tools',
 'blar_graph.db_managers',
 'blar_graph.examples.blar-example-repos.debugger_agent.src',
 'blar_graph.examples.blar-example-repos.debugger_agent.src.graph_construction',
 'blar_graph.examples.blar-example-repos.debugger_agent.src.test_documents',
 'blar_graph.examples.blar-example-repos.debugger_agent.src.utils',
 'blar_graph.examples.blar-example-repos.unit_test_agent',
 'blar_graph.graph_construction.core',
 'blar_graph.graph_construction.languages.python',
 'blar_graph.graph_construction.utils']

package_data = \
{'': ['*'],
 'blar_graph': ['examples/*',
                'examples/blar-example-repos/*',
                'examples/blar-example-repos/.git/*',
                'examples/blar-example-repos/.git/hooks/*',
                'examples/blar-example-repos/.git/info/*',
                'examples/blar-example-repos/.git/logs/*',
                'examples/blar-example-repos/.git/logs/refs/heads/*',
                'examples/blar-example-repos/.git/logs/refs/remotes/origin/*',
                'examples/blar-example-repos/.git/objects/pack/*',
                'examples/blar-example-repos/.git/refs/heads/*',
                'examples/blar-example-repos/.git/refs/remotes/origin/*',
                'examples/blar-example-repos/debugger_agent/*']}

install_requires = \
['langchain-openai>=0.1.1,<0.2.0',
 'langchain>=0.1.13,<0.2.0',
 'llama-index-packs-code-hierarchy>=0.1.1,<0.2.0',
 'llama-index>=0.10.20,<0.11.0',
 'neo4j>=5.18.0,<6.0.0',
 'python-dotenv>=1.0.1,<2.0.0',
 'tree-sitter-languages>=1.10.2,<2.0.0']

setup_kwargs = {
    'name': 'blar-graph',
    'version': '0.0.10a0',
    'description': 'Llm agent to search within a graph',
    'long_description': '# code-base-agent\n\n## Introduction\n\nThis repo introduces a method to represent a local code repository as a graph structure. The objective is to allow an LLM to traverse this graph to understand the code logic and flow. Providing the LLM with the power to debug, refactor, and optimize queries. However, several tasks are yet unexplored.\n\n## Technology Stack\n\nWe used a combination of `llama-index`, `CodeHierarchy` module, and `tree-sitter-languages` for parsing code into a graph structure, `Neo4j` for storing and querying the graph data, and `langchain` to create the agents.\n\n## Installation\n\n**Install the package:**\n\n```shell\npip install blar-graph\n```\n\nSet the env variables\n\n```.env\nNEO4J_URI=neo4j+s://YOUR_NEO4J.databases.neo4j.io\nNEO4J_USERNAME=neo4j\nNEO4J_PASSWORD=YOUR_NEO4J_PASSWORD\nOPENAI_API_KEY=YOUR_OPEN_AI_KEY\n```\n\nIf you are new to Neo4j you can deploy a free instance of neo4j with [Aura](https://login.neo4j.com/u/signup/identifier?state=hKFo2SBIWW01eGl6SEhHVTVZQ2g1VU9rSk1BZlVVblJPd2FzSqFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIFNSUXR5UEtwZThoQTBlOWs0ck1hN0ZTekFOY3JfWkNho2NpZNkgV1NMczYwNDdrT2pwVVNXODNnRFo0SnlZaElrNXpZVG8). Also you can host your own version in [AWS](https://aws.amazon.com/marketplace/seller-profile?id=23ec694a-d2af-4641-b4d3-b7201ab2f5f9) or [GCP](https://console.cloud.google.com/marketplace/product/endpoints/prod.n4gcp.neo4j.io?rapt=AEjHL4O-iQH8W8STKpH0_zwz8HEyQqA9XFkpnFUkJotAt2wAT0Zmjhraww8X6covdYdzJdUi_LwtQtG8qDChLOLYHeEG4x1kZyhfzukM2WkabnwQlQpu5ws&project=direct-album-395214)\n\n### Quick start guide\n\nTo build the graph, you have to instantiate the graph manager and constructor. The graph manager handles the connection with Neo4j, and the graph constructor processes the directory input to create the graph.\n\n```python\nfrom blar_graph.graph_construction.graph_builder import GraphConstructor\nfrom blar_graph.graph_construction.neo4j_manager import Neo4jManager\n\ngraph_manager = Neo4jManager()\ngraph_constructor = GraphConstructor(graph_manager)\ngraph_constructor.build_graph("YOUR_LOCAL_DIRECTORY", "python")\ngraph_manager.close()\n```\n\nNow you can use our agent tools, or build your own, to create agents that resolves specific tasks. In the folder \'agents_tools\' you will find all our tools (for now is just the Keyword search) and examples of agent implementations. For example, for a debugger agent you could do:\n\n```python\nfrom langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder\nfrom langchain.agents.format_scratchpad.openai_tools import (\n    format_to_openai_tool_messages,\n)\nfrom langchain.agents.output_parsers.openai_tools import (\n    OpenAIToolsAgentOutputParser,\n)\nfrom blar_graph.agents_tools.tools.KeywordSearchTool import KeywordSearchTool\nfrom blar_graph.db_managers.base_manager import BaseDBManager\nfrom langchain.agents import AgentExecutor\nfrom langchain_openai import ChatOpenAI\n\nllm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)\n\nsystem_prompt = """\n    You are a code debugger, Given a problem description and an initial function, you need to find the bug in the code.\n    You are given a graph of code functions,\n    We purposly omited some code If the code has the comment \'# Code replaced for brevity. See node_id ..... \'.\n    You can traverse the graph by calling the function keword_search.\n    Prefer calling the function keword_search with query = node_id, only call it with starting nodes or neighbours.\n    Explain why your solution solves the bug. Extensivley traverse the graph before giving an answer\n"""\n\n\nprompt = ChatPromptTemplate.from_messages(\n    [\n        (\n            "system",\n            system_prompt,\n        ),\n        ("user", "{input}"),\n        MessagesPlaceholder(variable_name="agent_scratchpad"),\n    ]\n)\n\ntools = [KeywordSearchTool(db_manager=graph_manager)]\nllm_with_tools = llm.bind_tools(tools)\n\nagent = (\n    {\n        "input": lambda x: x["input"],\n        "agent_scratchpad": lambda x: format_to_openai_tool_messages(\n            x["intermediate_steps"]\n        ),\n    }\n    | prompt\n    | llm_with_tools\n    | OpenAIToolsAgentOutputParser()\n)\n```\n\nNow you can ask yur agent to perform a debugging process.\n\n```python\nlist(\n    agent.stream(\n        {\n            "input": """\n            The directory nodes generates multiples conections,\n            it doesn\'t distinguish betweem different directories, can you fix it?\n            The initial functions is run\n            """\n        }\n    )\n)\n```\n\nYou can find more examples in the folder \'examples\'. They are comprehensive jupiter notebooks that guide you from creating the graph to deploying the agent.\n\n*Note: The supported language for now is python, we are going to include Typescript (or other language) if you ask for it enough. So don\'t hesitate to reach out through the [issues](https://github.com/blarApp/code-base-agent/issues) or directly to benjamin@blar.io or jose@blar.io*\n',
    'author': 'Benjamín Errazuriz',
    'author_email': 'benjamin@blar.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://blar.io',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.12',
}


setup(**setup_kwargs)
