import os, re

"""
SNJ402 vcd文件转换思路

1. 校验vcd文件
    校验vcd文件每行都满足我们的正则规则，保证了SNJ402 vcd文件完全符合我们的预期，不出现错漏。若匹配有问题，需完善正则规则。
    转换pattern时必须检验，之后的程序就不需要再判断格式是否满足要求。
2. 转换vcd文件

    1. 获取管脚名同时实现可用于输出pattern文件中的管脚列表，形式同vcd的管脚形式，方便查看
    2. 获取0时刻初始状态
    3. 遍历每行，获取时刻点，该时刻点减去上一行的时刻点就是上一行pattern状态的维持时间。
    4. 将每行的pattern状态的时间统计timerDict（时间=>次数），若不满足要求，则需特殊处理，一般情况下是能满足的
    5. 重新遍历vcd文件，获取每行patten的状态及时间，根据timerDict来判断是否需要修改TS，生成未压缩的简单pattern（该pattern需要确认是否转换正常，压缩的pattern不好确认）
    6. 对未压缩的pattern压缩，使用RPT指令（最好增加通过解压RPT指令来生成未压缩的pattern，用于核对转换是否正常）
"""

# VCD文件sample
"""
//Power on, After power on(< 1ms), PA[3]/PA[2] set i2c command to enter I2C mode,
//wait 100us, PB[3]/PB[2] send Command 
<< time      | ADR >> PP PP // SITE
<< ..........| ....>> AA BB // ..........
<< ..........| ....>> 32 32 // ..........
<< ..........| ....>> .. .. // ..........
<< ..........| ....>> .. .. // ..........
<< ..........| ....>> .. .. // ..........
<< ..........| ....>> .. .. // ..........
<< ..........| ....>> ii ib // ..........
<< ..........| ....>> 11 XX // wait about 1060 clock enter SLEEP
<<        438| xx00>> 00 00 // 00000003
<<        563| xx00>> 00 00 // 00000004
<<        688| xx00>> 00 00 // 00000005
<<        813| xx00>> 10 00 // 00000006
<<        938| ffff>> 10 00 // 00000007
"""


# 客供pattern核对所需的正则
# << time      | ADR >> PP PP // SITE
re_fileFormatCommentCheck = re.compile(r"^\/\/")  # 开头两行注释
# << time      | ADR >> PP PP // SITE
re_fileFormatItemCheck = re.compile(
    r"^<<\s+time\s+\|\s+ADR\s+>>\s+[a-zA-Z ]+\s+//\sSITE$"
)
# << ..........| ....>> AA BB // ..........
re_fileFormatItemPinBodyCheck = re.compile(
    r"^<<\s+\.+\|\s+\.+>>\s+[a-zA-Z0-9_ ]+//\s+\.+$"
)
# << ..........| ....>> .. .. // ..........
re_fileFormatItemBlankCheck = re.compile(r"^<<\s+\.+\|\s+\.+>>[ .]+//\s+\.+$")

"""
<< ..........| ....>> ii ib // ..........
<< ..........| ....>> 11 XX // wait about 1060 clock enter SLEEP
"""
re_fileFormatItemEndCheck = re.compile(
    r"^<<\s+\.+\|\s+\.+>>\s+[a-zA-Z0-9 ]+//\s+[a-zA-Z0-9 ]+$"
)  # ... ... ... end

# <<        438| xx00>> 00 00 // 00000003
re_fileFormatBodyCheck = re.compile(r"^<<\s+\d+\|\s+\w+>>\s+[01HXLZz ]+\s+//\s+.*?$")

re_fileFormCheckRegexPlainStrDict = {
    r"^\/\/"=False,
    r"^<<\s+time\s+\|\s+ADR\s+>>\s+[a-zA-Z ]+\s+//\sSITE$"=False,
    r"^<<\s+\.+\|\s+\.+>>\s+[a-zA-Z0-9_ ]+//\s+\.+$"=False,
    r"^<<\s+\.+\|\s+\.+>>[ .]+//\s+\.+$"=False,
    r"^<<\s+\d+\|\s+\w+>>\s+[01HXLZz ]+\s+//\s+.*?$"=False,
    r"^<<\s+\d+\|\s+\w+>>\s+[01HXLZz ]+\s+//\s+.*?$",
}

'''
re_fileFormatCommentCheck = re.compile(r"^\/\/")  # 开头两行注释
# << time      | ADR >> PP PP // SITE
re_fileFormatItemCheck = re.compile(
    r"^<<\s+time\s+\|\s+ADR\s+>>\s+(?P<pinHead>[a-zA-Z ]+)\s+//\sSITE$"
)
# << ..........| ....>> AA BB // ..........
re_fileFormatItemPinBodyCheck = re.compile(
    r"^<<\s+\.+\|\s+\.+>>\s+(?P<pinBody>[a-zA-Z0-9_ ]+)//\s+\.+$"
)
# << ..........| ....>> .. .. // ..........
re_fileFormatItemBlankCheck = re.compile(r"^<<\s+\.+\|\s+\.+>>[ .]+//\s+\.+$")

"""
<< ..........| ....>> ii ib // ..........
<< ..........| ....>> 11 XX // wait about 1060 clock enter SLEEP
"""
re_fileFormatItemEndCheck = re.compile(
    r"^<<\s+\.+\|\s+\.+>>\s+(?P<pattern>[a-zA-Z0-9 ]+)//\s+(?P<comment>[a-zA-Z0-9 ]+)$"
)  # ... ... ... end

# <<        438| xx00>> 00 00 // 00000003
re_fileFormatBodyCheck = re.compile(
    r"^<<\s+(?P<time>\d+)\|\s+\w+>>\s+(?P<pattern>[01HXLZz ]+)\s+//\s+(?P<comment>.*)?$"
)
'''


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
