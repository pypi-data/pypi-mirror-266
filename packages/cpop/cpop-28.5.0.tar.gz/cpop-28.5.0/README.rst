====
cPOP
====

cPop is used to express the Plugin Oriented Programming Paradigm. The Plugin
Oriented Programming Paradigm has been designed to make pluggable software
easy to write and easy to extend.

Plugin Oriented Programming presents a new way to scale development teams
and deliver complex software. This is done by making the applications entirely
out of plugins, and also making the applications themselves natively pluggable
with each other.

Using Plugin Oriented Programming it then becomes easy to have the best of both
worlds, software can be built in small pieces, making development easier to
maintain. The small pieces can then be merged and deployed in a single
binary, making code deployment easy as well.

All this using Cython, one of the world's most popular and powerful programming
languages.

Getting Started
===============

First off, install ``cPop`` from pypi:

.. code-block:: bash

    pip3 install cPop

Now all it takes to create a pluggable application is a few lines of code.
This is the root of every pop project.
We create a hub, we add dynamic subsystems, and then we call them through the hub's namespace.

.. code-block:: python

    import pop.hub

    # Create the hub, which initializes its own event loop
    hub = pop.hub.Hub()

    # Run the main coroutine, which uses the hub's event loop
    hub._sync.my_sub.init.cli()


You can also initialize pop from the cli:

.. code-block:: bash

    python -m hub my_sub.init.cli

or:

.. code-block:: bash

    hub my_sub.init.cli

Specify a namespace that should host the authoritative CLI by calling using --cli as the first argument:

.. code-block:: bash

    hub --cli=my_app my_sub.init.cli

If you don't specify a --cli, unknown args will be forwarded as parameters to the reference you give:


.. code-block:: bash

    hub pop.test.func arg1 arg2 --kwarg1=asdf --kwarg2 asdf


You can access anything that is on the hub, this is very useful for debugging.

Try this to see the subs that made it onto the hub:

.. code-block:: bash

    hub _subs

You can do this to see everything that made it into hub.OPT:

.. code-block:: bash

    hub OPT


When creating a cpop app, we put all of the pop configuration in a config.yaml

.. code-block:: yaml

    # Every config option for your plugin
    config:
        my_namespace:
            my_opt:
                default: True

    # Options that should be exposed on the CLI when your app controls the CLI
    cli_config:
        my_namespace:
            my_opt:
                # All options that are accepted by ArgParser.add_argument are good here
                help: description of this option
                subcommands:
                    - my_subcommand
                group: My arg group

    # Subcommands to expose for your project
    subcommands:
        my_namespace:
            my_subcommand:
                help: My subcommand

    # Dynamic namespaces that your app merges onto and which folders extend those namespaces
    dyne:
        my_dyne:
        - src_dir

    # python imports that your app uses which should be added to hub.lib for your app
    import:
        - asyncio
        - importlib
        - importlib.resources
        - os
        - toml

Create a pop config file:

.. code-block:: yaml

    # The default location is in ~/.pop/config.yaml
    # But you can change that by setting the POP_CONFIG environment variable

    pop_cli:
        # Setting this option will make your hub persist on the cli between calls
        hub_state: ~/.pop/hub.msgpack
    log:
        log_plugin: async

From the above example, all arguments would be loaded onto the namespace under hub.OPT.my_namesapce.
One config.yaml can add config options to multiple namespaces.
They are all merged together in the order they are found in sys.path


Testing
=======
Clone the repo

.. code-block:: bash

    git clone https://gitlab.com/Akm0d/cpop.git
    cd cpop

Install ``cpop`` with the testing extras

.. code-block:: bash

    pip3 install .\[test\]

Run the tests in your cloned fork of cPop:

.. code-block:: bash

    pytest tests


Documentation
=============

Check out the docs for more information:

https://pop.readthedocs.io

There is a much more in depth tutorial here, followed by documents on how to
think in Plugin Oriented Programming. Take your time to read it, it is not long
and can change how you look at writing software!
