import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA
from const import *


def pca(pd_events_fv):

    fv_matrix = np.array(pd_events_fv[FV].tolist())
    pca_model = PCA(n_components=2, random_state=1111)
    pca_rep = pca_model.fit_transform(fv_matrix)

    pca_df = pd.DataFrame(data={"x": pca_rep[:, 0],
                                "y": pca_rep[:, 1]})
    for attr in pd_events_fv.columns:
        pca_df[attr] = pd_events_fv[attr].tolist()

    return pca_df, pca_rep


def viz(pca_df, color_att=None, with_annots=True):
    clr = color_att if color_att else XES_NAME_DF_NUM
    plt.figure(figsize=(30, 30), dpi=300)
    plt.scatter(pca_df["x"], pca_df["y"],
                c=pca_df[clr].tolist(),
                # label=tsne_df["variant"].tolist(),
                s=1)
    if with_annots:
        for idx, row in pca_df.iterrows():
            #print(row[annotate_attr])
            plt.annotate(str(int(row[clr])),
                         (row["x"], row["y"]),
                         fontsize=3,
                         weight="bold")
