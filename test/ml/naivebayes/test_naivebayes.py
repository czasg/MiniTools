import json
import jieba
from pprint import pprint
import numpy as np
from minitools.ml.naivebayes import NaiveBayes

if __name__ == '__main__':
    # with open('news3.json', 'r', encoding='utf-8') as f:
    #     json_data = json.loads(f.read())
    #
    # trainSets = []
    # trainSetLabels = []
    # for doc in json_data:
    #     trainSets.append(doc['标题'])
    #     trainSetLabels.append(doc['金融分类'])
    # assert len(trainSets) == len(trainSetLabels)
    # _trainSets = trainSets[:]
    # trainSets[:] = []
    # for trainSet in _trainSets:
    #     new = [i for i in set(jieba.cut(trainSet, cut_all=False)) if len(i) > 0]
    #     trainSets.append(new)
    # assert len(trainSets) == len(trainSetLabels)
    # wordsSet = NaiveBayes.generatingSet(*trainSets)
    # print('已生成词模板')
    # _trainSets = trainSets[:]
    # trainSets[:] = []
    # for trainSet in _trainSets:
    #     trainSets.append(NaiveBayes.set2vector(trainSet, wordsSet))
    # trainDataSet = NaiveBayes.trainDataSet(np.array(trainSets), trainSetLabels)  # todo 内存爆掉了==，什么鬼
    # print('已转化')
    # with open('train3.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps([trainDataSet, wordsSet], ensure_ascii=False))

    with open('train3.json', 'r', encoding='utf-8') as f:
        trainDataSet, wordsSet = json.loads(f.read())
    test1 = "办理失业险时社保局给了办理邮政的签约单"
    test2 = "生育就医登记时填错了怀孕时间有什么影响"
    test3 = "关于印发《武汉市职工基本养老保险参保补缴暂行办法》的通知(武人社规〔2017〕2号)"
    test4 = "六师农产品价格调查表"
    test5 = "师市党委召开深化团场综合配套改革工作会议：扎实深入抓好改革试点"

    ttt = [test1, test2, test3, test4]
    for t in ttt:
        words = [i for i in set(jieba.cut(t, cut_all=False)) if len(i) > 1]
        print(words)
        vector = NaiveBayes.set2vector(words, wordsSet)
        print(f"当前标题: \"{t}\"")
        print(f"预测标题金融分类: 【{NaiveBayes.classify(vector, *trainDataSet)}】\n")
