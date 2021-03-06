import bisect
import random
import os
import os.path
import xlwt
import xlrd
import time
from xlutils.copy import copy
solFolder="D:\PythonProject\Essay\lp_files\\"
outFolder="D:\PythonProject\Essay\sol_files\\"
valFolder="D:\PythonProject\Essay\\val_files\\"#储存算法所需数据的val文件的文件夹
colDict={'runningTime':1,'coverPOI':2,'coverValue':3,'sensorUsage':4}#excel表格中相应的行的字典
lpMode={'slack_origin':1,'slack_single':2,'origin_single':3,'unknown':0}#自动识别是两种lp文件都有还是单独只有一种，与xls文件排版有关
curMode=lpMode['unknown']
#val文件中数据的顺序是pos,dis,v
N_sensor= 0
N_point= 0
PORTION= 0.0
pos=[]
dis=[]
v=[]
sensorLeft=[]#运行过程中剩余未使用传感器
sLeftNum=0
pointLeft=[]#运行过程中剩余未覆盖POI
pLeftNum=0
curMaxV=0#本轮中每一个传感器所能覆盖的最大价值
curMaxS=0#本轮中覆盖最大价值的传感器
curMaxJ=0#本轮最大单位覆盖价值的摆放点
leftBound=[]
rightBound=[]
#储存结果数据的变量
coverPoint=0
coverValue=0
totalValue=0
timeUsed=0
sensorUsage=0

countFile=0
os.chdir(solFolder)
files=os.listdir()
for f in files:
    if os.path.isfile(f) and os.path.splitext(f)[1]==".lp":
        xlsNamePre=os.path.splitext(f)[0]
        countFile+=1
        if os.path.splitext(f)[0].split("_")[0]=="slack":#当发现线性规划文件时改变lp模式
            if curMode==lpMode['unknown']:
                curMode=lpMode['slack_single']
            elif curMode==lpMode['origin_single']:
                curMode=lpMode['slack_origin']
        if os.path.splitext(f)[0].split("_")[0]=='origin':#当发现整数规划文件时改变lp模式
            if curMode==lpMode['unknown']:
                curMode=lpMode['origin_single']
            elif curMode==lpMode['slack_origin']:
                curMode=lpMode['slack_origin']
if curMode==lpMode['slack_origin']:
    pairNum=int(countFile/2)
else:
    pairNum=int(countFile)

def disCmp(x):
    """按照dis的大小顺排序"""
    return dis[x]
def getMaxCover(i):
    """找到使本轮i传感器最佳的j，并返回最大单位覆盖价值以及j"""
    global rightBound,leftBound,N_point,maxV,maxJ
    maxV=0
    maxJ=0
    total=0
    trueCover=0
    for j in range(N_point):#找到令i传感器单位巡逻范围覆盖价值最大的j点
        total=0#统计i传感器放在j点时的有效覆盖价值
        for k in range(leftBound[j][i],rightBound[j][i]):
            if pointLeft[k]==True:
                total+=v[k]
        if (total/dis[i])>maxV:
            maxV=total/dis[i]
            maxJ=j
    an=[]
    an.append(maxV)
    an.append(maxJ)
    return an
def coverSensor(i,j):
    global sensorLeft,pointLeft,sLeftNum,leftBound,rightBound,pLeftNum
    """将第i个传感器放置在第j个点处"""
    sLeftNum=sLeftNum-1
    for k in range(leftBound[j][i],rightBound[j][i]):
        if(pointLeft[k]==True):
            pLeftNum=pLeftNum-1
        pointLeft[k]=False
def solve():
    """执行贪婪算法"""
    global sLeftNum,pLeftNum,N_point,N_sensor,curMaxJ,curMaxS,curMaxV
    i=0
    while(sLeftNum>0 and pLeftNum>0):
        ans=getMaxCover(sensorLeft[i])
        curMaxJ=ans[1]
        coverSensor(sensorLeft[i],curMaxJ)
        i+=1

