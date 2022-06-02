import streamlit as st

from const import *

from read import reader
from config import Config
from main import BPI17_NAME, BPI17_REP
import plotly.express as px
# the config object
config = Config("input/", "output/", BPI17_NAME, dict(), BPI17_REP, clust="k_means")

st.set_page_config(layout="wide")

result, loaded = reader.load_result(config)

clr = XES_NAME_DF
#px.figure(figsize=(30, 30), dpi=300)
fig = px.scatter(result.pca, x="x", y="y", color=clr, width=800, height=800)

st.header('Exploratory Event Abstraction')
st.subheader('Event group recommendation for the ' + result.config.log_name + ' log')

col1, col2 = st.columns(2)
with col1:
    # Plot!
    st.plotly_chart(fig, use_container_width=True)

with col2:
    container = st.container()
    for clustering in result.description.keys():
        for clust_num, clust_description in result.description[clustering].items():
            container.write("#### Description of event group " + str(clust_num+1)+"")
            container.write(clust_description)
