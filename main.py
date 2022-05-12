import time
import sys

from recommendation.group_property_computation import PropertyComputer
from recommendation.text_generation import TextGen
from clustering import preprocessing
from clustering.clusterer import Clusterer
from clustering.retrieve import compute_similarities, retrieve_most_similar_events
from config import Config
from const import CLUST_COL
from read import reader

config = Config("input/", "output/", "MPPNTaskAbstractionMobIS_pd_cases_fv_fine_1", clust="k_means")


def main():
    # first read the representations leaned
    pd_events_fv, loaded = reader.load_mppn_representations(config)
    if loaded:
        # Do PCA
        pca, pca_rep = preprocessing.pca(pd_events_fv)
        preprocessing.viz(pca)

        # Cluster
        clust = Clusterer(pd_events_fv, config)
        # TODO how to set number of clusters?
        # TODO how to rank different clusters?
        clust.cluster(pca_rep, 27)
        pd_events_fv[CLUST_COL] = clust.pred_labels

        # Compute key properties
        props = PropertyComputer(pd_events_fv)
        props.compute_props_for_clusters()

        # Generate cluster descriptions
        text_gen = TextGen(pd_events_fv, props.clust_to_prop)
        text_gen.generate_descriptions_for_clusters()

        for clust, clust_description in text_gen.description.items():
            print(clust, clust_description)


        # Get similar events
        #pd_events_fv = compute_similarities(pd_events_fv)
        # Retrieve most similar events
        #retrieve_most_similar_events(pd_events_fv, 5523, 1, top_n=5)
    else:
        print(config.log_name, "could not be loaded")
        return




if __name__ == '__main__':
    main_tic = time.perf_counter()
    main()
    main_toc = time.perf_counter()
    print(f"Program finished all operations in {main_toc - main_tic:0.4f} seconds")
    sys.exit()
