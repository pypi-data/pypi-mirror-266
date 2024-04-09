import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def choose_position(change):
    """
    Identify position according to value of change.
    
    This function will take change and decide the position. 
    If change is larger than 0, position will be long position,
    if change is smaller than 0, position will be short position,
    otherwise position will be neutral position.

    Parameters
    ----------
    change : numpy.float32
    
    Returns
    -------
    pos : int
    """
    if change >0:
        pos = 1
    elif change == 0:
        pos = 0
    else:
        pos = -1
    
    return pos

def backtest_position_ps(position, change): 
    """
    Parameters
    ----------
    position : 
    change :
    
    Returns
    -------
    pnk_long_short : 
    """
    pos = pd.Series(position).shift(1).fillna(0)
    ch = pd.Series(change).shift(1).fillna(0)

    pos_long = np.where(pos > 0, pos, 0)
    pos_short = np.where(pos < 0, pos, 0)
    pnl_long_short = ch * pos_long + ch * pos_short

    return pnl_long_short

def draw_corr(corr):
    """
    Vẽ biểu đồ ma trận tương quan.

    Args:
    corr (numpy.ndarray or pandas.DataFrame): Ma trận tương quan.

    Returns:
    None
    """
    plt.matshow(corr)  # Invert y-axis to get origo at lower left corner
    plt.gca().xaxis.tick_bottom()
    plt.gca().invert_yaxis()
    plt.colorbar()
    plt.show()
    
def cov2corr(cov):
    """
    Chuyển ma trận hiệp phương sai thành ma trận tương quan tương ứng.

    Args:
    cov (numpy.ndarray): Ma trận hiệp phương sai.

    Returns:
    numpy.ndarray: Ma trận tương quan tương ứng.
    """
    # Tính độ lệch chuẩn của từng biến
    std = np.sqrt(np.diag(cov))
    
    # Tính ma trận tương quan từ ma trận hiệp phương sai
    corr = cov / np.outer(std, std)
    
    # Xử lý các giá trị ngoại lai gây ra bởi lỗi số học
    corr[corr < -1] = -1
    corr[corr > 1] = 1
    
    return corr
