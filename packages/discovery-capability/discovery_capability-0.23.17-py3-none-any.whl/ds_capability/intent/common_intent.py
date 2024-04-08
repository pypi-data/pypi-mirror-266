import time
from typing import Callable

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from ds_capability.components.commons import Commons
from ds_core.handlers.abstract_handlers import ConnectorContract

__author__ = 'Darryl Oatridge'


class CommonsIntentModel(object):

    @classmethod
    def __dir__(cls):
        """returns the list of available methods associated with the parameterized intent"""
        rtn_list = []
        for m in dir(cls):
            if not m.startswith('_'):
                rtn_list.append(m)
        return rtn_list

    """
        PRIVATE METHODS SECTION
    """

    @staticmethod
    def _seed(seed: int=None, increment: bool=False):
        if not isinstance(seed, int):
            return int(time.time() * np.random.default_rng().random())
        if increment:
            seed += 1
            if seed > 2 ** 31:
                seed = int(time.time() * np.random.default_rng(seed=seed-1).random())
        return seed

    @staticmethod
    def _set_table_nulls(canonical: pa.Table, header: str, null_mask: pa.BooleanArray):
        """ Returns a table where the null_mask has been applied to the canonical header column values """
        values = canonical.column(header).combine_chunks()
        result = CommonsIntentModel._set_nulls(values=values, null_mask=null_mask)
        return Commons.table_append(canonical, pa.table([result], names=[header]))

    @staticmethod
    def _set_nulls(values: pa.Array, null_mask: pa.BooleanArray):
        """ Returns an array where the null_mask has been applied to the column values"""
        if len(values) != len(null_mask):
            null_list = Commons.list_resize(null_mask.to_pylist(), len(values))
            null_mask = pa.array(null_list, pa.bool_())
        return pc.if_else(null_mask, None, values)

    def _add_null_mask(self, values: pa.Array, num_nulls: [int, float], seed: int=None):
        """ Adds null values randomly over a given set of values in an array

        :param values: a pyarrow array
        :param num_nulls: the integer number of nulls or probability between 0 and 1
        :param seed: (optional) a seed for the random generator
        :return: pa.Array
        """
        num_nulls = self._extract_value(num_nulls)
        if num_nulls is None or num_nulls == 0:
            return values
        size = len(values)
        num_nulls = int(num_nulls * size) if isinstance(num_nulls, float) and 0 <= num_nulls <= 1 else int(num_nulls)
        num_nulls = num_nulls if 0 <= num_nulls < size else size
        rng = np.random.default_rng(seed)
        mask = [True] * size
        mask[:num_nulls] = [False] * num_nulls
        rng.shuffle(mask)
        return pc.if_else(mask, values, None)

    def _set_quantity(self, selection, quantity, seed=None):
        """Returns the quantity percent of good values in selection with the rest fill"""
        quantity = self._quantity(quantity)
        if quantity == 1:
            return selection
        if quantity == 0:
            return [np.nan] * len(selection)
        seed = self._seed(seed=seed)
        quantity = 1 - quantity
        generator = np.random.default_rng(seed)
        length = len(selection)
        size = int(length * quantity)
        nulls_idx = generator.choice(length, size=size, replace=False)
        result = pd.Series(selection)
        result.iloc[nulls_idx] = pd.NA
        return result.to_list()

    @staticmethod
    def _quantity(quantity: [float, int]) -> float:
        """normalises quantity to a percentate float between 0 and 1.0"""
        if not isinstance(quantity, (int, float)) or not 0 <= quantity <= 100:
            return 1.0
        if quantity > 1:
            return round(quantity / 100, 2)
        return float(quantity)


    @staticmethod
    def _extract_value(value: [str, int, float]):
        if isinstance(value, str):
            if value.startswith('${') and value.endswith('}'):
                value = ConnectorContract.parse_environ(value)
                if value.isnumeric():
                    return int(value)
                elif value.replace('.', '', 1).isnumeric():
                    return float(value)
                else:
                    return str(value)
            else:
                return str(value)
        return value

    """
        UTILITY METHODS SECTION
    """

    @staticmethod
    def _freq_dist_size(relative_freq: list, size: int, dist_length: int=None, dist_on: str=None, seed: int=None):
        """ utility method taking a list of relative frequencies and based on size returns the size distribution
        of element based on the frequency. The distribution is based upon binomial distributions.

        :param relative_freq: a list of int or float values representing a relative distribution frequency
        :param size: the size of the values to be distributed
        :param dist_length: (optional) the expected length of the element's in relative_freq
        :param dist_on: (optional) if element length differs. distribute on 'left', 'right' or 'center'. Default 'right'
        :param seed: (optional) a seed value for the random function: default to None
        :return: an integer list of the distribution that sum to the size
        """
        if not isinstance(relative_freq, list) or not all(isinstance(x, (int, float)) for x in relative_freq):
            raise ValueError("The weighted pattern must be an list of numbers")
        dist_length = dist_length if isinstance(dist_length, int) else len(relative_freq)
        dist_on = dist_on if dist_on in ['right', 'left'] else 'both'
        seed = seed if isinstance(seed, int) else int(time.time() * np.random.random())
        # sort the width
        if len(relative_freq) > dist_length:
            a = np.array(relative_freq)
            trim = dist_length - a.size
            if dist_on.startswith('right'):
                relative_freq = a[:trim]
            elif dist_on.startswith('left'):
                relative_freq = a[abs(trim):]
            else:
                l_size = int(trim/2)
                r_size = a.size + l_size - dist_length
                relative_freq = a[r_size:l_size].tolist()
        if len(relative_freq) < dist_length:
            a = np.array(relative_freq)
            rvalue = a[-1:]
            lvalue = a[:1]
            if dist_on.startswith('left'):
                r_dist = []
                l_dist = np.tile(lvalue, dist_length - a.size)
            elif dist_on.startswith('right'):
                r_dist = np.tile(rvalue, dist_length - a.size)
                l_dist = []
            else:
                l_size = int((dist_length - a.size) / 2)
                r_dist = np.tile(rvalue, l_size)
                l_dist = np.tile(lvalue, dist_length - l_size - a.size)
            relative_freq = np.hstack([l_dist, a, r_dist]).tolist()
        # turn it to percentage
        if sum(relative_freq) != 1:
            relative_freq = np.round(relative_freq / np.sum(relative_freq), 5)
        # generate occurrence based on relative frequency
        generator = np.random.default_rng(seed=seed)
        result = list(generator.binomial(n=size, p=relative_freq, size=len(relative_freq)))
        diff = size - sum(result)
        adjust = [0] * len(relative_freq)
        # There is a possibility the required size is not fulfilled, therefore add or remove elements based on freq
        if diff != 0:
            unit = diff / sum(relative_freq)
            for idx in range(len(relative_freq)):
                adjust[idx] = int(round(relative_freq[idx] * unit, 0))
        result = [a + b for (a, b) in zip(result, adjust)]
        # rounding can still make us out by 1
        if sum(result) != size:
            gap = sum(result) - size
            result[result.index(max(result))] -= gap
        return result

    @staticmethod
    def _gen_category(column: pa.Array, size: int, generator: np.random.default_rng):
        """"""
        if not pa.types.is_dictionary(column.type):
            column = column.dictionary_encode()
        column = column.fill_null('<N>')
        vc = column.value_counts()
        t = pa.table([vc.field(1), vc.field(0).dictionary], names=['v','n']).sort_by([("v", "descending")])
        frequency = pc.round(pc.divide_checked(t.column('v').cast(pa.float64()), pc.sum(t.column('v'))),3).to_pylist()
        select = pc.cast(t.column('n'), pa.string()).to_pylist()
        if sum(frequency) != 1:
            frequency = np.round(frequency / np.sum(frequency), 5)
            frequency[0] += 1-sum(frequency)
        result = generator.choice(a=select, size=size, replace=True, p=frequency)
        rtn_arr = pa.array(result)
        mask = pc.is_in(rtn_arr, pa.array(['<N>']))
        rtn_arr = pc.if_else(mask, None, rtn_arr)
        return rtn_arr

    @staticmethod
    def _jitter(column: pa.Array, size: int, generator: np.random.default_rng, variance: float=None, probability: list=None):
        """"""
        variance = variance if isinstance(variance, float) else 0.4
        values = column.to_numpy()
        values = generator.choice(values, size=size, replace=True, p=probability)
        zeros = pc.equal(values, 0)
        jitter = pc.round(pc.multiply(pc.stddev(column), variance), 5).as_py()
        result = np.add(values, generator.normal(loc=0, scale=jitter, size=size))
        arr = pa.Array.from_pandas(result)
        if pa.types.is_integer(column.type):
            arr = pc.round(arr, 0).cast(column.type)
        else:
            arr = pc.round(arr, Commons.column_precision(column))
        return pc.if_else(zeros, 0, arr)

    @staticmethod
    def _jitter_date(column: pa.Array, size: int, generator: np.random.default_rng, variance: int=None, units: str=None,
                     ordered: str=None, probability: list=None):
        """"""
        variance = variance if isinstance(variance, int) else 2
        units_allowed = ['W', 'D', 'h', 'm', 's', 'milli', 'micro']
        units = units if isinstance(units, str) and units in units_allowed else 'D'
        s_values = column.to_pandas()
        s_values = generator.choice(s_values, size=size, replace=True, p=probability)
        jitter = pd.Timedelta(value=variance, unit=units) if isinstance(variance, int) else pd.Timedelta(value=0)
        jitter = int(jitter.to_timedelta64().astype(int) / 10 ** 3)
        _ = generator.normal(loc=0, scale=jitter, size=size)
        _ = pd.Series(pd.to_timedelta(_, unit='micro'), index=s_values.index)
        result = s_values.add(_)
        if isinstance(ordered, str) and ordered.lower() in ['asc', 'des']:
            result = result.sort_values(ascending=True if ordered.lower() == 'asc' else False)
        return pa.TimestampArray.from_pandas(result)

class AnalysisOptions(object):

    def __init__(self):
        self._options = {}

    def add_option(self, name: str, **kwargs):
        self._options[name] = kwargs

    def get_option(self, name: str):
        return self._options.get(name, {})

    @property
    def options(self):
        return self._options.copy()

    def __len__(self):
        return self._options.__len__()

    def __str__(self):
        return self._options.__str__()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._options.__str__()}"

    def __eq__(self, other: dict):
        return self._options.__eq__(other)
