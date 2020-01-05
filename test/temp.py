from minitools.db.mongodb import get_mongodb_client

client = get_mongodb_client()

col = client['house_price']
all_city = ['武汉', '南京', '天津', '广州', '成都', '杭州', '深圳', '上海', '北京']
"""
武汉: 33353|9 {'汉阳', '江岸', '武昌', '东西湖', '硚口', '江夏', '东湖高新', '洪山', '江汉'}
南京: 9225|8 {'栖霞', '玄武', '鼓楼', '雨花台', '浦口', '秦淮', '建邺', '江宁'}
天津: 5579|11 {'西青', '河北', '和平', '南开', '东丽', '河西', '津南', '河东', '北辰', '红桥', '海河教育园区'}
广州: 4828|9 {'花都', '海珠', '越秀', '白云', '增城', '天河', '荔湾', '番禺', '黄埔'}
成都: 8032|8 {'成华', '双流', '天府新区', '锦江', '武侯', '高新', '金牛', '青羊'}
杭州: 10592|10 {'下城', '江干', '萧山', '滨江', '余杭', '下沙', '钱塘新区', '拱墅', '西湖', '上城'}
深圳: 8704|6 {'龙华区', '龙岗区', '罗湖区', '宝安区', '南山区', '福田区'}
上海: 15919|14 {'青浦', '宝山', '静安', '黄浦', '长宁', '嘉定', '新静安', '浦东', '闵行', '虹口', '徐汇', '普陀', '杨浦', '松江'}
北京: 19067|13 {'门头沟', '通州', '东城', '朝阳', '亦庄开发区', '昌平', '丰台', '海淀', '西城', '房山', '石景山', '大兴', '顺义'}


"""
# for city in all_city:
#     cc = col[city]
#     count = cc.count_documents({})
#     ss = {doc['house_place'] for doc in cc.find({}, {'_id': 0, 'house_place': 1})}
#     print(f"{city}: {count}|{len(ss)} {ss}")

a = {
    "武汉": {'汉阳', '江岸', '武昌', '东西湖', '硚口', '江夏', '东湖高新', '洪山', '江汉'},
    "南京": {'栖霞', '玄武', '鼓楼', '雨花台', '浦口', '秦淮', '建邺', '江宁'},
    "天津": {'西青', '河北', '和平', '南开', '东丽', '河西', '津南', '河东', '北辰', '红桥', '海河教育园区'},
    "广州": {'花都', '海珠', '越秀', '白云', '增城', '天河', '荔湾', '番禺', '黄埔'},
    "成都": {'成华', '双流', '天府新区', '锦江', '武侯', '高新', '金牛', '青羊'},
    "杭州": {'下城', '江干', '萧山', '滨江', '余杭', '下沙', '钱塘新区', '拱墅', '西湖', '上城'},
    "深圳": {'龙华区', '龙岗区', '罗湖区', '宝安区', '南山区', '福田区'},
    "上海": {'青浦', '宝山', '静安', '黄浦', '长宁', '嘉定', '新静安', '浦东', '闵行', '虹口', '徐汇', '普陀', '杨浦', '松江'},
    "北京": {'门头沟', '通州', '东城', '朝阳', '亦庄开发区', '昌平', '丰台', '海淀', '西城', '房山', '石景山', '大兴', '顺义'},
}
# from collections import defaultdict
# for key, values in a.items():
#     source = client['house_price'][key]
#     cc = defaultdict(list)
#     for doc in source.find({}):
#         cci = doc['house_place'].split('-')[1]
#         cc[cci].append(doc)
#     for _key, _value in cc.items():
#         client[key][_key].insert_many(_value)
#     print(f"{key}-done")

# for key, values in a.items():
#     for value in values:
#         col = client[key][value]
#         col.delete_many({'distance_from_subway': ''})
#         for doc in col.find({'distance_from_subway': ''}):
#             print(doc)

import re
int_filter = re.compile('([\d.]+)').search

lr = 0.0001
k1 = 0
k2 = 0
b = 0

