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
                comment = regexList[1].search(line).group(0)
                break
        outputFp.write(header)
        for lineCnt, line in enumerate(fp, start=lineCnt + 1):
            match = regexList[0].search(line)
            if match:
                timeStrOld = timeStr
                timeStr = match.group(1)
                pattern = match.group(2)
                comment = match.group(3)
                time = int(timeStr) - int(timeStrOld)  # nS
                outputFp.write(" *")
                outputFp.write(pattern)
                outputFp.write(f"* RPT {time}; {comment}")
                outputFp.write("\n")
                continue
            print(
                f"{file}文件 {lineCnt}行不满足正则条件,按理校验通过文件不应该出现该提示"
            )
