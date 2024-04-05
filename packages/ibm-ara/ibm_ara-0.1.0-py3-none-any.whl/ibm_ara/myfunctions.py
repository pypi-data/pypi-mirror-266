import lazy_import
from typing import List
from sklearn.cluster import KMeans
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

kneed = lazy_import.lazy_module("kneed")
pd = lazy_import.lazy_module("pandas")


def scale_data(df: pd.DataFrame,
               scale_method: str = "minmax",
               **kwargs):
    if scale_method == 'minmax':
        from sklearn.preprocessing import MinMaxScaler
        scaled_df = MinMaxScaler(**kwargs).fit_transform(df)
    elif scale_method == 'standard':
        from sklearn.preprocessing import StandardScaler
        scaled_df = StandardScaler(**kwargs).fit_transform(df)
    elif scale_method == 'max':
        from sklearn.preprocessing import MaxAbsScaler
        scaled_df = MaxAbsScaler(**kwargs).fit_transform(df)
    elif scale_method == 'robust':
        from sklearn.preprocessing import RobustScaler
        scaled_df = RobustScaler(**kwargs).fit_transform(df)
    else:
        scaled_df = df
    return scaled_df


def find_regime(df, n_clusters):
    scaled_df = scale_data(df)
    kmeans = KMeans(init="random", n_clusters=n_clusters, n_init=10, max_iter=300, random_state=42)
    kmeans.fit(scaled_df)
    df['Label'] = kmeans.predict(scaled_df)+1
    return df

def plot_k_regimes(y_axis,y_label,data_df,upper_clip=None,folder=None):
    plt.figure(figsize=(20, 10))
    if upper_clip != None:
        sns.boxplot(data=data_df.clip(upper=upper_clip), x='Label', y=y_axis,showfliers=False)
    else:
        sns.boxplot(data=data_df, x='Label', y=y_axis,showfliers=False)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.xlabel('Cluster ID', fontsize=25)
    plt.ylabel(y_label, fontsize=25)
    # plt.ylim([350, 500])
    plt.grid("on")
     