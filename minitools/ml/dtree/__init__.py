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


def createDTree(dataSet: np.ndarray, dataSetLabel):
    dataSetLabelCounter = collections.Counter(dataSetLabel)
    if dataSetLabelCounter.__len__() == 1 or len(dataSet[0]) == 1:
        return dataSetLabelCounter.most_common(1)[0][0]
    nextFutureIndex = DecisionTree.chooseFeature(dataSet, dataSetLabel)
    print(nextFutureIndex)
    nextFutureDataSetLabel = dataSetLabel[nextFutureIndex]
    decisionTree = {nextFutureDataSetLabel: {}}
    uniqueVals = set(dataSet.T[nextFutureIndex])
    for value in uniqueVals:
        dataSetNew, dataSetLabelNew = DecisionTree.splitdataSetLabel(dataSet, dataSetLabel, nextFutureIndex, value)
        decisionTree[nextFutureDataSetLabel][value] = createDTree(dataSetNew, dataSetLabelNew)
    return decisionTree

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

    # print(test.chooseFeature(test1, test2))

    test3 = np.array([
        [1, 1, 1],
        [1, 0, 1],
        [0, 1, 1],
        [1, 0, 0],
        [0, 0, 1],
        [0, 0, 0]
    ])
    test4 = np.array(['cza', 'cza', 'cza', 'cza', '0-0', '0-0'])
    # print(test.chooseFeature(test3, test4))

    # print(test.max(test4))

    # print(createDTree(test3, test4))

    tt = np.array([
        [1, ],
        [1, ],
        [2, ],
    ])
    # print(test.splitdataSetLabel(tt, [1, 2, 1], 0, 1))

    from pprint import pprint
    pprint(createDTree(test3, test4))
