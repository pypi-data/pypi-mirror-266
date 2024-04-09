import numpy as np
import pandas as pd

def remove_outliers(df, threshold=90):
    """
    Remove outliers from dataset.

    Parameters
    ----------
    df : pandas.DataFrame 
        DataFrame chứa dữ liệu cần xử lý, có cột 'close' chứa giá đóng cửa.
    threshold : float (default=90)
        Ngưỡng phần trăm để xác định giá trị outlier. Mặc định là 90.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame đã được xử lý để loại bỏ các giá trị outlier.
    """
    # Tính toán phần trăm thay đổi giá đóng cửa
    percentage_change = df['close'].pct_change() * 100

    # Tạo mask để xác định các giá trị outlier dựa trên ngưỡng threshold
    mask = (percentage_change > threshold) & (percentage_change < -threshold)

    # Thiết lập giá trị thay đổi dựa trên phần trăm thay đổi âm và dương
    change = df['close'].shift(-1) * (0.991)
    change[mask] = df['close'].shift(-1) * 1.009

    # Áp dụng giá trị thay đổi cho các giá trị outlier
    df.loc[mask, 'close'] = df.loc[mask, 'close'].shift(-1) * change.shift(-1)

    return df

def add_index(data):
    """
    Hàm này thêm các index mới cho dữ liệu.

    Args:
    data (pandas.DataFrame): DataFrame chứa dữ liệu cần thêm index.

    Returns:
    pandas.DataFrame: DataFrame đã được mở rộng với các index mới.
    """
    # Chia cột index thành cột 'time' và 'Date'
    data['time'] = [str(i)[11:] for i in data.index]
    data['Date'] = [str(i)[:10] for i in data.index]

    # Tạo bảng pivot với các cột 'open', 'high', 'low', 'close', 'volume' và giá trị là giá trị tương ứng của chúng
    pivot = data.pivot(index='Date', columns='time', values=['open', 'high', 'low', 'close', 'volume'])

    # Điền các giá trị NaN bằng phương pháp 'bfill' và stack lại dữ liệu
    fill = pivot.fillna(method='bfill').stack('time')

    return fill

