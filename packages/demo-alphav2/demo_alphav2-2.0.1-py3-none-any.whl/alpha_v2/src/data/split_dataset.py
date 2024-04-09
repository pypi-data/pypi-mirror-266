import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

def split_optuna_data(data):
    """
    Hàm này chia dữ liệu thành các tập train và test zđể sử dụng trong quá trình tối ưu hóa bằng Optuna.

    Args:
    data (pandas.DataFrame): DataFrame chứa dữ liệu cần chia.

    Returns:
    pandas.DataFrame: DataFrame chứa dữ liệu train (đã được chuẩn hóa).
    pandas.DataFrame: DataFrame chứa dữ liệu test (đã được chuẩn hóa).
    pandas.Series: Series chứa nhãn tương ứng với dữ liệu train.
    pandas.Series: Series chứa nhãn tương ứng với dữ liệu test.
    """
    new_part = np.array_split(data, 3)

    # Truy cập từng phần một
    hold_out = new_part[2]
    train_data = pd.concat([new_part[0], new_part[1]], axis=0)
    
    # Loại bỏ các cột không cần thiết
    if 'open' in train_data.columns:
        optuna_data = train_data.drop(['close', 'open', 'high', 'low', 'volume', 'Changes'], axis=1)
    else:
        optuna_data = train_data.drop(['close', 'Changes'], axis=1)
    
    scaler = StandardScaler()
    scaler.fit(optuna_data)
    optuna_data = pd.DataFrame(scaler.transform(optuna_data))    
    
    # Chia dữ liệu thành tập train và tập test
    X_train, X_valid, y_train, y_valid = train_test_split(optuna_data, train_data['Changes'], test_size=0.5, shuffle=False)

    return X_train, X_valid, y_train, y_valid