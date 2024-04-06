"""!!! note "模块说明"
- 所有驱动继承自BaseDriver，类名统一为Driver，并要求实现open/close/read/write四个方法。样板见VirtualDevice
- 所有厂家提供的底层库，均放于driver/common内，各自新建文件夹分别放置
"""


try:
    # import URL from dev in systemq
    from dev import URL
except Exception as e:
    URL = 'Not Found'
