from __init__ import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from bisect import bisect_left
import seaborn as sns
from pylab import mpl
import os
mpl.rcParams['font.sans-serif']=['SimHei']
sns.set()

#------------------------------------------------------------------------------------------2022-9-8
class gradeEvaluation():
    def __init__(self, method='dominate', direction='min', levels=None, percent=None):
        """
        note：...
        函数功能：初始化
        输入参数：x: 二维数据，二维列表或二维数组
                 method:等级评价方法，dominate/front
                 direction：最优方向，min/max, 默认越小越优---多个指标需要设置相同的优化方向
                 levels：划分等级数量
                 percent：各等级划分比例               
        """
        self.levels=levels
        self.method=method
        self.direction=direction
        self.grade=[]
        # self.level和self.percent同时存在或同时不存在
        if percent!=None:
            self.percent=[i/sum(percent) for i in percent]
            self.levels=len(percent)
        else:
            if self.levels!=None:
                self.percent=[1/levels for i in range(levels)]   # 按等级分四个比例
    def _paretoFront(self, x,):
        """
        note：内部函数，不建议直接调用
        函数功能：判断各样本是否为pareto第一前沿
        函数描述：输入二维数据及最优方向，判断各样本是否为pareto第一前沿
        输入参数：x: 二维数据，二维列表或二维数组
        输出参数：一维1/0数组，表示各样本是否属于pareto第一前沿
        """
        x=np.array(x)
        m, n=x.shape
        result=[]
        for i, xi in enumerate(x):
            if self.direction=='min':
                judge1=(x<=xi).sum(axis=1)
                judge2=(x==xi).sum(axis=1)
            else:
                judge1=(x>=xi).sum(axis=1)
                judge2=(x==xi).sum(axis=1)
            judge1=(judge1==n).sum()
            judge2=(judge2==n).sum()
            paretoFront_xi=judge1-judge2      # 回旋踢
            result.append(int(paretoFront_xi==0))
        return np.array(result)
    def paretoFront(self, x,):
        """
        note：...
        函数功能：计算各样本所属前沿
        函数描述：输入二维数据及最优方向，计算各样本所属前沿
        输入参数：x: 二维数据，二维列表或二维数组
        输出参数：整形1维数组，表示各样本所属前沿
        """
        x=np.array(x)
        m, n= x.shape
        x=np.c_[x, [i for i in range(m)]]   # tracker is ready
        tracker, pf=[], []
        i=0
        while True:
            i+=1
            _=self._paretoFront(x[:, :-1],)    # （当前）是否为第一前沿
            tracker+=(x[_==1])[:,-1].tolist()
            pf+=([i for j in range(sum(_))])
            x=x[_==0]    # （当前）非第一前沿的样本
            if x.shape[0]==0 or i==m:
                break
        res=pd.DataFrame([tracker, pf]).T
        res.sort_values(0, inplace=True)
        return res.iloc[:,1].values 
    def _paretoLevel_by_front(self, xfront,):
        """
        note:内部函数，不建议直接调用
        函数功能：计算pareto等级
        函数描述：基于原始样本x和其所属前沿，将数据分为levels个等级，给出各个样本所属等级
        输入参数：x: 二维数据，二维列表或二维数组
                 xfront：各样本前沿
                 percent：等级划分比例
        输出参数：一维数组，[按顺序的各个样本的所属等级, 各等级划分的pareto前沿阈值]
        """
        pfx, pfxn=[], []
        unique=np.unique(xfront)
        for i in unique:
            pfxn.append(len(xfront[xfront==i]))    # 从小到大排序的每个前沿包含样本数量
        cumsum=np.cumsum(pfxn)/len(xfront)   # 各个前沿样本累加数量比例
        ids=[]
        percent=np.cumsum(self.percent)    # 指定的各等级样本数量比例
        for i, percent_i in enumerate(percent):
            mid=np.abs((cumsum-percent_i))
            idi=np.argmin(mid)
            ids.append(unique[idi])
            cumsum=cumsum[idi+1:]
            unique=unique[idi+1:]
            if len(cumsum)==0:
                break
        return np.array([bisect_left(ids, i)+1 for i in xfront]), [int(i) for i in ids]
    def paretoDonimated(self, x,):
        """
        函数功能：计算支配各个样本的所有样本数量//样本支配度
        函数描述：输入二维数据及最优方向，计算支配各个样本的样本数量
        输入参数：x: 二维数据，二维列表或二维数组
        输出参数：pl：一维数组，按顺序的，各个样本被支配的数量(被支配度)
        """
        x=np.array(x)
        m, n=x.shape
        pl=[]
        for i, xi in enumerate(x):
            if self.direction=='min':
                judge1=(x<=xi).sum(axis=1)
                judge2=(x==xi).sum(axis=1)
            else:
                judge1=(x>=xi).sum(axis=1)
                judge2=(x==xi).sum(axis=1)
            judge1=(judge1==n).sum()
            judge2=(judge2==n).sum()
            donimated_xi=judge1-judge2      # 回旋踢
            pl.append(donimated_xi)
        return np.array(pl)
    def _paretoLevel_by_dominate(self, xdominated,):
        """
        note:内部函数，不建议直接调用
        函数功能：计算pareto等级
        函数描述：基于原始样本x和其被支配数量pl，将数据分为levels个等级，给出各个样本所属等级
        输入参数：x:二维数据，二维列表或二维数组
                 xdominated:各个样本的被支配度
        输出参数：一维数组，[按顺序的各个样本的所属等级, 各等级划分的被支配度阈值]
        """
        pfx, pfxn=[], []
        unique=np.unique(xdominated)
        for i in unique:
            pfxn.append(len(xdominated[xdominated==i]))    # 从小到大排序的每个支配度的数量
        cumsum=np.cumsum(pfxn)/len(xdominated)   # 各个支配度的累加比例
        ids=[]
        percent=np.cumsum(self.percent)
        for i, percent_i in enumerate(percent):
            mid=np.abs((cumsum-percent_i))
            idi=np.argmin(mid)
            ids.append(unique[idi])
            cumsum=cumsum[idi+1:]
            unique=unique[idi+1:]
            if len(cumsum)==0:
                break
        return np.array([bisect_left(ids, i)+1 for i in xdominated]), [int(i) for i in ids]
    def fit(self, x,):
        """
        note:训练函数
        函数功能：训练pareto等级评价器，获得当前样本pareto前沿/被支配度，等级，等级区间
        函数描述：基于原始样本x，获得当前样本pareto前沿/被支配度，等级，等级区间
        输入参数：x:二维数据，二维列表或二维数组
        输出参数：样本pareto前沿/被支配度，等级，等级划分阈值
        """
        x=np.array(x)
        self.x0=x
        m,n=np.array(x).shape
        self.dim=n
        if self.method=='front':
            xfront=self.paretoFront(x,)
            self.fd=xfront    # pareto前沿
            if self.levels!=None:
                if self.levels>int(max(self.fd)):    # 预设levels数量大于pareto前沿数量是不允许的
                    self.levels=int(max(self.fd))
                grade, ids=self._paretoLevel_by_front(xfront,)
                self.grade=grade
                self.ids=ids
        else:
            xdominated=self.paretoDonimated(x,)
            self.fd=xdominated # pareto支配度
            if self.levels!=None:
                if self.levels>int(max(self.fd)):    # 预设levels数量大于pareto前沿数量是不允许的
                    self.levels=int(max(self.fd))                
                grade, ids=self._paretoLevel_by_dominate(xdominated,)
                self.grade=grade
                self.ids=ids
    def _evaluation(self, x):
        """
        note:内部函数，不建议直接调用
        函数功能：评估函数
        函数描述：获得当前样本pareto前沿/被支配度，等级
        输入参数：x:单元素二维数据，形式为[[1,2]]
        输出参数：获得当前样本pareto---fd(前沿/被支配度)，等级
        """
        x=np.array(x)
        if self.method=='front':   
            x=np.r_[x, self.x0,]
            i=0
            while True:
                i+=1
                _=self._paretoFront(x,)
                if _[0]==1:
                    break
                x=x[_==0]
                if x.shape[0]==0:
                    break
            fd=i
        else:
            n=len(x)
            if self.direction=='min':
                judge=(self.x0<x).sum(axis=1)
            else:
                judge=(self.x0>x).sum(axis=1)
            judge=(judge==n).sum()
            fd=judge
        grade=None
        if self.levels!=None:
            grade=bisect_left(self.ids, fd)+1
            if grade>self.levels:
                grade=self.levels
        return fd, grade
    def evaluation(self, x):
        """
        note:
        函数功能：评估函数
        函数描述：获得当前样本pareto前沿/被支配度，等级
        输入参数：x:任意元素二维数据，形式为[[1,2]] 或[[1,2], [0, 3]...]
        输出参数：获得当前样本pareto前沿/被支配度，等级
        """
        x=np.array(x)
        if x.ndim<2:
            raise Exception('x must a 2D data.')
        fd, grade=[], []
        for xi in x:
            fd_i, grade_i=self._evaluation([xi])
            fd.append(fd_i)
            grade.append(grade_i)
        return fd, grade
    def show(self, size=(10, 10), dpi=120):
        """
        note:
        函数功能：可视化
        函数描述：等级评价的二维/三维可视化
        输入参数：size, 画布尺寸, 
                 dpi, 分辨率
        输出参数：二维三维可视化图像
        """      
        font = {'family' : 'Times New Roman','weight' : 'normal','size' : 20}
        fig=plt.figure(figsize=size, dpi=dpi)
        if self.dim==2:
            if self.levels!=None:
                for i in range(1, self.levels+1):
                    plt.scatter(self.x0[self.grade==i][:,0], self.x0[self.grade==i][:,1], label='等级%s'%(i),)
                plt.legend(framealpha=0, loc='best', fontsize=15)
            else:
                plt.scatter(self.x0[:,0], self.x0[:,1], c=self.fd, cmap='jet')
            plt.xlabel('x of samples',font)
            plt.ylabel('y of samples',font)
        elif self.dim==3:
            ax = plt.axes(projection='3d')
            if self.levels!=None:
                for i in range(1, self.levels+1):
                    ax.scatter(self.x0[self.grade==i][:,0], self.x0[self.grade==i][:,1], self.x0[self.grade==i][:,2], label='等级%s'%(i),)
                plt.legend(framealpha=0, loc='best', fontsize=15)
            else:
                ax.scatter(self.x0[:,0], self.x0[:,1], self.x0[:,2], c=self.fd, cmap='jet')
            ax.set_xlabel('X',font)
            ax.set_ylabel('Y',font)
            ax.set_zlabel('Z',font)
        else:
            raise Exception('x0 should be a 2D or 3D data.')