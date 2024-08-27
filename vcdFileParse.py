def vcdFileParse(file, regexList):

    with open(file, "r") as fp:
        # 跳过无效行，但到达0时刻位置，获取pattern及注释
        for lineCnt, line in enumerate(fp, start=1):
            if regexList[1].search(line):
                pattern = regexList[1].search(line).group(1)
                comment = regexList[1].search(line).group(0)

                break
        for lineCnt, line in enumerate(fp, start=lineCnt + 1):
            print(line, lineCnt)
            break
