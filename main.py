import random
import time
import sys
import itertools
import numpy as np

from abstraction.abstractor import Abstractor
from model.log import Log
from recommendation.group_property_computation import PropertyComputer
from recommendation.text_generation import TextGen
from clustering import preprocessing
from clustering.clusterer import Clusterer
from recommendation.ranking import Ranker
from clustering.retrieve import compute_similarities, retrieve_most_similar_events
from config import Config
from const import *
from read import reader
from write import writer
from write.writer import export_log_as_xes

MOBIS_NAME = "Mobis.csv"
MOBIS_REP = "MPPNTaskAbstractionMobIS_pd_cases_fv_fine_1"
MOBIS_ATT_MAPPING = {XES_CASE: "case", XES_NAME: "activity", XES_ROLE: "type", XES_RESOURCE: "user", XES_TIME: "start"}

BPI17_NAME = "BPI Challenge 2017.xes"
BPI17_REP = "MPPNTaskAbstractionBPIC2017_pd_cases_fv_fine_1"


def main(config):
    result, loaded_res = reader.load_result(config)
    if loaded_res:
        print("found", config)
        # return result
    # first read the raw log
    if ".xes" in config.log_name:
        pd_log = reader.read_xes_log(config)
    elif ".csv" in config.log_name:
        pd_log = reader.read_csv_log(config)
    else:
        raise Warning("Unsupported format, use .csv or .xes")

    # then read the leaned representations
    pd_events_fv, loaded = reader.load_mppn_representations(config)
    if loaded:
        if len(pd_events_fv) > 100000:
            print("filtering due to size")
            cases = list(pd_log[XES_CASE].unique())
            filtered = random.choices(cases, k=1000)
            to_remove = []
            for f in filtered:
                if len(pd_events_fv[pd_events_fv[XES_CASE] == int(f.replace("Application_", ""))]) != len(
                        pd_log[pd_log[XES_CASE] == f]):
                    # print(f, "!!!", len(pd_events_fv[pd_events_fv[XES_CASE] == int(f.replace("Application_", ""))]), len(pd_log[pd_log[XES_CASE] == f]))
                    to_remove.append(f)
            for f in to_remove:
                filtered.remove(f)
            pd_log = pd_log[pd_log[XES_CASE].isin(filtered)]
            if config.log_name == BPI17_NAME:
                filtered = [int(s.replace("Application_", "")) for s in filtered]
            pd_events_fv = pd_events_fv[pd_events_fv[XES_CASE].isin(filtered)]
        else:
            cases = list(pd_log[XES_CASE].unique())
            to_remove = []
            for f in cases:
                if len(pd_events_fv[pd_events_fv[XES_CASE] == int(f.replace("Application_", ""))]) != len(
                        pd_log[pd_log[XES_CASE] == f]):
                    # print(f, "!!!", len(pd_events_fv[pd_events_fv[XES_CASE] == int(f.replace("Application_", ""))]), len(pd_log[pd_log[XES_CASE] == f]))
                    to_remove.append(f)
            for f in to_remove:
                cases.remove(f)
            pd_log = pd_log[pd_log[XES_CASE].isin(cases)]
            if config.log_name == BPI17_NAME:
                cases = [int(s.replace("Application_", "")) for s in cases]
            pd_events_fv = pd_events_fv[pd_events_fv[XES_CASE].isin(cases)]
        pd_events_fv.reset_index(inplace=True)
        pd_log.reset_index(inplace=True)
        print(len(pd_events_fv[XES_CASE].unique()), len(pd_log[XES_CASE].unique()))

        print(len(pd_events_fv), len(pd_log))
        log = Log(pd_log, pd_events_fv)
        tic = time.perf_counter()

        clust, clust_is_there = reader.deserialize_clustering(config)
        if False:
            # TODO fix this
            pass
        else:
            if config.dim_red == PCA_S:
                # Do PCA
                dim_red_df, dim_red_rep = preprocessing.pca(log.pd_fv, comp=2)
                toc = time.perf_counter()
                print(f"PCA done in {toc - tic:0.4f} seconds")
            elif config.dim_red == TSNE_S:
                # preprocessing.viz(pca)
                # Do t-SNE
                dim_red_df, dim_red_rep = preprocessing.tsne(log.pd_fv)
                tic = time.perf_counter()
            else:
                dim_red_rep = np.array(pd_events_fv[FV].tolist())
            # Cluster
            clust = Clusterer(log, config)
            # TODO how to set number of clusters?
            # TODO how to rank different clusters?
            clust.cluster(dim_red_rep)
            toc = time.perf_counter()
            print(f"Clustering done in {toc - tic:0.4f} seconds")
            writer.serialize_clustering(clust, config)
        clustering_num = ""
        # Since k means is fast we can create multiple clusterings and use alternative options to present to the user
        if config.multi_clustering:
            for clustering_num, pred_labels in clust.pred_labels.items():
                pd_events_fv[CLUST_COL + str(clustering_num)] = pred_labels
                pd_events_fv[CLUST_COL + str(clustering_num)] = pd_events_fv[CLUST_COL + str(clustering_num)].astype(
                    int)
            # print(pd_events_fv[CLUST_COL + str(clustering_num)].unique())
        else:
            pd_events_fv[CLUST_COL] = clust.pred_labels
            pd_events_fv[CLUST_COL] = pd_events_fv[CLUST_COL].astype(int)
        # pd_events_fv.to_csv(config.out_path + config.log_name + "_c.csv")
        tic = time.perf_counter()
        # Compute key properties
        props = PropertyComputer(log, config, clust)
        props.compute_props_for_clusters()
        ranker = Ranker(log, config, props.clust_to_prop)
        clust_to_att_unique, clust_to_att_distinct, clust_to_att_distinct_per_case, comp_red = ranker.create_ranking()
        toc = time.perf_counter()
        print(f"Props computed in {toc - tic:0.4f} seconds")
        # print(len(props.clust_to_prop))
        # print(props.clust_to_prop)
        # Generate cluster descriptions
        text_gen = TextGen(log, props.clust_to_prop, clust_to_att_unique, clust_to_att_distinct,
                           clust_to_att_distinct_per_case, config)
        text_gen.generate_descriptions_for_clusters()
        # print(text_gen.description)
        for clustering in text_gen.description.keys():
            for clust_num, clust_description in text_gen.description[clustering].items():
                print(clust_num, clust_description)

        writer.write_result_to_disk(config, text_gen)

        # TODO list that reflects which groups have been chosen --> implement top-k picking
        selected = [9]
        # apply groups to low-level log

        abstractor = Abstractor(log, config, selected, CLUST_COL + str(clustering_num))
        abstracted_log = abstractor.apply_abstraction()
        export_log_as_xes(abstracted_log, config)
        return text_gen
        # Get similar events
        # pd_events_fv = compute_similarities(pd_events_fv)
        # Retrieve most similar events
        # retrieve_most_similar_events(pd_events_fv, 5523, 1, top_n=5)
    else:
        print(config.log_name, "could not be loaded")
        return None


