#!/usr/bin/env python
# coding: utf-8
# 趋势分析工具Trend Analysis Tools 
# 开发人：蔡权周
# 第一部分：导入基本模块及初始化 ########################################################################
# 导入一些基本模块
import warnings
import traceback
import ast
import re
import xlrd
import xlwt
import openpyxl
import pandas as pd
import numpy as np
import math
import tkinter as Tk
from tkinter import ttk
from tkinter import *
import tkinter.font as tkFont
from tkinter import filedialog, dialog, PhotoImage
from tkinter.messagebox import showinfo
from tkinter.scrolledtext import ScrolledText
import collections
from collections import Counter
import datetime
from datetime import datetime, timedelta
from tkinter import END
import xlsxwriter
import os
import time
import threading
import pip
import matplotlib as plt
import requests
import random

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.ticker import PercentFormatter
from tkinter import ttk,Menu,Frame,Canvas,StringVar,LEFT,RIGHT,TOP,BOTTOM,BOTH,Y,X,YES,NO,DISABLED,END,Button,LabelFrame,GROOVE, Toplevel,Label,Entry,Scrollbar,Text, filedialog, dialog, PhotoImage
pd.options.display.float_format="{:,.12f}".format
# 定义一些全局变量
global TT_ori  # 源文件
global TT_biaozhun  # 趋势分析标准
global TT_modex #趋势分析模式
global TT_ori_backup
global version_now
global usergroup
global setting_cfg
global csdir
TT_biaozhun = {}#标准初始化  
TT_ori = ""  # 源文件初始化
TT_modex=0  # 趋势分析模式初始化
TT_ori_backup=""
version_now="0.0.20" 
usergroup="用户组=0"
setting_cfg=""

csdir =str (os .path .abspath (__file__ )).replace (str (__file__ ),"")#line:60
if csdir=="":
    csdir =str (os .path .dirname (__file__ ))#
    csdir =csdir +csdir.split ("treadtools")[0 ][-1 ]#


# 第二部分：函数模块 ##################################################################

    
#序列号与用户组验证模块。


def extract_zip_file(zip_file_path, extract_path):
    #import shutil
    import zipfile
    if extract_path=="":
        return 0
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():

            file_info.filename = file_info.filename.encode('cp437').decode('gbk')
            zip_ref.extract(file_info, extract_path)
            #source_path = os.path.join(extract_path, file_info.filename)
            #print(file_info)
            #target_path = os.path.join(extract_path, file_info.filename.encode('gbk').decode('utf-8'))
            #shutil.move(source_path, extract_path)

def get_directory_path(directory_path):
    # 创建一个 Tkinter 窗口
    global csdir
    # 检查目录是否存在 A.txt 文件
    if not (os.path.isfile(os.path.join(directory_path, '规则文件.xls'))):
        # 解压 A.zip 到指定目录

        #with zipfile.ZipFile(csdir+"def.py",'r') as zip_ref:
        #    zip_ref.extractall(directory_path, encoding="utf-8")
        extract_zip_file(csdir+"def.py", directory_path)
    # 返回目录路径
    if directory_path=="":
        quit()
    return directory_path
    


def convert_and_compare_dates(date_str):
    import datetime
    current_date = datetime.datetime.now()

    try:
       date_obj = datetime.datetime.strptime(str(int(int(date_str)/4)), "%Y%m%d") 
    except:
        print("fail")
        return  "已过期"
  
    if date_obj > current_date:
        
        return "未过期"
    else:
        return "已过期"
    
def read_setting_cfg():
    global csdir
    # 读取 setting.cfg 文件
    if os.path.exists(csdir+'setting.cfg'):
        text.insert(END,"已完成初始化\n")
        with open(csdir+'setting.cfg', 'r') as f:
            setting_cfg = eval(f.read())
    else:
        # 创建 setting.cfg 文件，如果文件已存在则覆盖
        setting_cfg_path =csdir+ 'setting.cfg'
        with open(setting_cfg_path, 'w') as f:
            f.write('{"settingdir": 0, "sidori": 0, "sidfinal": "11111180000808"}')
        text.insert(END,"未初始化，正在初始化...\n")
        setting_cfg = read_setting_cfg()
    return setting_cfg
    

def open_setting_cfg():
    global csdir
    # 打开 setting.cfg 文件
    with open(csdir+"setting.cfg", "r") as f:
        # 将文件内容转换为字典
        setting_cfg = eval(f.read())
    return setting_cfg

def update_setting_cfg(keys,values):
    global csdir
    # 打开 setting.cfg 文件
    with open(csdir+"setting.cfg", "r") as f:
        # 将文件内容转换为字典
        setting_cfg = eval(f.read())
    
    if setting_cfg[keys]==0 or setting_cfg[keys]=="11111180000808" :
        setting_cfg[keys]=values
        # 保存字典覆盖源文件
        with open(csdir+"setting.cfg", "w") as f:
            f.write(str(setting_cfg))


def generate_random_file():
    # 生成一个六位数的随机数
    random_number = random.randint(200000, 299999)
    # 将随机数保存到文本文件中
    update_setting_cfg("sidori",random_number)

def display_random_number():
    global csdir
    mroot = Toplevel()
    mroot.title("ID")
    
    sw = mroot.winfo_screenwidth()
    sh = mroot.winfo_screenheight()
    # 得到屏幕高度
    ww = 80
    wh = 70
    # 窗口宽高为100
    x = (sw - ww) / 2
    y = (sh - wh) / 2
    mroot.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
    
    # 打开 setting.cfg 文件
    with open(csdir+"setting.cfg", "r") as f:
        # 将文件内容转换为字典
        setting_cfg = eval(f.read())
    random_number=int(setting_cfg["sidori"])
    sid=random_number*2+183576

    print(sid)
    # 创建标签和输入框
    label = ttk.Label(mroot, text=f"机器码: {random_number}")
    entry = ttk.Entry(mroot)

    # 将标签和输入框添加到窗口中
    label.pack()
    entry.pack()

    # 监听输入框的回车键事件
    #entry.bind("<Return>", check_input)
    ttk.Button(mroot, text="验证", command=lambda:check_input(entry.get(),sid)).pack()
    
def check_input(input_numbers,sid):

    # 将输入的数字转换为整数'

    try:
        input_number = int(str(input_numbers)[0:6])
        day_end=convert_and_compare_dates(str(input_numbers)[6:14])
    except:
        showinfo(title="提示", message="不匹配，注册失败。")
        return 0
    # 核对输入的数字是否等于随机数字
    if input_number == sid and day_end=="未过期":
        update_setting_cfg("sidfinal",input_numbers)
        showinfo(title="提示", message="注册成功,请重新启动程序。")
        quit()
    else:
        showinfo(title="提示", message="不匹配，注册失败。")





#######################################################            

def Tread_TOOLS_fileopen(methon):
    """-导入多个文件，已完成更新"""
    global TT_ori
    global TT_ori_backup
    global TT_biaozhun
    warnings.filterwarnings('ignore')

    if methon==0:#导入原始文件模式
        allfileName = filedialog.askopenfilenames(filetypes=[("XLS", ".xls"), ("XLSX", ".xlsx")])
        k = [pd.read_excel(x, header=0, sheet_name=0) for x in allfileName] 
        data = pd.concat(k, ignore_index=True).drop_duplicates()
        try:
            data=data.loc[ : , ~TT_ori.columns.str.contains("^Unnamed")]
        except:
            pass
        TT_ori_backup=data.copy()
        TT_ori=Tread_TOOLS_CLEAN(data).copy()

        text.insert(END,"\n原始数据导入成功，行数："+str(len(TT_ori)))
        text.insert(END,"\n数据校验：\n")
        text.insert(END,TT_ori)
        text.see(END)
        
    if methon==1:#导入规则文件模式
        ume=filedialog.askopenfilename(filetypes=[("XLS", ".xls")])
        TT_biaozhun["关键字表"]=pd.read_excel(ume,sheet_name=0,header=0,index_col=0,).reset_index()
        TT_biaozhun["产品批号"]=pd.read_excel(ume,sheet_name="产品批号",header=0,index_col=0,).reset_index()        
        TT_biaozhun["事件发生月份"]=pd.read_excel(ume,sheet_name="事件发生月份",header=0,index_col=0,).reset_index()    
        TT_biaozhun["事件发生季度"]=pd.read_excel(ume,sheet_name="事件发生季度",header=0,index_col=0,).reset_index()  
        TT_biaozhun["规格"]=pd.read_excel(ume,sheet_name="规格",header=0,index_col=0,).reset_index()
        TT_biaozhun["型号"]=pd.read_excel(ume,sheet_name="型号",header=0,index_col=0,).reset_index()   
        TT_biaozhun["设置"]=pd.read_excel(ume,sheet_name="设置",header=0,index_col=0,).reset_index()  
        Tread_TOOLS_check(TT_ori,TT_biaozhun["关键字表"],0)
        text.insert(END,"\n标准导入成功，行数："+str(len(TT_biaozhun)))    
        text.see(END)

