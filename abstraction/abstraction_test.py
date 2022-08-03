import sys

import pandas as pd

from config import Config
from read import reader
from const import *

SIM_NAME = "EventLog_LowLevel_v3.csv"
SIM_REP = "MPPNMultiTaskAbstractionSynthetic_concept-name_org-role_org-resource_isCompletetime-timestamp_pd_cases_fv_fine"
SIM_ATT_MAPPING = {XES_CASE: XES_CASE, XES_NAME: XES_NAME, XES_ROLE: XES_ROLE, XES_RESOURCE: XES_RESOURCE, XES_TIME: XES_TIME+":start"}

base_config = Config("../input/", "output/", SIM_NAME, SIM_ATT_MAPPING, SIM_REP, clust="k_means", noise_tau=0.2,
                     multi_clustering=False, dim_red=PCA_S, comp=.99, with_ranker=False)

def main(config):
    print(config)
    result, loaded_res = reader.load_result(config)
    if loaded_res:
        print("found", config)
        # return result
    # first read the raw log
    if ".xes" in config.log_name:
        pd_log = reader.read_xes_log(config)
    elif ".csv" in config.log_name:
        pd_log = reader.read_csv_log(config)
        pd_log.loc[pd_log[SIM_ATT_MAPPING[XES_ROLE]] == "Manager", XES_NAME] = pd_log["High Level Transition"]
        pd_log.loc[pd_log[SIM_ATT_MAPPING[XES_ROLE]] == "Expert", XES_NAME] = pd_log["High Level Transition"]
        pd_log.loc[pd_log["High Level Transition"] == "Communicate decision", XES_NAME] = pd_log["High Level Transition"]
        g = pd_log.groupby([XES_CASE, XES_NAME, XES_RESOURCE, "High Level Transition"])
        #pd_log.loc[g[XES_LIFECYCLE].head(1).index, XES_LIFECYCLE] = 'start'
        #pd_log.loc[g[XES_LIFECYCLE].tail(1).index, XES_LIFECYCLE] = 'complete'
        # in each case retain only the first and last event of each group
        pd_log = (pd.concat([g.tail(1)]).drop_duplicates().reset_index(drop=True))
        pd_log.to_csv(config.out_path+"/"+"abs.csv")
    else:
        raise Warning("Unsupported format, use .csv or .xes")
    sys.exit(0)


#main(base_config)