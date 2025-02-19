#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import struct
from bp import *
from datetime import datetime
# 手写数字识别是个比较简单的任务，数字只可能是0-9中的一个，这是个10分类问题


# 数据加载器基类
class Loader(object):
    def __init__(self, path, count):
        '''
        初始化加载器
        path: 数据文件路径
        count: 文件中的样本个数
        '''
        self.path = path
        self.count = count

    def get_file_content(self):
        '''
        读取文件内容
        '''
        f = open(self.path, 'rb')
        content = f.read()
        f.close()
        return content

    def to_int(self, byte):
        '''
        将unsigned byte字符转换为整数

        python中的struct主要是用来处理C结构数据的，读入时先转换为Python的字符串类型，
        然后再转换为Python的结构化类型，比如元组(tuple)啥的~。
        一般输入的渠道来源于文件或者网络的二进制流。


        '''
        # print(type(byte))
        return struct.unpack('B', byte)[0]


# 图像数据加载器
class ImageLoader(Loader):
    def get_picture(self, content, index):
        '''
        内部函数，从文件中获取图像
        '''
        start = index * 28 * 28 + 16
        picture = []
        # print(type(content))
        # print(content[start])
        # print(type(content[start]))
        # for i in range(28):
        #     print(content[start + i])
        for i in range(28):
            picture.append([])
            for j in range(28):
                picture[i].append(content[start + i * 28 + j])
        return picture

    def get_one_sample(self, picture):
        '''
        内部函数，将图像转化为样本的输入向量
        '''
        sample = []
        for i in range(28):
            for j in range(28):
                sample.append(picture[i][j])
        return sample

    def load(self):
        '''
        加载数据文件，获得全部样本的输入向量
        '''
        content = self.get_file_content()
        data_set = []
        for index in range(self.count):
            data_set.append(
                self.get_one_sample(
                    self.get_picture(content, index)))
        return data_set


# 标签数据加载器
class LabelLoader(Loader):
    def load(self):
        '''
        加载数据文件，获得全部样本的标签向量
        '''
        content = self.get_file_content()
        labels = []
        for index in range(self.count):
            labels.append(self.norm(content[index + 8]))
        return labels

    def norm(self, label):
        '''
        内部函数，将一个值转换为10维标签向量
        '''
        label_vec = []
        # print("label is" + str(type(label)))
        label_value = label
        for i in range(10):
            if i == label_value:
                label_vec.append(0.9)
            else:
                label_vec.append(0.1)
        return label_vec


def get_training_data_set():
    '''
    获得训练数据集
    '''
    # image_loader = ImageLoader('train-images-idx3-ubyte', 60000)
    # label_loader = LabelLoader('train-labels-idx1-ubyte', 60000)
    image_loader = ImageLoader('train-images-idx3-ubyte', 600)
    label_loader = LabelLoader('train-labels-idx1-ubyte', 600)
    return image_loader.load(), label_loader.load()


def get_test_data_set():
    '''
    获得测试数据集
    '''
    # image_loader = ImageLoader('t10k-images-idx3-ubyte', 10000)
    # label_loader = LabelLoader('t10k-labels-idx1-ubyte', 10000)
    image_loader = ImageLoader('t10k-images-idx3-ubyte', 200)
    label_loader = LabelLoader('t10k-labels-idx1-ubyte', 200)
    return image_loader.load(), label_loader.load()


# 网络的输出是一个10维向量，这个向量第n个(从0开始编号)元素的值最大，那么就是网络的识别结果。下面是代码实现：
def get_result(vec):
    max_value_index = 0
    max_value = 0
    for i in range(len(vec)):
        if vec[i] > max_value:
            max_value = vec[i]
            max_value_index = i
    return max_value_index


# 我们使用错误率来对网络进行评估，下面是代码实现：
def evaluate(network, test_data_set, test_labels):
    error = 0
    total = len(test_data_set)
    for i in range(total):
        label = get_result(test_labels[i])
        predict = get_result(network.predict(test_data_set[i]))
        if label != predict:
            error += 1
    return float(error) / float(total)


# 最后实现我们的训练策略：每训练10轮，评估一次准确率，当准确率开始下降时终止训练。下面是代码实现：
def train_and_evaluate():
    last_error_ratio = 1.0
    epoch = 0
    train_data_set, train_labels = get_training_data_set()
    test_data_set, test_labels = get_test_data_set()
    network = Network([784, 300, 10])
    while True:
        epoch += 1
        network.train(train_labels, train_data_set, 0.3, 1)
        print('%s epoch %d finished' % (datetime.now(), epoch))
        if epoch % 10 == 0:
            error_ratio = evaluate(network, test_data_set, test_labels)
            print('%s after epoch %d, error ratio is %f' % (datetime.now(), epoch, error_ratio))
            if error_ratio > last_error_ratio:
                print("end")
                break
            else:
                last_error_ratio = error_ratio


if __name__ == '__main__':
    train_and_evaluate()
