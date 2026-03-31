import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.openrouter import OpenRouter

from core.cli_chat import CliChat
from core.cli import CliApp


load_dotenv()

# OpenRouter Config
openrouter_model = os.getenv("OPENROUTER_MODEL", "")

assert openrouter_model, "Error: OPENROUTER_MODEL cannot be empty. Update .env"
assert os.getenv("OPENROUTER_API_KEY"), (
    "Error: OPENROUTER_API_KEY cannot be empty. Update .env"
)


async def main():
    server_scripts = sys.argv[1:]
    clients = {}

    command, args = (
        ("uv", ["run", "mcp_server.py"])
        if os.getenv("USE_UV", "0") == "1"
        else ("python", ["mcp_server.py"])
    )

    async with AsyncExitStack() as stack:
        doc_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        clients["doc_client"] = doc_client

        for i, server_script in enumerate(server_scripts):
            client_id = f"client_{i}_{server_script}"
            client = await stack.enter_async_context(
                MCPClient(command="uv", args=["run", server_script])
            )
            clients[client_id] = client

        openrouter_service = OpenRouter(model=openrouter_model)
        cli = CliChat(
            doc_client=doc_client,
            clients=clients,
            openrouter_service=openrouter_service,
        )
        app = CliApp(cli)
        await app.initialize()
        await app.run()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
