"""### 与systemq交互的接口
- 如果接口路径发生变动以便于修改
- 主要导入lib(来自systemq)，qlisp|qlispc(systemq或独立安装)，waveforms
"""


from copy import deepcopy

from loguru import logger

try:
    # lib: systemq
    from lib import stdlib
except Exception as e:
    logger.critical('systemq may not be installed', e)
    raise e


# latest waveforms/qlisp/qlispc
from qlispc import Signal, get_arch, register_arch
from qlispc.arch.baqis import baqisArchitecture
from qlispc.arch.baqis.config import QuarkLocalConfig
from qlispc.kernel_utils import get_all_channels, qcompile, sample_waveform


# waveform==1.7.7
# from qlisp import Signal,get_arch,register_arch
# from lib.arch.baqis import baqisArchitecture
# from lib.arch.baqis_config import QuarkLocalConfig
# from qlisp.kernel_utils import get_all_channels,qcompile,sample_waveform


# waveforms.math: waveforms or waveform-math
from waveforms import Waveform, WaveVStack, square, wave_eval
from waveforms.namespace import DictDriver


class CompilerContext(QuarkLocalConfig):
    """编译所需上下文环境，即cfg表信息
    """

    def __init__(self, data) -> None:
        super().__init__(data)
        self.reset(data)
        self.initial = {}
        self.bypass = {}
        self._keys = []

    def reset(self, snapshot):
        """每个任务重置一次

        Args:
            snapshot (_type_): server中实时获取的cfg
        """
        self._getGateConfig.cache_clear()
        if isinstance(snapshot, dict):
            self._QuarkLocalConfig__driver = DictDriver(deepcopy(snapshot))
        else:
            self._QuarkLocalConfig__driver = snapshot

    def snapshot(self):
        return self._QuarkLocalConfig__driver

    def export(self):
        return self._QuarkLocalConfig__driver()


def _form_signal(sig):
    """signal类型
    """
    sig_tab = {
        'trace': Signal.trace,
        'iq': Signal.iq,
        'state': Signal.state,
        'count': Signal.count,
        'diag': Signal.diag,
        'population': Signal.population,
        'trace_avg': Signal.trace_avg,
        'iq_avg': Signal.iq_avg,
        'remote_trace_avg': Signal.remote_trace_avg,
        'remote_iq_avg': Signal.remote_iq_avg,
        'remote_state': Signal.remote_state,
        'remote_population': Signal.remote_population,
        'remote_count': Signal.remote_count,
    }
    if isinstance(sig, str):
        if sig == 'raw':
            sig = 'iq'
        try:
            return sig_tab[sig]
        except KeyError:
            pass
    elif isinstance(sig, Signal):
        return sig
    raise ValueError(f'unknow type of signal "{sig}".'
                     f" optional signal types: {list(sig_tab.keys())}")