def Tread_TOOLS_check(data,guize,methon):
        """校验是否存在未定义的源数据，已完成修改"""
        global TT_ori
        result=Tread_TOOLS_Countall(data).df_psur(guize)  
        #如果是导入规则阶段，则直接显示结果
        if methon==0:

            Tread_TOOLS_tree_Level_2(result,0,TT_ori.copy())
            
        #校验是否存在未定义的源数据，如果有，则提示             
        result["核验"]=0
        result.loc[(result["关键字标记"].str.contains("-其他关键字-", na=False)),"核验"]=result.loc[(result["关键字标记"].str.contains("-其他关键字-", na=False)),"总数量"]
        if result["核验"].sum()>0:
            showinfo(title="温馨提示", message="存在未定义类型的报告"+str(result["核验"].sum())+"条，趋势分析可能会存在遗漏，建议修正该错误再进行下一步。")     

def Tread_TOOLS_tree_Level_2(input_TT_ori, methon, data_ori, *selection):  # methon=0表示原始报表那个层级，其他就使用传入文件。
    """-报表查看器"""
    ##########预处理模块：判断属于哪个层级和根据条件筛选报表#################
    global TT_ori_backup

    columns_list_TT_ori = input_TT_ori.columns.values.tolist()
    methon = 0
    TT_ori_owercount_easyread = input_TT_ori.loc[:]
    
    
    #接受selection，并判断是否为空：
    mmm=0
    try:
        target=selection[0]
        mmm=1
    except:
        pass

    ##########报表查看器模块#################
    treeQ = Toplevel()
    treeQ.title("报表查看器")
    sw_treeQ = treeQ.winfo_screenwidth()
    # 得到屏幕宽度
    sh_treeQ = treeQ.winfo_screenheight()
    # 得到屏幕高度
    ww_treeQ = 1300
    wh_treeQ = 600
    # 窗口宽高为100
    x_treeQ = (sw_treeQ - ww_treeQ) / 2
    y_treeQ = (sh_treeQ - wh_treeQ) / 2
    treeQ.geometry("%dx%d+%d+%d" % (ww_treeQ, wh_treeQ, x_treeQ, y_treeQ))
    frame0 = ttk.Frame(treeQ, width=1300, height=20)
    frame0.pack(side=BOTTOM)
    
    frame = ttk.Frame(treeQ, width=1300, height=20)
    frame.pack(side=TOP)



    if 1>0:

        BX_var = Button(
            frame0,
            text="控制图(所有)",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: Tread_TOOLS_DRAW_make_risk_plot(TT_ori_owercount_easyread[:-1],target,[x for x in TT_ori_owercount_easyread.columns if (x not in [target])], "关键字趋势图", 100),
            )
        if mmm==1:
            BX_var.pack(side=LEFT)

        BX_var = Button(
            frame0,
            text="控制图(总数量)",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: Tread_TOOLS_DRAW_make_risk_plot(TT_ori_owercount_easyread[:-1],target,[x for x in TT_ori_owercount_easyread.columns if (x in ["该元素总数量"])], "关键字趋势图", 100),
            )
        if mmm==1:
            BX_var.pack(side=LEFT)

        B_SAVE = Button(
            frame0,
            text="导出",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: TOOLS_save_dict(TT_ori_owercount_easyread),
        )  #
        B_SAVE.pack(side=LEFT)
        
        B_SAVE = Button(
            frame0,
            text="发生率测算",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: Tread_TOOLS_fashenglv(TT_ori_owercount_easyread,target),
        )  #
        if "关键字标记" not in TT_ori_owercount_easyread.columns and  "报告编码" not in TT_ori_owercount_easyread.columns:
            if "对象" not in TT_ori_owercount_easyread.columns:
                B_SAVE.pack(side=LEFT)
                
        B_SAVE = Button(
            frame0,
            text="直方图",
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",
            command=lambda: Tread_TOOLS_DRAW_histbar(TT_ori_owercount_easyread.copy()),
        )  #
        if "对象" in TT_ori_owercount_easyread.columns:
            B_SAVE.pack(side=LEFT)
            
        B_tmd = Button(
            frame0,
            text="行数:"+str(len(TT_ori_owercount_easyread)),
            bg="white",
            font=("微软雅黑", 10),
            relief=GROOVE,
            activebackground="green",

        )
        B_tmd.pack(side=LEFT)              
        
    # 以下是在treeview上显示整个表格 ，并调节特定列的间距！！！！！！！！！！！！！！！！！！！！
    bookList = TT_ori_owercount_easyread.values.tolist()
    columns_list = TT_ori_owercount_easyread.columns.values.tolist()
    tree = ttk.Treeview(frame, columns=columns_list, show="headings", height=45)

    for i in columns_list:
        tree.heading(i, text=i)
    for item in bookList:
        tree.insert("", "end", values=item)
    for b in columns_list:
        tree.column(b, minwidth=0, width=120, stretch=NO)

    yscrollbar = Scrollbar(frame, orient="vertical")  # hTT_orizontal
    yscrollbar.pack(side=RIGHT, fill=Y)
    yscrollbar.config(command=tree.yview)
    tree.config(yscrollcommand=yscrollbar.set)

    xscrollbar = Scrollbar(frame, orient="horizontal")  # hTT_orizontal
    xscrollbar.pack(side=BOTTOM, fill=X)
    xscrollbar.config(command=tree.xview)
    tree.config(yscrollcommand=yscrollbar.set)

    def trefun_1(event, columns_list, TT_ori_owercount_easyread):
        # del owercount_easyread["评估对象"]
        
        for item in tree.selection():
            selection = tree.item(item, "values")      
            m_dict=dict(zip(columns_list,selection))  
            
        if "该分类下各项计数" in  columns_list:
            data_ori2=data_ori.copy()
            data_ori2["关键字查找列"] = ""
            for x in TOOLS_get_list(m_dict["查找位置"]):
                data_ori2["关键字查找列"] = data_ori2["关键字查找列"] + data_ori2[x].astype("str")        
            data_temp_x = data_ori2.loc[data_ori2["关键字查找列"].str.contains(m_dict["关键字标记"], na=False)].copy()
            data_temp_x = data_temp_x.loc[~data_temp_x["关键字查找列"].str.contains(m_dict["排除值"], na=False)].copy()    
 
            #data_ori2=data_temp_x[["报告编码","关键字查找列"]].copy()
            #print(TT_ori_backup)
            #print(data_ori2)
            #data_ori2=pd.merge(data_ori2,TT_ori_backup,on="报告编码", how="left")#.reset_index(drop)        
            Tread_TOOLS_tree_Level_2(data_temp_x, 0, data_temp_x)
            return 0
        
        if "报告编码" in  columns_list:
            viewtable = Toplevel()
            sw = viewtable.winfo_screenwidth()
            # 得到屏幕宽度
            sh = viewtable.winfo_screenheight()
            # 得到屏幕高度
            ww = 800
            wh = 600
            # 窗口宽高为100
            x = (sw - ww) / 2
            y = (sh - wh) / 2
            viewtable.geometry("%dx%d+%d+%d" % (ww, wh, x, y))

            text_viewtable = ScrolledText(
                viewtable, height=1100, width=1100, bg="#FFFFFF"
            )
            text_viewtable.pack(padx=10, pady=10)
            def callback1(event=None):
                text_viewtable.event_generate('<<Copy>>')   
            def callback3(data,filename):    
                filenames = open(filename,"w",encoding='utf-8') 
                filenames.write(data)
                # 刷新缓存
                filenames.flush()  
                showinfo(title="提示信息", message="保存成功。")

            menu = Menu(text_viewtable,tearoff=False,)
            menu.add_command(label="复制", command=callback1)
            menu.add_command(label="导出", command=lambda:thread_it(callback3,text_viewtable.get(1.0,'end'),filedialog.asksaveasfilename(title=u"保存文件",initialfile=m_dict["报告编码"],defaultextension="txt",filetypes=[("txt", "*.txt")])))

            def popup(event):
                menu.post(event.x_root, event.y_root)   # post在指定的位置显示弹出菜单
            text_viewtable.bind("<Button-3>", popup)                 # 绑定鼠标右键,执行popup函数
            
            viewtable.title(m_dict["报告编码"])
            for i in range(len(columns_list)):  # 根据部分字段来分行

                text_viewtable.insert(END, columns_list[i])
                text_viewtable.insert(END, "：")
                text_viewtable.insert(END,m_dict[columns_list[i]])
                text_viewtable.insert(END, "\n")
            text_viewtable.config(state=DISABLED)
            return 0
            
            
        y = selection[1:-1]  # [x for x in selection][2:]

        x = TT_ori_owercount_easyread.columns.tolist()
        x=x[1:-1]
        #s_dict=dict(zip(x,y))      
        s_dict = {'关键词': x, '数量': y}
        s_dict=pd.DataFrame.from_dict(s_dict)
        s_dict["数量"]=s_dict["数量"].astype(float)
        Tread_TOOLS_draw(s_dict, "帕累托图",'关键词','数量',"帕累托图") 
        return 0
    

 
    
    tree.bind(
        "<Double-1>",
        lambda event: trefun_1(event, columns_list, TT_ori_owercount_easyread),
    )
    tree.pack()
    
