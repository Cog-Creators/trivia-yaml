====================
Trivia Lists -> YAML
====================

Use this script to convert Red-DiscordBot's V2 trivia list format to YAML,
which is used in V3.

Installation
============
::

    pip install trivia-yaml

Usage
=====
Converting a single trivia list::

    trivia-yaml mylist.txt

Converting a folder containing multiple trivia lists::

    trivia-yaml mylists

By default these commands output ``.yaml`` files to a sub-directory named ``yaml_output``.

For outputting files to a particular folder::

    trivia-yaml mylists -t my_output_folder
