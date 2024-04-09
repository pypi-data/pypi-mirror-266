async def find(hub, ref: str) -> object:
    """
    Take a string that represents an attribute nested underneath the hub.
    Parse the string and retrieve the object form the hub.

    Args:
        hub (pop.hub.Hub): The global namespace.
        ref (str): A string separated by "." with each part being a level deeper into objects on the hub.

    Returns:
        any: The object found on the hub
    """
    # Get the named reference from the hub
    finder = hub
    parts = ref.split(".")
    for p in parts:
        if not p:
            continue
        try:
            # Grab the next attribute in the reference
            finder = getattr(finder, p)
        except AttributeError:
            try:
                # It might be a dict-like object, try getitem
                finder = finder.__getitem__(p)
            except TypeError:
                # It might be an iterable, if the next part of the ref is a digit try to access the index
                if p.isdigit() and isinstance(finder, hub.lib.typing.Iterable):
                    finder = tuple(finder).__getitem__(int(p))
                else:
                    raise
    return finder


async def resolve(hub, ref: object, *args, **kwargs) -> object:
    """
    Take an object found on the hub and if it is a funciton, call it.
    If it is a generator, retrieve all its values.
    As a last resort just return the plain object as is.

    Args:
        hub (pop.hub.Hub): The global namespace
        ref (object): An object found on the hub
    """
    try:
        if hub.lib.asyncio.iscoroutinefunction(ref) or isinstance(
            ref, (hub.lib.typing.Callable, hub.lib.cpop.contract.Contracted)
        ):
            # Call the named reference on the hub
            ret = ref(*args, **kwargs)
            # If the return was an Async Generator, then yield all the results
            if hub.lib.inspect.isasyncgen(ret):
                ret = [_ async for _ in ret]
            # If the return was a coroutine then await it
            elif hub.lib.asyncio.iscoroutine(ret):
                ret = await ret
        else:
            # This wasn't a callable function, just return the object on the hub
            ret = ref
    except Exception as e:
        await hub.log.error(f"Error calling {ref}: {e}")
        ret = ref

    return ret


async def output(hub, ret: object):
    """
    Output a serialized version of the given object to the console.

    Args:
        hub (pop.hub.Hub): The global namespace
        ret (object): A resolved object from the hub
    """
    if isinstance(ret, int):
        hub.lib.sys.exit(ret)
    elif isinstance(ret, str):
        print(ret)
    else:
        try:
            hub.lib.pprint.pprint(ret.__dict__)
        except Exception:
            if ret is not None:
                hub.lib.pprint.pprint(ret)
