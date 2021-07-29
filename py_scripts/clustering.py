import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA


# perform univariate clustering
# output dict of cluster years
# return --> { "High": [years...], "Medium": [years...], "Low": [years...] }
def univariate_clustering(data, col_name, nb_clusters=3, metric="euclidean", linkage_method="ward"):
    # isolate data of weather variable
    data_cluster = isolate_data_col(data, col_name)

    # perform clustring
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



# preform multivariate clustering 
# weather vars --> PCA --> merge weather vars --> cluster
def multivariate_clustering(data, nb_clusters=3, metric="euclidean", linkage_method="ward"):
    # prepare data: isolate data of each weather variable
    selected_cols = ["cumulative_GDD", "cumulative_PRECTOT", "cumulative_RH2M", "cumulative_WS2M"]
    dict_data = {}

    for col in selected_cols:
        dict_data[col] = isolate_data_col(data, col_name=col)

    # standarize and rescale
    # standarize
    dict_standarized_data = {}

    for col in selected_cols:
      # select data
      data = dict_data[col].copy()

      # scale data
      max_val = np.max(data.values)
      min_val = np.min(data.values)
      data = (data - min_val) / (max_val - min_val)

      # standarize each var
      for var in dict_data[col]:
        data[var] = (data[var] - data[var].mean())

      dict_standarized_data[col] = data
    
    # perform PCA: nb selected components are from PCA univariate analysis
    arr_nb_PC = [6, 7, 8, 8]
    # where to store pca
    dict_pca = {}
    # where to store transformed data
    dict_transformed_data = {}

    # loop over weather vars
    for col, n in zip(selected_cols, arr_nb_PC):
      # build pca
      pca = PCA(n_components=n)
      pca.fit(dict_standarized_data[col])

      dict_pca[col] = pca
    
      # transform data
      dict_transformed_data[col] = pd.DataFrame(pca.transform(dict_standarized_data[col]), index=dict_standarized_data[col].index)

    # join transformed data sets
    merged_data = dict_transformed_data["cumulative_GDD"].join(dict_transformed_data["cumulative_PRECTOT"], rsuffix='_other')

    # for col in selected_cols[2:]:
    #     merged_data = merged_data.join(dict_transformed_data[col], rsuffix='_other_')
    
    # perform the clustering
    X = merged_data
    model = AgglomerativeClustering(n_clusters=nb_clusters, linkage=linkage_method, affinity=metric)
    model = model.fit(X)

    labels = model.fit_predict(X)

    # isolate clusters (according to precipitation)
    # to re name cluster { High, Medium, Low }
    col_name = "cumulative_PRECTOT"
    data_cluster = dict_data[col_name]

    data_cluster[f"cluster_{col_name}"] = labels

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


# split function
# split according to weather variables
def isolate_data_col(data, col_name):

  frame = {}

  for year in data["crop_year"].value_counts().sort_index().index:
    # select crop year
    query = data["crop_year"] == year
    frame[year] = data[query][col_name].values


  # build data and then transpose
  data_cluster = pd.DataFrame(frame)
  data_cluster = data_cluster.T

  return data_cluster