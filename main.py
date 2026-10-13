from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  
import uuid
from langchain.mcp import MCPAdapter
from dotenv import load_dotenv
load_dotenv()
import asyncio
from tools import list_directory, read_safe_file
import logging
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("langchain_google_genai._function_utils").setLevel(logging.ERROR)
logging.disable(logging.WARNING)
import warnings
from langchain_core._api import LangChainBetaWarning
warnings.filterwarnings("ignore", category=LangChainBetaWarning)


async def main():

    async def get_response(prompt: str) -> str:
            result = await agent.ainvoke(
                {"messages": [{"role": "user", "content": prompt}]},
                thread_config,
            )
            return result["messages"][-1].text
    
    mcpConfig={
        "mcpServers": {
            "docs-langchain": {
            "url": "https://docs.langchain.com/mcp"
            },
            "memory": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-memory"
                ]
            },
            "filesystem": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                r"C:\Users\BuffBard\Documents\Folder\AI_folder"
            ]
            },
        }
        
    }
    async with MCPAdapter(mcpConfig) as adapter:
        mcpTools = await adapter.list_tools()
        agent = create_agent(
            model="google_genai:gemini-flash-lite-latest",
            tools=[read_safe_file, list_directory,*mcpTools],
            checkpointer=InMemorySaver(),
        )
        thread_config = {"configurable": {"thread_id": uuid.uuid4()}}
    

        while True:
            print("\n-------- User ---------")
            try:
                prompt = input("Input: ")
                if prompt == "exit": break
                response = await get_response(prompt)
            except EOFError:
                break
            print("\n--------- AI ----------")
            print(response)
    

if __name__ == "__main__":
    asyncio.run(main())