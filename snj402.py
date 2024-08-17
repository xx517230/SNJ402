import os, re

# 客供pattern解析所需的正则
re_fileFormatCommentCheck = re.compile(r"^\/\/")  # 开头两行注释

re_fileFormatItemCheck = re.compile(
    r"^<<\s+time\s+\|\s+ADR\s+>>\s+(?P<pinHead>[a-zA-Z ]+)\s+//\sSITE$"
)  # time/adr/pin/line

re_fileFormatItemPinBodyCheck = re.compile(
    r"^<<\s+\.+\|\s+\.+>>\s+(?P<pinBody>[a-zA-Z0-9 ]+)//\s+\.+$"
)  # ...pinBody...

re_fileFormatItemBlankCheck = re.compile(
    r"^<<\s+\.+\|\s+\.+>>[ .]+//\s+\.+$"
)  # ... ... ...

re_fileFormatItemEndCheck = re.compile(
    r"^<<\s+\.+\|\s+\.+>>\s+(?P<pattern>[a-zA-Z0-9 ]+)//\s+(?P<comment>[a-zA-Z0-9 ]+)$"
)  # ... ... ... end

re_fileFormatBodyCheck = re.compile(
    r"^<<\s+(?P<time>\d+)\|\s+\w+>>\s+(?P<pattern>[01HXLZz ]+)\s+//\s+(?P<comment>.*)?$"
)

# 获取当前目录
workPath = os.getcwd()
sourceFile = r"TPn_I2C_Read_IDx.txt"
outputFile = r"I2C_Read_IDx.pat"
# sourceFile = r"I2C_program.txt"
# outputFile = r"I2C_program.pat"
# sourceFile = r"I2C_trim_32K.txt"
# outputFile = r"I2C_trim_32K.pat"


SOURCEFILE = open(os.path.join(workPath, sourceFile), "r")
OUTPUTFILE = open(os.path.join(workPath, outputFile), "w")

lineCnt = 0
pinEndFlag = 0
patternStartFlag = 0
oldTimeStr = "0"  # 用于保存上一行的时刻点
timeStr = "0"  # 用于保存当前行的时刻点
time = 0  # 用于保存状态维持时间
pattern = ""  # 用于获取pattern内容
comment = ""  # 用于保存pattern文件中的注释行数及指令说明
pinStr = []  # 用于保存pattern文件中的管脚
timeSet = (
    set()
)  # 用于保存本pattern中所有时间的集合，用于TS的确认，因为按本pattern的时间，测试机精度无法达到

timeDict = {}  # 用于保存"时间:时间出现次数"
while True:
    fileLine = SOURCEFILE.readline()
    lineCnt += 1
    if not fileLine:  # 文件末尾跳出
        break
    if patternStartFlag == 0:
        if re_fileFormatCommentCheck.search(fileLine):
            if lineCnt < 3:
                continue
            else:
                print("pattern %d行存在注释,请确认格式!!!" % lineCnt)
        if re_fileFormatItemCheck.search(fileLine):
            str = re_fileFormatItemCheck.search(fileLine).group("pinHead")
            pinStr.append(str)
        if re_fileFormatItemPinBodyCheck.search(fileLine) and pinEndFlag == 0:
            str = re_fileFormatItemPinBodyCheck.search(fileLine).group("pinBody")
            pinStr.append(str)
        if re_fileFormatItemBlankCheck.search(fileLine):
            pinEndFlag = 1
        if re_fileFormatItemEndCheck.search(fileLine) and pinEndFlag == 1:
            patternStartFlag = 1
            pattern = re_fileFormatItemEndCheck.search(fileLine).group("pattern")
            comment = re_fileFormatItemEndCheck.search(fileLine).group("comment")
            for i in pinStr:
                OUTPUTFILE.write("//")
                OUTPUTFILE.write(i)
                OUTPUTFILE.write("\n")
        continue
    if re_fileFormatBodyCheck.search(fileLine):
        oldTimeStr = timeStr
        timeStr = re_fileFormatBodyCheck.search(fileLine).group("time")
        time = int(timeStr) - int(oldTimeStr)  # 本行的时间
        timeSet.add(time)
        if time > 1:
            OUTPUTFILE.write(" *%s*RPT %d; // %s" % (pattern, time, comment))
            OUTPUTFILE.write("\n")
        else:
            OUTPUTFILE.write(" *%s*; // %s" % (pattern, comment))
            OUTPUTFILE.write("\n")
        pattern = re_fileFormatBodyCheck.search(fileLine).group("pattern")
        comment = re_fileFormatBodyCheck.search(fileLine).group("comment")
    else:
        print("check body line failed to match pattern!!!")
        print("line=%d, %s not match!!!" % (lineCnt, fileLine))
        break
print(timeSet)
SOURCEFILE.close()
OUTPUTFILE.close()


for time in timeSet:
    timeDict[time] = 0

SOURCEFILE = open(os.path.join(workPath, sourceFile), "r")
lineCnt = 0
oldTimeStr = "0"  # 用于保存上一行的时刻点
timeStr = "0"  # 用于保存当前行的时刻点
time = 0  # 用于保存状态维持时间
while True:
    fileLine = SOURCEFILE.readline()
    lineCnt += 1
    if not fileLine:  # 文件末尾跳出
        break
    if re_fileFormatBodyCheck.search(fileLine):
        oldTimeStr = timeStr
        timeStr = re_fileFormatBodyCheck.search(fileLine).group("time")
        time = int(timeStr) - int(oldTimeStr)  # 本行的时间
        timeDict[time] += 1

for key in timeDict.keys():
    print("%d=>%d" % (key, timeDict[key]))
SOURCEFILE.close()
