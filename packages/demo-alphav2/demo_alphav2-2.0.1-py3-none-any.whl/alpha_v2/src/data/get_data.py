import requests
import pandas as pd
from datetime import datetime, timedelta

def get_vn30f():
    """
    Hàm này trả về dữ liệu giá cổ phiếu VN30F từ API

    Parameters
    ----------
    None
    
    Returns
    --------
    vn30fm : pandas.DataFrame
        DataFrame chứa dữ liệu giá cổ phiếu VN30F bao gồm cột 'Date' là thời gian, 
        'open' là giá mở cửa, 'high' là giá cao nhất, 'low' là giá thấp nhất, 'close' là giá đóng cửa, 
        và 'volume' là khối lượng giao dịch.
    """
    def vn30f():
        """
        Hàm này truy vấn API để lấy dữ liệu giá cổ phiếu VN30F từ API.

        Returns:
        pandas.DataFrame: Dữ liệu giá cổ phiếu VN30F dưới dạng pandas dataframe
        """
        return requests.get("https://services.entrade.com.vn/chart-api/chart?from=0000000000&resolution=1&symbol=VN30F1M&to=9999999999").json()

    # Lấy dữ liệu từ API và chuyển đổi thành DataFrame
    vn30fm = pd.DataFrame(vn30f()).iloc[:, :6]

    # Chuyển đổi cột 't' sang định dạng datetime và cập nhật múi giờ
    vn30fm['t'] = vn30fm['t'].astype(int).apply(lambda x: datetime.utcfromtimestamp(x) + timedelta(hours=7))

    # Đổi tên cột
    vn30fm.columns = ['Date', 'open', 'high', 'low', 'close', 'volume']

    # Tạo dictionary chứa các hàm tổng hợp cho các cột giá
    ohlc_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
    }

    # Đưa dữ liệu về định dạng chuẩn OHLC (Open, High, Low, Close)
    vn30fm = vn30fm.set_index('Date').resample('1D').apply(ohlc_dict)

    return vn30fm