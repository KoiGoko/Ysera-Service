# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 10:11:06 2022
对makegeo.inp文件进行参数修改，并运行程序
"""
def pregeo(dir_in,dir_out,grd):
    '''
    将输入文件中涉及投影信息的参数进行替换,9个变量
    grd 包含读入的5个变量，程序内重新赋值，依次替换
    '''
    import os
    
    # 自定义字符串替换函数
    def str_replace(info,keystr,newstr):
        '''
        将info包含关键字keystr的字符串，替换为newstr，并做适当调整
        '''    
        for i in range(len(info)):
            if keystr in info[i]:
                temp=info[i].split('=')[0]+'= '+newstr+' !\n'
                info[i]=temp
                break
        return info  
    
    (lon0,lat0,nx,ny,dx)=[grd['lon0'],grd['lat0'],grd['nx'],grd['ny'],grd['dx']]
    xref=-nx*dx/2
    yref=-ny*dx/2
    with open (dir_in,"r") as f1:
        info=f1.readlines()

    info=str_replace(info,'(RLAT0)',"{:.4f}{N}".format(lat0, N=('N' if  lat0>0 else 'S')))
    info=str_replace(info,'(RLON0)',"{:.4f}{E}".format(lon0, E=('E' if  lon0>0 else 'W')))

    info=str_replace(info,'(RLAT1)',"{:.2f}{N}".format(30.0, N=('N' if  lat0>0 else 'S')))
    info=str_replace(info,'(RLAT2)',"{:.2f}{N}".format(60.0, N=('N' if  lat0>0 else 'S')))

    info=str_replace(info,'(NX)','{:d}'.format(int(nx)))
    info=str_replace(info,'(NY)','{:d}'.format(int(ny)))

    info=str_replace(info,'(XREFKM)','{:.2f}'.format(xref))
    info=str_replace(info,'(YREFKM)','{:.2f}'.format(yref))
    info=str_replace(info,'(DGRIDKM)','{:.3f}'.format(dx))

    with open(os.path.join(dir_out,"makegeo.inp"),  "w") as f1:
        for templine in info:
            f1.write(templine)
    print('geo.inp文件修改完成！')    

    cmd1=dir_out+'\MAKEGEOrun.bat'
    pwd=os.getcwd()
    os.chdir(dir_out)
    os.system(cmd1) 
    os.chdir(pwd) 