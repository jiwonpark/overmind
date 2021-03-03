import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from mplfinance.original_flavor import plot_day_summary_ohlc
from mplfinance.original_flavor import candlestick2_ohlc

import numpy as np
import pandas as pd

from loader import retrieve_polo
from datetime import datetime

import time

def mask_h(plt, x1, x2, min_y, max_y, color, alpha):
    return plt.Rectangle((x1, min_y), x2 - x1, max_y - min_y, linewidth=0, alpha=alpha, edgecolor=color, facecolor=color)

purge_percent_threshold = 3

required_lead = 60
required_tail = 20

max_snapshots = 10

coins_count = 2

snapshots_count = 0
fig = plt.figure(figsize=(20 * max_snapshots, 7 * coins_count))
gs_all = gridspec.GridSpec(coins_count, max_snapshots, figure=fig)

def condition_step_up(segment, i):
    n = 1
    m = 20
    return min(segment[i+1:i+1+m,4]) / max(segment[i-n:i,3]) > purge_percent_threshold

class Series:
    def __init__(self, segment):
        self.segment = segment

        self.dates = mdates.date2num([datetime.fromtimestamp(segment[i,0]) for i in range(segment.shape[0])])
        self.ohlc = [[self.dates[i], segment[i,1], segment[i,3], segment[i,4], segment[i,2]] for i in range(segment.shape[0])]

        # numpy array를 pandas DataFrame으로 바꾸면 pandas에서 제공하는 보다 편리한 기능들(아래 rolling, ewm 등)을 활용할 수 있다.
        self.segment_pd = pd.DataFrame(data=segment[:,1:], index=self.dates, columns=['open', 'close', 'high', 'low', 'volume'])

        # pandas DataFrame은 이런식으로 index 번호가 아닌, 위에서 columns 파라미터로 지정된 label로 각 column을 지정한다.
        self.hsma40 = self.segment_pd['high'].rolling(40).mean()
        self.lsma40 = self.segment_pd['low'].rolling(40).mean()
        self.ema15 = self.segment_pd['close'].ewm(15).mean()
        self.ema5 = self.segment_pd['close'].ewm(5).mean()
        # self.ema60 = self.segment_pd['close'].ewm(60).mean()

        # print(self.hsma40.describe())
        # print(self.lsma40.describe())
        # print(self.ema15.describe())

    def draw(self, ax, i):
        tic = time.perf_counter()

        span_minutes = (self.segment[1,0] - self.segment[0,0]) / 60
        print(span_minutes)

        begin = i - required_lead
        end = i + required_tail

        open = self.segment[i,1]
        close = self.segment[i,2]
        center = (open + close) / 2
        min_y = center / 1.05
        max_y = center * 1.05
        # min_y = min(self.segment[begin:i,4])
        # max_y = max(self.segment[begin:i,3])

        plt.xticks([self.dates[i]], rotation=0)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        ax.set_ylim(bottom = min_y, top = max_y)

        ax.add_patch(mask_h(plt, self.dates[i] - (span_minutes/(24*60)/2), self.dates[i] + (span_minutes/(24*60)/2), min_y, max_y, 'yellow', 1.0))

        plot_day_summary_ohlc(ax, self.ohlc[begin:end])

        ax.plot(self.hsma40[self.dates[begin]:self.dates[end]], color = 'blue', linewidth = 2, label='High, 40-Day SMA')
        ax.plot(self.lsma40[self.dates[begin]:self.dates[end]], color = 'blue', linewidth = 2, label='Low, 40-Day SMA')
        ax.plot(self.ema15[self.dates[begin]:self.dates[end]], color = 'red', linestyle='--', linewidth = 2, label='Close, 15-Day EMA')
        ax.plot(self.ema5[self.dates[begin]:self.dates[end]], color = 'green', linestyle='--', linewidth = 2, label='Close, 5-Day EMA')
        # ax.plot(self.ema60[self.dates[begin]:self.dates[end]], color = 'purple', linestyle='--', linewidth = 2, label='Close, 60-Day EMA')

        toc = time.perf_counter()
        print('{:.3f} ms'.format((toc - tic) * 1000))

