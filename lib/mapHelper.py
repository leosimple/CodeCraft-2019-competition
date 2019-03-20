# -*- coding:UTF-8 -*-
"""
@File    : mapHelper.py
@Time    : 2019/3/10 19:54
@Author  : Blue Keroro
"""
import operator
from collections import defaultdict
from heapq import *
import datetime
# import matplotlib.pyplot as plt
import pandas as pd
from lib import initialData
from lib.car import Cars, Car
from lib.cross import Crosses
from lib.road import Roads
# import networkx as nx

from lib_fqy.map import Map
from lib_fqy.road import generateRoadInstances
from lib_tsy import findMinPath

plt = '' # linux環境下會報錯，暫不使用
nx = ''  # release下不使用networkx


class MapHelper(object):
    def __init__(self, dataCross, dataRoad):
        """
        :param dataCross: dataFrame cross数据
        :param dataRoad: dataFrame road数据
        """
        self.crosses = Crosses(dataCross)
        self.roads = Roads(dataRoad)
        self.hasAddMap = {}
        self.interval = 20
        self.font1 = {'family': 'Times New Roman',
                      'weight': 'normal',
                      'size': 10,
                      }
        self.graph = None

    def getRoadIdByDirection(self, crossId, direction):
        """
        根据方向获取cross的四条通路，不可通行则返回-1
        :param crossId:
        :param direction: String 方向 {up,right,down,left}
        :return:
        """
        roadId = None
        if direction == 'up':
            roadId = self.crosses.getUpRoadId(crossId)
        elif direction == 'right':
            roadId = self.crosses.getRightRoadId(crossId)
        elif direction == 'down':
            roadId = self.crosses.getDownRoadId(crossId)
        elif direction == 'left':
            roadId = self.crosses.getLeftRoadId(crossId)
        if roadId is None or roadId == -1:
            return -1
        if (not self.roads.isDuplexByRoadId(roadId)) and self.roads.getRoadFromCrossByRoadId(roadId) != crossId:
            return -1
        return roadId

    def getRoadIdByTwoCrossIds(self, crossId1, crossId2):
        """
        根据两个相邻的路口获取其间的roadId,不考虑方向
        该方法在实际运行中非常耗时，不建议使用，可考虑getRoadIdByTwoCrossIdsInCrossRelation
        :param crossId1: int
        :param crossId2: int
        :return: int
        """
        crossIdList = [crossId1, crossId2]
        roadIdList = self.roads.getRoadIdList()
        for roadId in roadIdList:
            if (self.roads.getRoadFromCrossByRoadId(roadId) in crossIdList) \
                    and (self.roads.getRoadToCrossByRoadId(roadId) in crossIdList):
                return roadId
        return None

    def getRoadIdByTwoCrossIdsInCrossRelation(self, fromCrossId, toCrossId, crossRelation):
        """
        通过fqy的crossRelation确定RoadId，效率会提高一些
        :param fromCrossId: str
        :param toCrossId: str
        :param crossRelation:
        :return: int 最后输出的答案需要是int
        """
        roadId = crossRelation[fromCrossId][toCrossId]
        return int(roadId.split('-')[0])

    def addArrow(self, crossId, roadId, x, y, newX, newY):
        """
        绘制箭头函数，可判断若不符合可行驶方向，则不绘制
        :param crossId: 为空时则直接画箭头
        :param roadId: 为空时则直接画箭头
        :param x: 箭头起始坐标
        :param y: 箭头起始坐标
        :param newX: 箭头终点坐标
        :param newY: 箭头终点坐标
        :return:
        """
        width = 0.3
        head_width = 6 * width  # 3
        head_length = 2.5 * head_width  # 1.5
        if (crossId is None or roadId is None) \
                or (self.roads.getRoadFromCrossByRoadId(roadId) is crossId or self.roads.isDuplexByRoadId(roadId)):
            plt.arrow(x, y, newX - x, newY - y, color='r', width=width, head_width=head_width, head_length=head_length,
                      length_includes_head=True)

    def showRoadIdAndLengthFunc(self, x, y, roadId, roadLength, showRoadId):
        if showRoadId is True:
            plt.text(x, y,
                     str(roadId) + '(' + str(roadLength) + ')',
                     fontdict=self.font1)

    def __dfs(self, x, y, crossId, showRoadId):
        if crossId in self.hasAddMap:
            return
        plt.scatter(x, y, color='', marker='o', edgecolors='g', s=200)
        plt.text(x, y, crossId)
        self.hasAddMap[crossId] = True
        upRoadId = self.crosses.getUpRoadId(crossId)
        rightRoadId = self.crosses.getRightRoadId(crossId)
        downRoadId = self.crosses.getDownRoadId(crossId)
        leftRoadId = self.crosses.getLeftRoadId(crossId)
        if upRoadId != -1:
            newX = x
            newY = y + self.interval
            self.addArrow(crossId, upRoadId, x, y, newX, newY)
            # print('x=', x, 'y=', y, 'oldCrossId=', crossId, 'newCrossId=',
            #       self.roads.getAnotherCrossIdByRoadId(crossId, upRoadId))
            self.showRoadIdAndLengthFunc((newX + x) / 2, (newY + y) / 2, upRoadId,
                                         self.roads.getRoadLengthByRoadId(upRoadId), showRoadId)
            self.__dfs(newX, newY, self.roads.getAnotherCrossIdByRoadId(crossId, upRoadId), showRoadId)
        if rightRoadId != -1:
            newX = x + self.interval
            newY = y
            self.addArrow(crossId, rightRoadId, x, y, newX, newY)
            self.showRoadIdAndLengthFunc((newX + x) / 2, (newY + y) / 2, rightRoadId,
                                         self.roads.getRoadLengthByRoadId(rightRoadId), showRoadId)
            # print('x=', x, 'y=', y, 'oldCrossId=', crossId, 'newCrossId=',
            #       self.roads.getAnotherCrossIdByRoadId(crossId, rightRoadId))
            self.__dfs(newX, newY, self.roads.getAnotherCrossIdByRoadId(crossId, rightRoadId), showRoadId)
        if downRoadId != -1:
            newX = x
            newY = y - self.interval
            self.addArrow(crossId, downRoadId, x, y, newX, newY)
            self.showRoadIdAndLengthFunc((newX + x) / 2, (newY + y) / 2, downRoadId,
                                         self.roads.getRoadLengthByRoadId(downRoadId), showRoadId)
            # print('x=', x, 'y=', y, 'oldCrossId=', crossId, 'newCrossId=',
            #       self.roads.getAnotherCrossIdByRoadId(crossId, downRoadId))
            self.__dfs(newX, newY, self.roads.getAnotherCrossIdByRoadId(crossId, downRoadId), showRoadId)
        if leftRoadId != -1:
            newX = x - self.interval
            newY = y
            self.addArrow(crossId, leftRoadId, x, y, newX, newY)
            self.showRoadIdAndLengthFunc((newX + x) / 2, (newY + y) / 2, leftRoadId,
                                         self.roads.getRoadLengthByRoadId(leftRoadId), showRoadId)
            # print('x=', x, 'y=', y, 'oldCrossId=', crossId, 'newCrossId=',
            #       self.roads.getAnotherCrossIdByRoadId(crossId, leftRoadId))
            self.__dfs(newX, newY, self.roads.getAnotherCrossIdByRoadId(crossId, leftRoadId), showRoadId)

    def plotMap(self, showRoadId=True):
        """
        绘制地图，由于路段长短弯直不一，无法精确绘制。
        绘制各点距离暂定为self.interval.在自带的10张地图没有出现问题。
        :param showRoadId: 决定是否显示RoadId和长度
        :return:
        """
        self.__dfs(0, 0, self.crosses.getCrossIdList()[0], showRoadId)
        plt.show()

    def initialDirGraph(self, crossRelation, roadInstances):
        """
        使用networkx初始化有向图，使用fqy的crossRelation和roadInstances结构
        :param crossRelation:
        :param roadInstances:
        :return:
        """
        G = nx.DiGraph()
        for i in crossRelation.keys():
            for j in crossRelation[i].keys():
                G.add_weighted_edges_from([(i, j, roadInstances[crossRelation[i][j]].length)])
        # nx.draw_networkx(G, with_labels=True, arrows=True)
        self.graph = G

    def getDirGraph(self):
        return self.graph

    def findShortestPathByNetworkx(self, source, target):
        """
        使用Networkx计算两点之间的最短路径
        :param source:
        :param target:
        :return:
        """
        crossesIdList = nx.shortest_path(self.getDirGraph(), source=source, target=target, weight='weight')
        roadIdList = list()
        for index in range(1, len(crossesIdList)):
            roadIdList.append(
                self.getRoadIdByTwoCrossIds(int(crossesIdList[index - 1]), int(crossesIdList[index])))
        return roadIdList

    def findShortestPathByMyDijkstra(self, fromCrossId, toCrossId, crossRelation, roadInstances):
        """
        使用自定义的Dijkstra计算两点之间的最短路径，使用fqy的crossRelation和roadInstances结构
        :param fromCrossId:
        :param toCrossId:
        :param crossRelation:
        :param roadInstances:
        :return:
        """
        ret = self.__dijkstra(fromCrossId, toCrossId, crossRelation, roadInstances)
        if ret is None:
            return None
        crossesIdList = list(ret[1])
        roadIdList = list()
        for index in range(1, len(crossesIdList)):
            roadIdList.append(
                self.getRoadIdByTwoCrossIds(int(crossesIdList[index - 1]), int(crossesIdList[index])))
        return roadIdList

    def __dijkstra(self, fromCrossId, toCrossId, crossRelation, roadInstances):
        edges = list()
        for i in crossRelation.keys():
            for j in crossRelation[i].keys():
                edges.append((i, j, roadInstances[crossRelation[i][j]].length))
        g = defaultdict(list)
        for l, r, c in edges:
            g[l].append((c, r))
        # dist records the min value of each node in heap.
        q, seen, dist = [(0, fromCrossId, ())], set(), {fromCrossId: 0}
        while q:
            (cost, v1, path) = heappop(q)
            if v1 in seen: continue
            seen.add(v1)
            path += (v1,)
            if v1 == toCrossId: return (cost, path)
            for c, v2 in g.get(v1, ()):
                if v2 in seen: continue
                # Not every edge will be calculated. The edge which can improve the value of node in heap will be useful.
                if v2 not in dist or cost + c < dist[v2]:
                    dist[v2] = cost + c
                    heappush(q, (cost + c, v2, path))
        return None

    def findShortPathByTSY(self, fromCrossId, toCrossId):
        """
        整合tsy接口寻路接口，相对短路径
        :param fromCrossId: str
        :param toCrossId: str
        :return:
        """
        return findMinPath.findMinPath(self, self.crosses, self.roads, int(fromCrossId), int(toCrossId))

    def findAllShortestPathByMyDijkstra(self, fromCrossId, crossRelation, roadInstances):
        """
        使用自定义的Dijkstra计算起点到所有点的最短路径，使用fqy的crossRelation和roadInstances结构
        :param fromCrossId: str
        :param crossRelation:
        :param roadInstances:
        :return: dict 起点到所有点的最短路径
        """
        graph_dict = {}
        for i in crossRelation.keys():
            graph_dict[i] = {}
            graph_dict[i][i] = 0
            for j in crossRelation[i].keys():
                graph_dict[i][j] = roadInstances[crossRelation[i][j]].length

        distance, pathByCrossesIdDict = self.__dijkstra_find_all_shortest_path(graph_dict, fromCrossId)
        pathByRoadIdDict = {}
        for i in pathByCrossesIdDict:
            pathByRoadIdDict[i] = {}
            for j in pathByCrossesIdDict[i]:
                if len(pathByCrossesIdDict[i][j]) == 0:
                    continue
                pathByRoadIdDict[i][j] = list()
                pathByRoadIdDict[i][j].append(
                    self.getRoadIdByTwoCrossIdsInCrossRelation(i, pathByCrossesIdDict[i][j][0], crossRelation))
                for k in range(0, len(pathByCrossesIdDict[i][j]) - 1):
                    pathByRoadIdDict[i][j].append(
                        self.getRoadIdByTwoCrossIdsInCrossRelation(pathByCrossesIdDict[i][j][k],
                                                                   pathByCrossesIdDict[i][j][k + 1],
                                                                   crossRelation))
        return pathByRoadIdDict

    def __dijkstra_find_all_shortest_path(self, graph, src):
        """
        :param graph:  dict
        :param src:  起点
        :return:
        """
        nodes = list(graph.keys())
        visited = [src]
        path = {src: {src: []}}
        nodes.remove(src)
        distance_graph = {src: 0}
        next = src
        pre = next
        while nodes:
            distance = float('inf')
            for v in visited:
                for d in nodes:
                    if d not in graph[v]:
                        continue
                    new_dist = graph[src][v] + graph[v][d]
                    if new_dist <= distance:
                        distance = new_dist
                        next = d
                        pre = v
                        graph[src][d] = new_dist
            path[src][next] = [i for i in path[src][pre]]
            path[src][next].append(next)
            distance_graph[next] = distance
            visited.append(next)
            nodes.remove(next)
        return distance_graph, path


