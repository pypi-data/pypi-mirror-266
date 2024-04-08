async def restore(hub, opts: dict) -> str:
    # Try to get a saved hub
    if opts.cli.hub_state:
        hub_state = opts.cli.hub_state

        # Evaluate a reference the hub as the hub_state
        if hub_state.startswith('f"'):
            safe_env = {"hub": hub.lib.cpop.data.NamespaceDict(lib=hub.lib)}
            hub_state = eval(hub_state, safe_env)

        # Load the saved state of the hub from a file in memory
        hub_state_file = hub.lib.pathlib.Path(hub_state).expanduser()
        await hub.cli.state.load(hub_state_file)
    else:
        hub_state_file = None

    return hub_state_file


async def load(hub, state_file: str):
    """_summary_
    Read a hub state from a pickle file and add its attributes to the current hub.

    Args:
        hub (pop.hub.Hub): The global namespace
        state_file (str): A pickle file that contains serialized hub data
        cli (str): The cli config to load on the new hub
    """
    if state_file.exists():
        try:
            async with hub.lib.aiofiles.open(state_file, "rb") as f:
                state = hub.lib.pickle.loads(await f.read())
        except Exception:
            return

        if not state:
            return

        if hub._init_kwargs != state["init_kwargs"]:
            # The config has already been loaded and logging has already been initialized
            state["init_kwargs"].pop("cli", None)
            state["init_kwargs"].pop("load_config", None)
            state["init_kwargs"].pop("logs", None)

            # Re-initialize the hub with the parameters from pickled state
            await hub.__ainit__(**state["init_kwargs"], load_config=False, logs=True)


async def save(hub, state_file: str):
    """_summary_
    Serialize the hub and write it to a file.

    Args:
        hub (pop.hub.Hub): The global namespace
        state_file (str): A pickle file to writ ethe serialized hub to.
    """
    # Manually retrieve the state using __getstate__
    state = hub.__getstate__()
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with state_file.open("wb") as f:
        hub.lib.pickle.dump(state, f)
