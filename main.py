import time
import sys

from recommendation.group_property_computation import PropertyComputer
from recommendation.text_generation import TextGen
from clustering import preprocessing
from clustering.clusterer import Clusterer
from clustering.retrieve import compute_similarities, retrieve_most_similar_events
from config import Config
from const import *
from read import reader
from write import writer

config = Config("input/", "output/", "Mobis.csv",
                {XES_CASE: "case", XES_NAME: "activity", XES_ROLE: "type", XES_RESOURCE: "user", XES_TIME: "start"},
                "MPPNTaskAbstractionMobIS_pd_cases_fv_fine_1", clust="k_means", noise_tau=0, multi_clustering=True)


def main():
    # first read the raw log
    pd_log = reader.read_csv_log(config)
    # then read the representations leaned
    pd_events_fv, loaded = reader.load_mppn_representations(config)
    if loaded:
        # Do PCA
        pca_df, pca_rep = preprocessing.pca(pd_events_fv)
        #preprocessing.viz(pca)

        # Cluster
        clust = Clusterer(pd_events_fv, config)
        # TODO how to set number of clusters?
        # TODO how to rank different clusters?
        clust.cluster(pca_rep, 27)

        # Since k means is fast we can create multiple clusterings and use alternative options to present to the user
        if config.multi_clustering:
            for clust_num, pred_labels in clust.pred_labels.items():
                pd_events_fv[CLUST_COL+str(clust_num)] = pred_labels
            print(pd_events_fv[CLUST_COL + str(clust_num)].unique())
        else:
            pd_events_fv[CLUST_COL] = clust.pred_labels


        # Compute key properties
        props = PropertyComputer(pd_events_fv, pd_log, config, clust)
        props.compute_props_for_clusters()
        print(len(props.clust_to_prop))
        print(props.clust_to_prop)
        # Generate cluster descriptions
        text_gen = TextGen(pd_events_fv, pca_df, props.clust_to_prop, config)
        text_gen.generate_descriptions_for_clusters()
        print(text_gen.description)
        for clustering in text_gen.description.keys():
            for clust_num, clust_description in text_gen.description[clustering].items():
                print(clust_num, clust_description)

        writer.write_result_to_disk(config, text_gen)
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
