.. PipeSim documentation master file, created by
   sphinx-quickstart on Wed Jun 12 13:41:55 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PipeSim's documentation!
===================================

Pipesim is a tool for simulating water residence times in a plumbing system inside a building (“premise plumbing”).

It takes as input the pipe network e.g. from building blueprints, and a time series of flow events at outlets such as fountains or faucets, and simulates aging of water in the system as well as disinfectant decay and resulting concentrations. 
 
Ages and concentrations at effluent water are computed, with some simple automatic graphing of these quantities. Pipesim is a “particle-tracking” code in that is sprinkles imaginary particles both initially along the entire network and in the influent during flow events.

Each particle has a list of attributes including Age (total, and age in each pipe traversed) and disinfectant concentration (that decays according to specified rates). The simulation will run at time steps specified by the user and for a total Run Time before producting charts and raw data. Simple demonstration files are provided to exploring how the code works.

.. toctree::
   Get Started <get_started>
   Build a Simulation <build_sim>
   Simulation Arguments <sim_arguments>
   Outputs <outputs>
   Download Logs <download_logs>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

