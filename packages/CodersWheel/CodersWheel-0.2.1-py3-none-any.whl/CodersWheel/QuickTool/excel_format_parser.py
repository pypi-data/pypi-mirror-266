# coding=utf-8
import pandas as pd

import numpy as np

if __name__ == "__main__":
    dt = '2023-03-17'
    file_type = '周报观察池'

    f_path = "/pf_analysis/analysis\\output_2023-03-03(周报观察池).xlsx"

    f_path = "/pf_analysis/analysis\\output_2023-03-03(周报观察池).xlsx"

    x = pd.read_excel(f_path, sheet_name='指增')

    pct_cols = ['近3月区间收益率', '近6月区间收益率', '近12月区间收益率',
                '近3月年化收益率', '近6月年化收益率', '近12月年化收益率', '近3月年化波动率', '近6月年化波动率',
                '近12月年化波动率', '近3月信息比率', '近6月信息比率',
                '近12月信息比率', '近3月周胜率', '近6月周胜率',
                '近12月周胜率', '近3月最大回撤率', '近6月最大回撤率', '近12月最大回撤率', '近3月超额年化收益率',
                '近6月超额年化收益率', '近12月超额年化收益率', '近3月超额年化波动率', '近6月超额年化波动率',
                '近12月超额年化波动率',
                '近3月超额周胜率', '近6月超额周胜率',
                '近12月超额周胜率', '近3月超额的最大回撤', '近6月超额的最大回撤', '近12月超额的最大回撤',
                '近3月择时能力', '近6月择时能力', '近12月择时能力', '近3月选股能力', '近6月选股能力', '近12月选股能力',
                '近3月r2', '近6月r2', '近12月r2']

    numeric_cols = ['近3月年化夏普', '近6月年化夏普', '近12月年化夏普', '近3月卡玛比率', '近6月卡玛比率',
                    '近12月卡玛比率',
                    '近3月超额年化夏普', '近6月超额年化夏普', '近12月超额年化夏普', '近3月上涨市beta',
                    '近6月上涨市beta', '近12月上涨市beta', '近3月下跌市beta', '近6月下跌市beta', '近12月下跌市beta',
                    ]

    format_dict = {}  #
    pct_format = {col: '{:.2%}' for col in pct_cols}

    numeric_format = {num: '{:.2f}' for num in numeric_cols}

    format_dict.update(pct_format)

    format_dict.update(numeric_format)

    subset = ['近3月年化收益率', '近6月年化收益率', '近12月年化收益率',
              '近3月超额年化收益率', '近6月超额年化收益率', '近12月超额年化收益率',
              '近3月择时能力', '近6月择时能力', '近12月择时能力',
              '近3月选股能力', '近6月选股能力', '近12月选股能力',
              ]

    # with pd.ExcelWriter(f'test.xlsx') as f:
    #     x2.to_excel(f, 'test')
    x2 = x.sort_values('近3月区间收益率').style.format(format_dict).background_gradient(subset=subset, cmap='RdYlGn_r')
    print(1)

    pass
