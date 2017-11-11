#随机生成数据
#   y_i:i点是否被覆盖--要求的优化变量
#   x_ij:i传感器是否从j点开始覆盖--要求的优化变量
#   p_ij:如果i传感器从j点开始覆盖，则其覆盖的点的集合--用表达式表示
#   v_i:i点的价值--随机生成数据
#   pos_i:i点的位置--随机生成数据
#   dis_i:传感器i所能够检测的最大距离--随机生成数据

#   常量
#   LEN:区间的总长度
#   N_sensor:传感器的数量
#   N_point:需要检测的点的个数
#   Std_Check_Num:标准的检查的点的数量
#   Std_Dis:标准的检查的距离

from pulp import *
import random
from timeit import timeit
import time
import gc
import bisect
import generateSol

LEN = 10000.0
N_sensor = 30
N_point =  300
PORTION=0.8
Std_Check_Num = 5
Std_Check_Dis = (LEN/N_sensor)/2*PORTION#前后各此长度
lpFolder="D:\PythonProject\Essay\lp_files\\"
valFolder="D:\PythonProject\Essay\\val_files\\"
time_origin=0
time_slack=0

##生成各个随机数据
v=[ random.randint(10,100) for i in range(N_point) ]
pos=[ random.uniform(0,LEN) for i in range(N_point)]
pos.sort()
dis=[ random.uniform(Std_Check_Dis/2,Std_Check_Dis*2) for i in range(N_sensor)]

leftbound=[[] for i in range(N_point) ]
rightbound=[[] for i in range(N_point)]
for i in range(N_point) :
    leftbound[i]=[ bisect.bisect_left(pos,pos[i]-dis[j]) for j in range(N_sensor) ]
    rightbound[i]=[ bisect.bisect_left(pos,pos[i]+dis[j]) for j in range(N_sensor) ]

def saveValue():
    vfile=open(valFolder+str(N_sensor)+"_"+str(N_point)+"_"+str(PORTION)+".val","w")
    vfile.write("N_sensor: "+str(N_sensor)+"\n")
    vfile.write("N_point: "+str(N_point)+"\n")
    vfile.write("PORTION: "+str(PORTION))
    vfile.write('\n')
    for position in pos:
        vfile.write(str(position)+" ")
    vfile.write('\n')
    for distance in dis:
        vfile.write(str(distance)+" ")
    vfile.write('\n')
    for val in v :
        vfile.write(str(val)+" ")

###原始线性规划代码###
def indexOfij(i,j):
    """返回ij在一维列表中的位置"""
    return i*N_point+j
def originAlg():
    prob1=LpProblem("algorithm",LpMaximize)

    ij_index = [i for i in range(N_sensor*N_point) ]
    i_index = [i for i in range(N_point) ]
    y=pulp.LpVariable.dicts("y",
                            i_index,
                            0,
                            1,
                            LpInteger
                            )
    x=pulp.LpVariable.dicts("x",
                            ij_index,
                            0,
                            1,
                            LpInteger
                            )

    prob1+=sum([ v[i]*y[i] for i in range(N_point) ]) #最大化的表达式

    for i in range(N_sensor):
        prob1+=sum([ x[indexOfij(i,j)] for j in range(N_point) ])<=1

    for k in range(N_point):#约束条件1
        prob1+=sum([ x[indexOfij(i,j)] for i in range(N_sensor)
                                        for j in range(leftbound[k][i],rightbound[k][i]
                                        )])>=y[k]

    
    lpFileName="origin_"+str(N_sensor)+"_"+str(N_point)+"_"+str(PORTION)
    prob1.writeLP(lpFolder+lpFileName+".lp")
    time_origin=time.time()
#    result=generateSol.runGLPK(lpFileName) #暂时不启用，用于提高速度
    time_origin=time.time()-time_origin
#    print(result)
    print("完成\n")
    return prob1
    

    



###松弛后的线性规划###
def slackAlg():
    prob2=LpProblem("algorithm",LpMaximize)

    ij_index = [i for i in range(N_sensor*N_point) ]
    i_index = [i for i in range(N_point) ]
    y=pulp.LpVariable.dicts("y",
                            i_index,
                            None,
                            1,
                            LpContinuous
                            )
    x=pulp.LpVariable.dicts("x",
                            ij_index,
                            0,
                            1,
                            LpContinuous
                            )

    prob2+=sum([ v[i]*y[i] for i in range(N_point) ]) #最大化的表达式

    for i in range(N_sensor):
        prob2+=sum([ x[indexOfij(i,j)] for j in range(N_point) ])<=1

    for k in range(N_point):#约束条件1
        prob2+=sum([ x[indexOfij(i,j)] for i in range(N_sensor)
                                        for j in range(leftbound[k][i],rightbound[k][i])] )>=y[k]

    lpFileName="slack_"+str(N_sensor)+"_"+str(N_point)+"_"+str(PORTION)
    prob2.writeLP(lpFolder+lpFileName+".lp")
    time_slack=time.time()
 #   result=generateSol.runGLPK(lpFileName)
    time_slack=time.time()-time_slack
 #   print(result)
    print("完成\n")
    return prob2
    




if __name__=='__main__':
    order =1
    saveValue()
    while int(order) > 0 :
        order=input("输入1运行原始函数，2运行松弛函数，3输出两者对比")
        if(int(order)==1):
            prob1=originAlg()
            del prob1
            gc.collect()
        elif(int(order)==2):
            prob2=slackAlg()
            del prob2
            gc.collect()
        elif (int(order)==3):
            pass