if __name__ == "__main__":
    starttime = datetime.datetime.now()
    configPath = "../config"
    initialData.initial(configPath+"/car.txt",configPath+"/cross.txt",configPath+"/road.txt")
    dataCross = pd.read_csv(configPath + '/cross.csv')
    dataRoad = pd.read_csv(configPath + '/road.csv')
    dataCar = pd.read_csv(configPath + '/car.csv')
    mapHelperVar = MapHelper(dataCross, dataRoad)
    mapHelperVar.plotMap(showRoadId=False)
    trafficMap = Map(configPath,configPath+"/cross.txt",configPath+"/road.txt")
    roadInstances = generateRoadInstances(configPath+"/road.txt")
    mapHelperVar.initialDirGraph(trafficMap.crossRelation, roadInstances)
    print(mapHelperVar.findShortestPathByNetworkx('2', '31'))
    print(mapHelperVar.findShortestPathByMyDijkstra('2', '31', trafficMap.crossRelation,
                                                    roadInstances))
    carDict = {}
    carVar = Cars(dataCar)
    file = open(configPath + '/answer.txt', 'w')
    path = {}
    for carId in carVar.getCarIdList():
        carDict[carId] = Car(carId, carVar)
        fromCrossId = str(carDict[carId].getCarFrom())
        toCrossId = str(carDict[carId].getCarTo())
        if fromCrossId not in path:
            path[fromCrossId] = {}
        if toCrossId not in path[fromCrossId]:
            # pathTemp = mapHelperVar \
            #     .findShortestPathByMyDijkstra(fromCrossId, toCrossId, trafficMap.crossRelation, roadInstances)
            pathTemp = mapHelperVar.findShortPathByTSY(fromCrossId, toCrossId)
            path[fromCrossId][toCrossId] = pathTemp
        print(carId)
        carDict[carId].addDrivePath(path[fromCrossId][toCrossId])
        string = str((carId, carDict[carId].getCarPlanTime(), carDict[carId].getDrivePath()))
        string = string.replace('[', '')
        string = string.replace(']', '')
        file.write(string + '\n')
    file.close()
    endtime = datetime.datetime.now()
    print('运行时间:', (endtime - starttime).total_seconds())

    # roadsVar = Roads(dataRoad)
    # for i in range(1, 36):
    #     for j in range(1, 36):
    #         roadIdList1 = mapHelperVar.findShortestPathByNetworkx(str(i), str(j))
    #         roadIdList2 = mapHelperVar.findShortestPathByMyDijkstra(str(i), str(j), trafficMap.crossRelation,
    #                                                                 generateRoadInstances(configPath))
    #         print("start=", i, "end=", j, "Len1=",
    #               roadsVar.getSumRoadLength(roadIdList1), 'Len2=', roadsVar.getSumRoadLength(roadIdList2))
    #         if (not operator.eq(roadIdList1, roadIdList2)) \
    #                 and (roadsVar.getSumRoadLength(roadIdList1) != roadsVar.getSumRoadLength(roadIdList2)):
    #             print("     roadIdList1=", roadIdList1)
    #             print("     roadIdList2=", roadIdList2)
    #         else:
    #             print("equal")
