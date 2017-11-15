import bisect
import random
import os
import os.path
import xlwt
import xlrd
from xlutils.copy import copy
solFolder="D:\PythonProject\Essay\lp_files\\"
outFolder="D:\PythonProject\Essay\sol_files\\"
lpMode={'slack_origin':1,'slack_single':2,'origin_single':3,'unknown':0}#自动识别是两种lp文件都有还是单独只有一种，与xls文件排版有关
curMode=lpMode['unknown']
xlsNamePre=""
#为写入excel表格作准备
colDict={'runningTime':1,'coverPOI':2,'coverValue':3,'sensorUsage':4}#excel表格中相应的行的字典
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
nameParts=xlsNamePre.split("_")#默认文件夹中的文件都是一种规模的而且名字符合规范
xlsName=nameParts[1]+"_"+nameParts[2]+"_"+nameParts[3]+".xls"
blackStyle=xlwt.easyxf('font: color-index black, bold off')#数据储存的默认格式
oldWb=xlrd.open_workbook(outFolder+xlsName, formatting_info=True)#打开上一步中建立的xls文件
newWb=copy(oldWb)
newWs=newWb.get_sheet(0)




def readOrigin(file_object,N_sensor,N_points,order):
    """读取整数规划sol文件并统计数据"""
    coverYNum=0
    coverValue=0
    usedXNum=0
    x=[ [ 0 for j in range(N_points) ] for i in range(N_sensor)]##每个传感器给予的分配量
    y=[ 0 for i in range(N_points) ]#每一个PIO是否被覆盖
    for line in file_object:
        parts=line.strip().split()
        if len(parts)>=2 and parts[1][0]=='x':
            xNameParts=parts[1].strip().split("_")
            xIndex=int(xNameParts[1])
            xValue=int(parts[3])
            x[int(xIndex/N_points)][xIndex%N_points]=xValue
        elif len(parts)>=2 and parts[1][0]=='y':
            yNameParts=parts[1].strip().split("_")
            yIndex=int(yNameParts[1])
            yValue=int(parts[3])
            y[yIndex]=yValue
        elif len(parts)>=4 and parts[0][0]=='O' and parts[1][0]=='O':
            coverValue=float(parts[3])
    for i in range(N_points):
        if y[i]==1:
            coverYNum+=1
    for i in range(N_sensor):
        for j in range(N_points):
            if x[i][j]==1:
                usedXNum+=1
                break

    newWs.write(order,colDict['coverPOI'],coverYNum,blackStyle)
    newWs.write(order,colDict['coverValue'],coverValue,blackStyle)
    newWs.write(order,colDict['sensorUsage'],usedXNum,blackStyle)



def readSlack(file_object,vfile_name,N_sensor,N_points,order):
    """读取改进算法val文件并且进行改进算法的最后一步"""
    valFileHeader="D:\PythonProject\Essay\\val_files\\"
    valFIle = open(valFileHeader+vfile_name+".val","r")
    lines = [line for line in valFIle.readlines()]
    v=[]
    pos=[]
    dis=[]
    leftbound=[[] for i in range(N_points) ]
    rightbound=[[] for i in range(N_points)]
    x=[ [ 0 for j in range(N_points) ] for i in range(N_sensor)]##每个传感器给予的分配量
    y=[ False for i in range(N_points) ]#每一个PIO是否被覆盖
    ###val_files中顺序是pos到dis到val数组
    parts=lines[3].strip().split()
    for position in parts:
        pos.append(float(position))
    parts=lines[4].strip().split()
    for distance in parts:
        dis.append(float(distance))
    parts=lines[5].strip().split()
    for value in parts:
        v.append(int(value))
    ##算法需要重新分配,leftbound_ij表示以j传感器以i为起点的覆盖范围的左边界
    for i in range(N_points) :
        leftbound[i]=[ bisect.bisect_left(pos,pos[i]-dis[j]) for j in range(N_sensor) ]
        rightbound[i]=[ bisect.bisect_left(pos,pos[i]+dis[j]) for j in range(N_sensor) ]

    coverValue=0
    coverYNum=0
    usedXNum=0
    ##读入基本信息，准备统计
    for line in file_object:
        parts=line.strip().split()
        if len(parts)>=2 and parts[1][0]=='x':
            xNameParts=parts[1].strip().split("_")
            xIndex=int(xNameParts[1])
            xValue=float(parts[3])
            x[int(xIndex/N_points)][xIndex%N_points]=xValue
        elif len(parts)>=2 and parts[1][0]=='y':
            pass
    
    ##准备按照概率处理连续的数据
    sensorSum=[]
#    testFile=open("testFile.tes",'w')
    ##统计xi以便于使用轮盘算法按照概率分配
    for i in range(N_sensor):
        sum=0
        for j in range(N_points):
            sum+=x[i][j]
        sensorSum.append(sum)
    ##开始轮盘算法
    for i in range(N_sensor):
        if sensorSum[i]>0 :
            usedXNum+=1
            chance=random.uniform(0,1)
            chance_now=0
            for j in range(N_points):
                chance_now+=x[i][j]
                if chance_now>=chance:
                    ###此时已经找到所取出发点，更新yi
                    for k in range(leftbound[j][i],rightbound[j][i]):
                        y[k]=True
                    break
    for i in range(N_points):
        if y[i]==True:
            coverYNum+=1
            coverValue+=v[i]
    newWs.write(order+pairNum,colDict['coverPOI'],coverYNum,blackStyle)
    newWs.write(order+pairNum,colDict['coverValue'],coverValue,blackStyle)
    newWs.write(order+pairNum,colDict['sensorUsage'],usedXNum,blackStyle)

def compare():
    """填入表格中待填写的对比信息"""
    oldWb=xlrd.open_workbook(outFolder+xlsName, formatting_info=True)#打开上一步中建立的xls文件
    oldWs=oldWb.sheet_by_index(0)
    tmp=[ [] for i in range(5)]#不能同时读取和写入所以缓存
    for col in colDict:
        for i in range(pairNum):
            order=i+1
            cmpResult=oldWs.cell(order+pairNum,colDict[col]).value/oldWs.cell(order,colDict[col]).value#获取两种算法的效率比值
            tmp[colDict[col]].append(cmpResult)
    newWb=copy(oldWb)
    newWs=newWb.get_sheet(0)
    for col in colDict:
        for i in range(pairNum):
            order=i+1
            newWs.write(order+2*pairNum,colDict[col],tmp[colDict[col]][i],blackStyle)
    newWb.save(outFolder+xlsName)

if __name__ == "__main__":
    """用于读取.sol文件，给出分析数据"""
    ###表示用于储存sol文件的文件夹,可以改动
    fileHeader = "D:\PythonProject\Essay\sol_files\\"
    fileName = "origin"  
    os.chdir(fileHeader)
    files=os.listdir()
    for f in files:
        if os.path.isfile(f):
            fileType= os.path.splitext(f)
            print(fileType)
            fileName=fileType[0]
            if fileType[1]==".sol":
                nameParts=fileName.split("_")
                vfileName=nameParts[1]+"_"+nameParts[2]+"_"+nameParts[3]+"_"+nameParts[4]
                solFile = open(fileHeader+fileName+".sol","r")
                N_sensor=int(nameParts[1])
                N_points=int(nameParts[2])
                order=int(nameParts[4])
                if(nameParts[0]=="slack"):
                    readSlack(solFile,vfileName,N_sensor,N_points,order)
                elif nameParts[0]=="origin":
                    readOrigin(solFile,N_sensor,N_points,order)
                
    newWb.save(outFolder+xlsName)
#    compare()#对比信息不再填入