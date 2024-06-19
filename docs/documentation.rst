Get Started
===========

Pipesim is a tool for simulating water residence times in a plumbing system inside a building (“premise plumbing”).

It takes as input the pipe network e.g. from building blueprints, and a time series of flow events at outlets such as fountains or faucets, and simulates aging of water in the system as well as disinfectant decay and resulting concentrations. 
 
Ages and concentrations at effluent water are computed, with some simple automatic graphing of these quantities. Pipesim is a “particle-tracking” code in that is sprinkles imaginary particles both initially along the entire network and in the influent during flow events.

Each particle has a list of attributes including Age (total, and age in each pipe traversed) and disinfectant concentration (that decays according to specified rates). The simulation will run at time steps specified by the user and for a total Run Time before producting charts and raw data. Simple demonstration files are provided to exploring how the code works.

Accessing PipeSim
*****************

PipeSim can be accessed in multiple ways. The easiest involves visiting the PipeSim  `Web App <https://psim-app-2ngq6iwzrq-uw.a.run.app/>`_ 

For Windows users, an executable version of the program can be installed directly from the *install* branch our `GitHub <https://github.com/aidanmgriffin/Pipesim-App/tree/install>`_

Cloning the *no-install* branch of the `GitHub <https://github.com/aidanmgriffin/Pipesim-App/tree/no-install>`_ and running app.py will allow PipeSim to run on LocalHost:5000