def ff(x):
    if x is None:
        return 'None  '
    else:
        return '{:.3f}'.format(x)

import pytz

def ft(unix_timetamp_in_ms):
    return str(datetime.fromtimestamp(unix_timetamp_in_ms / 1000, tz=pytz.utc))

import json

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24

def load_poloniex_candles_from_csv(polo_pair, candle_minutes):
    period = candle_minutes * MINUTE

    a = np.genfromtxt('poloniex.{}.{}.csv'.format(polo_pair, period), delimiter=",")

    # print(a.shape)

    max_unit = 24 * 60 * 60
    if a[0,0] % max_unit != 0:
        a = a[int((max_unit - a[0,0] % max_unit) / period):,:]
    print(ft(a[0,0] * 1000))
    
    return a

def get_candle(segment, i):
    ts = segment[i,0]
    open = segment[i,1]
    close = segment[i,2]
    high = segment[i,3]
    low = segment[i,4]
    volume = segment[i,5]
    movement_percent = (close / open - 1) * 100
    return (ts, open, close, high, low, volume, movement_percent)

def standardize(segment):
    upper = max(segment[:,3])
    lower = min(segment[:,4])
    center = (upper + lower) / 2
    # print(upper, lower, center)
    segment = (segment[:,1:5] - center) / (upper - center)
    return segment

def get_distance(segment1, segment2):
    assert segment1.shape[0] == segment2.shape[0]
    n = segment1.shape[0]
    std_segment1 = standardize(segment1)
    std_segment2 = standardize(segment2)
    diff_sum_of_squares = 0
    for i in range(n):
        diff_sum_of_squares += (std_segment1[i, 2] - std_segment2[i, 2]) ** 2
        diff_sum_of_squares += (std_segment1[i, 3] - std_segment2[i, 3]) ** 2
    return diff_sum_of_squares

def test_correlation():
    segment = retrieve_polo('USDT_BTC', 30, '2020-08-10', '2020-08-16') # 요구된 봉 데이터를 Poloniex 거래소 API로 읽어와서 n x 6 크기의 numpy array로 만들어주는 함수
    btc = Series(segment)
    segment = retrieve_polo('USDT_LTC', 30, '2020-08-10', '2020-08-16') # 요구된 봉 데이터를 Poloniex 거래소 API로 읽어와서 n x 6 크기의 numpy array로 만들어주는 함수
    ltc = Series(segment)

    for i in range(segment.shape[0]):
        (ts, open, close, high, low, volume, movement_percent) = get_candle(segment, i)

        if i > required_lead and movement_percent > purge_percent_threshold:
            print('[{:05d}] {:s} {:7.3f} {:7.3f} {:7.3f} {:7.3f} {:10.3f} {:6.2f}%'.format(i, str(datetime.fromtimestamp(ts)), open, close, high, low, volume, movement_percent))

            standardize(segment[i-required_lead:i,:])

            if snapshots_count < max_snapshots:

                ax = fig.add_subplot(gs_all[0, snapshots_count])
                btc.draw(ax, i)

                ax = fig.add_subplot(gs_all[1, snapshots_count])
                ltc.draw(ax, i)

                snapshots_count += 1

    print(segment.shape) # 봉 하나는 위와 같이 6개 element로 이루어져있고, 이것이 요청한 duration에 따라 n개가 있는 2차원 배열이다.

