import fim
import pandas as pd
import numpy as np
from marca.utils import transform_to_sequential, transform_to_sparse_data
from ..data_structures import CARs
from ._base import Extract


class Apriori(Extract):
    def __init__(
            self,
            support,
            confidence,
            max_len,
            remove_redundant=False,
    ):
        super().__init__()
        self.support = support
        self.confidence = confidence
        self.max_len = max_len
        self.remove_redundant = remove_redundant

    def _check_redundant(self, rules):
        if self.remove_redundant:
            aux = pd.DataFrame(rules)
            aux = aux.drop_duplicates(subset=[1], keep=False)
            rules = aux.values.tolist()
            del aux
        return rules

    def fit(self, X, y):
        data = transform_to_sequential(X, y)
        self.data_sparse = transform_to_sparse_data(data)
        appear = {None: 'a', }
        appear.update({consequent: 'c' for consequent in np.unique(data[:, -1])})
        print(appear)
        rules = fim.apriori(data.tolist(), supp=self.support * 100, conf=self.confidence * 100,
                            mode="o", target="r", report="sxy", appear=appear, zmin=2, zmax=self.max_len)

        if len(rules) == 0:
            raise Exception("Zero rules extract")

        rules = self._check_redundant(rules)

        cars = CARs([])
        cars.from_fim(rules, len(np.unique(data)))

        return cars
