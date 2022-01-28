'''
Usefull functions for visualizing data and/or clusters.
'''

from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px

def metric_w_knee_plot(numbers_of_clusters, metric_vals, knee_val,\
     title = "Metric/ Number of Clusters (Kmedoids)",x_label = 'Number of Clusters',
     y_label="Metric", legend = ["",""]  ):
    
    fig, ax = plt.subplots(figsize=(8, 6), dpi=240)
    plt.plot(numbers_of_clusters, metric_vals, color='blue')
    plt.axvline(x=knee_val, linestyle="--", color='red')
    plt.xlabel(x_label, fontsize=15)
    plt.ylabel(y_label, fontsize=15)
    plt.title(title, fontsize=15)
    plt.legend(legend)
    plt.grid()
    plt.show()




def knns_distance_plot(input_X, k =15, metric="precomputed", plot = True):
    
    # X_embedded is your data
    nbrs = NearestNeighbors(n_neighbors=k, metric=metric ).fit(input_X)
    distances, indices = nbrs.kneighbors(input_X)
    distance_asc= sorted(distances[:,-1])
    if plot:
        fig, ax = plt.subplots(figsize=(8, 6), dpi=240)
        plt.plot(list(range(len(distance_asc))), distance_asc)
        plt.ylabel(str(k) + '-NN distance', fontsize=15)
        plt.xlabel('Points sorted by distance', fontsize=15)
        plt.xlabel('Distances of samples\' K-NN neighbors', fontsize=15)
        plt.grid()
        plt.show()

    return distance_asc


from sklearn.manifold import MDS

def mds_def_precomputed_execution(input_X, n_dimensions=2, metric=True, n_init=4, max_iter=300,\
     verbose=0, eps=0.001, n_jobs=None, random_state=1, dissimilarity='precomputed'):
    
    mds_model = MDS(n_components = n_dimensions, metric=metric, n_init=n_init, max_iter=max_iter,\
     verbose=verbose, eps=eps, n_jobs=n_jobs, random_state=random_state, dissimilarity = dissimilarity)

    X_transformed = mds_model.fit_transform(input_X)
 
    return X_transformed


def plot_2D_mds_array(mds_2d_array, title = "2D MDS plot of data", s=10, c=None, marker=None, cmap=None, 
norm=None, vmin=None, vmax=None, alpha=None, linewidths=None, 
edgecolors=None, plotnonfinite=False, data=None, **kwargs):

    
    if c is not None:
        if min(c) < 0:
            mds_2d_array = [spot for index,spot in enumerate(mds_2d_array) if c[index] >=0]
            mds_2d_array = np.vstack(mds_2d_array)
            c = [i for i in c if i >=0]
    plt.figure(figsize=(8, 6), dpi=240)
    plt.scatter(mds_2d_array[:,0], mds_2d_array[:,1],s=s, c=c, marker=marker, cmap=cmap, \
        norm=norm, vmin=vmin, vmax=vmax, alpha=alpha, linewidths=linewidths, \
        edgecolors=edgecolors, plotnonfinite=plotnonfinite, data=data, **kwargs )
    plt.title(title)
    plt.xlabel("Dimension 1")
    plt.ylabel("Dimension 2")
    
    plt.show()
# mds_2d_array

def plot_3D_mds_array(mds_3d_array, title = "3D MDS plot of data", s=10, c=None, marker=None, cmap=None, 
norm=None, vmin=None, vmax=None, alpha=None, linewidths=None, 
edgecolors=None, plotnonfinite=False, data=None, **kwargs):

    
    if c is not None:
        if min(c) < 0:
            mds_3d_array = [spot for index,spot in enumerate(mds_3d_array) if c[index] >=0]
            mds_3d_array = np.vstack(mds_3d_array)
            c = [i for i in c if i >=0]
    
    fig = plt.figure(figsize=(8, 6), dpi=240)
    ax = fig.add_subplot(projection='3d')


    ax.scatter(mds_3d_array[:,0], mds_3d_array[:,1], mds_3d_array[:,2], s=s, c=c, marker=marker, cmap=cmap, \
        norm=norm, vmin=vmin, vmax=vmax, alpha=alpha, linewidths=linewidths, \
        edgecolors=edgecolors, plotnonfinite=plotnonfinite, data=data, **kwargs )
    ax.set_title(title)
    ax.set_xlabel("Dimension 1")
    ax.set_ylabel("Dimension 2")
    ax.set_zlabel("Dimension 3")
    plt.show()

# import plotly.express as px 
# mds_3d_array = mds_model_3D
# c = clustering_model.labels_
# if c is not None:
#     if min(c) < 0:
#         mds_3d_array = [spot for index,spot in enumerate(mds_3d_array) if c[index] >=0]
#         mds_3d_array = np.vstack(mds_3d_array)
#         c = [i for i in c if i >=0]
# fig = px.scatter_3d(x=mds_3d_array[:,0], y=mds_3d_array[:,1], z=mds_3d_array[:,2], color = c)
# fig.show()