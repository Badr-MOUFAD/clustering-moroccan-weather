import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering


# perform univariate clustering
# output dict of cluster years
# return --> { "High": [years...], "Medium": [years...], "Low": [years...]}
def univariate_clustering(data, col_name, nb_clusters=3, metric="euclidean", linkage_method="ward"):
    # prepare data
    frame = {}

    for year in data["crop_year"].value_counts().sort_index().index:
        # select crop year
        query = data["crop_year"] == year
        frame[year] = data[query][col_name].values

    # build data and then transpose
    data_cluster = pd.DataFrame(frame)
    data_cluster = data_cluster.T

    # perform clustring
    # data
    X = data_cluster

    # build clustering model
    model = AgglomerativeClustering(n_clusters=nb_clusters, linkage=linkage_method, affinity=metric)
    model = model.fit(X)

    # assign cluster label to each observation
    data_cluster[f"cluster_{col_name}"] = model.fit_predict(data_cluster)

    # isolate each cluster
    dict_cluster = {}
    # to store max val of each cluster
    arr_max_vals = []

    for cluster_index in range(nb_clusters):
        query = data_cluster[f"cluster_{col_name}"] == cluster_index

        # drop col of cluster
        copy_data = data_cluster[query].copy()
        copy_data = copy_data.drop(labels=[f"cluster_{col_name}"], axis=1)

        dict_cluster[cluster_index] = copy_data
        arr_max_vals.append(
            (cluster_index, np.max(copy_data.values))
            )

    # give name to clusters { High, medium, low }
    arr_max_vals.sort(key=lambda item: item[1], reverse=True)

    for key, new_cluster_name in zip([item[0] for item in arr_max_vals], ["High", "Medium", "Low"]):
        dict_cluster[new_cluster_name] = dict_cluster.pop(key)

    # return dict { cluster_name: arr_years }
    return { key: val.index for key, val in dict_cluster.items() }
