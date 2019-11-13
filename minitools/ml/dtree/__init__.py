import math
import collections
import numpy as np

from minitools.ml.base import Classification, SupervisedLearning

__all__ = "DecisionTree", "createDTree",

"""
ELEMENT:  value of K / distance measure / classified decision rule
INPUT:    the feature-vector of the instance
OUTPUT:   the class of instance
MODEL:    the training data set
THEORY:   using training data set to partition the feature-vector-space
FORMULA:  d(x, y) = (∑(x(i) - y(i))**2) ** 0.5
"""


class DecisionTree(Classification, SupervisedLearning):

    @classmethod
    def calculateEntropy(cls, dataSetLabel, initEntropy=0.0):
        length = len(dataSetLabel)
        counters = collections.Counter(dataSetLabel)
        for counter in counters.values():
            prob = float(counter) / length
            initEntropy -= prob * math.log(prob, 2)
        return initEntropy

    @classmethod
    def splitdataSetLabel(cls, dataSet: np.ndarray, dataSetLabel, index, value):
        dataSetNew = []
        dataSetLabelNew = []
        for i, dataSetRow in enumerate(dataSet.tolist()):
            if dataSetRow[index] == value:
                reduceDataVec = dataSetRow[:index]
                reduceDataVec.extend(dataSetRow[index + 1:])
                dataSetNew.append(reduceDataVec)
                dataSetLabelNew.append(dataSetLabel[i])
        return np.array(dataSetNew), dataSetLabelNew

    @classmethod
    def chooseFeature(cls, dataSet: np.ndarray, dataSetLabel, featureIndex=-1):
        assert len(dataSet) == len(dataSetLabel)
        length = float(len(dataSet))
        initEntropy = cls.calculateEntropy(dataSetLabel)
        baseMeasure = 0.0
        for index, dataSetRow in enumerate(dataSet.T):
            uniqueVals = set(dataSetRow)
            newEntropy = 0.0
            for value in uniqueVals:
                dataSetNew, dataSetLabelNew = cls.splitdataSetLabel(dataSet, dataSetLabel, index, value)
                newEntropy += (len(dataSetLabelNew) / length) * cls.calculateEntropy(dataSetLabelNew)
            entropyMeasure = initEntropy - newEntropy
            if entropyMeasure >= baseMeasure:
                baseMeasure = entropyMeasure
                featureIndex = index
        return featureIndex


def createDTree(dataSet: np.ndarray, dataSetLabel, dataSetColumnLabel: list):
    dataSetLabelCounter = collections.Counter(dataSetLabel)
    if dataSetLabelCounter.__len__() == 1 or len(dataSet[0]) == 0:
        return dataSetLabelCounter.most_common(1)[0][0]
    nextFutureIndex = DecisionTree.chooseFeature(dataSet, dataSetLabel)
    nextFutureDataSetLabel = dataSetColumnLabel.pop(min(nextFutureIndex, (len(dataSetColumnLabel) - 1)))
    decisionTree = {nextFutureDataSetLabel: {}}
    uniqueVals = set(dataSet.T[nextFutureIndex])
    for value in uniqueVals:
        dataSetNew, dataSetLabelNew = DecisionTree.splitdataSetLabel(dataSet, dataSetLabel, nextFutureIndex, value)
        nextDataSetColumnLabel = dataSetColumnLabel[:]
        decisionTree[nextFutureDataSetLabel][value] = createDTree(dataSetNew, dataSetLabelNew, nextDataSetColumnLabel)
    return decisionTree