def readValFile(valFile):
    """读取保存在val文件中的数据用来执行贪婪算法"""
    global N_point,N_sensor,sensorLeft,pLeftNum,sLeftNum,leftBound,rightBound
    pos.clear()
    dis.clear()
    v.clear()
    sensorLeft.clear()
    pointLeft.clear()
    vfile=open(valFile)
    count=1
    for line in vfile:
        parts=line.split()
        if(count==1):#读取N_sensor
            N_sensor=int(parts[1])
        elif (count==2):#读取N_point
            N_point=int(parts[1])
        elif (count==4):#读取pos数组
            for n in parts:
                pos.append(float(n))
        elif (count==5):#读取dis数组
            for n in parts:
                dis.append(float(n))
        elif (count==6):#读取v数组
            for n in parts:
                v.append(int(n))
            break
        count+=1

    for i in range(N_point):
        pointLeft.append(True)
    pLeftNum=N_point
    for i in range(N_sensor):
        sensorLeft.append(i)
    sensorLeft=sorted(sensorLeft,key=disCmp,reverse=True)#自定义按照dis的顺序排序
    sLeftNum=N_sensor
    curMaxV=0
    leftBound.clear()
    rightBound.clear()
    for i in range(N_point):
        leftBound.append([])
        rightBound.append([])
    for i in range(N_point) :
        leftBound[i]=[ bisect.bisect_left(pos,pos[i]-dis[j]) for j in range(N_sensor) ]
        rightBound[i]=[ bisect.bisect_left(pos,pos[i]+dis[j]) for j in range(N_sensor) ]
    solve()
    getStat()

def getStat():
    """最后的统计数据"""
    global sensorLeft,pointLeft,sensorUsage,coverPoint,coverValue,totalValue
    sensorUsage=0
    coverPoint=0
    coverValue=0
    totalValue=0
    sensorUsage=N_sensor-sLeftNum
    for j in range(N_point):
        totalValue+=v[j]
        if pointLeft[j]==False:
            coverPoint+=1
            coverValue+=v[j]
def saveToXLS(f,t):
    xlsPrefix=os.path.splitext(f)[0]
    xlsNameParts=xlsPrefix.split("_")
    xlsFileName=xlsNameParts[0]+"_"+xlsNameParts[1]+"_"+xlsNameParts[2]+".xls"
    blackStyle=xlwt.easyxf('font: color-index black, bold off')#数据储存的默认格式
    oldWb=xlrd.open_workbook(outFolder+xlsFileName, formatting_info=True)#打开上一步中建立的xls文件
    newWb=copy(oldWb)
    newWs=newWb.get_sheet(0)
    order=int(xlsPrefix.split("_")[3])
    newWs.write(order+pairNum*2,colDict['runningTime'],t)
    newWs.write(order+pairNum*2,colDict['coverPOI'],coverPoint,blackStyle)
    newWs.write(order+pairNum*2,colDict['coverValue'],coverValue,blackStyle)
    newWs.write(order+pairNum*2,colDict['sensorUsage'],sensorUsage,blackStyle)
    newWb.save(outFolder+xlsFileName)

if __name__=="__main__":
    os.chdir(valFolder)
    files=os.listdir()
    for f in files:
        if os.path.isfile(f):
            nameParts=os.path.splitext(f)
            if nameParts[1]==".val":
                tStart=time.time()
                readValFile(valFolder+f)
                tStop=time.time()
#                print("-----------------------------------------------")
                print(f)
#                print("覆盖价值/总价值\n"+str(coverValue)+"/"+str(totalValue))
#                print("覆盖数/POI总数\n"+str(coverPoint)+"/"+str(N_point))
#                print("使用数/传感器总数\n"+str(sensorUsage)+"/"+str(N_sensor))
#                print("运行时间\n"+str(tStop-tStart)+"s")
#                print("-----------------------------------------------")
                saveToXLS(f,tStop-tStart)