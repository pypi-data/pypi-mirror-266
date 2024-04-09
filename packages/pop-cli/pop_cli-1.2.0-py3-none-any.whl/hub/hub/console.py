BANNER = """
This console is running in an asyncio event loop with a hub.
It allows you to wait for coroutines using the 'await' syntax.
Try: "await hub.lib.asyncio.sleep(1)"
""".strip()


async def run(hub, **kwargs):
    """
    Run an interractive python console that contains the hub

    Args:
        hub (pop.hub.Hub): The global namespace.
        kwargs (dict): Any locals to add to the console namespace.
    """
    history_file = hub.lib.os.path.expanduser(hub.OPT.cli.history_file)
    session = hub.lib.prompt_toolkit.PromptSession(
        history=hub.lib.prompt_toolkit.history.FileHistory(history_file)
    )

    print(BANNER)

    # Prepare the local namespace for execution
    local_namespace = {"hub": hub, **kwargs}

    # Start the interactive loop
    while True:
        try:
            user_input = await session.prompt_async(">>> ")
            if user_input.strip():
                # Modify the user input to capture the result
                modified_input = f"__result__ = {user_input}"

                try:
                    # Try to execute the modified input
                    await hub.lib.aioconsole.aexec(modified_input, local_namespace)
                    result = local_namespace.get("__result__", None)

                    if result is not None:
                        print(result)

                except SyntaxError:
                    # If it's a syntax error, execute the original input
                    await hub.lib.aioconsole.aexec(user_input, local_namespace)

        except EOFError:
            # Exit handling...
            break
        except KeyboardInterrupt:
            # Keyboard interrupt handling...
            break
        except Exception:
            # Error handling...
            await hub.log.error(hub.lib.traceback.format_exc())
