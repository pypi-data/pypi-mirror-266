Liacord
==========

.. image:: https://discord.com/api/guilds/930415100718878750/embed.png
   :target:https://discord.gg/H7FQFGEPz5
   :alt: Discord server invite
.. image:: https://img.shields.io/pypi/v/Liacord.svg
   :target: https://pypi.python.org/pypi/discord.py
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/discord.py.svg
   :target: https://pypi.python.org/pypi/Liacord
   :alt: PyPI supported Python versions

Key Features
-------------

- Modern Pythonic API using ``async`` and ``await``.
- Proper rate limit handling.
- Optimised in both speed and memory.

Installing
----------

**Python 3.8 or higher is required**

To install the library without full voice support, you can just run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U Liacord

    # Windows
    py -3 -m pip install -U Liacord

Bot Example
~~~~~~~~~~~~~

.. code:: py

    import asyncio
    from Liacord import Client, Intents
    
    intents = Intents().all()
    client = Client("your_token_here", prefix="#", intents=intents)
    
    @client.command(name="name")
    async def hello(ctx):
        await ctx.send(f"{ctx.author.name}")
    
    @client.command(name="ping")
    async def ping(ctx):
        await ctx.send(f"pong {round(client.latency)}ms.")
    
    @client.command(name='server_id', brief='get the server id')
    async def server_id_command(ctx):
        server_id = ctx.guild.id
        await ctx.send(f"server id: {server_id}")
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.run())

You can find more examples in the examples directory.

Links
------

- `Documentation No`_
- `Official Discord Server <https://discord.gg/H7FQFGEPz5>`_
- `Discord API <https://discord.gg/discord-api>`_
