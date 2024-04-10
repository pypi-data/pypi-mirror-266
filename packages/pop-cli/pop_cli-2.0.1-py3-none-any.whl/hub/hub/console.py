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

    # Prepare the local namespace for execution
    local_namespace = {"hub": hub, **kwargs}

    # Set up hub and locals completion
    completer = await hub.cli.console.get_completer(**kwargs)

    session = hub.lib.prompt_toolkit.PromptSession(
        history=hub.lib.prompt_toolkit.history.FileHistory(history_file),
        completer=completer,
    )

    print(BANNER)

    # Start the interactive loop
    while True:
        try:
            user_input = await session.prompt_async(">>> ")
            if user_input.strip():
                previous = {k: v for k, v in local_namespace.items() if k != "hub"}
                # Modify the user input to capture the result
                modified_input = f"__result__ = {user_input}"

                try:
                    # Try to execute the modified input
                    await hub.lib.aioconsole.aexec(modified_input, local_namespace)

                except SyntaxError:
                    # If it's a syntax error, execute the original input
                    await hub.lib.aioconsole.aexec(user_input, local_namespace)

                result = local_namespace.pop("__result__", None)
                post = {k: v for k, v in local_namespace.items() if k != "hub"}

                # The locals didn't change, this wasn't a variable assignment
                if previous == post:
                    # If an async function was called without being assigned to a variable then await it
                    if hub.lib.asyncio.iscoroutine(result):
                        result = await result

                    # If the result wasn't assigned to a variable then print it out
                    if result is not None:
                        print(result)

        except EOFError:
            # Exit handling...
            break
        except KeyboardInterrupt:
            # Keyboard interrupt handling...
            break
        except Exception:
            # Error handling...
            await hub.log.error(hub.lib.traceback.format_exc())


async def get_completer(hub, **kwargs):
    """
    Creates a completer for the interactive console that provides completion suggestions for the 'hub' namespace.

    Args:
        hub (pop.hub.Hub): The global namespace.

    Returns:
        HubCompleter: A completer object for the interactive console.
    """

    class HubCompleter(hub.lib.prompt_toolkit.completion.Completer):
        def get_completions(self, document, complete_event):
            # Get the text before the cursor
            text = document.text_before_cursor
            # Find the start index of the "hub." reference
            hub_ref_start = text.find("hub.")

            # Check if "hub." is present in the text
            if hub_ref_start != -1:
                # Remove "hub." prefix and split the reference into parts
                ref = text[hub_ref_start + 4 :]
                parts = ref.split(".")
                # Start with the hub as the root of the reference
                finder = hub
                # Iterate over parts except the last one to traverse the hub namespace
                for p in parts[:-1]:
                    if not p:
                        continue
                    try:
                        finder = getattr(finder, p)
                    except AttributeError:
                        try:
                            finder = finder.__getitem__(p)
                        except TypeError:
                            if p.isdigit() and isinstance(
                                finder, hub.lib.typing.Iterable
                            ):
                                try:
                                    finder = tuple(finder).__getitem__(int(p))
                                except Exception:
                                    # No completions if the path is invalid
                                    return
                            else:
                                # No completions if the path is invalid
                                return
                        except KeyError:
                            # No completions if the path is invalid
                            return

                # Get the prefix of the current attribute being completed
                current_attr_prefix = parts[-1]
                attrs = []
                try:
                    # Get all attributes and methods of the current object in the hub namespace
                    attrs += [_ for _ in finder]
                except Exception:
                    ...

                try:
                    attrs += [attr for attr in dir(finder) if attr not in attrs]
                except Exception:
                    ...

                # Yield completions that match the current attribute prefix
                for name in attrs:
                    try:
                        if name.startswith(current_attr_prefix):
                            display = f"hub.{'.'.join(parts[:-1] + [name])}"
                            yield hub.lib.prompt_toolkit.completion.Completion(
                                name,
                                start_position=-len(current_attr_prefix),
                                display=display,
                            )
                    except:
                        continue

    completer = HubCompleter()
    # Create a completer for local variables
    local_completer = hub.lib.prompt_toolkit.completion.WordCompleter(
        list(kwargs.keys()), ignore_case=True
    )

    # Create a completer for built-in functions
    builtins = list(dir(hub.lib.builtins)) + ["await", "hub"]
    builtins_completer = hub.lib.prompt_toolkit.completion.WordCompleter(
        builtins, ignore_case=True
    )

    # Combine the hub, local, and built-in completers
    combined_completer = hub.lib.prompt_toolkit.completion.merge_completers(
        [completer, local_completer, builtins_completer]
    )
    return combined_completer
