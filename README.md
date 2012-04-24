PyBossa data reconciliation application
=======================================

This is a hastily hacked together attempt at a data reconciliation game for PyBossa. Built at National Hack The Government Day 2012, it's aimed at breaking down the problem of data reconciliation into small chunks. For an introduction to how this is usually done, see [this introduction](http://onlinejournalismblog.com/2011/07/05/cleaning-data-using-google-refine-a-quick-guide/) to Google Refine's data cleaning features.

**NB**: Due to limitations in the PyBossa API, you must currently run an additional backend for the game, which you can do by running `backend.py`. It should be possible to integrate some or all of this backend into PyBossa core. Fancy a short project?

Getting setup
-------------
  
First you'll need to setup and run PyBossa. See the [PyBossa documentation](http://pybossa.readthedocs.org/en/latest/install.html). Once you've got that working, you can install the requirements for the backend and run it:

    pip install -r requirements.txt
    PORT=5001 python backend.py

How to load data
----------------

Create a data file (say, `names.txt`) consisting of one name per line, e.g.:

    Department of Health
    Dept of Health
    Health, Department of
    DoH
    Home Office
    ...

Load the data into PyBossa (this might take a while if you have several thousand names) and the backend:

    python createTasks.py -k <PYBOSSA_API_KEY> <names.txt
    curl -XPUT  -H 'Content-type: text/plain' 127.0.0.1:5001/names --data-binary @names.txt

Visit PyBossa (probably running on 127.0.0.1:5000) and play "Identify"!

How to get access to reconciliations
------------------------------------

Once you've been playing Identify for a while, you'll have built up a load of reconciliations. You can either get these out of PyBossa (for which see their documentation), allowing you to compare different users' proposed reconciliations, or you can just see the latest reconciliations in the backend by running:

    curl 127.0.0.1:5001

Disclaimer
----------

This is meant to be a proof-of-concept hack, not a fully-functional application. The algorithm for deciding match likelihood isn't particularly intelligent (a simple Levenshtein distance comparison). The aim was to show that reconciliation can be broken down into easy chunks -- a lot more work needs to be done before this can compete with the likes of Google Refine.

That said, it's open source, released under the terms of the MIT license, so please do feel free to fork and improve it.