# def mulComputeError(dataSetX1, dataSetX2, dataSetY, k1, k2, b, baseError=0):
#     m = len(dataSetX1)
#     for i in range(m):
#         baseError += (dataSetY[i] - (k1 * dataSetX1[i] + k2 * dataSetX2[i] + b)) ** 2
#     return baseError / (2 * float(m))
# def mulCompute(dataSetX1, dataSetX2, dataSetY, k1, k2, b, learningRate, maxIter):
#     m = float(len(dataSetX1))
#     for i in range(maxIter):
#         k1_t = k2_t = b_t = 0
#         for j in range(int(m)):
#             k1_t += (1 / m) * ((k1 * dataSetX1[j] + k2 * dataSetX2[j] + b) - dataSetY[j]) * dataSetX1[j]
#             k2_t += (1 / m) * ((k1 * dataSetX1[j] + k2 * dataSetX2[j] + b) - dataSetY[j]) * dataSetX2[j]
#             b_t += (1 / m) * ((k1 * dataSetX1[j] + k2 * dataSetX2[j] + b) - dataSetY[j])
#         k1 = k1 - learningRate * k1_t
#         k2 = k2 - learningRate * k2_t
#         b = b - learningRate * b_t
#     return k1, k2, b

# coll = client['南京']['栖霞']
# m = coll.count_documents({})

xxx1 = []
xxx2 = []
yyyy = []

# for doc in coll.find({}, {'_id':0, 'house_price':1, 'house_area':1, 'distance_from_subway':1}):
#     if doc['house_price'] < 100:
#         continue
#     # print(int_filter(doc['house_area']).group(1),int_filter(doc['distance_from_subway']).group(1))
#     _x1 = float(int_filter(doc['house_area']).group(1))
#     _x2 = float(int_filter(doc['distance_from_subway']).group(1))
#     y = doc['house_price']
#     # _y = (k1*_x1+k2*_x2+b)
#     xxx1.append(_x1)
#     xxx2.append(_x2)
#     yyyy.append(y)

# xxx1_max = max(xxx1)
# xxx1_min = min(xxx1)
# diff = xxx1_max - xxx1_min
# xxx1[:] = [(i-xxx1_min)/diff for i in xxx1]

# xxx2_max = max(xxx2)
# xxx2_min = min(xxx2)
# diff = xxx2_max - xxx2_min
# xxx2[:] = [(i-xxx2_min)/diff for i in xxx2]

# print('starting...')
# print(mulComputeError(xxx1, xxx2, yyyy, k1, k2, b))
# k1, k2, b = mulCompute(xxx1, xxx2, yyyy, k1, k2, b, lr, 3000)
# print(k1, k2, b)
# print(mulComputeError(xxx1, xxx2, yyyy, k1, k2, b))

# t1 = 10
# t2 = 600
#
# print(t1*k1+t2*k2+b)


# t1 = 20
# t2 = 900
#
# print(t1*k1+t2*k2+b)



# def computeError(dataSetX, dataSetY, k, b, baseError=0):
#     m = len(dataSetX)
#     for i in range(m):
#         baseError += (dataSetY[i] - (k * dataSetX[i] + b)) ** 2
#     return baseError / (2 * float(m))
# def compute(dataSetX, dataSetY, k, b, learningRate, maxIter):
#     m = float(len(dataSetX))
#     for i in range(maxIter):
#         k_t = b_t = 0
#         for j in range(int(m)):
#             k_t += (1 / m) * ((k * dataSetX[j] + b) - dataSetY[j]) * dataSetX[j]
#             b_t += (1 / m) * ((k * dataSetX[j] + b) - dataSetY[j])
#         k = k - learningRate * k_t
#         b = b - learningRate * b_t
#     return k, b
# print(computeError(xxx1, yyyy, k1, b))
# k1, b = compute(xxx1, yyyy, k1, b, lr, 3000)
# print(k1, b)
# print(computeError(xxx1, yyyy, k1, b))
# print(50*k1 + b)
# print(20*k1 + b)
# print(10*k1 + b)
#
# import numpy as np
# print(max(xxx2), min(xxx2), np.average(xxx2))