class Tread_TOOLS_Countall():
    """通用的统计模块"""    
    def __init__(self,data):
        """通用的统计模块"""            
        self.df=data

    def df_psur(self, my_guize,*methon):
        """趋势分析核心准备文件"""
        global TT_biaozhun 
        data_temp=self.df.copy()

        allnumber=len(data_temp.drop_duplicates("报告编码"))
    

        guize2 = my_guize.copy()

        #增加透视列
        setting=TT_biaozhun["设置"] 
        if setting.loc[1,"值"]:
            toushi=setting.loc[1,"值"]    
        else:
            toushi="透视列"
            data_temp[toushi]="未正确设置"            
        #追加其他关键字
        result_all = ""
        allkeyword = "-其他关键字-"
        for ids, cols in guize2.iterrows():
            allkeyword = allkeyword + "|" + str(cols["值"])
            mute=cols    
        mute[3]=allkeyword
        mute[2]="-其他关键字-|"
        guize2.loc[len(guize2)]= mute
        guize2 = guize2.reset_index(drop=True)
        
        
        #定义在什么位置查找
        data_temp["关键字查找列"] = ""
        for x in TOOLS_get_list(guize2.loc[0,"查找位置"]):
            data_temp["关键字查找列"] = data_temp["关键字查找列"] + data_temp[x].astype("str")        

        # 进入到单一的关键字环节
        result_all_list=[]    
        for ids,cols in guize2.iterrows(): 
            keyword_value = cols["值"]    
            data_temp_x = data_temp.loc[data_temp["关键字查找列"].str.contains(keyword_value, na=False)].copy()
            if  str(cols["排除值"])!="nan":  
                data_temp_x = data_temp_x.loc[~data_temp_x["关键字查找列"].str.contains(str(cols["排除值"]), na=False)].copy()
            
            data_temp_x["关键字标记"] = str(keyword_value)
            data_temp_x["关键字计数"] = 1    
                                
            if len(data_temp_x) > 0:
                data_temp_x2 = pd.pivot_table(
                        data_temp_x.drop_duplicates("报告编码"),
                        values=["关键字计数"],
                        index="关键字标记",
                        columns=toushi,
                        aggfunc={"关键字计数": "count"},
                        fill_value="0",
                        margins=True,
                        dropna=False,
                    )  
                data_temp_x2 = data_temp_x2[:-1]
                data_temp_x2.columns = data_temp_x2.columns.droplevel(0)
                data_temp_x2=data_temp_x2.reset_index()

                #统计各类不良事件计数
                if len(data_temp_x2)> 0:
                    rm=str(Counter(TOOLS_get_list0("use(关键字查找列).file",data_temp_x,1000))).replace("Counter({", "{")
                    rm=rm.replace("})", "}")
                    rm = ast.literal_eval(rm)
                    
                    data_temp_x2.loc[0,"事件分类"]=str(TOOLS_get_list(data_temp_x2.loc[0,"关键字标记"])[0])
                    data_temp_x2.loc[0,"该分类下各项计数"]=str({k:v for k, v in rm.items() if STAT_judge_x(str(k),TOOLS_get_list(keyword_value))==1 })
                    data_temp_x2.loc[0,"其他分类各项计数"]=str({k:v for k, v in rm.items() if STAT_judge_x(str(k),TOOLS_get_list(keyword_value))!=1 })
                    data_temp_x2["查找位置"]=cols["查找位置"]    
                    
                
                    result_all_list.append(data_temp_x2)    
        result_all = pd.concat(result_all_list)
        


        #以下是做一些排版
        result_all=result_all.sort_values(by=["All"], ascending=[False], na_position="last")
        result_all=result_all.reset_index() 

        result_all["All占比"]=round(result_all["All"]/allnumber * 100, 2)
        result_all=result_all.rename(columns={"All": "总数量","All占比": "总数量占比"})
        
        
        for idp,cpl in guize2.iterrows():
            result_all.loc[(result_all["关键字标记"].astype(str)==str(cpl["值"])), "排除值"] = cpl["排除值"]  
            result_all.loc[(result_all["关键字标记"].astype(str)==str(cpl["值"])), "查找位置"] = cpl["查找位置"]  

        result_all["排除值"]=result_all["排除值"].fillna("-没有排除值-")


        result_all["报表类型"]="PSUR"
        del result_all["index"]    
        try:
            del result_all["未正确设置"]
        except:
            pass
        return result_all

            
    def df_find_all_keword_risk(self,methon,*gn):
        """关键字评分及预警模块主模块""" 
        global TT_biaozhun
        #以后这几项作为参数传入
        df=self.df.copy()
        time1=time.time()

        guize1 = TT_biaozhun["关键字表"].copy()
        
        maincol="作用对象"
        
        countcol="报告编码"
        work_table=df.groupby([maincol]).agg(
                总数量=(countcol,"nunique"),
        ).reset_index()
        
        col_listttt=[maincol,methon]   #增加事件发生批号/型号/月份等
        
        work_table2=df.groupby(col_listttt).agg(
                该元素总数量=(maincol,"count"),
        ).reset_index()
                
        result_list=[]
        

        
        counterxx=0
        counterxx_all=int(len(work_table))
        for name_maincol,num in zip(work_table[maincol].values,work_table["总数量"].values):
            counterxx+=1
            df1=df[(df[maincol]==name_maincol)].copy()    
            
            for key_value,key_site,key_out in zip(guize1["值"].values,guize1["查找位置"].values,guize1["排除值"].values):
                    df2=df1.copy()
                    keyword=TOOLS_get_list(key_value)[0]

                    df2["关键字查找列"] = ""
                    for x in TOOLS_get_list(key_site):
                        df2["关键字查找列"] = df2["关键字查找列"] + df2[x].astype("str")
                
                    df2.loc[df2["关键字查找列"].str.contains(key_value, na=False),"关键字"]=keyword
                    

                    
                    #排除值
                    if str(key_out)!="nan":  # 需要排除的
                        df2 = df2.loc[~df2["关键字查找列"].str.contains(key_out, na=False)].copy()
                    
                    if(len(df2))<1:

                        continue 

                    result_temp=STAT_find_keyword_risk(df2,[maincol,"关键字"],"关键字",methon,int(num)) ######key
                    if len(result_temp)>0:
                        result_temp["关键字组合"]=key_value
                        result_temp["排除值"]=key_out
                        result_temp["关键字查找列"]=key_site                        
                        result_list.append(result_temp) 
                        

        if len(result_list)<1:
            showinfo(title="错误信息", message="该注册证号未检索到任何关键字，规则制定存在缺陷。")
            return 0            
        result=pd.concat(result_list)
        
        #增加比例的预警
        result=pd.merge(result,work_table2,on=col_listttt, how="left")#.reset_index(drop)    
        result["关键字数量比例"]=round(result["计数"]/result["该元素总数量"],2)
        
        result=result.reset_index(drop=True)
        
        #这一段暂时没有用处，为后续开发做基础
        if len(result)>0:
            result["风险评分"]=0
            result["报表类型"]="keyword_findrisk"+methon
            result.loc[(result["计数"]>=3), "风险评分"] = result["风险评分"]+3    
            result.loc[(result["计数"]>=(result["数量均值"]+result["数量标准差"])), "风险评分"] = result["风险评分"]+1            
            result.loc[(result["计数"]>=result["数量CI"]), "风险评分"] = result["风险评分"]+1    
            result.loc[(result["关键字数量比例"]>0.5)&(result["计数"]>=3), "风险评分"] = result["风险评分"]+1            

            result =result.sort_values(by="风险评分", ascending=[False], na_position="last").reset_index(drop=True)    


            #writer = pd.ExcelWriter("Tall.xls",engine="xlsxwriter")  # 
            #result.to_excel(writer, sheet_name="字典数据")
            #writer.close()    
        
        #Tread_TOOLS_tree_Level_2(result,1,df)

        #只展示需要的那个表格
        xx=result.columns.to_list()
        target=xx[xx.index("关键字")+1]

        result2 = pd.pivot_table(
                result,
                index=target,
                columns="关键字",
                values=["计数"],
                aggfunc={"计数": "sum"},
                fill_value="0",
                margins=True,
                dropna=False,
            )  # .reset_index()
        result2.columns = result2.columns.droplevel(0)
        #result2=result2[:-1].reset_index()
        
        result2=pd.merge(result2,result[[target,"该元素总数量"]].drop_duplicates(target), on=[target], how="left")
        #result=result.rename(columns={"All":"总数量"}).reset_index() 
        del result2["All"]
        result2.iloc[-1,-1] = result2["该元素总数量"].sum(axis = 0)
        
        print("耗时：",(time.time()-time1))
        
        
        return result2
        #Tread_TOOLS_tree_Level_2(result2,1,df)






def Tread_TOOLS_bar(methon):
         """数据对比分析（数量或者占比）"""
         allfileName = filedialog.askopenfilenames(filetypes=[("XLS", ".xls"), ("XLSX", ".xlsx")])
         k = [pd.read_excel(x, header=0, sheet_name=0) for x in allfileName] 
         data = pd.concat(k, ignore_index=True)
         result1 = pd.pivot_table(
                data,
                index="对象",
                columns="关键词",
                values=methon,
                aggfunc="sum",
                fill_value="0",
                margins=True,
                dropna=False,
            ).reset_index()
        
         del result1["All"]    
         result1=result1[:-1]        
            
         Tread_TOOLS_tree_Level_2(result1,0,0)


       

