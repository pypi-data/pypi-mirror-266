import numpy as np
import pandas as pd
import xgboost as xgb

from ..utils import choose_position, backtest_position_ps

def calculate_sharpe_ratio(pnl):
    """
    Calculate Sharpe ratio given PNL.
    
    Sharpe ratio illustrates of expected profit for each unit of risk in specific time interval
    and will be calculated by this formula: 
    = (Average of PNL values / Standard deviation of PNL values) * sqrt(252)
    252 is the number of trading days in a year, 
    we multiply with square root of 252 to convert sharpe ratio daily to sharpe ratio annually.
    
    Parameters
    ----------
    pnl : pandas.core.series.Series
        The Series of PNL values during the time interval (252).
    
    Returns
    -------
    sharpe : numpy.float64
        The sharpe ratio during the time interval.
    """
    avg_return = np.mean(pnl)
    std_return = np.std(pnl)
    sharpe = (avg_return / std_return)* np.sqrt(len(pnl))
    return sharpe

def sharpe_for_vn30f(y_pred, y_groud):
    """
    Tính toán tỷ lệ Sharpe cho một mô hình dự đoán giá VN30F.

    Args:
    y_pred (numpy.ndarray): Mảng chứa dự đoán của mô hình.
    y_groud (numpy.ndarray): Mảng chứa giá trị thực tế của VN30F.

    Returns:
    numpy.ndarray: Mảng chứa các vị trí được chọn dựa trên dự đoán của mô hình.
    pandas.Series: Chuỗi chứa PNL tích lũy.
    pandas.Series: Chuỗi chứa PNL hàng ngày được tích lũy.
    float: Tỷ lệ Sharpe của PNL hàng ngày.
    """
    # Chọn vị trí dựa trên dự đoán của mô hình
    pos = [choose_position(change) for change in y_pred]
    pos = np.array(pos)
    
    # Tính toán PNL hàng ngày
    pnl = backtest_position_ps(pos, y_groud)
    pnl = np.cumsum(pnl)
    cumulative_sum = pnl.groupby(level=0).last().values
    unique_dates = pnl.groupby(level=0).last().index

    # Tạo một Series mới với các giá trị của cumulative_sum và unique_dates
    daily_pnl = pd.Series(cumulative_sum, index=unique_dates)
    
    # Tính toán tỷ lệ Sharpe
    sharpe = calculate_sharpe_ratio(daily_pnl)

    return pos, pnl, daily_pnl, sharpe

def retrieve_top_pnl(top_hyperparameters, X_train, y_train, X_valid, y_valid):
    """
    Truy xuất PNL hàng đầu từ các siêu tham số và dữ liệu huấn luyện.

    Args:
    top_hyperparameters (list): Danh sách chứa các siêu tham số hàng đầu.
    X_train (numpy.ndarray or pandas.DataFrame): Dữ liệu huấn luyện.
    y_train (numpy.ndarray or pandas.Series): Nhãn của dữ liệu huấn luyện.
    X_valid (numpy.ndarray or pandas.DataFrame): Dữ liệu kiểm tra.
    y_valid (numpy.ndarray or pandas.Series): Nhãn của dữ liệu kiểm tra.

    Returns:
    list: Danh sách chứa PNL của các siêu tham số hàng đầu.
    """
    top_pnl = []
    
    for params in top_hyperparameters:
        # Tạo và huấn luyện mô hình
        model = xgb.XGBRegressor(**params)
        model.fit(X_train, y_train)
        
        # Đưa ra dự đoán
        y_pred_valid = model.predict(X_valid)
        _, pnl_valid, _, _ = sharpe_for_vn30f(y_pred_valid, y_valid)
        pnl_valid_no_nan = np.nan_to_num(pnl_valid, nan=0)
        top_pnl.append(pnl_valid_no_nan)

    return top_pnl

