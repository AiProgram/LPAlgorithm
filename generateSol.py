import os
import re
import xlwt
import xlrd
from xlutils.copy import copy
solFolder="D:\PythonProject\Essay\lp_files\\"
outFolder="D:\PythonProject\Essay\sol_files\\"


#为写入excel表格作准备
colDict={'runningTime':1,'coverPOI':2,'coverValue':3,'sensorUsage':4}#excel表格中相应的行的字典
countFile=0
os.chdir(solFolder)
files=os.listdir()
for f in files:
    if os.path.isfile(f) and os.path.splitext(f)[1]==".lp":
        countFile+=1
blackStyle=xlwt.easyxf('font: color-index black, bold off')
redStyle=xlwt.easyxf('font: color-index red, bold off')
greenStyle=xlwt.easyxf('font: color-index green, bold off')
blueStyle=xlwt.easyxf('font: color-index blue, bold off')

wb=xlwt.Workbook();  
ws=wb.add_sheet("algorithm");  
#为excel文件添加坐标轴 
ws.write(0,1,"runningTime",blackStyle)
ws.write(0,2,"coverPOI",blackStyle)
ws.write(0,3,"coverValue",blackStyle)
ws.write(0,4,"sensorUsage",blackStyle)
pairNum=int(countFile/2)
for i in range(pairNum):
    order=i+1
    ws.write(order,0,"origin_"+str(order),blueStyle)
    ws.write(order+pairNum,0,"slack_"+str(order),greenStyle)
    ws.write(order+2*pairNum,0,"compare_"+str(order),redStyle)
nameParts=files[0].split("_")#默认文件夹中的文件都是一种规模的而且名字符合规范
xlsName=nameParts[1]+"_"+nameParts[2]+"_"+nameParts[3]+".xls"

def runGLPK(fileName):
    os.chdir("E:\ProgramFiles\glpk-4.63\w64\\")#这是GLPK的文件路径
#    result=os.system("glpsol --cpxlp "+solFolder+fileName+".lp -o "+outFolder+fileName+".sol ")
    r=os.popen("glpsol --cpxlp "+solFolder+fileName+".lp -o "+outFolder+fileName+".sol ")
    result=r.read()
    r.close()
    return result

def testGLPK():
    """用于运行所有的lp文件并且记录下所需的统计数据"""
    infoFile=open("running_info.txt","w")#清空旧的统计信息
    infoFile.close()

    count=0
    solFolder="D:\PythonProject\Essay\lp_files\\"
    os.chdir(solFolder)
    files=os.listdir()
    for file in files:
        print(str(file))
        nameParts=file.strip().split(".")
        fileType=nameParts[len(nameParts)-1]
        if fileType=="lp":
            rawName=file.replace(".lp","")
            result=runGLPK(rawName)
            count+=1
            writeInfo(file,result)
            print("已经运行了"+str(count)+"个lp文件")
def writeInfo(file,result):
    """用于记录下所耗费时间等信息"""
    os.chdir("D:\PythonProject\Essay\lp_files\\")
    time=0
#    print(str(result))
    parts=result.split()
    for i in range(len(parts)):
        if parts[i]=="secs" :
            time=float(parts[i-1])
            break
    #尝试记录运行时间信息在excel表格中
    nameParts=file.split("_")
    order= int(nameParts[4].split(".")[0])
    if nameParts[0]=="origin":
        ws.write(order,colDict['runningTime'],time,blackStyle)
    elif nameParts[0]=="slack":
        ws.write(order+pairNum,colDict['runningTime'],time,blackStyle)

if __name__ == "__main__":
    testGLPK()
    wb.save(outFolder+xlsName)