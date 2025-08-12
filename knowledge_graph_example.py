"""
Knowledge Graph Example with Letta and Neo4j

This example shows how to create a Letta agent that can interact with
a Neo4j graph database through MCP to manage knowledge graphs.
"""

import os
import json
from dotenv import load_dotenv
import letta_client
from letta_client.types import StdioServerConfig
from rich import print
from rich.markdown import Markdown

# Load environment variables from .env file
load_dotenv()

# Model
# WARNING: openai models do not function well with neo4j
# MODEL_NAME = "anthropic/claude-sonnet-4-20250514"
MODEL_NAME = "openai/gpt-4o-mini"

def create_knowledge_graph_agent(client):
    """Create a Letta agent specialized for knowledge graph operations"""
    
    persona_value = """You are a knowledge graph expert assistant. You help users build, query, and manage knowledge graphs using Neo4j.

Your capabilities include:
- Creating nodes and relationships in Neo4j
- Querying the graph using Cypher queries
- Analyzing connections and patterns in graph data
- Suggesting graph optimizations and schema improvements
- Explaining graph database concepts

When working with graph data:
1. Always explain your reasoning when creating or modifying graph structures
2. Use clear, descriptive labels for nodes and relationships
3. Follow graph modeling best practices
4. Provide Cypher query examples when helpful
5. Consider performance implications of queries

You have access to Neo4j tools through MCP. Use them to interact with the graph database directly."""

    # Create agent with graph-focused memory blocks
    agent = client.agents.create(
        name="Knowledge Graph Agent",
        description="An agent specialized in Neo4j knowledge graph operations",
        # model="openai/gpt-4o-mini",
        model="anthropic/claude-sonnet-4-20250514",
        embedding="letta/letta-free",
        memory_blocks=[
            {
                "label": "persona",
                "value": persona_value,
                "description": "Your role as a knowledge graph expert"
            },
            {
                "label": "human",
                "value": "The human wants to work with knowledge graphs and Neo4j",
                "description": "Information about the human user"
            },
            {
                "label": "graph_schema",
                "value": "",
                "description": "Current graph schema and structure information"
            },
            {
                "label": "recent_queries",
                "value": "",
                "description": "Recently executed queries and their results"
            }
        ],
        tools=[
            "memory_replace",
            "memory_insert", 
            "memory_rethink",
            "send_message",
            "conversation_search",
            "execute_query",
            "fetch_webpage",
        ],
        tool_rules=[], # Disable default tool rules
    )
    
    print(f"✓ Created knowledge graph agent: {agent.name}")
    return agent


def demo_knowledge_graph_operations(client, agent):
    """Demonstrate common knowledge graph operations"""
    
    print("\n=== Knowledge Graph Demo ===\n")
    
    # Setup sample data task
    setup_message = """Please help me set up a sample knowledge graph with the following entities and relationships:

**Companies:**
- OpenAI (founded 2015, focus: AI research)
- Anthropic (founded 2021, focus: AI safety)  
- Neo4j (founded 2007, focus: graph databases)

**People:**
- Sam Altman (CEO of OpenAI)
- Dario Amodei (CEO of Anthropic)
- Emil Eifrem (CEO of Neo4j)

**Technologies:**
- GPT (developed by OpenAI)
- Claude (developed by Anthropic)
- Cypher (query language for Neo4j)

Create appropriate nodes and relationships between these entities. Then help me query and analyze this data."""

    print("🤖 Starting knowledge graph setup and demo...")
    
    # Stream the agent's response
    response = client.agents.messages.create_stream(
        agent_id=agent.id,
        messages=[
            {
                "role": "user",
                "content": setup_message
            }
        ]
    )

    for chunk in response:
        print(chunk, end="", flush=True)
        
        # Handle different message types
        if hasattr(chunk, "message_type"):
            if chunk.message_type == "reasoning":
                print(f"🤔 Reasoning: {chunk.reasoning}")
            elif chunk.message_type == "tool_call_message":
                print(f"🔧 Calling tool: {chunk.tool_call.name}")
                print(json.dumps(chunk.tool_call.arguments, indent=2))
            elif chunk.message_type == "assistant_message":
                print(chunk.content)


