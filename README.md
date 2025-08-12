# Knowledge Graph Example

This example demonstrates how to use Letta with a Neo4j graph database through MCP (Model Context Protocol).

All you need to do is run this example, which will construct an agent with graph database tools. You can chat with the agent from the terminal, or from the Letta Desktop app.

## Setup

### 1. Install Letta Desktop

Find the latest version of Letta Desktop [here](https://docs.letta.com/desktop).

Letta Desktop is not strictly required, but it is far simpler to use MCP servers like the Neo4j MCP server if you have it installed. 

Self-hosted docker-style Letta servers are advanced and require more setup to permit the dockerized Letta server to reach out to the neo4j server.

Make sure you add your provider keys to the Letta Desktop settings. You can do this by clicking the "Integrations" tab on the left sidebar:

![Letta Desktop Settings](./integrations.png)

**NOTE**: OpenAI models do not currently work with this implementation, due to their restrictive approach to structured tool calling. We are currently working on a solution. For now, use Anthropic or other providers.

### 2. Install Neo4j

Option A - Docker (Recommended):
```bash
docker run \
    --name neo4j-knowledge-graph \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/password \
    neo4j:latest
```

Option B - Neo4j Desktop or Aura (Cloud)

### 3. Install the MCP Neo4j Server

```bash
npm install -g @alanse/mcp-neo4j-server
```

### 4. Configure Environment

Create a `.env` file:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

### 5. Run the Example

```bash
uv pip install letta
python knowledge_graph_example.py
```

`knowledge_graph_example.py` will drop you into a REPL where you can chat with the agent, though you can also just open the Letta Desktop app and chat with the agent there.

### 6. Look at your graph using the Neo4j Browser

You can query the agent's graph using the Neo4j browser. By default, it will be available at `http://localhost:7474`.

To retrieve your full graph, you can run the following query:

```cypher
MATCH (a)
OPTIONAL MATCH (a)-[b]-(c)
RETURN *
```

Which will return something like this:

![Neo4j Browser](./graph.png)

## What This Example Does

- Creates a Letta agent with Neo4j MCP tools
- Demonstrates querying and updating a knowledge graph
- Shows relationship mapping and entity management
- Includes sample data about companies, people, and technologies