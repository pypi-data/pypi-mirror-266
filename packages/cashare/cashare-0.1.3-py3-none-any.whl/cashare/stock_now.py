from cashare.common.dname import url1
import pandas as pd
from cashare.common.get_data import _retry_get
def now_data(type,token):
    li = handle_url(type=type, token=token)
    r =_retry_get(li,timeout=100)
    if str(r) == 'token无效或已超期':
        return r
    else:
        if r.empty:
            return r
        else:
            #将最后一列更新为时间
            r = r.rename(columns={'timestamp':'time'})
            r['time'] = pd.to_datetime(r['time'], unit='s')
            return r
def handle_url(type,token):
    g_url=url1+'/us/stock/nowprice/'+type+'/'+token
    return g_url
if __name__ == '__main__':
    df = now_data(type='hk', token='you_token')
    print(df)




