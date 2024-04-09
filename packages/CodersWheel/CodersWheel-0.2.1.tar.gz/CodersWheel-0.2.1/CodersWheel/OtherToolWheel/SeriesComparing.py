# coding=utf8
import copy
import pandas as pd
from Needleman_Wunsch import Needleman_Wunsch
from CodersWheel.OtherToolWheel.typeassert import typeassert


class DataPoint(object):
    def __init__(self, label, value):
        self.__label_info = label
        self.__value_info = value

    @property
    def label(self):
        return self.__label_info

    @property
    def value(self):
        return self.__value_info


class DataSett(object):

    @classmethod
    @typeassert(object, series=pd.Series)
    def _transform(cls, series):
        index_list = series.index
        value_list = series.values
        return list(cls._transform_with_label(index_list, value_list))

    @staticmethod
    def _transform_with_label(index_list, value_list):
        for items in zip(index_list, value_list):
            yield DataPoint(*items)

    @staticmethod
    @typeassert(DataSettlist=list, label_name=str, value_name=str)
    def _parse_datapoint(DataSettlist, label_name=None, value_name=None):
        label_name = 'label' if label_name is None else label_name
        value_name = 'value' if value_name is None else value_name

        info = ((item.label, item.value) for item in DataSettlist)
        return pd.DataFrame(info, columns=[label_name, value_name])

    @classmethod
    @typeassert(object, pd.Series, label_name=str, value_name=str)
    def _parse(cls, series, label_name=None, value_name=None):
        return cls._transform(series)


class CheckSeries(object):

    def __init__(self, test_series, **src_series):
        self.test_series = test_series
        self.src_series = src_series

        self.length = len(test_series)
        self.length_src = [len(sr) for sr in self.src_series]
        pass

    @staticmethod
    @typeassert(test_series=pd.Series, test_name=str, compare_series=pd.Series, compare_name=str, empty_slot=DataPoint)
    def _do_NM(test_series, test_name, compare_series, compare_name, empty_slot=None):
        empty_slot = DataPoint('inserted', '-') if empty_slot is None else empty_slot
        dp_test_series = DataSett._parse(test_series)
        dp_compare_series = DataSett._parse(compare_series)
        NW_test, NM_compared = Needleman_Wunsch(dp_test_series, dp_compare_series, empty_slot=empty_slot)
        NW_test_df = DataSett._parse_datapoint(NW_test, value_name=test_name, label_name=test_name + 'label')
        NM_compared_df = DataSett._parse_datapoint(NM_compared, value_name=compare_name,
                                                   label_name=compare_name + 'label')

        wd = pd.concat([NW_test_df, NM_compared_df], axis=1)
        wd['cmp'] = (wd[wd.columns[1]] != wd[wd.columns[3]]) * 1

        return wd

    @staticmethod
    def _parse_numeric_compare_error(numeric_compare):
        print(numeric_compare)

    @staticmethod
    @typeassert(test_series=pd.Series, compare_series=pd.Series)
    def _get_coverage(test_series, compare_series):
        lentest_series = len(test_series)
        lensrc_series = len(compare_series)
        if lentest_series == lensrc_series and not test_series.empty and not compare_series.empty:
            numeric_compare = (test_series == test_series) * 1
            boolsum = numeric_compare.sum()
            coverage = boolsum * 1.0 / lentest_series
            return coverage, boolsum, numeric_compare
        else:
            if test_series.empty and compare_series.empty:
                raise ValueError('test series and compare series both are empty!')
            elif test_series.empty:
                raise ValueError('test series is empty!')
            elif compare_series.empty:
                raise ValueError('compare series is empty!')
            elif lentest_series > lensrc_series:
                raise ValueError('test series owns more rows than compare series!')
            elif lentest_series < lensrc_series:
                raise ValueError('compare series owns more rows than test series!')
            else:
                raise Exception('Unknown　Error!')


if __name__ == '__main__':
    # hs = SearchTools4HSNewMacroDatabase('hs')
    # testdata = hs.sql2data('select ID,ContractInnerCode from Fut_TradingQuote limit 100')
    # copied_testdata = copy.deepcopy(testdata)
    # CheckSeries._get_coverage(testdata.ID, copied_testdata.ID)
    # wd = CheckSeries._do_NM(testdata.ID, 'testid', copied_testdata[:97].ID, 'comparedid')

    # print(Needleman_Wunsch("AGCACACA", "ACACTA"))
    pass
