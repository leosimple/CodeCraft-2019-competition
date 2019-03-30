# -*- coding:UTF-8 -*-
"""
@File    : initialData.py
@Time    : 2019/3/10 19:26
@Author  : Blue Keroro
"""
import pandas as pd

from lib_plot.car import Cars
from lib_plot.cross import Crosses
from lib_plot.road import Roads


def initial(carTxtPath, crossTxtPath, roadTxtPath):
    """
    将txt数据转为csv,以便于使用pandas读取
    :param configPath: txt数据文件路径
    :return:
    """
    rawPathList = [carTxtPath, crossTxtPath, roadTxtPath]
    for path in rawPathList:
        CSVPath = changeTXTpathToCSV(path)
        with open(CSVPath, 'w') as f, open(path, 'r') as f1:
            for line in f1:
                line = line.replace("#", '')
                line = line.replace("(", '')
                line = line.replace(")", '')
                f.write(line)
    # 可视化的数据初始化
    Cars.initial(pd.read_csv(changeTXTpathToCSV(carTxtPath)))
    Crosses.initial(pd.read_csv(changeTXTpathToCSV(crossTxtPath)))
    Roads.initial(pd.read_csv(changeTXTpathToCSV(roadTxtPath)))


def changeTXTpathToCSV(path):
    """
    將txt文件路徑換位為相同的csv文件路徑
    :param path:
    :return:
    """
    return path[:-3] + 'csv'


if __name__ == "__main__":
    carTxtPath = "../config/car.txt"
    crossTxtPath = "../config/cross.txt"
    roadTxtPath = "../config/road.txt"
    initial(carTxtPath, crossTxtPath, roadTxtPath)
