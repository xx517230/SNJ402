import re

# sub的高级使用，函数替换

# 匹配所有数字，
# 并且将>=6的数字替换成9， 否则替换为0
str = "AB3C9E8A147"


def covert(value):

    # 获取匹配到的字符串的值
    matched = value.group()
    print(matched)
    # 判断逻辑 >=6 则返回字符串9，否则返回字符串0
    if int(matched) >= 6:
        return "9"
    else:
        return "0"


# 将covert函数以参数传入，
# 将sub匹配到的字符串的结果传入covert函数中
replaceStr = re.sub(
    "\d", covert, str
)  # "\d"为需要匹配的字符串，covert为需要执行替换的函数(简单的是自己用相应字符串替换，当简单的字符串无法满足时，可以使用函数来完成这步)，str为需要被操作的字符串

print(replaceStr)
