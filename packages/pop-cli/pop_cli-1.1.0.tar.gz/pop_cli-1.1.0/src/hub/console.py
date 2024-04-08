import os

HISTORY_FILE = os.path.expanduser("~/.python_history")

BANNER = """
This console is running in an asyncio event loop with a hub.
It allows you to wait for coroutines using the 'await' syntax.
Try: await hub.lib.asyncio.sleep(1)"
"""


async def run(hub, **kwargs):
    """
    Run an interractive python console that contains the hub

    Args:
        hub (pop.hub.Hub): The global namespace.
        kwargs (dict): Any locals to add to the console namespace.
    """
    hub.lib.readline.parse_and_bind("tab: complete")
    try:
        # Run python interactive hook in order to configure binding and history support
        hub.lib.sys.__interactivehook__()
    except Exception as exc:
        hub.warnings.warn(f"Interactive hook failed: {exc!r}", stacklevel=2)

    await hub.lib.asyncio.sleep(0)

    try:
        hub.lib.readline.read_history_file(HISTORY_FILE)
    except FileNotFoundError:
        pass  # It's okay if the history file doesn't exist

    await hub.lib.aioconsole.interact(
        locals=dict(hub=hub, **kwargs),
        banner=BANNER,
        prompt_control=hub.lib.aioconsole.apython.ZERO_WIDTH_SPACE,
    )

    # Write the history to the file when the console is exited
    hub.lib.readline.write_history_file(HISTORY_FILE)
