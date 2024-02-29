Generate scripts that generate your simulations!
================================================

This is a hyper specific script that I use to generate files that will run my Tissue-Simulation-Toolkit simulations.
  It is a bit overcomplicated because I hacked it together from some other pieces that I had lying around. 

Setup
-----

Clone the script 

.. code-block:: bash

  git clone git@github.com:koen219/generatesimulationstructure

Then create a virtual env and install it:

.. code-block:: bash
  python3 -m venv venv
  . ./venv/bin/activate
  python -m pip install generatesimulationstructure

Copy the example directory and hack it so it is usable for you. You manily want to change the template.sh, template.par files. 
  Then you edit the config.py file to specify which parameters you want to try.
  

