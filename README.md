# Multi-perspective Identification of Event Groups for Event Abstraction

Prototype of the appproach presented in 
<i>Rebmann, A., Pfeiffer, P., Fettke, P., and van der Aa, H.: Multi-perspective Identification of Event Groups
for Event Abstraction</i> under submission for the Third International Workshop on Event Data and Behavioral Analytics.

## About
An approach that suggests multi-perspective groups of low-level events for event abstraction. 
It does not require the user to provide input upfront, but allows them
to inspect and select groups of events that are related based on their common
multi-perspective contexts. To achieve this, our approach learns representations
of events that capture this context and automatically identifies and suggests interesting groups of related events. 
The user can inspect group descriptions and select meaningful groups to abstract the low-level log. 

The scenario description and models to generate the data used in the proof of concept can be found in the notebook 
<code>simulationmodels.ipynb</code>, to create the event log use the notebook <code>simulation/simulation_event_abstraction.ipynb</code>

The high-level model looks like this

![alt text](https://github.com/a-rebmann/exploratory-abstraction/blob/master/high-level.png?raw=true)

Note, that the code for training the MPPN in the masked attribute task cannot be included in this repository. 
Thus, we provide the set R of representations for download (see below).
If you are interested in the code, please contact <i>peter.pfeiffer@dfki.de</i>.

## Setup
1. create virtual env
2. install requirements in requirements.txt via pip
3. Place the <a href="https://www.dropbox.com/s/cltxwb2dik203mc/MPPNMultiTaskAbstractionSynthetic_v3_concept-name_org-role_org-resource_isComplete_isAccepted__time-timestamp_big_pd_cases_fv_fine.pkl?dl=0">trained representations R</a> in the <code>input</code> directory
## Usage
run <code>main.py</code>

## MPPN
The original MPPN, which is trained by predicting the next attributes values instead of filling masks is described in https://doi.org/10.1007/978-3-030-85469-0_21 
