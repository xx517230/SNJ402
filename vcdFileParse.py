header = """//PP PP
//AA BB 
//32 32 
"""
# .*\/\/\s+\d+\s+[\S+\s]+


def vcdFileParse(file, outputFile, regexList):
    comment = ""
    pattern = ""
    timeStrOld = "0"
    timeStr = "0"
    time = 0

    with open(file, "rt") as fp, open(outputFile, "wt") as outputFp:
        # 跳过无效行，但到达0时刻位置，获取pattern及注释
        for lineCnt, line in enumerate(fp, start=1):
            if regexList[1].search(line):
                pattern = regexList[1].search(line).group(1)
                comment = regexList[1].search(line).group(2)
                break
        outputFp.write(header)
        for lineCnt, line in enumerate(fp, start=lineCnt + 1):
            match = regexList[0].search(line)
            if match:
                timeStrOld = timeStr
                timeStr = match.group(1)
                time = int(timeStr) - int(timeStrOld)  # nS
                outputFp.write(" *")
                outputFp.write(pattern)
                outputFp.write(f"* RPT {time}; //{comment}")
                outputFp.write("\n")
                # 本行的pattern及comment在下一行才输出，因为结束时刻需到下一行才能拿到
                pattern = match.group(2).replace("z", "Z").replace("Z", "X")
                comment = match.group(3)

                continue
            print(
                f"{file}文件 {lineCnt}行不满足正则条件,按理校验通过文件不应该出现该提示"
            )


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


# lineCnt = 0
# pinEndFlag = 0
# patternStartFlag = 0
# oldTimeStr = "0"  # 用于保存上一行的时刻点
# timeStr = "0"  # 用于保存当前行的时刻点
# time = 0  # 用于保存状态维持时间
# pattern = ""  # 用于获取pattern内容
# comment = ""  # 用于保存pattern文件中的注释行数及指令说明
# pinStr = []  # 用于保存pattern文件中的管脚
# timeSet = (
#     set()
# )  # 用于保存本pattern中所有时间的集合，用于TS的确认，因为按本pattern的时间，测试机精度无法达到

# timeDict = {}  # 用于保存"时间:时间出现次数"
# while True:
#     fileLine = SOURCEFILE.readline()
#     lineCnt += 1
#     if not fileLine:  # 文件末尾跳出
#         break
#     if patternStartFlag == 0:
#         if re_fileFormatCommentCheck.search(fileLine):
#             if lineCnt < 3:
#                 continue
#             else:
#                 print("pattern %d行存在注释,请确认格式!!!" % lineCnt)
#         if re_fileFormatItemCheck.search(fileLine):
#             str = re_fileFormatItemCheck.search(fileLine).group("pinHead")
#             pinStr.append(str)
#         if re_fileFormatItemPinBodyCheck.search(fileLine) and pinEndFlag == 0:
#             str = re_fileFormatItemPinBodyCheck.search(fileLine).group("pinBody")
#             pinStr.append(str)
#         if re_fileFormatItemBlankCheck.search(fileLine):
#             pinEndFlag = 1
#         if re_fileFormatItemEndCheck.search(fileLine) and pinEndFlag == 1:
#             patternStartFlag = 1
#             pattern = re_fileFormatItemEndCheck.search(fileLine).group("pattern")
#             comment = re_fileFormatItemEndCheck.search(fileLine).group("comment")
#             for i in pinStr:
#                 OUTPUTFILE.write("//")
#                 OUTPUTFILE.write(i)
#                 OUTPUTFILE.write("\n")
#         continue
#     if re_fileFormatBodyCheck.search(fileLine):
#         oldTimeStr = timeStr
#         timeStr = re_fileFormatBodyCheck.search(fileLine).group("time")
#         time = int(timeStr) - int(oldTimeStr)  # 本行的时间
#         timeSet.add(time)
#         if time > 1:
#             OUTPUTFILE.write(" *%s*RPT %d; // %s" % (pattern, time, comment))
#             OUTPUTFILE.write("\n")
#         else:
#             OUTPUTFILE.write(" *%s*; // %s" % (pattern, comment))
#             OUTPUTFILE.write("\n")
#         pattern = re_fileFormatBodyCheck.search(fileLine).group("pattern")
#         comment = re_fileFormatBodyCheck.search(fileLine).group("comment")
#     else:
#         print("check body line failed to match pattern!!!")
#         print("line=%d, %s not match!!!" % (lineCnt, fileLine))
#         break
# print(timeSet)
# SOURCEFILE.close()
# OUTPUTFILE.close()

# for time in timeSet:
#     timeDict[time] = 0

# SOURCEFILE = open(os.path.join(workPath, sourceFile), "r")
# lineCnt = 0
# oldTimeStr = "0"  # 用于保存上一行的时刻点
# timeStr = "0"  # 用于保存当前行的时刻点
# time = 0  # 用于保存状态维持时间
# while True:
#     fileLine = SOURCEFILE.readline()
#     lineCnt += 1
#     if not fileLine:  # 文件末尾跳出
#         break
#     if re_fileFormatBodyCheck.search(fileLine):
#         oldTimeStr = timeStr
#         timeStr = re_fileFormatBodyCheck.search(fileLine).group("time")
#         time = int(timeStr) - int(oldTimeStr)  # 本行的时间
#         timeDict[time] += 1

# for key in timeDict.keys():
#     print("%d=>%d" % (key, timeDict[key]))
# SOURCEFILE.close()


# if re_fileFormatBodyCheck.search(line):
#     fileFormatCheckRegexDict[re_fileFormatBodyCheck] += 1
#     continue
# if re_fileFormatCommentCheck.search(line):
#     fileFormatCheckRegexDict[re_fileFormatCommentCheck] += 1
#     continue
# if re_fileFormatItemCheck.search(line):
#     fileFormatCheckRegexDict[re_fileFormatItemCheck] += 1
#     continue
# if re_fileFormatItemPinBodyCheck.search(line):
#     fileFormatCheckRegexDict[re_fileFormatItemPinBodyCheck] += 1
#     continue
# if re_fileFormatItemBlankCheck.search(line):
#     fileFormatCheckRegexDict[re_fileFormatItemBlankCheck] += 1
#     continue
# if re_fileFormatItemEndCheck.search(line):
#     fileFormatCheckRegexDict[re_fileFormatItemEndCheck] += 1
#     continue
