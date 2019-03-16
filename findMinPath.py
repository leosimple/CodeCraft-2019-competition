import pandas as pd
from lib import initialData
from lib.cross import Crosses
from lib import mapHelper
from lib.road import Roads


direct = ["up", "right", "down", "left"]
ret = []

def findMinPath(map, crosses, roads, crossId1, crossId2):
    """
    根据地图获取地图上每个路口到其余路口的最短路径
    两次遍历所有点，求各点之间最短路径
    :param map:
    :return:
    """
    crossList = []
    flag = [0] * len(crosses.getCrossIdList())
    if crossId1 == crossId2:
        return
    else:
        helper(crossId1, crossId2, map, roads, crossList, flag)
        print(str(crossId1) + "to" + str(crossId2) + ":")
        # print(ret)
        ret.reverse()
        # print(ret)
        ans = [ret[0]]
        curCross = roads.getAnotherCrossIdByRoadId(crossId2, ret[0])
        i = 1
        ret.pop(0)
        ans1 = []
        flag = [False]
        dfs(curCross, ret, ans, ans1,roads, crosses, crossId1,flag)
        print("zhieli")
        print(ans)
        ans.reverse()
        print(ans)


def dfs(curCross, ret, ans, ans1,roads, crosses, crossId1,flag):
    if curCross == crossId1:
        print("zheli")
        print(ans)
        flag[0] = True
        return
    roundRoad = []
    if crosses.getUpRoadId(curCross) in ret:
        roundRoad.append(crosses.getUpRoadId(curCross))
        ret.remove(crosses.getUpRoadId(curCross))
    if crosses.getDownRoadId(curCross) in ret:
        roundRoad.append(crosses.getDownRoadId(curCross))
        ret.remove(crosses.getDownRoadId(curCross))
    if crosses.getLeftRoadId(curCross) in ret:
        roundRoad.append(crosses.getLeftRoadId(curCross))
        ret.remove(crosses.getLeftRoadId(curCross))
    if crosses.getRightRoadId(curCross) in ret:
        roundRoad.append(crosses.getRightRoadId(curCross))
        ret.remove(crosses.getRightRoadId(curCross))
    for road in roundRoad:
        ans.append(road)
        newCross = roads.getAnotherCrossIdByRoadId(curCross, road)
        dfs(newCross,ret,ans,ans1,roads,crosses,crossId1,flag)
        if flag[0] == True:
            break
        ans.remove(road)


def helper(crossid1, crossid2, map, roads, crosslist, flag):
    """
    回溯算法的辅助函数, 从crossid1出发至crossId2 找一条路
    :param crossId1,出发点
           crossId2,终点
           map, maphelper对象
           roads，roads对象
           crosslist, 存储当前路口集合
           flag， 标记是否访问
    :return:
    """
    crosslist.append(crossid1)
    flag[crossid1] = 1
    if crossid2 in crosslist:
        return
    nextCross = 0
    nextRoad = 0
    min = 1000
    for cross in crosslist:
        for dir in direct:
            newRoadId = map.getRoadIdByDirection(cross, dir)
            if newRoadId == -1:
                continue
            newCross = roads.getAnotherCrossIdByRoadId(cross, newRoadId)
            if newCross == crossid2:
                ret.append(newRoadId)
                return
            elif flag[newCross] == 1:
                continue
            else :
                if roads.getRoadLengthByRoadId(newRoadId) < min:
                    min = roads.getRoadLengthByRoadId(newRoadId)
                    nextCross = newCross
                    nextRoad = newRoadId
            # print("newRoadId in " + dir + " is " + str(newRoadId))
    ret.append(nextRoad)
    helper(nextCross,crossid2,map,roads,crosslist,flag)
    return


if __name__ == '__main__':
    configPath = "CodeCraft-2019/config_10"
    initialData.initial(configPath)
    dataCross = pd.read_csv(configPath + '/cross.csv')
    dataRoad = pd.read_csv(configPath + '/road.csv')
    mapHelperVar = mapHelper.MapHelper(dataCross, dataRoad)
    crossesVar = Crosses(dataCross)
    roadsVar = Roads(dataRoad)
    findMinPath(mapHelperVar, crossesVar, roadsVar, 1, 34)