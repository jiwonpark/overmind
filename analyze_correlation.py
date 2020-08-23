import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from mpl_finance import plot_day_summary_ohlc

from loader import retrieve_polo
from datetime import datetime

def mask_h(plt, x1, x2, min_y, max_y, color, alpha):
    return plt.Rectangle((x1, min_y), x2 - x1, max_y - min_y, linewidth=0, alpha=alpha, edgecolor=color, facecolor=color)

segment = retrieve_polo('USDT_LTC', 30, '2020-08-10', '2020-08-16') # 요구된 봉 데이터를 Poloniex 거래소 API로 읽어와서 n x 6 크기의 numpy array로 만들어주는 함수

purge_percent_threshold = 1

required_lead = 100

max_snapshots = 5
snapshots_count = 0

fig = plt.figure(figsize=(20, 7 * max_snapshots))
gs_all = gridspec.GridSpec(max_snapshots, 1, figure=fig)

dates = mdates.date2num([datetime.fromtimestamp(segment[i,0]) for i in range(segment.shape[0])])
ohlc = [[dates[i], segment[i,1], segment[i,3], segment[i,4], segment[i,2]] for i in range(segment.shape[0])]

for i in range(segment.shape[0]):
    ts = segment[i,0]
    open = segment[i,1]
    close = segment[i,2]
    high = segment[i,3]
    low = segment[i,4]
    volume = segment[i,5]
    movement_percent = (close / open - 1) * 100

    if i > required_lead and movement_percent > purge_percent_threshold:
        print('[{:05d}] {:s} {:7.3f} {:7.3f} {:7.3f} {:7.3f} {:10.3f} {:6.2f}%'.format(i, str(datetime.fromtimestamp(ts)), open, close, high, low, volume, movement_percent))

        if snapshots_count < max_snapshots:

            begin = i - required_lead
            end = i + 50

            center = (open + close) / 2
            min_y = center - 5
            max_y = center + 5

            ax = fig.add_subplot(gs_all[snapshots_count], ylim=(min_y, max_y))

            plot_day_summary_ohlc(ax, ohlc[begin:end])
            plt.xticks([dates[i]], rotation=0)
            ax.add_patch(mask_h(plt, dates[i] - (30/(24*60)/2), dates[i] + (30/(24*60)/2), min_y, max_y, 'yellow', 1.0))
            plot_day_summary_ohlc(ax, ohlc[begin:end])

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

            snapshots_count += 1

print('INDEX   TIMESTAMP            OPEN    CLOSE   HIGH    LOW     VOLUME      MOVE')

print(segment.shape) # 봉 하나는 위와 같이 6개 element로 이루어져있고, 이것이 요청한 duration에 따라 n개가 있는 2차원 배열이다.

print('Rendering...')
fig.savefig("analyze_correlation.png", bbox_inches='tight', dpi=100)
plt.close(fig)
print('done')
