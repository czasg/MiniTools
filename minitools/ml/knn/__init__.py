import numpy as np

from collections import OrderedDict

from minitools.ml.base import Classification, SupervisedLearning

__all__ = 'KNearestNeighbor',

"""
ELEMENT:  value of K / distance measure / classified decision rule
INPUT:    the feature-vector of the instance
OUTPUT:   the class of instance
MODEL:    the training data set
THEORY:   using training data set to partition the feature-vector-space
FORMULA:  d(x, y) = (∑(x(i) - y(i))**2) ** 0.5
"""


class KNearestNeighbor(Classification, SupervisedLearning):
    k = 1

    @classmethod
    def box2vector(cls, box: np.ndarray) -> np.ndarray:
        vector = []
        for row in box:
            vector.extend(row)
        return np.array(vector)

    @classmethod
    def normalized(cls, dataSet: np.ndarray):
        r = dataSet.shape[0]
        minVal, maxVal = np.min(dataSet), np.max(dataSet)
        gap = maxVal - minVal
        return (dataSet - np.tile(minVal, (r, 1))) / np.tile(gap, (r, 1))

    @classmethod
    def classify(cls, vector: np.ndarray, trainSet: np.ndarray, trainLabel: list):
        sortedDistIndicies = (((np.tile(vector, (trainSet.shape[0], 1)) - trainSet) ** 2).sum(axis=1) ** 0.5).argsort()
        classCount = OrderedDict()
        for i in range(cls.k):
            kLabel = trainLabel[sortedDistIndicies[i]]
            classCount[kLabel] = classCount.get(kLabel, 0) + 1
        resSorted = sorted(classCount.items(), key=lambda x: x[1], reverse=True)
        return resSorted[0][0]
