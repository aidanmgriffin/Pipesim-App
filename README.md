![PipeSim Python Logo](https://github.com/WSUCptSCapstone-Fall2022Spring2023/nsf-pipesimpython/blob/main/Resources/testlogo5.png)

# Python Pipe Simulation Modeling

## National Science Foundation - PipeSim in Python

###  Simulating the pipe system underneath the Paccar building to determine the influence of drinking water chemical composition on biofilm properties and decay of disinfectant residual.

### Abstract and Motivation
Risk of exposure to pathogens such as Legionella and Mycobacteria from drinking water are heightened by long residence times of water in water distribution systems and elimination of disinfection agents such as chlorine through contact with biofilms inside pipe networks.   Municipal water distribution systems are multiscale, mainly dendritic networks analogous to mature trees, with large diameter main pipes (trunks) terminating at a large number of taps (leaves) connected through small diameter lines (twigs).  Both the accumulation of residence time (age), and the specific surface area in such systems are maximal in the final branches and twigs of the network, typically in “premise plumbing”, that is, the pipe network inside buildings.  Consequently there is a critical need for simulation tools that can identify locations of maximum residence time and minimum disinfection agents in premise plumbing drinking water networks.

Prof. Timothy Ginn is seeking a team of students to extend an existing (Python) code that keeps track of water ages in a building pipe network and to apply the code to the cold water premise plumbing subnetwork of the PACCAR building on the WSU campus.  The code, “Pipesim,” authored by WSU CS student Nikita Ostrander working as a research assistant in the Ginn lab 2020-2021, has been validated and is computationally stable.  Pipesim simulates transient flows in the network in response to flow events at taps such as water fountains, kitchen faucets, and toilets, and uses a “particle-tracking” approach to compute ages of water throughout the pipe network at one-second resolution in time.  Typical simulations span months, so with one-second resolution of water ages that vary in time, the code generates massive data sets.  
