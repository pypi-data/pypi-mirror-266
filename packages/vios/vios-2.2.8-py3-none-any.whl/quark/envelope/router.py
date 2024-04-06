"""### 数据后处理
- 任务结束之后对结果进行后处理, 如返回云端或其他处理.
"""

import json
import shutil
import time
from pathlib import Path

import numpy as np
import requests
from loguru import logger

from quark.proxy import QuarkProxy


def savefig(result):
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use('agg')

    fig, ax = plt.subplots(2, 2, figsize=[9, 9])
    ax = ax.flatten()
    for a in ax:
        a.plot([1, 2, 3])
    plt.savefig('test.png')


def schedule():
    """执行事先设定好的定时任务, 默认为每天凌晨2点到6点.

    Example: `定时规则由etc.schedule指定`
        - year(int | str): 年(4位数字)
        - month(int | str): 月(范围1-12)
        - day(int | str): 日(范围1-31)
        - week(int | str): 周(范围1-53)
        - day_of_week(int | str): 周内第几天或者星期几(0-6 或 mon,tue,wed,thu,fri,stat,sun)
        - hour(int | str): 时(0-23)
        - minute(int | str): 分(0-59)
        - second(int | str): 秒(0-59)
    """
    # dst = shutil.move(Path('../../home/dat/144v3-swj-221013-normalJJ_2023-03-01-22-37-23.hdf5'),Path.home())
    # for path in sorted(Path('../../home/dat').glob('**/*.hdf5')):
    #     print((time.time() - path.stat().st_mtime)/(24*60*60),shutil.disk_usage(path))
    def test1():
        print(time.strftime('%Y-%m-%d %H:%M:%S'), 'do something1 ...')

    def test2():
        print(time.strftime('%Y-%m-%d %H:%M:%S'), 'do something2 ...')

    return {}  # {'job1': test1,'job2': test2}
    # return [(r'C:\Usersddd\sesam\Desktop\home\dat\baqis\testtask_2023-08-31-12-35-12.hdf5',r'\home\dat\baqis\testtask_2023-08-31-12-35-12.hdf5')]


def postprocess(result: dict):
    """任务执行完后对数据的操作, 如存储到自定义路径或回传到云平台等

    Args:
        result (dict): 任务结果

    Example: result例子
        ``` {.py3 linenums="1"}
        {'data': {'iq_avg': array([[ 6.98367485 +3.05121544j, 17.98372871+14.02688919j],
                                   [14.9855748 +16.99029603j, 12.00005981+10.98745889j],
                                   [ 5.05074742 +0.96293022j, 18.00112126 +5.98929904j]])},
         'meta': {'tid': 202403122306141782,
                  'name': 'testtask:/PowerRabi1D',
                  'user': 'baqis',
                  'priority': 1,
                  'system': 'checkpoint144',
                  'status': 'Finished',
                  'other': {'shots': 1024,
                            'signal': 'iq_avg',
                            'standby': True,
                            'autorun': True,
                            'filesize': 4000.0},
                  'axis': {'amps': {'amps_Q1001': array([0.1, 0.3, 0.5]),
                                    'amps_Q1101': array([0.1, 0.3, 0.5])}},
                  'committed': 'bbd5533a5863fb88dbb7eba5109ed624abda8e4c',
                  'created': '2024-03-12-23-06-15',
                  'finished': '2024-03-12-23-06-17'}
        }
        ``` 
    """

    # print(result.keys(),result['meta'].keys())

    quafu = result['meta'].get('coqis', {})
    # savefig(result)
    if not quafu.get('token', ''):
        return

    res = QuarkProxy.process(result)

    rshot = 0
    post_data = {"task_id": quafu['eid'],
                 "status": res['status'],
                 "raw": "",
                 "res": "",
                 'transpiled_circuit': res['transpiled'],
                 "server": quafu['systemid']}

    if res['status'] == 'finished':
        rshot = sum(res['count'].values())
        post_data.update({"raw": str(res['count']).replace("\'", "\""),
                          "res": str(res['corrected']).replace("\'", "\""),
                          })

    try:
        resp = requests.post(url=f"http://124.70.54.59/qbackend/scq_result/",
                             data=post_data,
                             headers={'api_token': quafu['token']})
        logger.info(f'Back to quafu: {resp.text} {rshot}')
    except Exception as e:
        logger.error(f'Failed to post result: {e}')
