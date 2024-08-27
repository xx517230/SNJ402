def regexCnt(line, regexList, regexDict):
    for regex in regexList:
        if regex.search(line):
            regexDict[regex] += 1
            return True
    return False


def check_vcd_file(file, fileFormatCheckRegexDict):
    with open(file, "r") as fp:
        for lineCnt, line in enumerate(fp, start=1):
            if not regexCnt(
                line, fileFormatCheckRegexDict.keys(), fileFormatCheckRegexDict
            ):
                print(f"行{lineCnt}: 行格式不符合要求，请检查")
                return False
    headCnt = 0
    for i in range(len(fileFormatCheckRegexDict)):
        if i:
            headCnt += fileFormatCheckRegexDict[
                list(fileFormatCheckRegexDict.keys())[i]
            ]
    print(f"vcd头共有{headCnt}行")
    for regex, cnt in fileFormatCheckRegexDict.items():
        print(f"{regex}: {cnt} 行")

    return True
