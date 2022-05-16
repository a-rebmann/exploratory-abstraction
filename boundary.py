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

# Get event representations from disk
pd_events_fv, loaded = reader.load_mppn_representations(config)


pca_df, pca_rep = preprocessing.pca(pd_events_fv)
print("PCA done")

clust = Clusterer(pd_events_fv, config)
clust.cluster(pca_rep, 27)
print("Clustering done")

# add the cluster labels to the dataframe
pd_events_fv[CLUST_COL] = clust.pred_labels
pca_df[CLUST_COL] = clust.pred_labels


clr = XES_NAME_DF_NUM
#px.figure(figsize=(30, 30), dpi=300)
fig = px.scatter(pca_df["x"], pca_df["y"])

# Plot!
st.plotly_chart(fig, use_container_width=True)