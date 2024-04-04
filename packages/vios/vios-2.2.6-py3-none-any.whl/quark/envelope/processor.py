"""### 数据处理
- read操作返回见各设备驱动,
- write操作返回None)
- 原始结果传给process进行处理
"""


import numpy as np
from loguru import logger

from .systemq import baqisArchitecture, get_arch, register_arch

register_arch(baqisArchitecture)


def demodulate(raw_data, **kwds):
    pass


def process(raw_data, **kwds):
    """处理数据

    Args:
        raw_data (dict): 从设备获取的原始结果

    Returns:
        result (dict): 处理后的数据, 形式为{'key1':np.array,'key2':np.array, ...}

    Example: raw_data例子
        ``` {.py3 linenums="1"}
        {'main': {'DAx86_153': {'CH1.Waveform': None}, 
                                'DAx86_50': {'CH1.Waveform': None}, 
                                'ADx86_159': {'CH10.CaptureMode': None,
                                              'CH11.CaptureMode': None, 
                                              'CH10.StartCapture': None, 
                                              'CH11.StartCapture': None}}, 
         'tigger': {'Trigger': {'CH1.TRIG': None}}, 
         'READ': {'ADx86_159': {'CH10.IQ': (array([[16.62256833],
                                                   ...,
                                                   [14.58617952]]), 
                                            array([[4.0120324 ],
                                                   ...,
                                                   [4.97671573]])), 
                                'CH11.IQ': (array([[14.6038444],
                                                   ...,
                                                   [15.33774413]]),
                                            array([[10.76387584],
                                                   ...,
                                                   [11.23863306]]))}}
        }
        ```
    """
    # print('ddddddddddoooooooooooooooooooooo', kwds)
    # print("=============================================", raw_data)

    dataMap = kwds.get('dataMap', {'arch': 'baqis'})
    result = {}

    try:

        if 'arch' in dataMap and dataMap['arch'] == 'general':
            return raw_data['READ']['AD']
        elif list(dataMap.keys()) == ['arch']:  # for NA
            if 'READ' in raw_data:
                print(raw_data)
                nadata = result['data'] = raw_data['READ']['NA']
                if 'CH1.Trace' in nadata:
                    result['data'] = raw_data['READ']['NA'].pop('CH1.Trace')
                elif 'CH1.S' in nadata:
                    result['data'] = raw_data['READ']['NA'].pop('CH1.S')
            result['extra'] = raw_data
        else:
            result = get_arch(dataMap['arch']).assembly_data(raw_data, dataMap)

            for k, v in result.items():
                if isinstance(v, dict):  # k: count
                    # v: {(0, 0): 100, (0, 1): 1, (1, 0): 2, (1, 1): 100}
                    base = np.array(tuple(v))
                    count = np.array(tuple(v.values()))
                    # result[k] = np.hstack((base, count[:, None]))
                    nb, nq, shots = *base.shape, kwds.get('shots', 1024)
                    result[k] = np.zeros((min(2**nq, shots), nq+1), int) - 1
                    result[k][:nb] = np.hstack((base, count[:, None]))
                else:
                    result[k] = np.asarray(v)
    except Exception as e:
        logger.error(f"{'>'*10} 'Failed to process the result', {e}, {'<'*10}")
        result['error'] = [
            f'Failed to process the result, raise Exception: {e.__class__.__name__}("{str(e)}")',
            raw_data,
            dataMap
        ]

    return result
