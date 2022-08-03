# Multi-perspective Identification of Event Groups for Event Abstraction

Prototype of the appproach presetned in <i>Rebmann, A., Pfeiffer, P., Fettke, P., and van der Aa, H.: Multi-perspective Identification of Event Groups
for Event Abstraction</i> under submission for the Third International Workshop on Event Data and 
Behavioral Analytics.

## About
An approach that suggests multi-perspective groups of low-level events for event abstraction. 
It does not require the user to provide input upfront, but allows them
to inspect and select groups of events that are related based on their common
multi-perspective contexts. To achieve this, our approach learns representations
of events that capture this context and automatically identifies and suggests in-
teresting groups of related events. The user can inspect group descriptions and
select meaningful groups to abstract the low-level log. 

The scenario description and models to generate the data used in the proof of concept can be found in the notebook <code>simulationmodels.ipynb</code>
## Setup
1. create virtual env
2. install requirements in requirements.txt via pip
3. Place the <a href="https://www.dropbox.com/s/cltxwb2dik203mc/MPPNMultiTaskAbstractionSynthetic_v3_concept-name_org-role_org-resource_isComplete_isAccepted__time-timestamp_big_pd_cases_fv_fine.pkl?dl=0">trained representations</a> in the <code>input</code> directory
## Usage
run <code>main.py</code>

## Learning Representations of Events
The code for Step 1 (learning multi-perspective prepresentations of events) is available <a href="">here</a>. The original approach is described in https://doi.org/10.1007/978-3-030-85469-0_21 