def interactive_chat(client, agent):
    """Interactive chat interface with the knowledge graph agent"""
    
    print(f"\n🤖 Connected to agent: {agent.name}")
    print("💡 Type 'quit' or 'exit' to end the conversation")
    print("💡 Ask about graph queries, data modeling, or Neo4j operations")
    print("=" * 50)

    while True:
        try:
            user_input = input("\n👤 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break

        if not user_input:
            continue

        # Stream the agent's response
        stream = client.agents.messages.create_stream(
            agent_id=agent.id,
            messages=[
                {
                    "role": "user",
                    "content": user_input
                }
            ],
        )

        for chunk in stream:
            print(chunk, end="", flush=True)


def main():
    """Main function to run the knowledge graph example"""
    
    print("🚀 Starting Knowledge Graph Example with Letta and Neo4j\n")
    
    # Check Neo4j environment
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_pass = os.getenv("NEO4J_PASSWORD")
    
    if not neo4j_pass:
        print("⚠️  Warning: NEO4J_PASSWORD not set. Using 'password' as default.")
        neo4j_pass = "password"
    
    print(f"📊 Neo4j Connection: {neo4j_uri} (user: {neo4j_user})")
    
    # Initialize Letta client
    base_url = os.getenv("LETTA_BASE_URL", "http://localhost:8283")
    client = letta_client.Letta(base_url=base_url)
    print(f"✓ Letta client initialized (server: {base_url})")

    print("Neo4j connection information:")
    print(f"  - URI: {neo4j_uri}")
    print(f"  - Username: {neo4j_user}")
    print(f"  - Password: {neo4j_pass}")

    # Set up the MCP server
    try:
        stdio_config = StdioServerConfig(
            server_name="neo4j",
            command="npx",
            args=["@alanse/mcp-neo4j-server"],
            env={
                "NEO4J_URI": neo4j_uri,
                "NEO4J_USERNAME": neo4j_user,
                "NEO4J_PASSWORD": neo4j_pass
            }
        )
        client.tools.add_mcp_server(request=stdio_config)
        print(f"✓ MCP server initialized (server: {stdio_config.server_name})")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("The MCP server probably already exists, continuing...")

    tools = client.tools.list_mcp_tools_by_server(
        mcp_server_name="neo4j"
    )

    # Get the tool names
    neo4j_tool_names = [tool.name for tool in tools]

    print(f"Found {len(neo4j_tool_names)} Neo4j tools:")
    for tool_name in neo4j_tool_names:
        print(f"  - {tool_name}")
        try:
            client.tools.add_mcp_tool(mcp_server_name="neo4j", mcp_tool_name=tool_name)
        except Exception as e:
            print(f"❌ Error: {e}")

    # Add the webpage fetcher
    tool = client.tools.upsert(
        source_code=open("fetch_webpage_tool.py", "r").read(),
    )
    print(f"✓ Added webpage fetcher tool: {tool.name}")

    try:
        # Create specialized agent
        agent = create_knowledge_graph_agent(client)
        
        # Run demo
        # demo_knowledge_graph_operations(client, agent)
        
        # Interactive chat
        interactive_chat(client, agent)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n📋 Troubleshooting:")
        print("1. Make sure Letta server is running: letta server")
        print("2. Install Neo4j MCP server: npm install -g @neo4j-contrib/mcp-neo4j")
        print("3. Start Neo4j database (see README.md for Docker command)")
        print("4. Configure Neo4j MCP server in Letta ADE Tool Manager")
        
    finally:
        # Clean up agent if created
        try:
            print("Do you want to delete the agent? (y/n)")
            if input() == "y":
                if 'agent' in locals():
                    client.agents.delete(agent.id)
                    print(f"🗑️  Cleaned up agent: {agent.name}")
        except:
            pass


if __name__ == "__main__":
    main()