def Tread_TOOLS_analysis(methon):
    """选择分析间隔"""
    import datetime
    global TT_ori
    global TT_biaozhun
    # 校验一下，如果没有导入原始数据或者导入了规则数据，不可以往下执行。
    if len(TT_ori)==0:
       showinfo(title="提示", message="您尚未导入原始数据。")
       return 0
    if len(TT_biaozhun) == 0:
       showinfo(title="提示", message="您尚未导入规则。")
       return 0

    setting=TT_biaozhun["设置"]    
    TT_ori["作用对象"] = ""
    for x in TOOLS_get_list(setting.loc[0,"值"]):
        TT_ori["作用对象"] = TT_ori["作用对象"] + "-" + TT_ori[x].fillna("未填写").astype("str")    

    # 构建界面
    se = Toplevel()
    se.title("单品分析")
    sw_se = se.winfo_screenwidth()
    # 得到屏幕宽度
    sh_se = se.winfo_screenheight()
    # 得到屏幕高度
    ww_se = 580
    wh_se = 80
    # 窗口宽高为100
    x_se = (sw_se - ww_se) / 1.7
    y_se = (sh_se - wh_se) / 2
    se.geometry("%dx%d+%d+%d" % (ww_se, wh_se, x_se, y_se))


    import_sey2 = Label(se, text="作用对象：")
    import_sey2.grid(row=1, column=0, sticky="w")
    comvalue2 = StringVar()  # 窗体自带的文本，新建一个值
    comboxlist2 = ttk.Combobox(
        se, width=25, height=10, state="readonly", textvariable=comvalue2
    )  # 初始化
    comboxlist2["values"] = list(set(TT_ori["作用对象"].to_list())) 
    comboxlist2.current(0)  # 默认选择最后一个
    comboxlist2.grid(row=1, column=1)  # , sticky='w')    

    import_sey = Label(se, text="分析对象：")
    import_sey.grid(row=1, column=2, sticky="w")
    
    
    comvalue = StringVar()  # 窗体自带的文本，新建一个值
    comboxlist = ttk.Combobox(
        se, width=15, height=10, state="readonly", textvariable=comvalue
    )  # 初始化
    comboxlist["values"] = ["事件发生月份", "事件发生季度","产品批号", "型号","规格"]  
      
    comboxlist.current(0)  # 默认选择最后一个
    comboxlist.grid(row=1, column=3)  # , sticky='w')




    import_sey3 = Label(se, text="事件发生起止时间：")
    import_sey3.grid(row=2, column=0, sticky="w")

    import_se_entry=Entry(se, width = 10)
    import_se_entry.insert(0,min(TT_ori["事件发生日期"].dt.date))
    import_se_entry.grid(row=2, column=1, sticky="w")
    
    import_se_entry2=Entry(se, width = 10)
    import_se_entry2.insert(0,max(TT_ori["事件发生日期"].dt.date))
    import_se_entry2.grid(row=2, column=2, sticky="w")
      

    btn_se2 = Button(
        se,
        text="原始查看",
        width=10,
        bg="white",
        font=("微软雅黑", 10),
        relief=GROOVE,
        activebackground="green",
        command=lambda: thread_it(Tread_TOOLS_doing,TT_ori,comboxlist2.get(),comboxlist.get(),import_se_entry.get(),import_se_entry2.get(),1 ) ) # comboxlistz.get()
    btn_se2.grid(row=3, column=3, sticky="w")

    btn_se2 = Button(
        se,
        text="分类查看",
        width=10,
        bg="white",
        font=("微软雅黑", 10),
        relief=GROOVE,
        activebackground="green",
        command=lambda: thread_it(Tread_TOOLS_doing,TT_ori,comboxlist2.get(),comboxlist.get(),import_se_entry.get(),import_se_entry2.get(),0) ) # comboxlistz.get()
    btn_se2.grid(row=3, column=2, sticky="w")
    
    btn_se2 = Button(
        se,
        text="趋势分析",
        width=10,
        bg="white",
        font=("微软雅黑", 10),
        relief=GROOVE,
        activebackground="green",
        command=lambda: thread_it(Tread_TOOLS_doing,TT_ori,comboxlist2.get(),comboxlist.get(),import_se_entry.get(),import_se_entry2.get(),2) ) # comboxlistz.get()
    btn_se2.grid(row=3, column=1, sticky="w")    
    
def Tread_TOOLS_doing(data,zhenghao,target,time_start,time_end,methonx):
    """选择分析间隔之后的执行文件"""
    global TT_biaozhun
    data=data[(data["作用对象"]==zhenghao)].copy()
    #date_format = "%Y-%m-%d"
    time_start =pd.to_datetime(time_start) #datetime.datetime.strptime(time_start, date_format)
    time_end = pd.to_datetime(time_end) #datetime.datetime.strptime(time_end, date_format)    
    data=data[((data["事件发生日期"]>=time_start)&(data["事件发生日期"]<=time_end))]
    if target=="事件发生日期!":
        data["timeq"]=data["事件发生日期"].copy()
        print(data)
        data=data.set_index("timeq")
        data=data.resample('D').asfreq(fill_value=0)
        print(data)
        data["事件发生日期"]=data["事件发生日期"].astype(str)
    text.insert(END,"\n数据数量："+str(len(data)))
    text.see(END)

    if methonx==0:
        Tread_TOOLS_check(data,TT_biaozhun["关键字表"],0)
        return 0 
    if methonx==1:
        Tread_TOOLS_tree_Level_2(data, 1,data)
        return 0         
    if len(data)<1:
        showinfo(title="错误信息", message="没有符合筛选条件的报告。")
        return 0
    Tread_TOOLS_check(data,TT_biaozhun["关键字表"],1)    
    
    
    Tread_TOOLS_tree_Level_2(Tread_TOOLS_Countall(data).df_find_all_keword_risk(target), 1,0,target)


        


######################################################################
#其他小型函数
######################################################################
    
def STAT_countx(x):
    """所有成分关键字计数,返回一个字典""" 
    return x.value_counts().to_dict()
    
def STAT_countpx(x,y):
    """特定成分关键字计数,返回一个数值""" 
    return len(x[(x==y)])#.values
    
def STAT_countnpx(x,y):
    """不含特定成分关键字计数,返回一个数值""" 
    return len(x[(x not in y)])#.values
    
def STAT_get_max(df):
    """返回最大值""" 
    return df.value_counts().max()

def STAT_get_mean(df):
    """返回平均值""" 
    return round(df.value_counts().mean(),2)
    
def STAT_get_std(df):
    """返回标准差""" 
    return round(df.value_counts().std(ddof=1),2)
    
def STAT_get_95ci(df):
    """返回95%置信区间上限"""     
    return round(np.percentile(df.value_counts(), 97.5),2)#stats.norm.interval(0.95, loc=mean, scale=std)
    
def STAT_get_mean_std_ci(x,allx):
    """一次性返回MEAN,STD,CI,用于关键字统计模块"""     
    warnings.filterwarnings("ignore")
    dfe=TOOLS_strdict_to_pd(str(x))["content"].values/allx    
    xmean=round(dfe.mean(),2)
    xstd=round(dfe.std(ddof=1),2)
    xci=round(np.percentile(dfe, 97.5),2)            
    return pd.Series((xmean, xstd, xci))    
    
def STAT_findx_value(x,who):
    """一次性返回符合某个对象的值"""     
    warnings.filterwarnings("ignore")
    dfe=TOOLS_strdict_to_pd(str(x))    
    #print(dfe)
    result=dfe.where(dfe["index"] == str(who))    
    print(result)        
    return result    
    
def STAT_judge_x(a,b):
    """PSUR模块的辅助统计函数"""     
    for keyword_value1 in b:
        if a.find(keyword_value1)>-1:
            return 1
            

def STAT_basic_risk(df,a,b,c,d):
    """改良的省中心预警规则"""
    df["风险评分"]=0
    df.loc[((df[a]>=3)&(df[b]>=1))|(df[a]>=5), "风险评分"] = df["风险评分"]+5    
    df.loc[(df[b]>=3), "风险评分"] = df["风险评分"]+1    
    df.loc[(df[c]>=1), "风险评分"] = df["风险评分"]+10        
    df["风险评分"] = df["风险评分"]+df[d]/100
    return df



def STAT_find_keyword_risk(df,cols_list,main_col,target,allx):    
        """关键字评分及预警模块,cols_list为所要引入的列（列表形式），main_col统计对象列（关键字），target为月份、季度或者批号等,allx为证号总数量"""
        dfx_findrisk1=df.groupby(cols_list).agg(
            证号关键字总数量=(main_col,"count"),    
            包含元素个数=(target,"nunique"),
            包含元素=(target,STAT_countx),                
            ).reset_index()
        
        cols_list2=cols_list.copy()
        cols_list2.append(target)
        dfx_findrisk2=df.groupby(cols_list2).agg(
            计数=(target,"count"),                    
            ).reset_index()    
        
        #算出批号等计数
        cols_list3=    cols_list2.copy()
        cols_list3.remove("关键字") #不含关键字的
        dfx_findrisk3=df.groupby(cols_list3).agg(
            该元素总数=(target,"count"),                        
            ).reset_index()    
                
        dfx_findrisk2["证号总数"]=allx
        dfx_findrisk=pd.merge(dfx_findrisk2,dfx_findrisk1,on=cols_list,how="left")#.reset_index()            
        
        if len(dfx_findrisk)>0:        
            dfx_findrisk[['数量均值', '数量标准差', '数量CI']] = dfx_findrisk.包含元素.apply(lambda x: STAT_get_mean_std_ci(x,1))        
        return dfx_findrisk        
    




