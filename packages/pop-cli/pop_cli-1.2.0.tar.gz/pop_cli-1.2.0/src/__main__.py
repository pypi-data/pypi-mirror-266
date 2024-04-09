import asyncio

import pop.hub

try:
    import uvloop

    HAS_UVLOOP = True
except ImportError:
    HAS_UVLOOP = False


def main():
    # Initialize the event loop
    if HAS_UVLOOP:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # Set the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Start the async code
    asyncio.run(amain())


async def amain():
    # Create the hub within an async context
    hub = await pop.hub.AsyncHub(cli="cli")

    # Start the hub cli
    await hub.cli.init.run()


if __name__ == "__main__":
    main()
