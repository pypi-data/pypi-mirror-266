PROMPT = """
"""


async def run(hub, **kwargs):
    """
    Run an interractive python console that contains the hub

    Args:
        hub (pop.hub.Hub): The global namespace.
        kwargs (dict): Any locals to add to the console namespace.
    """
    await hub.lib.aioconsole.interact(locals=dict(hub=hub, **kwargs))