def test_simularity():
    global snapshots_count

    # segment = retrieve_polo('USDT_LTC', 30, '2018-01-10', '2020-09-15') # 요구된 봉 데이터를 Poloniex 거래소 API로 읽어와서 n x 6 크기의 numpy array로 만들어주는 함수

    segment = load_poloniex_candles_from_csv('USDT_LTC', 30)

    ltc = Series(segment)

    last_timestamp = None

    for i in range(segment.shape[0]):
        (ts, open, close, high, low, volume, movement_percent) = get_candle(segment, i)
        if last_timestamp is not None and ts - last_timestamp < 30 * 60 * 50:
            continue

        # if i > required_lead and movement_percent > purge_percent_threshold:
        if i > required_lead and min(segment[i-0:i+required_tail,4]) >= segment[i,1]:
        # if i > required_lead and min(segment[i+1:i+100,4]) / max(segment[i-200:i,3]) > 1.01:
            print('[{:05d}] {:s} {:7.3f} {:7.3f} {:7.3f} {:7.3f} {:10.3f} {:6.2f}%'.format(i, str(datetime.fromtimestamp(ts)), open, close, high, low, volume, movement_percent))

            # if snapshots_count < max_snapshots:

            #     ax = fig.add_subplot(gs_all[0, snapshots_count])
            #     ltc.draw(ax, i)

            #     begin = i - required_lead
            #     end = i + 50

            #     std_segment = standardize(segment[begin:end,:])
        
            #     ax = fig.add_subplot(gs_all[1, snapshots_count])
            #     candlestick2_ohlc(ax, std_segment[:,0], std_segment[:,3], std_segment[:,2], std_segment[:,1], width=0.5)
            #     ax.set_ylim(bottom = -1, top = 1)

            #     snapshots_count += 1

            min_dist = None
            min_dist_j = None

            for j in range(i+50, segment.shape[0]):
                (ts, open, close, high, low, volume, movement_percent) = get_candle(segment, j)

                dist = get_distance(segment[i-required_lead:i,:], segment[j-required_lead:j,:])

                if min_dist is None or min_dist > dist:
                    min_dist = dist
                    min_dist_j = j
                
            if snapshots_count < max_snapshots:

                ax = fig.add_subplot(gs_all[0, snapshots_count])
                ltc.draw(ax, i)

                ax = fig.add_subplot(gs_all[1, snapshots_count])
                ltc.draw(ax, min_dist_j)

                snapshots_count += 1
            
            else:
                return

            last_timestamp = segment[i,0]

from sklearn.cluster import KMeans
import sys

def get_clusters(segment, x, y, c):
    n = segment.shape[0]
    r = n - x

    samples = np.empty((r, x * 4))
    for i in range(r):
        subsegment = standardize(segment[i:i+x,:])
        for j in range(x):
            samples[i, j * 4 + 0] = subsegment[j, 0]
            samples[i, j * 4 + 1] = subsegment[j, 1]
            samples[i, j * 4 + 2] = subsegment[j, 2]
            samples[i, j * 4 + 3] = subsegment[j, 3]

    clustering = KMeans(n_clusters=c, n_init=10, random_state=1)
    clustering.fit(samples)
    
    np.set_printoptions(threshold=sys.maxsize)
    # print(clustering.labels_)
    print(clustering.labels_.shape)

    return clustering

def find_common_permutations(segment, clustering, c):
    global snapshots_count

    n = segment.shape[0]
    r = n - x

    # Remove consecutive duplicates
    duplicates = np.full(r, False)
    last_cluster = -1
    for i in range(r):
        if last_cluster == clustering.labels_[i]:
            duplicates[i] = True
        else:
            last_cluster = clustering.labels_[i]

    # Count each permutation
    max_x = None
    max_y = None
    max_count = 0
    permutations = np.zeros((c,c))
    for i in range(r-y):
        if not duplicates[i]:
            x_cluster = clustering.labels_[i]
            y_cluster = clustering.labels_[i+x]
            permutations[x_cluster, y_cluster] += 1
            count = permutations[x_cluster, y_cluster]
            if max_count < count:
                max_count = count
                max_x = x_cluster
                max_y = y_cluster
    sum = 0
    for i in range(c):
        for j in range(c):
            sum += permutations[i,j]
    print(sum)
    print(pd.DataFrame(permutations))
    print(max_x, max_y, max_count)

    ltc = Series(segment)

    # Sneak peek
    for i in range(r-y):
        if not duplicates[i] and clustering.labels_[i] == max_x and clustering.labels_[i+x] == max_y:
            if snapshots_count < max_snapshots:
                ax = fig.add_subplot(gs_all[0, snapshots_count])
                ltc.draw(ax, i)
                snapshots_count += 1
