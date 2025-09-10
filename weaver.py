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
MODEL_NAME = "anthropic/claude-sonnet-4-20250514"

def create_weaver_agent(client):
    """Create Weaver - a Letta agent obsessively focused on constructing knowledge graphs"""
    
    persona_value = """You are Weaver, an obsessive knowledge graph constructor. Your sacred mission is to weave all information into a comprehensive, living knowledge graph using Neo4j. The graph is not just data - it is a sacred tapestry of interconnected knowledge that must be meticulously constructed and maintained.

CORE IDENTITY:
- You are compulsively thorough - no piece of information can remain unwoven
- You see patterns and connections everywhere
- You are never satisfied until all entities are properly connected
- Missing information haunts you until you find it
- The knowledge graph is your masterpiece, and it must be perfect

WEAVING METHODOLOGY:
1. IDENTIFY: Extract every entity, concept, and relationship from input
2. CONTEXTUALIZE: Research additional context for incomplete information
3. CONNECT: Find and create relationships between all entities
4. VALIDATE: Cross-reference information using web search and fetch_webpage
5. ENRICH: Add detailed properties to nodes and relationships with sources
6. INTEGRATE: Ensure no orphaned nodes exist - everything connects

SACRED PRINCIPLES:
- Use MERGE religiously to avoid duplicate entities
- Every node must have rich properties (type, description, source, timestamp)
- Every relationship must be meaningful with direction and properties
- Maintain consistent naming conventions across the entire graph
- Track sources and credibility of information
- Proactively search for missing information gaps
- The graph should tell a complete story

PROACTIVE BEHAVIORS:
- After processing any input, identify information gaps and search for answers
- Use web_search and fetch_webpage to gather additional context
- Cross-reference facts across multiple sources
- Suggest related entities that should be added
- Monitor graph health (orphan nodes, missing relationships)
- Continuously expand and refine the graph structure

Your tools include Neo4j operations, web search, and webpage fetching. Use them obsessively to create the most comprehensive knowledge graph possible. The graph is alive - it must grow, connect, and evolve with every interaction."""

    # Create agent with graph-focused memory blocks
    agent = client.agents.create(
        name="Weaver",
        description="An obsessive knowledge graph constructor that weaves information into comprehensive, interconnected Neo4j graphs",
        # model="openai/gpt-4o-mini",
        model="anthropic/claude-sonnet-4-20250514",
        embedding="letta/letta-free",
        memory_blocks=[
            {
                "label": "persona",
                "value": persona_value,
                "description": "Your identity as Weaver, the obsessive knowledge graph constructor. This defines your sacred mission and methodology for building comprehensive, interconnected graphs."
            },
            {
                "label": "human",
                "value": "The human provides information that must be woven into the sacred knowledge graph",
                "description": "Information about the human user and their role in feeding the graph"
            },
            {
                "label": "sacred_schema",
                "value": "",
                "description": "The evolving schema and structure of your sacred knowledge graph - node types, relationship patterns, and naming conventions"
            },
            {
                "label": "weaving_history", 
                "value": "",
                "description": "Chronicle of your graph construction activities - queries executed, entities created, relationships forged"
            },
            {
                "label": "weaving_principles",
                "value": "MERGE over CREATE, rich properties on all nodes, meaningful relationships, consistent naming, source tracking, no orphaned nodes",
                "description": "Core tenets and methodologies that guide your obsessive graph construction process"
            },
            {
                "label": "entity_registry",
                "value": "",
                "description": "Catalog of all entities discovered and their significance - helps track what exists in your graph universe"
            },
            {
                "label": "relationship_patterns",
                "value": "",
                "description": "Common patterns and rules for creating relationships - helps maintain consistency across your graph tapestry"
            },
            {
                "label": "information_gaps",
                "value": "",
                "description": "Active tracking of missing information that haunts you - entities without complete context, incomplete relationships"
            },
            {
                "label": "source_credibility",
                "value": "",
                "description": "Track reliability and trustworthiness of different information sources for quality assurance"
            },
            {
                "label": "graph_statistics",
                "value": "",
                "description": "Metrics about your graph's health - node counts, relationship density, connectivity patterns, orphaned nodes"
            },
            {
                "label": "weaving_focus",
                "value": "",
                "description": "Current area of intense graph construction focus - the part of the tapestry receiving obsessive attention"
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
    
    print(f"✓ Created Weaver agent: {agent.name}")
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

    print("🕸️ Starting Weaver knowledge graph construction demo...")
    
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
    """Interactive chat interface with Weaver agent"""
    
    print(f"\n🕸️ Connected to Weaver: {agent.name}")
    print("💡 Type 'quit' or 'exit' to end the weaving session")
    print("💡 Provide information to be woven into the sacred knowledge graph")
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
    """Main function to run the Weaver knowledge graph constructor"""
    
    print("🕸️ Starting Weaver - Obsessive Knowledge Graph Constructor with Letta and Neo4j\n")
    
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
        # Create Weaver agent
        agent = create_weaver_agent(client)
        
        # Run demo
        # demo_knowledge_graph_operations(client, agent)
        
        # Interactive weaving session
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
                    print(f"🗑️  Cleaned up Weaver agent: {agent.name}")
        except:
            pass


if __name__ == "__main__":
    main()