def STAT_find_risk(df,cols_list,main_col,target):    
        """评分及预警模块,cols_list为所要引入的列（列表形式），main_col统计对象列（关键字），target为月份、季度或者批号等""" 
        dfx_findrisk1=df.groupby(cols_list).agg(
            证号总数量=(main_col,"count"),    
            包含元素个数=(target,"nunique"),
            包含元素=(target,STAT_countx),        
            均值=(target,STAT_get_mean),
            标准差=(target,STAT_get_std),
            CI上限=(target,STAT_get_95ci),                
            ).reset_index()
                    
        cols_list2=cols_list.copy()
        cols_list2.append(target)
        dfx_findrisk2=df.groupby(cols_list2).agg(
            计数=(target,"count"),
            严重伤害数=("伤害",lambda x: STAT_countpx(x.values,"严重伤害")),
            死亡数量=("伤害",lambda x: STAT_countpx(x.values,"死亡")),    
            单位个数=("单位名称","nunique"),    
            单位列表=("单位名称",STAT_countx),                            
            ).reset_index()                

        dfx_findrisk=pd.merge(dfx_findrisk2,dfx_findrisk1,on=cols_list,how="left")#.reset_index()    
                
        dfx_findrisk["风险评分"]=0
        dfx_findrisk["报表类型"]="dfx_findrisk"+target
        dfx_findrisk.loc[((dfx_findrisk["计数"]>=3)&(dfx_findrisk["严重伤害数"]>=1)|(dfx_findrisk["计数"]>=5)), "风险评分"] = dfx_findrisk["风险评分"]+5    
        dfx_findrisk.loc[(dfx_findrisk["计数"]>=(dfx_findrisk["均值"]+dfx_findrisk["标准差"])), "风险评分"] = dfx_findrisk["风险评分"]+1            
        dfx_findrisk.loc[(dfx_findrisk["计数"]>=dfx_findrisk["CI上限"]), "风险评分"] = dfx_findrisk["风险评分"]+1        
        dfx_findrisk.loc[(dfx_findrisk["严重伤害数"]>=3)&(dfx_findrisk["风险评分"]>=7), "风险评分"] = dfx_findrisk["风险评分"]+1    
        dfx_findrisk.loc[(dfx_findrisk["死亡数量"]>=1), "风险评分"] = dfx_findrisk["风险评分"]+10        
        dfx_findrisk["风险评分"] = dfx_findrisk["风险评分"]+dfx_findrisk["单位个数"]/100    
        dfx_findrisk =dfx_findrisk.sort_values(by="风险评分", ascending=[False], na_position="last").reset_index(drop=True)        

        return dfx_findrisk

def TOOLS_get_list(TT_ori_list):
    """将字符串转化为列表，返回一个经过整理的列表，get_list0的精简版"""
    TT_ori_list = str(TT_ori_list)
    uselist_key = []
    uselist_key.append(TT_ori_list)
    uselist_key = ",".join(uselist_key)
    uselist_key = uselist_key.split("|")
    uselist_temp = uselist_key[:]
    uselist_key = list(set(uselist_key))
    uselist_key.sort(key=uselist_temp.index)
    return uselist_key    
    
def TOOLS_get_list0(TT_ori_list, search_result, *methon): #methon=1000:不去重
    """创建单元格支持多个甚至表单（文件）传入的方法，返回一个经过整理的清单"""
    TT_ori_list = str(TT_ori_list)
    # print(methon)
    if pd.notnull(TT_ori_list):
        try:
            if "use(" in str(TT_ori_list):  # 创建支持列表传入的方法
                string = TT_ori_list
                p1 = re.compile(r"[(](.*?)[)]", re.S)
                arr = re.findall(p1, string)
                uselist_key = []
                if ").list" in TT_ori_list:  # 使用配置表的表
                    umeu = "配置表/" + str(arr[0]) + ".xls"
                    uselist_keyfile = pd.read_excel(
                        umeu, sheet_name=arr[0], header=0, index_col=0
                    ).reset_index()
                    uselist_keyfile["检索关键字"] = uselist_keyfile["检索关键字"].astype(str)
                    uselist_key = uselist_keyfile["检索关键字"].tolist() + uselist_key
                if ").file" in TT_ori_list:  # 使用原始文件中的列
                    #search_result[arr[0]] = search_result[arr[0]].astype(str)
                    uselist_key = search_result[arr[0]].astype(str).tolist() + uselist_key

                # 增加药品ADR名称的一些适应：
                try:
                    if "报告类型-新的" in search_result.columns:
                        uselist_key = ",".join(uselist_key)  # 拆解含有、的列表元素
                        uselist_key = uselist_key.split(";")
                        uselist_key = ",".join(uselist_key)  # 拆解含有、的列表元素
                        uselist_key = uselist_key.split("；")
                        uselist_key = [c.replace("（严重）", "") for c in uselist_key]
                        uselist_key = [c.replace("（一般）", "") for c in uselist_key]
                except:
                    pass
                # 药品ADR名称适应结束。

                uselist_key = ",".join(uselist_key)  # 拆解含有、的列表元素
                uselist_key = uselist_key.split("、")
                uselist_key = ",".join(uselist_key)
                uselist_key = uselist_key.split("，")
                uselist_key = ",".join(uselist_key)
                uselist_key = uselist_key.split(",")

                uselist_temp = uselist_key[:]
                try:
                    if methon[0]==1000:
                      pass
                except:
                      uselist_key = list(set(uselist_key))
                uselist_key.sort(key=uselist_temp.index)

            else:
                TT_ori_list = str(TT_ori_list)
                uselist_key = []
                uselist_key.append(TT_ori_list)
                uselist_key = ",".join(uselist_key)  # 拆解含有、的列表元素
                uselist_key = uselist_key.split("、")
                uselist_key = ",".join(uselist_key)
                uselist_key = uselist_key.split("，")
                uselist_key = ",".join(uselist_key)
                uselist_key = uselist_key.split(",")

                uselist_temp = uselist_key[:]
                try:
                    if methon[0]==1000:
                      uselist_key = list(set(uselist_key))
                except:
                      pass  
                uselist_key.sort(key=uselist_temp.index)
                uselist_key.sort(key=uselist_temp.index)

        except ValueError2:
            showinfo(title="提示信息", message="创建单元格支持多个甚至表单（文件）传入的方法，返回一个经过整理的清单出错，任务终止。")
            return False

    return uselist_key    
def TOOLS_strdict_to_pd(strdict):  # 2222222
    """-文本格式的字典转PD"""
    return pd.DataFrame.from_dict(eval(strdict), orient="index",columns=["content"]).reset_index()  

def Tread_TOOLS_view_dict(str_helper, methon):
    """查看可复制的图标数据"""
    helper = Toplevel()
    helper.title("查看数据")
    helper.geometry("700x500")

    yscrollbar = Scrollbar(helper)
    text_helper = Text(helper, height=100, width=150)
    yscrollbar.pack(side=RIGHT, fill=Y)
    text_helper.pack()
    yscrollbar.config(command=text_helper.yview)
    text_helper.config(yscrollcommand=yscrollbar.set)
    if methon == 1:
        # for x in range(len(str_helper)):
        text_helper.insert(END, str_helper)
        text_helper.insert(END, "\n\n")
        return 0
    for i in range(len(str_helper)):
        text_helper.insert(END, str_helper.iloc[i, 0])
        text_helper.insert(END, ":")
        text_helper.insert(END, str_helper.iloc[i, 1])
        text_helper.insert(END, "\n\n")


def Tread_TOOLS_fashenglv(data,target):
    global TT_biaozhun
    data = pd.merge(data, TT_biaozhun[target], on=[target], how="left").reset_index(drop=True)
    #del data["注册证编号/曾用注册证编号"]
    mean_x=data["使用次数"].mean()
    
    has_nan=data["使用次数"].isnull()
    if has_nan.any():
        a_values=data[target][has_nan].tolist()
        a_values.remove("All")
    else:
        a_values=[]
    
    if len(a_values)!=0:
        showinfo(title="提示", message=str(a_values)+"没有分母，用均值"+str(mean_x)+"填充计算。")	
    
    data["使用次数"]=data["使用次数"].fillna(int(mean_x))
    sum_x=data["使用次数"][:-1].sum()    
    data.iloc[-1,-1]=sum_x
    list_x=[x for x in data.columns if (x not in ["使用次数",target])]
    for ids, cols in data.iterrows():
        for x in list_x:
            data.loc[ids,x]=int(cols[x])/int(cols["使用次数"])
    del data["使用次数"]
    Tread_TOOLS_tree_Level_2(data,1,1,target)

