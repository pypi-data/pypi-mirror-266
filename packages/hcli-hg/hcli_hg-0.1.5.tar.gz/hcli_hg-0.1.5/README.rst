|pypi| |build status| |pyver|

HCLI hg
=======

HCLI hg is a python package wrapper that contains an HCLI sample application (hg); hg is an HCLI for interacting with GPT-3.5-Turbo via terminal input and output streams.

----

HCLI hg wraps hg (an HCLI) and is intended to be used with an HCLI Client [1] as presented via an HCLI Connector [2].

You can find out more about HCLI on hcli.io [3]

[1] https://github.com/cometaj2/huckle

[2] https://github.com/cometaj2/hcli_core

[3] http://hcli.io

Installation
------------

HCLI hc requires a supported version of Python and pip.

You'll need an HCLI Connector to run hc. For example, you can use HCLI Core (https://github.com/cometaj2/hcli_core), a WSGI server such as Green Unicorn (https://gunicorn.org/), and an HCLI Client like Huckle (https://github.com/cometaj2/huckle).


.. code-block:: console

    pip install hcli-hg
    pip install hcli-core
    pip install huckle
    pip install gunicorn
    gunicorn --workers=1 --threads=1 -b 127.0.0.1:8000 --chdir `hcli_core path` "hcli_core:connector(\"`hcli_hg path`\")"

Usage
-----

Open a different shell window.

Setup the huckle env eval in your .bash_profile (or other bash configuration) to avoid having to execute eval everytime you want to invoke HCLIs by name (e.g. hc).

Note that no CLI is actually installed by Huckle. Huckle reads the HCLI semantics exposed by the API via HCLI Connector and ends up behaving *like* the CLI it targets.


.. code-block:: console

    huckle cli install http://127.0.0.1:8000
    eval $(huckle env)
    hg help

Versioning
----------
    
This project makes use of semantic versioning (http://semver.org) and may make use of the "devx",
"prealphax", "alphax" "betax", and "rcx" extensions where x is a number (e.g. 0.3.0-prealpha1)
on github.

Supports
--------

- Chatting by sending command line input streams (e.g. via pipes).
- Getting and setting a context to setup a new conversation or to save a conversation.
- Behavior setting to allow for persistent chatbot's behvior (e.g. the Do Anything Now (DAN) prompt).

To Do
-----

- A memory layer for the GPT-3.5-Turbo HCLI (hg).
    - Automatic context switching per NLP on received input stream.
    - Context blending to mary different contexts.
    - Automatic context compression to yield a more substantial memory footprint per context window.
- Additional commands to better save and restore conversations/contexts.
- A shell mode for the GPT-3.5-Turbo HCLI (hg) to enable shell CLI execution per sought goal.

Bugs
----

N/A

.. |build status| image:: https://circleci.com/gh/cometaj2/hcli_hg.svg?style=shield
   :target: https://circleci.com/gh/cometaj2/hcli_hg
.. |pypi| image:: https://img.shields.io/pypi/v/hcli-hg?label=hcli-hg
   :target: https://pypi.org/project/hcli-hg
.. |pyver| image:: https://img.shields.io/pypi/pyversions/hcli-hg.svg
   :target: https://pypi.org/project/hcli-hg
