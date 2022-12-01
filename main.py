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
from recommendation.pre_selection import PreSelector
from config import Config
from const import *
from read import reader
from write import writer
from write.writer import export_log_as_xes

SIM_NAME = "EventLog_LowLevel.csv"
SIM_REP = "MPPNMultiTaskAbstractionSynthetic_v3_concept-name_org-role_org-resource_isComplete_isAccepted__time-timestamp_big_pd_cases_fv_fine"
SIM_ATT_MAPPING = {XES_CASE: XES_CASE, XES_NAME: XES_NAME, XES_ROLE: XES_ROLE, XES_RESOURCE: XES_RESOURCE,
                   XES_TIME: XES_TIME + ":start"}


def main(config, with_select_and_abstract=None):
    print(config)
    #result, loaded_res = reader.load_result(config)
    #if loaded_res:
    #    print("found", config)
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
        if len(pd_events_fv) > 50000000:
            print("filtering due to size")
            cases = list(pd_log[XES_CASE].unique())
            filtered = random.choices(cases, k=500)
            to_remove = []
            for f in filtered:
                if len(pd_events_fv[pd_events_fv[XES_CASE] == f]) != len(pd_log[pd_log[XES_CASE] == f]):
                    to_remove.append(f)
            for f in to_remove:
                filtered.remove(f)
            pd_log = pd_log[pd_log[XES_CASE].isin(filtered)]
            pd_events_fv = pd_events_fv[pd_events_fv[XES_CASE].isin(filtered)]
        else:
            pass
        pd_events_fv.reset_index(inplace=True)
        pd_log.reset_index(inplace=True)
        print(len(pd_events_fv[XES_CASE].unique()), len(pd_log[XES_CASE].unique()))

        print(len(pd_events_fv), len(pd_log))
        log = Log(pd_log, pd_events_fv)
        tic = time.perf_counter()

        clust, clust_is_there = reader.deserialize_clustering(config)
        if clust_is_there:
            print(f"Clustering loaded")
            pass
        else:
            if config.dim_red == PCA_S:
                # Do PCA
                dim_red_df, dim_red_rep = preprocessing.pca(log.pd_fv, comp=config.comp)
                toc = time.perf_counter()
                print(f"PCA done in {toc - tic:0.4f} seconds")
            elif config.dim_red == TSNE_S:
                # Do t-SNE
                dim_red_df, dim_red_rep = preprocessing.tsne(log.pd_fv)
                tic = time.perf_counter()
            else:
                dim_red_rep = np.array(pd_events_fv[FV].tolist())
            # Cluster
            clust = Clusterer(log, config)
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
        print(f"Computing properties")
        tic = time.perf_counter()
        # Compute key properties
        props = PropertyComputer(log, config, clust)
        props.compute_props_for_clusters()
        ranker = PreSelector(log, config, props.clust_to_prop)
        clust_to_att_unique, clust_to_att_distinct, clust_to_att_unique_per_case, comp_red = ranker.create_ranking()
        toc = time.perf_counter()
        print(f"Props computed in {toc - tic:0.4f} seconds")
        pd_log.to_csv(config.out_path + config.log_name + "all_groups_with_noise.csv")
        # Generate cluster descriptions
        text_gen = TextGen(log, props.clust_to_prop, clust_to_att_unique, clust_to_att_distinct,
                           clust_to_att_unique_per_case, config)
        text_gen.generate_descriptions_for_clusters()
        # print(text_gen.description)
        for clustering in text_gen.description.keys():
            for clust_num, clust_description in text_gen.description[clustering].items():
                print(clust_num, clust_description)
        writer.write_result_to_disk(config, text_gen)
        if with_select_and_abstract:
        # The following is the group selection (actually done by the user) and a very basic abstraction strategy.
            selected = [0, 1, 4, 5]
            print(f"Abstracting log...")
            abstractor = Abstractor(log, config, selected, CLUST_COL + str(clustering_num))
            abstracted_log = abstractor.apply_abstraction()
            abstracted_log.to_csv(config.out_path + config.log_name + "_a.csv")
            export_log_as_xes(abstracted_log, config)
        return text_gen
    else:
        print(config.rep_name, "could not be loaded")
        return None


base_config = Config("input/", "output/", SIM_NAME, SIM_ATT_MAPPING, SIM_REP, clust="k_means", noise_tau=0.2,
                     multi_clustering=False, dim_red=PCA_S, comp=.99, with_ranker=False)

LOGS = [(SIM_NAME, SIM_REP, SIM_ATT_MAPPING)]
CLUST = ["k_means"]
NOISE_TAU = [0.2]
DIM_RED = [PCA_S]
COMPS = [0.99]

INPUT, OUTPUT = "input/", "output/"

def evaluate():
    prepare_configs = [LOGS, CLUST, NOISE_TAU, DIM_RED, COMPS]
    raw_configs = list(itertools.product(*prepare_configs))
    for raw_config in raw_configs:
        conf = Config(INPUT, OUTPUT, log_name=raw_config[0][0],
                      att_names=raw_config[0][2], rep_name=raw_config[0][1],
                      clust=raw_config[1], noise_tau=raw_config[2],
                      dim_red=raw_config[3], comp=raw_config[4], with_ranker=False)
        main(conf)
        # break


if __name__ == '__main__':
    main_tic = time.perf_counter()
    evaluate()
    main_toc = time.perf_counter()
    print(f"Program finished all operations in {main_toc - main_tic:0.4f} seconds")
    sys.exit()