def TOOLS_save_dict(data):
    """保存文件"""
    file_path_flhz = filedialog.asksaveasfilename(
        title=u"保存文件",
        initialfile="【排序后的原始数据】.xls",
        defaultextension="xls",
        filetypes=[("Excel 97-2003 工作簿", "*.xls")],
    )
    try:
        data["详细描述T"]=data["详细描述T"].astype(str)
    except:
        pass
    try:
        data["报告编码"]=data["报告编码"].astype(str)
    except:
        pass
    try:   
        machd=re.search("\【(.*?)\】", file_path_flhz)
        data["对象"]=machd.group(1)
    except:
        pass
    writer = pd.ExcelWriter(file_path_flhz,engine="xlsxwriter")  # 
    data.to_excel(writer, sheet_name="字典数据")
    writer.close()
    showinfo(title="提示", message="文件写入成功。")
    

    
def Tread_TOOLS_DRAW_histbar(data):
    """直方图"""
    #data 当前表(字典)  bar_x X轴的列，BAR_Y y轴的列。  
    # 创建窗体  
    view_pic = Toplevel()
    view_pic.title("直方图")
    frame0 = ttk.Frame(view_pic, height=20)  # , width = 1200,
    frame0.pack(side=TOP)

    drawPic_f = Figure(figsize=(12, 6), dpi=100)  # fast100
    drawPic_canvas = FigureCanvasTkAgg(drawPic_f, master=view_pic)
    drawPic_canvas.draw()
    drawPic_canvas.get_tk_widget().pack(expand=1)  # grid(row=0, column=0)
    # 解决汉字乱码问题
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 使用指定的汉字字体类型（此处为黑体）
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # 创建和显示工具条
    toolbar = NavigationToolbar2Tk(drawPic_canvas, view_pic)
    toolbar.update()
    drawPic_canvas.get_tk_widget().pack()

    drawPic_a = drawPic_f.add_subplot(111)
   
    drawPic_a.set_title("直方图")
    
    x=data.columns.to_list()
    x.remove("对象")
    x_ticksa=np.arange(len(x))

    
    
    for i in x:
        data[i]= data[i].astype(float)
    
    data['数据'] = data[x].values.tolist()
    m=0
    for ids,cols in data.iterrows():
        drawPic_a.bar([i+m for i in x_ticksa],data.loc[ids,'数据'],label=x, width=0.1)


        for x00,y00 in zip([i+m for i in x_ticksa],data.loc[ids,'数据']):   
           drawPic_a.text(x00-0.015,y00+0.07,str(int(y00)), color = 'black', size=8) ##在图上写文本 
           
        m=m+0.1        
    #drawPic_a.xticks(x_ticksa,x)    
    drawPic_a.set_xticklabels(data.columns.to_list(), rotation=-90, fontsize=8)  
    
  
              
    drawPic_a.legend(data["对象"])
            

    drawPic_canvas.draw()
        
def Tread_TOOLS_DRAW_make_risk_plot(data, bar_x,bar_y, title, methon,*gn):
    """风险预警栏目的专用绘图函数"""
    #data 当前表(字典)  bar_x X轴的列，BAR_Y y轴的列。  
    # 创建窗体  
    view_pic = Toplevel()
    view_pic.title(title)
    frame0 = ttk.Frame(view_pic, height=20)  # , width = 1200,
    frame0.pack(side=TOP)
    drawPic_f = Figure(figsize=(12, 6), dpi=100)  # fast100
    drawPic_canvas = FigureCanvasTkAgg(drawPic_f, master=view_pic)
    drawPic_canvas.draw()
    drawPic_canvas.get_tk_widget().pack(expand=1)  # grid(row=0, column=0)
    # 解决汉字乱码问题
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 使用指定的汉字字体类型（此处为黑体）
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # 创建和显示工具条
    toolbar = NavigationToolbar2Tk(drawPic_canvas, view_pic)
    toolbar.update()
    drawPic_canvas.get_tk_widget().pack()

    drawPic_a = drawPic_f.add_subplot(111)
   
    drawPic_a.set_title(title)
    x_label = data[bar_x] #X标签
    
    #from pandas.api.types import is_datetime64_any_dtype
    if methon!=999: #这个是时间的，不转格式   
        drawPic_a.set_xticklabels(x_label, rotation=-90, fontsize=8)


    x_value = range(0, len(x_label), 1) #X轴


        
    #其余的折线图
    for y_col in bar_y:
        y_values= data[y_col].astype(float)  #Y轴
        
        if y_col=="关注区域":
            drawPic_a.plot(list(x_label), list(y_values),label=str(y_col),color="red") # width, label="num",
        else:
            drawPic_a.plot(list(x_label), list(y_values),label=str(y_col))  # width, label="num",
  
        #添加关键字标记（关键字方法使用）        
        if methon==100:
            for x00,y00 in zip(x_label,y_values):   
                if y00==max(y_values) and y00>=3 and len(bar_y)!=1:
                     drawPic_a.text(x00,y00,(str(y_col)+":"+str(int(y00))), color = 'black', size=8) ##在图上写文本                      
                if len(bar_y)==1 and y00>=0.01:
                     drawPic_a.text(x00,y00,str(int(y00)), color = 'black', size=8) ##在图上写文本    
    #添加风险标记 
    #try:
    #    for x00,y00 in zip(x_label,data["风险评分"]):   
    #        if y00>0:
    #             drawPic_a.text(x00,y00,"!", color = 'r', size=8) ##在图上写文本
    #except:
    #    pass
    
    #增加UCL
    try:
        if gn[0] and '控制线' in gn[0]:
            modelxx=gn[0]
            wind=gn[1]
    except:
        modelxx="ucl"
        
    if len(bar_y)==1:


        if modelxx=="更多控制线分位数":
            print('windows=',gn[1])
            data[bar_y]=data[bar_y].astype(float)
            data[bar_y]=data[bar_y].fillna(0)            
            window_size = int(gn[1])  # 假设 gn[1] 是你从某处获取的窗口大小  
            min_periods = 1  # 可以根据需求设置  
              
            rolling_stats=data[bar_y].copy()
            rolling_stats['mean'] = data[bar_y].rolling(window=window_size).mean() 
            rolling_stats['25%'] = data[bar_y].rolling(window=window_size).quantile(0.25) 
            rolling_stats['50%'] = data[bar_y].rolling(window=window_size).quantile(0.50) 
            rolling_stats['75%'] = data[bar_y].rolling(window=window_size).quantile(0.75) 
              
            # 计算异常上下限  
            rolling_stats['IQR'] = rolling_stats['75%'] - rolling_stats['25%']  
            rolling_stats['UCL'] = rolling_stats['75%'] + 1.5 * rolling_stats['IQR']  
            rolling_stats['LCL'] = rolling_stats['25%'] - 1.5 * rolling_stats['IQR']  
              
              
            # 绘制中位数、分位数和异常上下限  
            for column in ['mean', '25%', '50%', '75%', 'UCL', 'LCL']:  
                drawPic_a.plot(rolling_stats.index, rolling_stats[column], label=column, linestyle='--')   
  
 
                          
        elif modelxx=="更多控制线STD":
            print('windows=', gn[1])  
            data[bar_y] = data[bar_y].astype(float)  
            data[bar_y] = data[bar_y].fillna(0)  
              
            window_size = int(gn[1])  # 获取窗口大小  
            min_periods = int(gn[1])   # 设置最小非NA值数量  
              
            # 复制bar_y列到一个新的DataFrame，用于计算滚动统计量  
            rolling_stats = data[bar_y].copy()  
              
            # 计算滚动均值和滚动标准差  
            rolling_stats['mean'] = data[bar_y].rolling(window=window_size, min_periods=min_periods).mean()  
            rolling_stats['std'] = data[bar_y].rolling(window=window_size, min_periods=min_periods).std()  
              
            # 基于均值和标准差计算上限  
            rolling_stats['mean+1std'] = rolling_stats['mean'] + rolling_stats['std']  
            rolling_stats['mean+2std'] = rolling_stats['mean'] + 2 * rolling_stats['std']  
            rolling_stats['mean+3std'] = rolling_stats['mean'] + 3 * rolling_stats['std']  
            rolling_stats['mean-1std'] = rolling_stats['mean'] - rolling_stats['std']  
            rolling_stats['mean-2std'] = rolling_stats['mean'] - 2 * rolling_stats['std']  
            rolling_stats['mean-3std'] = rolling_stats['mean'] - 3 * rolling_stats['std']    
            # 绘制曲线图  
            for column in ['mean', 'mean+1std', 'mean+2std', 'mean+3std', 'mean-1std', 'mean-2std', 'mean-3std']:  
                drawPic_a.plot(rolling_stats.index, rolling_stats[column], label=column, linestyle='--')  
 
            


                                                   
    drawPic_a.set_title("控制图")
    drawPic_a.set_xlabel("项")
    drawPic_f.tight_layout(pad=0.4, w_pad=3.0, h_pad=3.0)
    box1 = drawPic_a.get_position()
    drawPic_a.set_position([box1.x0, box1.y0, box1.width * 0.7, box1.height])
    drawPic_a.legend(loc=2, bbox_to_anchor=(1.05, 1.0), fontsize=10, borderaxespad=0.0)


    xt22 = StringVar()
    number_chosen = ttk.Combobox(frame0, width=15, textvariable=xt22, state='readonly')
    number_chosen['values'] = bar_y
    number_chosen.pack(side=LEFT)
    number_chosen.current(0)

    xt33 = StringVar()
    number_chosen33 = ttk.Combobox(frame0, width=15, textvariable=xt33)
    number_chosen33['values'] = ['12','4','25']
    number_chosen33.pack(side=LEFT)
    number_chosen33.current(0)


    

    B_draw5 = Button(
        frame0,
        text="控制图（单项-UCL(标准差法)）",
        bg="white",
        font=("微软雅黑", 10),
        relief=GROOVE,
        activebackground="green",
        command=lambda: Tread_TOOLS_DRAW_make_risk_plot(data,bar_x,[x for x in bar_y if xt22.get() in x], title, methon,"更多控制线STD",xt33.get()))       
    B_draw5.pack(side=LEFT,anchor="ne")  
    B_draw5 = Button(
        frame0,
        text="控制图（单项-分位数）",
        bg="white",
        font=("微软雅黑", 10),
        relief=GROOVE,
        activebackground="green",
        command=lambda: Tread_TOOLS_DRAW_make_risk_plot(data,bar_x,[x for x in bar_y if xt22.get() in x], title, methon,"更多控制线分位数",xt33.get()))       
    B_draw5.pack(side=LEFT,anchor="ne")      
          
    B_draw2 = Button(
        frame0,
        text="去除标记",
        bg="white",
        font=("微软雅黑", 10),
        relief=GROOVE,
        activebackground="green",
        command=lambda: Tread_TOOLS_DRAW_make_risk_plot(data,bar_x,bar_y, title, 0))

    B_draw2.pack(side=LEFT,anchor="ne")
    drawPic_canvas.draw()
    