base_config = Config("input/", "output/", BPI17_NAME, {}, BPI17_REP, clust="k_means", noise_tau=0.05,
                     multi_clustering=True, dim_red=PCA_S, comp=2)

LOGS = [(BPI17_NAME, BPI17_REP, {}), (MOBIS_NAME, MOBIS_REP, MOBIS_ATT_MAPPING)]
CLUST = ["k_means"]
NOISE_TAU = [0, 0.05, 0.1, 0.2]
DIM_RED = [None, PCA_S, TSNE_S]
COMPS = [2, 3, 0.95, 0.99]


def evaluate():
    prepare_configs = [LOGS, CLUST, NOISE_TAU, DIM_RED, COMPS]
    raw_configs = list(itertools.product(*prepare_configs))
    for raw_config in raw_configs:
        # print(raw_config)
        conf = Config("input/", "output/", log_name=raw_config[0][0],
                      att_names=raw_config[0][2], rep_name=raw_config[0][1],
                      clust=raw_config[1], noise_tau=raw_config[2],
                      dim_red=raw_config[3], comp=raw_config[4])
        if conf.log_name == BPI17_NAME and conf.noise_tau == 0.0 and conf.dim_red =="None" and conf.comp == 0.99:  # or conf.log_name == BPI17_NAME and conf.noise_tau == 0 and conf.dim_red==TSNE_S and conf.comp == 2 or conf.log_name == BPI17_NAME and conf.noise_tau == 0.2 and conf.dim_red==TSNE_S and conf.comp == 0.95:
            main(conf)
        # break


if __name__ == '__main__':
    main_tic = time.perf_counter()
    # main(base_config)
    evaluate()

    main_toc = time.perf_counter()
    print(f"Program finished all operations in {main_toc - main_tic:0.4f} seconds")
    sys.exit()
