import numpy as np
import collections

from minitools.ml.base import Classification, SupervisedLearning

__all__ = "NaiveBayes",

"""
Bag of words


"""


class NaiveBayes(Classification, SupervisedLearning):

    @classmethod
    def generatingSet(cls, *args, default=None):
        default = set(default) if default else set()
        for arg in args:
            default |= set(arg)
        return [i for i in default if len(i) > 1]

    @classmethod
    def set2vector(cls, words, wordsSet: list):
        vector = [0 for _ in range(len(wordsSet))]
        for word in words:
            if word in wordsSet:
                vector[wordsSet.index(word)] += 1
        return vector

    @classmethod
    def trainDataSet(cls, trainSets: np.ndarray, trainSetLabels) -> list:
        trainSetLabelLength = len(trainSetLabels)
        uniqueLabelLength = float(len(set(trainSetLabels)))
        trainSetRowLenght = len(trainSets[0])
        doc = dict()
        for key, count in collections.Counter(trainSetLabels).items():
            doc[key] = [float(count) / float(trainSetLabelLength), np.ones(trainSetRowLenght), uniqueLabelLength]
        for index, trainSet in enumerate(trainSets):
            doc[trainSetLabels[index]][1] += trainSet
            doc[trainSetLabels[index]][2] += np.sum(trainSet)
        # 类别标签 + 在某个类别下，每个特征元素出现的概率 + 唯一标签
        return [(key, list(np.log(value[1] / value[2])), value[0]) for key, value in doc.items()]

    @classmethod
    def classify(cls, dataSet, *trainSets):
        resData = None
        resLabel = None
        for trainSet in trainSets:
            # 乘法转化为加法：即log[p(x1|C)*p(x2|C)..] = log[p(x1|C)] + log[p(x2|C)] + ...
            # 这里的每一个特征元素值，均表示该特征在此标签类别下出现的概率
            # dataSet * trainSet[1] 表示将每个词与对应的概率相关联起来
            predict = np.array(trainSet[1]).dot(dataSet) + np.log(trainSet[2])
            if resData is None:
                resData = predict
                resLabel = trainSet[0]
                continue
            if predict >= resData:
                resData = predict
                resLabel = trainSet[0]
        return resLabel


if __name__ == '__main__':
    a = np.array([
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    ])
    b = ['A', 'B', 'D', 'D']

    trainSets = NaiveBayes.trainDataSet(a, b)
    # print(np.array(trainSets[1][1]))
    # print([1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0] * np.array(trainSets[1][1]))
    a = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    b = [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]
    c = [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0]
    d = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
    print(NaiveBayes.classify(a, *trainSets))
    print(NaiveBayes.classify(b, *trainSets))
    print(NaiveBayes.classify(c, *trainSets))
    print(NaiveBayes.classify(d, *trainSets))

"""
import jieba
raw = '搜狗实验室数据使用许可协议'
print(list(jieba.lcut(raw, cut_all=True)))

样本编号	职业	体型	身高	女神的喜好
    1	程序员	匀称	很高	喜欢
    2	产品	瘦	    很矮	不看
    3	美术	胖	    中等	喜欢
    4	产品	胖	    中等	喜欢
    5	程序员	胖	    很矮	不看
    6	美术	瘦	    很高	不看

P(产品, 很高, 匀称,|女神喜欢) = P(产品 | 女神喜欢) * P(很高 | 女神喜欢)* P( 匀称 | 女神喜欢 ) 
1/27 = (1/3)*(1/3)*(1/3)
"""
