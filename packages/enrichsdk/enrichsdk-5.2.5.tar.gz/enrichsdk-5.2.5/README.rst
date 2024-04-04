==========
Enrich SDK
==========

Enrich is a customizable, privacy law-aware enterprise Feature Store
of `Scribble Data`_. This SDK is part of the feature store stack. It
enables local development, testing and documentation of simple to
complex feature transformations and other modules required for
building and managing robust features.

This is not for general purpose use. Please get in touch with us at
hello@scribbledata.io to discuss potential use of this SDK.

For enterprise users of Enrich, the documentation is available on the
server. Please see the Developer section.

.. _Scribble Data: https://www.scribbledata.io


Usage
---------------

1. sudo apt-get update
2. sudo apt-get install python3.8-dev python3.8-venv
3. python3 -m venv venv
4. pip3 install wheel
5. pip3 install enrichsdk
6. enrichpkg start

Docs
---------------

1. python3 -m venv venv
2. pip3 install -r requirements.txt
3. mkdocs serve

Updating Release Tag
------------------------------

1. Add to $HOME/.bashrc. Make sure you source ~/.bashrc before using::

     function git_move_tag {
        git push origin; git tag -d $1; git tag $1 ; git push origin --tags --force
     }

     function git_push {
        git push origin $1; git push origin $1 --tags ;
        git push origin $1 refs/notes/*
     }

     function git_rm_tag {
        git push origin; git tag -d $1; git push --delete origin $1
     }

2. Bump the version. Version is typically a.b.c::

     # activate the environment
     workon dev
     cd scribble-enrichsdk # cd to the root

     # If bumpversion doesnt exist
     pip install bump2version

     # Check existing tags once
     git tag -l

     # Bump the right version
     bumpversion patch # for updating c
     bumpversion minor # for updating b
     bumpversion major # for updating a

3. Push the changes to github::

     # See above
     git_push master

4. Update deployment version::

     cd scribble-deploy-v2/configuration

     # update enrichsdk_branch
     vi defaults.json

     # Make
     git commit -a -m "Updated enrichsdk version"

     git push origin

5. Install at customer::

     cd scribble-deploy
     fab install_enrichsdk:role=demo

6. Upload to pypi.::

     python3 setup.py sdist

     # This will require token in ~/.pypirc
     twine upload -r pypi dist/enrichsdk-5.0.4.tar.gz

     cat ~/.pypirc
     [pypi]
     username = __token__
     password = pypi-AgEIcHlwaS5v...

7. Known issues

   The package dependencies are a jungle.Problematic packages include:

   boto3
   botocore
   aiobotocore
   jupyter-events
   nbconvert

   Use the fix environment script to monkey-patch any dependencies in the worst case::

        ./bin/fix-environment.py
        Usage: fix-environment.py [OPTIONS] COMMAND [ARGS]...

          This package will help fix the environment

        Options:
          --help  Show this message and exit.

        Commands:
          lib  Fix a library dependency


