import streamlit as st
import plotly.figure_factory as ff
import numpy as np

# Add histogram data
# x1 = np.random.randn(200) - 2
# x2 = np.random.randn(200)
# x3 = np.random.randn(200) + 2
#
# # Group data together
# hist_data = [x1, x2, x3]
#
# group_labels = ['Group 1', 'Group 2', 'Group 3']
#
# # Create distplot with custom bin_size
# fig = ff.create_distplot(
#          hist_data, group_labels, bin_size=[.1, .25, .5])
#
# # Plot!
# st.plotly_chart(fig, use_container_width=True)

import pandas as pd
from const import *
from clustering.retrieve import compute_similarities, retrieve_most_similar_events
from read import reader
from clustering import preprocessing
from clustering.clusterer import Clusterer
from config import Config
import plotly.express as px
# the config object
config = Config("input/", "output/", "Mobis.csv", dict(), "MPPNTaskAbstractionMobIS_pd_cases_fv_fine_1", clust="k_means")


result, loaded = reader.load_result(config)

clr = XES_NAME_DF
#px.figure(figsize=(30, 30), dpi=300)
fig = px.scatter(result.pca, x="x", y="y", color=clr, width=800, height=800)

st.header('Event representation space of the '+ result.config.log_name+ ' event log')
# Plot!
st.plotly_chart(fig, use_container_width=True)

container = st.container()
for clust_num, clust_description in result.description.items():
    container.write("### Description of event group " + str(clust_num))
    container.write(clust_description)