def Tread_TOOLS_draw(data, title, bar_x, bar_y,methon):
    """绘制柱状图饼图折线图（单个值）通用文件"""
    warnings.filterwarnings("ignore")
    view_pic = Toplevel()
    view_pic.title(title)
    frame0 = ttk.Frame(view_pic, height=20)  # , width = 1200,
    frame0.pack(side=TOP)             
    # 创造画布
    drawPic_f = Figure(figsize=(12, 6), dpi=100)  # fast100
    drawPic_canvas = FigureCanvasTkAgg(drawPic_f, master=view_pic)
    drawPic_canvas.draw()
    drawPic_canvas.get_tk_widget().pack(expand=1)  # grid(row=0, column=0)
    drawPic_a = drawPic_f.add_subplot(111)
    # 解决汉字乱码问题
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 使用指定的汉字字体类型（此处为黑体）
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # 创建工具条
    toolbar = NavigationToolbar2Tk(drawPic_canvas, view_pic)
    toolbar.update()
    # 显示工具条
    drawPic_canvas.get_tk_widget().pack()
    
    #为字典传入做一个兼容
    try:
        test_ini = data.columns
        data=data.sort_values(by=bar_y, ascending=[False], na_position="last")
    except:
        dict_TT_ori = eval(data)
        dict_TT_ori = pd.DataFrame.from_dict(
            dict_TT_ori, TT_orient=bar_x, columns=[bar_y]
        ).reset_index()
        data = dict_TT_ori.sort_values(by=bar_y, ascending=[False], na_position="last")    


    #如果是时间的显示，则做一些优化
    if ("日期" in title or  "时间" in title  or  "季度" in title) and "饼图" not in methon:
        data[bar_x] = pd.to_datetime(data[bar_x], format="%Y/%m/%d").dt.date
        data = data.sort_values(by=bar_x, ascending=[True], na_position="last")
    elif "批号" in title: 
        data[bar_x] = data[bar_x].astype(str)
        data = data.sort_values(by=bar_x, ascending=[True], na_position="last")
        drawPic_a.set_xticklabels(data[bar_x], rotation=-90, fontsize=8)                           
    else:
        data[bar_x] = data[bar_x].astype(str)
        drawPic_a.set_xticklabels(data[bar_x], rotation=-90, fontsize=8)
    #定义好X,Y等参数
    values= data[bar_y]  
    x_value = range(0, len(values), 1)

    drawPic_a.set_title(title)
    
    
    #绘图函数
    if methon=="柱状图":
        drawPic_a.bar(x=data[bar_x], height=values, width=0.2, color="#87CEFA")  # width, label="num",plt.bar(x='size',height = 'tip',data=df_bar)
    elif methon=="饼图":
        drawPic_a.pie(x=values, labels=data[bar_x], autopct="%0.2f%%")
    elif methon=="折线图":
        drawPic_a.plot(data[bar_x], values, lw=0.5, ls='-', c="r", alpha=0.5) 

    elif  "帕累托图" in str(methon):
        data_tps = data[bar_y].fillna(0)##将目标数据导入
        
        ##数据处理
        #data_tps.sort_values(ascending = False,inplace = True )##对数组进行排序,ascending 升序,inplace代表行和列的排序
        p=data_tps.cumsum()/data_tps.sum()*100
        data["百分比"]=round(data["数量"]/data_tps.sum()*100,2)
        data["累计百分比"]=round(p,2)
        key = p[p>0.8].index[0]##返回累计占比大于0.8的第一个索引名称
        key_num = data_tps.index.tolist().index(key)

        ##开始画图及结果输出

        drawPic_a.bar(x=data[bar_x], height=data_tps,color="C0",label=bar_y)##画条形图
        ax2 = drawPic_a.twinx()
        ax2.plot(data[bar_x], p, color="C1",alpha = 0.6,label="累计比例")
        ax2.yaxis.set_major_formatter(PercentFormatter())
        #if "时间" not in title:
        #    ax2.axvline(key_num,color='r',linestyle="--",alpha=0.3)  ##画红色的虚线
        #    ax2.text(key_num+0.2,p[key]-0.05,'%.3f%%' % (p[key]*100), color = 'r') ##在图上写文本

        drawPic_a.tick_params(axis="y", colors="C0")
        ax2.tick_params(axis="y", colors="C1")
        
        for x00,y00,u00,p00 in zip(data[bar_x],data_tps,data["百分比"],data["累计百分比"]):   
            drawPic_a.text(x00,y00+0.1,str(int(y00))+", "+str(int(u00))+"%,"+str(int(p00))+"%", color = 'black', size=8) ##在图上写文本 
            
        #超级的，增加多一个柱状图
        if  "超级帕累托图" in str(methon):
            p1 = re.compile(r'[(](.*?)[)]', re.S)
            bar_z=re.findall(p1, methon)[0]
            drawPic_a.bar(x=data[bar_x], height=data[bar_z],color="orangered",label=bar_z)##画条形图    
            

                
    #格式设置
    drawPic_f.tight_layout(pad=0.4, w_pad=3.0, h_pad=3.0)
    box1 = drawPic_a.get_position()
    drawPic_a.set_position([box1.x0, box1.y0, box1.width * 0.7, box1.height])
    drawPic_a.legend(loc=2, bbox_to_anchor=(1.05, 1.0), fontsize=10, borderaxespad=0.0)

    #开始绘制
    drawPic_canvas.draw()
    
    #柱状图增加数值
    if len(values)<=20 and methon!="饼图" and  methon!="帕累托图" :
        for x,y in zip(x_value,values):
            text = str(y)
            xy=(x,y+0.3)
            drawPic_a.annotate(text,xy=xy,fontsize=8,color="black",ha="center",va="baseline")


    
    B1 = Button(
        frame0,
        relief=GROOVE,
        activebackground="green",
        text="保存原始数据",
        command=lambda: TOOLS_save_dict(data),
    )
    B1.pack(side=RIGHT)
    
    B333 = Button(
        frame0, relief=GROOVE, text="查看原始数据", command=lambda: Tread_TOOLS_view_dict(data, 1)
    )
    B333.pack(side=RIGHT)    
    

    B0 = Button(
        frame0,
        relief=GROOVE,
        text="饼图",
        command=lambda: Tread_TOOLS_draw(data, title, bar_x, bar_y,"饼图"),
    )
    B0.pack(side=LEFT)

    B0 = Button(
        frame0,
        relief=GROOVE,
        text="柱状图",
        command=lambda: Tread_TOOLS_draw(data,title, bar_x, bar_y,"柱状图"),
    )
    B0.pack(side=LEFT)
    B0 = Button(
        frame0,
        relief=GROOVE,
        text="折线图",
        command=lambda: Tread_TOOLS_draw(data, title, bar_x, bar_y,"折线图"),
    )
    B0.pack(side=LEFT)

    B0 = Button(
        frame0,
        relief=GROOVE,
        text="帕累托图",
        command=lambda: Tread_TOOLS_draw(data, title, bar_x, bar_y,"帕累托图"),
    )
    B0.pack(side=LEFT)
    
    



def helper():
    """-程序使用帮助"""
    helper = Toplevel()
    helper.title("程序使用帮助")
    helper.geometry("700x500")

    yscrollbar = Scrollbar(helper)
    text_helper = Text(helper, height=80, width=150, bg="#FFFFFF", font="微软雅黑")
    yscrollbar.pack(side=RIGHT, fill=Y)
    text_helper.pack()
    yscrollbar.config(command=text_helper.yview)
    text_helper.config(yscrollcommand=yscrollbar.set)
    # text_helper.insert(END,"\n\n")
    text_helper.insert(
        END,
    "\n  本程序用于趋势分析,供广东省内参与医疗器械警戒试点的企业免费使用。如您有相关问题或改进建议，请联系以下人员：\n\n    佛山市药品不良反应监测中心\n    蔡权周 \n    微信：18575757461 \n    邮箱：411703730@qq.com" 
    )
    text_helper.config(state=DISABLED)



