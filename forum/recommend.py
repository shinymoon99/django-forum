import numpy as np
from scipy.spatial import distance
import pandas as pd


# table columns user item
def data_process(df):
    df.columns = ['user', 'item']
    users = df['user'].to_list()
    items = df['item'].to_numpy()
    df['ratings'] = 1.0
    df_piv = pd.pivot(df, index="user", columns="item", values="ratings")
    df = df_piv.fillna(0.0)
    return df.to_numpy(), users, items


def calc_similar_mat(mat):
    mat_len = mat.shape[0]
    similar_mat = np.zeros((mat_len, mat_len))
    for i in range(mat_len):
        for j in range(i + 1, mat_len):
            similar_mat[i, j] = distance.cosine(mat[i], mat[j])
    return similar_mat + similar_mat.T


def recommend(u_id, mat, similar_mat, k=5):
    k_nerghbor_ids = np.argsort(similar_mat).tolist()
    k_nerghbor_ids = k_nerghbor_ids[:k]
    k_mat = mat[k_nerghbor_ids].copy()
    k_mat_rating = np.sum(k_mat, axis=0)
    return np.argsort(k_mat_rating)[::-1][:5]


def model_establish(df, user_id):

    mat, users, items = data_process(df)
    sim_mat = calc_similar_mat(mat)
    u_id = users.index(user_id)
    recs = recommend(u_id, mat, sim_mat)
    return items[recs]
