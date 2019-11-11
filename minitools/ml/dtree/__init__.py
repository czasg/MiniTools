import math
import collections
import numpy as np

from minitools.ml.base import Classification, SupervisedLearning


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
    def splitdataSetLabel(cls, dataSet, dataSetLabel, index, value):
        return [dataSetLabel[i] for i, dataSetRow in enumerate(dataSet) if dataSetRow[index] == value]

    @classmethod
    def chooseFeature(cls, dataSet: np.ndarray, dataSetLabel, featureIndex=-1):
        length = float(len(dataSet))
        initEntropy = cls.calculateEntropy(dataSetLabel)
        baseMeasure = 0.0
        for index, dataSetRow in enumerate(dataSet.T):
            uniqueVals = set(dataSetRow)
            newEntropy = 0.0
            for value in uniqueVals:
                dataSetLabelNew = cls.splitdataSetLabel(dataSet, dataSetLabel, index, value)
                newEntropy += (len(dataSetLabelNew) / length) * cls.calculateEntropy(dataSetLabelNew)
            entropyMeasure = initEntropy - newEntropy
            if entropyMeasure >= baseMeasure:
                baseMeasure = entropyMeasure
                featureIndex = index
        return featureIndex


if __name__ == '__main__':
    test = DecisionTree()

    test1 = np.array([
        [1, 1],
        [1, 1],
        [1, 0],
        [0, 1],
        [0, 1],
    ])
    test2 = np.array([1, 1, 2, 2, 2])

    print(test.chooseFeature(test1, test2))

    test3 = np.array([
        [1, 1, 1],
        [1, 0, 1],
        [0, 1, 1],
        [1, 0, 0],
        [0, 0, 1],
        [0, 0, 0]
    ])
    test4 = np.array([1, 1, 1, 1, 0, 0])
    print(test.chooseFeature(test3, test4))
