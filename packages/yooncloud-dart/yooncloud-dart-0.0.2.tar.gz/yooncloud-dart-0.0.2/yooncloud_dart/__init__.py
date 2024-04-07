#-*- coding:utf-8 -*-
# 2020-2023 FinanceData.KR http://financedata.kr fb.com/financedata
import sys
from .dart import *

__version__ = '0.0.2'
__all__ = ['__version__', 'OpenDartReader']

sys.modules['yooncloud_dart'] = dart.OpenDartReader
