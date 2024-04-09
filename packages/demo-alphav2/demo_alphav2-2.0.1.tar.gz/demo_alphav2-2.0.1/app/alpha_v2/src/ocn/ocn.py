def clusterKMeansBase(corr0, maxNumClusters=10, n_init=10, debug=False):
    """
    Phân cụm các biến tài sản dựa trên ma trận tương quan sử dụng thuật toán KMeans.

    Args:
    corr0 (numpy.ndarray): Ma trận tương quan.
    maxNumClusters (int, optional): Số lượng cụm tối đa. Mặc định là 10.
    n_init (int, optional): Số lần khởi tạo ngẫu nhiên. Mặc định là 10.
    debug (bool, optional): Chế độ debug. Mặc định là False.

    Returns:
    numpy.ndarray: Ma trận tương quan đã được sắp xếp lại.
    dict: Từ điển chứa thông tin về các cụm.
    pandas.Series: Series chứa hệ số Silhouette tối ưu cho từng quan sát.
    """
    # Xử lý các giá trị ngoại lai trong ma trận tương quan
    corr0[corr0 > 1] = 1
    
    # Tính ma trận khoảng cách từ ma trận tương quan
    dist_matrix = ((1 - corr0) / 2.) ** 0.5
    
    # Tạo một Series trống để lưu trữ hệ số Silhouette tối ưu
    silh_coef_optimal = pd.Series(dtype='float64')
    
    # Xác định số cụm tối đa
    maxNumClusters = min(maxNumClusters, int(np.floor(dist_matrix.shape[0] / 2)))
    
    # Lặp qua các lần khởi tạo ngẫu nhiên
    for init in range(0, n_init):
        # Lặp qua số lượng cụm từ 2 đến maxNumClusters
        for num_clusters in range(2, maxNumClusters + 1):
            kmeans_ = KMeans(n_clusters=num_clusters, n_init=10)
            kmeans_ = kmeans_.fit(dist_matrix)
            silh_coef = silhouette_samples(dist_matrix, kmeans_.labels_)
            stat = (silh_coef.mean() / silh_coef.std(), silh_coef_optimal.mean() / silh_coef_optimal.std())

            # Nếu hệ số này tốt hơn hệ số tối ưu trước đó, thiết lập là tối ưu
            if np.isnan(stat[1]) or stat[0] > stat[1]:
                silh_coef_optimal = silh_coef
                kmeans = kmeans_
                if debug:
                    print(kmeans)
                    print(stat)
                    silhouette_avg = silhouette_score(dist_matrix, kmeans_.labels_)
                    print("For n_clusters = " + str(num_clusters) + " The average silhouette_score is : " + str(silhouette_avg))
                    print("********")
    
    # Sắp xếp lại ma trận tương quan theo nhãn cụm
    newIdx = np.argsort(kmeans.labels_)
    corr1 = corr0.iloc[newIdx]
    corr1 = corr1.iloc[:, newIdx]

    # Tạo từ điển chứa thông tin về các cụm
    clstrs = {i: corr0.columns[np.where(kmeans.labels_ == i)[0]].tolist() for i in np.unique(kmeans.labels_)}
    
    # Tạo Series chứa hệ số Silhouette tối ưu
    silh_coef_optimal = pd.Series(silh_coef_optimal, index=dist_matrix.index)
    
    return corr1, clstrs, silh_coef_optimal

''' Improve number clusters using silh scores

    :param corr_mat: (pd.DataFrame) Correlation matrix
    :param clusters: (dict) Clusters elements
    :param top_clusters: (dict) Improved clusters elements
    :return: (tuple) [ordered correlation matrix, clusters, silh scores]
'''
def makeNewOutputs(corr0, clstrs, clstrs2):
    """
    Tạo ra các đầu ra mới từ các thông tin về các cụm.

    Args:
    corr0 (numpy.ndarray or pandas.DataFrame): Ma trận tương quan gốc.
    clstrs (dict): Từ điển chứa thông tin về các cụm.
    clstrs2 (dict): Từ điển chứa thông tin về các cụm mới.

    Returns:
    numpy.ndarray or pandas.DataFrame: Ma trận tương quan mới.
    dict: Từ điển chứa thông tin về các cụm mới.
    pandas.Series: Series chứa hệ số Silhouette mới cho từng quan sát.
    """
    # Khởi tạo từ điển và danh sách mới
    clstrsNew, newIdx = {}, []
    
    # Tạo từ điển mới từ thông tin về các cụm gốc
    for i in clstrs.keys():
        clstrsNew[len(clstrsNew.keys())] = list(clstrs[i])
    
    # Thêm thông tin về các cụm mới vào từ điển mới
    for i in clstrs2.keys():
        clstrsNew[len(clstrsNew.keys())] = list(clstrs2[i])
    
    # Tạo danh sách mới của các chỉ số
    newIdx = [j for i in clstrsNew for j in clstrsNew[i]]
    
    # Tạo ma trận tương quan mới dựa trên danh sách mới của các chỉ số
    corrNew = corr0.loc[newIdx, newIdx]
    
    # Tính toán hệ số Silhouette mới
    dist = ((1 - corr0) / 2.) ** 0.5
    kmeans_labels = np.zeros(len(dist.columns))
    for i in clstrsNew.keys():
        idxs = [dist.index.get_loc(k) for k in clstrsNew[i]]
        kmeans_labels[idxs] = i
    
    silhNew = pd.Series(silhouette_samples(dist, kmeans_labels), index=dist.index)
    
    return corrNew, clstrsNew, silhNew


