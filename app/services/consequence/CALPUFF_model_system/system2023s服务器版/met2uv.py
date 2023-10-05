# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 10:11:06 2022
调用exe程序，将con文件转换为nc文件
"""
import os,glob,time
import yaml

# 第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
with  open('用户输入信息.YAML', 'r', encoding='utf-8') as f:
    grd = yaml.load(f.read(), Loader=yaml.FullLoader)

with  open('系统路径配置.YAML', 'r', encoding='utf-8') as f:
    dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)

dir_run=os.path.join(dir_sys['dir_out0'],grd['title'])
dir_out=os.path.join(dir_run,'3metuv')
dir_in=os.path.join(dir_run,'3metout')
dir_program=dir_sys['dir_model']+'\\met2uv'

print('uv解压程序开始执行', time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))

fn_met=glob.glob(dir_in+'\\cmet*.dat')
fn_met.sort()

for i in range(len(fn_met)):
    fn_met[i]=fn_met[i].split('\\')[-1]

with  open(os.path.join(dir_program,'input.txt'), 'w') as f:
    f.write(dir_in+'\n')
    f.write(dir_out+'\n')
    f.write('%i\n'%len(fn_met))
    for fn in fn_met:
        f.write(fn+'\n')
cmd1=os.path.join(dir_program,'ReadCalmetToNetCDF.exe')
dir0=os.getcwd()
os.chdir(dir_program)
os.system(cmd1)
os.chdir(dir0)

print('所有met数据文件处理完成!',time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