def Tread_TOOLS_CLEAN(data):
        """数据清洗模块"""    
            
        data["报告编码"] = data["报告编码"].astype("str")
        
        data["产品批号"] = data["产品批号"].astype("str")
        data["型号"] = data["型号"].astype("str")
        data["规格"] = data["规格"].astype("str")
        
        data["注册证编号/曾用注册证编号"] = data["注册证编号/曾用注册证编号"].str.replace("(", "（",regex=False)  # 转义
        data["注册证编号/曾用注册证编号"] = data["注册证编号/曾用注册证编号"].str.replace(")", "）",regex=False)  # 转义
        data["注册证编号/曾用注册证编号"] = data["注册证编号/曾用注册证编号"].str.replace("*", "※",regex=False)  # 转义
        
        data["产品名称"] = data["产品名称"].str.replace("*", "※",regex=False)  # 转义
        
        data["产品批号"] = data["产品批号"].str.replace("(", "（",regex=False)  # 转义
        data["产品批号"] = data["产品批号"].str.replace(")", "）",regex=False)  # 转义
        data["产品批号"] = data["产品批号"].str.replace("*", "※",regex=False)  # 转义

        #data['报告日期'] = pd.to_datetime(data['报告日期'], format='%Y-%m-%d', errors='coerce')     
        data['事件发生日期'] = pd.to_datetime(data['事件发生日期'], format='%Y-%m-%d', errors='coerce')     
                        
        #data["报告月份"] = data["报告日期"].dt.to_period("M").astype(str)    
        #data["报告季度"] = data["报告日期"].dt.to_period("Q").astype(str)                
        data["事件发生月份"] = data["事件发生日期"].dt.to_period("M").astype(str)            
        data["事件发生季度"] = data["事件发生日期"].dt.to_period("Q").astype(str)                
        #data["事件发生年份"]=data["报告月份"].str[0:4]    
        

        data["注册证编号/曾用注册证编号"]=data["注册证编号/曾用注册证编号"].fillna("未填写")
        data["产品批号"]=data["产品批号"].fillna("未填写")
        data["型号"]=data["型号"].fillna("未填写")
        data["规格"]=data["规格"].fillna("未填写")
        data["产品识别"]=data["注册证编号/曾用注册证编号"]+'-'+data["产品名称"]        
        return data


    
def thread_it(func, *args):
    """将函数打包进线程"""
    # 创建
    t = threading.Thread(target=func, args=args)
    # 守护 !!!
    t.setDaemon(True)
    # 启动
    t.start()


def showWelcome():  # 100100
    """欢迎屏幕"""
    sw = roox.winfo_screenwidth()
    # 得到屏幕宽度
    sh = roox.winfo_screenheight()
    # 得到屏幕高度
    roox.overrideredirect(True)
    roox.attributes("-alpha", 1)  # 窗口透明度（1为不透明，0为全透明）
    x = (sw - 475) / 2
    y = (sh - 200) / 2
    # 设置窗口位于屏幕中部
    roox.geometry("675x140+%d+%d" % (x, y))
    roox["bg"] = "royalblue"
    lb_welcometext = Label(
        roox, text="医疗器械警戒趋势分析工具", fg="white", bg="royalblue", font=("微软雅黑", 20)
    )
    lb_welcometext.place(x=0, y=15, width=675, height=90)
    lb_welcometext2 = Label(
        roox,
        text="Trend Analysis Tools V"+str(version_now),
        fg="white",
        bg="cornflowerblue",
        font=("微软雅黑", 15),
    )
    lb_welcometext2.place(x=0, y=90, width=675, height=50)


def closeWelcome():
    """欢迎屏幕:设置欢迎页停留时间"""
    for i in range(2):
        root.attributes("-alpha", 0)  # 窗口透明度
        time.sleep(1)
    root.attributes("-alpha", 1)  # 窗口透明度
    roox.destroy()


#####第三部分：主界面 ########################################################################
if __name__ == '__main__':
    pass
root = Tk()
root.title("医疗器械警戒趋势分析工具Trend Analysis Tools V"+str(version_now))
sw_root = root.winfo_screenwidth()
# 得到屏幕宽度
sh_root = root.winfo_screenheight()
# 得到屏幕高度
ww_root = 700
wh_root = 620
# 窗口宽高为100
x_root = (sw_root - ww_root) / 2
y_root = (sh_root - wh_root) / 2
root.geometry("%dx%d+%d+%d" % (ww_root, wh_root, x_root, y_root))
root.configure(bg="steelblue")  # royalblue

# 窗口按钮
try:
    frame0 = ttk.Frame(root, width=100, height=20)
    frame0.pack(side=LEFT)

    B_open_files1 = Button(
        frame0,
        text="导入原始数据",
        bg="steelblue",
        fg="snow",
        height=2,
        width=12,
        font=("微软雅黑", 12),
        relief=GROOVE,
        activebackground="lightsteelblue",
        command=lambda: thread_it(Tread_TOOLS_fileopen, 0),
    )
    B_open_files1.pack()  # floralwhite

    B_open_files3 = Button(
        frame0,
        text="导入分析规则",
        bg="steelblue",
        height=2,
        fg="snow",
        width=12,
        font=("微软雅黑", 12),
        relief=GROOVE,
        activebackground="lightsteelblue",
        command=lambda: thread_it(Tread_TOOLS_fileopen, 1),
    )
    B_open_files3.pack()



    B_open_files3 = Button(
        frame0,
        text="趋势统计分析",
        bg="steelblue",
        height=2,
        fg="snow",
        width=12,
        font=("微软雅黑", 12),
        relief=GROOVE,
        activebackground="lightsteelblue",
        command=lambda: thread_it(Tread_TOOLS_analysis, 0),
    )
    B_open_files3.pack()


    B_open_files3 = Button(
        frame0,
        text="直方图（数量）",
        bg="steelblue",
        height=2,
        fg="snow",
        width=12,
        font=("微软雅黑", 12),
        relief=GROOVE,
        activebackground="lightsteelblue",
        command=lambda: thread_it(Tread_TOOLS_bar, "数量"))
    B_open_files3.pack()
    B_open_files3 = Button(
        frame0,
        text="直方图（占比）",
        bg="steelblue",
        height=2,
        fg="snow",
        width=12,
        font=("微软雅黑", 12),
        relief=GROOVE,
        activebackground="lightsteelblue",
        command=lambda: thread_it(Tread_TOOLS_bar, "百分比"))
    B_open_files3.pack()          
    B_open_files3 = Button(
        frame0,
        text="查看帮助文件",
        bg="steelblue",
        height=2,
        fg="snow",
        width=12,
        font=("微软雅黑", 12),
        relief=GROOVE,
        activebackground="lightsteelblue",
        command=lambda: thread_it(helper))             
    B_open_files3.pack()   
    B_open_files3 = Button(
        frame0,
        text="更改用户分组",
        bg="steelblue",
        height=2,
        fg="snow",
        width=12,
        font=("微软雅黑", 12),
        relief=GROOVE,
        activebackground="lightsteelblue",
        command=lambda: thread_it(display_random_number))             
    B_open_files3.pack()        
except:#display_random_number
    pass


# 文本框
text = ScrolledText(root, height=400, width=400, bg="#FFFFFF", font="微软雅黑")
text.pack()  # (padx=5, pady=5)

text.insert(
    END,
    "\n  本程序用于趋势分析,供广东省内参与医疗器械警戒试点的企业免费使用。如您有相关问题或改进建议，请联系以下人员：\n\n    佛山市药品不良反应监测中心\n    蔡权周 \n    微信：18575757461 \n    邮箱：411703730@qq.com" 
    )
text.insert(END, "\n\n")

def A000():
    pass


#序列好验证、配置表生成与自动更新。
setting_cfg=read_setting_cfg()
generate_random_file()
setting_cfg=open_setting_cfg()
if setting_cfg["settingdir"]==0:
    showinfo(title="提示", message="未发现默认配置文件夹，请选择一个。如该配置文件夹中并无配置文件，将生成默认配置文件。")
    filepathu=filedialog.askdirectory()
    path=get_directory_path(filepathu)
    update_setting_cfg("settingdir",path)    	
setting_cfg=open_setting_cfg()
random_number=int(setting_cfg["sidori"])
input_number=int(str(setting_cfg["sidfinal"])[0:6])
day_end=convert_and_compare_dates(str(setting_cfg["sidfinal"])[6:14])
sid=random_number*2+183576
if input_number == sid  and day_end=="未过期":
    usergroup="用户组=1" 
    text.insert(END,usergroup+"   有效期至：")
    text.insert(END,datetime.strptime(str(int(int(str(setting_cfg["sidfinal"])[6:14])/4)), "%Y%m%d") )
else:
    text.insert(END,usergroup)	
text.insert(END,"\n配置文件路径："+setting_cfg["settingdir"]+"\n")


# 启动界面
roox = Toplevel()
tMain = threading.Thread(target=showWelcome)
tMain.start()
t1 = threading.Thread(target=closeWelcome)
t1.start()



root.lift()
root.attributes("-topmost", True)
root.attributes("-topmost", False)
root.mainloop()