''' Recursivly cluster
    Typical output: e.g if there are 4 clusters:
>>> _,_,_=clusterKMeansTop(corr0)
redo cluster:[0, 1, 2, 5]
redo cluster:[0, 1, 2]
redo cluster:[1]
redoCluster <=1:[1]
newTstatMean > tStatMean
newTstatMean > tStatMean
>>>

So it returns first time on base-case  >>>if len(redoClusters) <= 1
Then sub-sequent returnes are after the tail-recurrsion
'''
def clusterKMeansTop(corr0: pd.DataFrame, maxNumClusters=None, n_init=10):
    """
    Phân cụm các biến tài sản dựa trên ma trận tương quan sử dụng thuật toán KMeans với phương pháp tối ưu hóa.

    Args:
    corr0 (pandas.DataFrame): Ma trận tương quan gốc.
    maxNumClusters (int, optional): Số lượng cụm tối đa. Mặc định là None.
    n_init (int, optional): Số lần khởi tạo ngẫu nhiên. Mặc định là 10.

    Returns:
    pandas.DataFrame: Ma trận tương quan đã được sắp xếp lại.
    dict: Từ điển chứa thông tin về các cụm.
    pandas.Series: Series chứa hệ số Silhouette tối ưu cho từng quan sát.
    """
    if maxNumClusters is None:
        maxNumClusters = corr0.shape[1] - 1
        
    corr1, clstrs, silh = clusterKMeansBase(corr0, maxNumClusters=min(maxNumClusters, corr0.shape[1] - 1), n_init=10)
    print("clstrs length: " + str(len(clstrs.keys())))
    print("best cluster: " + str(len(clstrs.keys())))
    
    clusterTstats = {i: np.mean(silh[clstrs[i]]) / np.std(silh[clstrs[i]]) for i in clstrs.keys()}
    tStatMean = sum(clusterTstats.values()) / len(clusterTstats)
    redoClusters = [i for i in clusterTstats.keys() if clusterTstats[i] < tStatMean]
    
    if len(redoClusters) <= 2:
        print("If 2 or less clusters have a quality rating less than the average then stop.")
        print("redoCluster <= 1: " + str(redoClusters) + " clstrs len: " + str(len(clstrs.keys())))
        return corr1, clstrs, silh
    else:
        keysRedo = [j for i in redoClusters for j in clstrs[i]]
        corrTmp = corr0.loc[keysRedo, keysRedo]
        _, clstrs2, _ = clusterKMeansTop(corrTmp, maxNumClusters=min(maxNumClusters, corrTmp.shape[1] - 1), n_init=n_init)
        print("clstrs2.len, stat: " + str(len(clstrs2.keys())))
        
        # Tạo ra các đầu ra mới, nếu cần
        dict_redo_clstrs = {i: clstrs[i] for i in clstrs.keys() if i not in redoClusters}
        corrNew, clstrsNew, silhNew = makeNewOutputs(corr0, dict_redo_clstrs, clstrs2)
        newTstatMean = np.mean([np.mean(silhNew[clstrsNew[i]]) / np.std(silhNew[clstrsNew[i]]) for i in clstrsNew.keys()]) 
        
        if newTstatMean <= tStatMean:
            print("newTstatMean <= tStatMean " + str(newTstatMean) + " (len:newClst) " + str(len(clstrsNew.keys())) + " <= " + str(tStatMean) + " (len:Clst) " + str(len(clstrs.keys())))
            return corr1, clstrs, silh
        else: 
            print("newTstatMean > tStatMean " + str(newTstatMean) + " (len:newClst) " + str(len(clstrsNew.keys()))
                  + " > " + str(tStatMean) + " (len:Clst) " + str(len(clstrs.keys())))
            return corrNew, clstrsNew, silhNew