import os, re, time
from collections import OrderedDict
from fileFormatCheck import *
from vcdFileParse import *

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
startTime = time.time()

# 客供pattern核对所需的正则
# << time      | ADR >> PP PP // SITE
re_fileFormatCommentCheck = re.compile(r"^\/\/")  # 开头两行注释
# << time      | ADR >> PP PP // SITE
re_fileFormatItemCheck = re.compile(
    r"^<<\s+time\s+\|\s+ADR\s+>>\s+[a-zA-Z ]+\s+//\sSITE$"
)
# << ..........| ....>> AA BB // ..........
# << ..........| ....>> ii ib // ..........
re_fileFormatItemPinBodyCheck = re.compile(
    r"^<<\s+\.+\|\s+\.+>>\s+[a-zA-Z0-9_ ]+//\s+\.+$"
)
# << ..........| ....>> .. .. // ..........
re_fileFormatItemBlankCheck = re.compile(r"^<<\s+\.+\|\s+\.+>>[ .]+//\s+\.+$")

# << ..........| ....>> 11 XX // wait about 1060 clock enter SLEEP
re_fileFormatItemEndCheck = re.compile(
    r"^<<\s+\.+\|\s+\.+>>\s+[a-zA-Z0-9 ]+//\s+[a-zA-Z0-9 ]+$"
)

# <<        438| xx00>> 00 00 // 00000003
re_fileFormatBodyCheck = re.compile(r"^<<\s+\d+\|\s+\w+>>\s+[01HXLZz ]+(?://\s+.*)?$")


# vcd 文件主体内容正则
# << ..........| ....>> 11 XX // wait about 1060 clock enter SLEEP
re_0TimingStatus = re.compile(
    r"^<<\s+\.+\|\s+\.+>>\s+([a-zA-Z0-9 ]+)//\s+([a-zA-Z0-9 ]+)$"
)
re_timingStatus = re.compile(r"^<<\s+\d+\|\s+\w+>>\s+([01HXLZz ]+)(//.*)?$")

re_vcdFileParseList = [
    re_timingStatus,
    re_0TimingStatus,
]

if __name__ == "__main__":
    # 获取当前目录
    workPath = os.getcwd()
    # sourceFile = r"TPn_I2C_program_220302.txt"
    sourceFile = r"TPn_I2C_Read_IDx.txt"
    # outputFile = r"I2C_Read_IDx.pat"
    # # sourceFile = r"I2C_program.txt"
    # outputFile = r"I2C_program.pat"
    # sourceFile = r"I2C_trim_32K.txt"
    # outputFile = r"I2C_trim_32K.pat"

    # 校验vcd
    fileFormatCheckRegexDict = OrderedDict(
        {
            re_fileFormatBodyCheck: 0,  # 主要校验内容放第一个，减少判断
            re_fileFormatCommentCheck: 0,
            re_fileFormatItemCheck: 0,
            re_fileFormatItemPinBodyCheck: 0,
            re_fileFormatItemBlankCheck: 0,
            re_fileFormatItemEndCheck: 0,
        }
    )
    sourceFile = os.path.join(workPath, sourceFile)
    # check_vcd_file(sourceFile, fileFormatCheckRegexDict)
    vcdFileParse(sourceFile, re_vcdFileParseList)
    endTime = time.time()
    print(f"时间总共花费: {round(endTime-startTime, 3)} S")
