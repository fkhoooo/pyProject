from pathlib import Path
import shutil
import hashlib
import os
import time 
from git import Repo
import subprocess
# 相同目录结构同步
srcUrl = r"E:\zg\client\kingrbyz"
# 需要同步目录
srcList =[
    r"E:\zg\client\kingrbyz\config",
    r"E:\zg\client\kingrbyz\assets\res\dynamicSkin",
    r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\dress",
    r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\beauty",
    r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\activity",
    r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\package\itemicon",
    r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\player",
    r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\disciple\skill",
    r"E:\zg\client\kingrbyz\assets\act\act580\res\act580assetsRes\horseName",
    r"E:\zg\client\kingrbyz\assets\res\plist"
    ]

# 目标目录
desList = [
    r"F:\h5\zgh5\resource\json\config",
    r"F:\h5\zgh5\resource\assets\dynamicSkin",
    r"F:\h5\zgh5\resource\assets\icon\dress",
    r"F:\h5\zgh5\resource\assets\icon\beauty",
    r"F:\h5\zgh5\resource\assets\icon\activity",
    r"F:\h5\zgh5\resource\assets\icon\package\itemicon",
    r"F:\h5\zgh5\resource\assets\ui\player",
    r"F:\h5\zgh5\resource\assets\icon\disciple\skill",
    r"F:\h5\zgh5\resource\assets\ui\horse\name"
    r"F:\h5\zgh5\resource\assets\ui\player\plist"
    ]
filterList = [
     r"E:\zg\client\kingrbyz\assets\res\dynamicSkin\robe",
     r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\activity\5",
     r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\activity\12",
     r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\activity\actBox",
     r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\activity\cbAct",
     r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\activity\chongBangnewRes",
     r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\activity\doubleeleven",
     r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\activity\houseHold",
     r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\activity\jiarentoupiao",
     r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\activity\qingMing",
     r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\activity\redPacket",
     r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\activity\thank",
     r"E:\zg\client\kingrbyz\assets\stu\assetsRes\res\dress\ui"
]

print(333)
print("更新资源..")
repo =Repo("E:\zg\client\kingrbyz\.git") #git文件的路径
repo.remote().pull()
print("更新完成..")
logPath= Path.cwd() / "log.txt"
saveData = logPath.read_text()
isJsonUpdate = False
updateTimeList = []
addlist = []
updatelist = []
if saveData == "":
    lastTime  = 0
else:
    saveTime = saveData.split("\n")[0]
    timeList = time.strptime(saveTime,"%Y-%m-%d %H:%M:%S")
    lastTime = int(time.mktime(timeList))
def doCopyFile(data):
    srcPath = Path(data)
    print("对比资源.......")
    for i in srcPath.glob("**/*"):
        if not filterFile(i,srcList):
            continue
        if filterFile(i,filterList):
            continue
        if i.suffix == ".lua" or i.suffix == ".rej" or i.suffix == ".ttf" or i.suffix == ".lnk":
            continue
        if i.is_file():
            if i.stat().st_mtime < lastTime:
                continue
            desData = getDesPath(i)
            desPath = desData[0]
            if not desPath.parent.exists():
                if not desData[1] in updateTimeList:
                    updateTimeList.append(desData[1])
                desPath.parent.mkdir(parents = True)
                synchFile(i,desPath)
            else:
                synchFile(i,desPath)

    for i in updateTimeList:
        srcP = Path(srcList[i])
        os.utime(Path(desList[i]),(srcP.stat().st_atime,srcP.stat().st_mtime))
        for j in Path(desList[i]).glob("**/*"):
            if j.is_dir():
                  srcPath = Path(str(j).replace(desList[i],srcList[i]))
                  os.utime(str(j),(srcPath.stat().st_atime,srcPath.stat().st_mtime))
    addlist.extend(updatelist)
    if len(addlist) <= 0:
        print("没有可同步的资源")
        return
    # 更新配置表
    if isJsonUpdate == True:
        bat = Path.cwd() / "zgCfg.bat"
        p = subprocess.Popen("cmd.exe /c" + str(bat), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        curline = p.stdout.readline()
        while (curline != b''):
            print(curline)
            curline = p.stdout.readline()
        p.wait()
        print(p.returncode)
        print("配置表更新完成")

    #转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    timeArray = time.localtime(int(time.time()))
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    log1 = '\n'.join(str(i) for i in addlist)
    logTx = otherStyleTime + "\n" + log1
    logPath.write_text(logTx)
    print("资源同步完成-------") 

def synchFile(srcPath:Path,desPath:Path):
     if str(desPath.parent) == r"F:\h5\zgh5\resource\json\config":
        global isJsonUpdate
        isJsonUpdate = True
     if(not desPath.exists()):
        shutil.copy2(str(srcPath),str(desPath))
        print("新增加:",str(desPath))
        addlist.append("ADD:" + str(desPath))
     else:
        #  if srcPath.stat().st_mtime > desPath.stat().st_mtime: #修改时间对比
             if getMD5(str(srcPath)) != getMD5(desPath):
                shutil.copy2(str(srcPath),str(desPath))
                print("更新:",str(desPath))
                updatelist.append("UPDATE:" + str(desPath))
            #  else :
                #虽然时间不同但是文件内容没变. 更改当前文件时间为系统时间 防止下次对比MD5
                #  os.utime(str(desPath))

def filterFile(data,list):
    for i in data.parents:
        if (str(i) in list):
           return True
    return False

def getDesPath(data):
    for i in data.parents:
        for idx in range(len(srcList)):
            if str(i) == srcList[idx]:
                return [Path(str(data).replace(str(i),desList[idx])),idx]

# MD5值
def getMD5(path):
    f=open(path,'rb')
    d5 = hashlib.md5()      #生成一个hash的对象
    with open(path,'rb') as f:
        while True:
            content = f.read(40960)
            if not content:
                break
            d5.update(content)   # 每次读取一部分，然后添加到hash对象里
    return d5.hexdigest()        # 打印16进制的hash值
if __name__ == '__main__':
    doCopyFile(srcUrl)


    