from loader import retrieve_polo
from datetime import datetime

segment = retrieve_polo('USDT_LTC', 30, '2020-08-10', '2020-08-16') # 요구된 봉 데이터를 Poloniex 거래소 API로 읽어와서 n x 6 크기의 numpy array로 만들어주는 함수

for i in range(segment.shape[0]):
    ts = segment[i,0]
    open = segment[i,1]
    close = segment[i,2]
    high = segment[i,3]
    low = segment[i,4]
    volume = segment[i,5]
    print('{:s} {:.3f} {:.3f} {:.3f} {:.3f} {:10.3f}'.format(str(datetime.fromtimestamp(ts)), open, close, high, low, volume))

print('TIMESTAMP           OPEN   CLOSE  HIGH   LOW    VOLUME')

print(segment.shape) # 봉 하나는 위와 같이 6개 element로 이루어져있고, 이것이 요청한 duration에 따라 n개가 있는 2차원 배열이다.

