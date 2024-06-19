********************
Simulation Arguments
********************

When running a new simulation, there are several arguments which must be initially defined. These include diffusion status / rate, particle density, and time granularity.

Diffusion
*********

Diffusion is the net spreading of water particles in the pipe network. This can be turned on or off by selecting/deselecting the "Diffusion Enabled" box while building a simulation. 

The (pre-asymptotic) dispersion coefficient is D(ω) = (D_inf - D_m)(1 - e ^ (- ω / α)) where ω is time in flow, D_m s molecular diffusion coefficient, D_inf is asymptotic dispersion coefficient, and ɑ is a scaling parameter. If you do not wish to model pre-asymptotic dispersion, set α = 1, and D_m = D_inf = the asymptotic diffusion coefficient for each pipe.

Once diffusion is chosen, it can be customized in multiple ways.

**Diffusion Rate**

The rate of diffusion is given in gallons per minute. 

**Diffusion During Stagnant Periods**

Diffusion can be turned on / off for periods of no flow in the pipe system. 

**Diffusion & Dispersion During Advective Periods**

Diffusion & dispersion can be turned on / off for periods of flow in the pipe system. Periods of flow are defined as time periods between an endpoint's starttime and endtime.

Particle Density
****************

The distance (in inches) between particle placements in the pipe network. A smaller particle density value results in more particles being entered into the pipe network. This way of adding particles to the inflow water does not maintain constant particle numbers per inflow volume.

Density range is held within [0.1,1]

Time Granularity
****************

The time increment in which the simulation advances towards the total simulation lifetime, chosen in units of seconds.

i.e. if the total sim lifetime is given as 1 day: 
- If time granularity is chosen as hours (custom granularity of 3600), the simulation will update a total of 24 times. 
- If time granularity is chosen as minutes (custom granularity of 60), the simulation will update a total of 1440 times. 
- If time granularity is chosen as seconds (granularity of 1), the simulation will update a total of 86400 times. 