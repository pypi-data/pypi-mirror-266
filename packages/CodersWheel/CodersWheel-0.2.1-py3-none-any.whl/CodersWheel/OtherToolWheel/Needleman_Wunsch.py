# coding=utf8


def Needleman_Wunsch(l1, l2, empty_slot='-'):
    if not l1:
        return 'l1 is empty list'
    elif not l2:
        return 'l2 is empty list'
    else:
        pass

    m = len(l1)
    n = len(l2)
    # 初始化
    lcs = [[i * (-2)] for i in range(0, m + 1)]
    lcs[0] = [j * (-2) for j in range(0, n + 1)]
    #
    for i in range(m):
        for j in range(n):
            lcs[i + 1].append(
                max(lcs[i][j] + (1 if l1[i] == l1[j] else -1), lcs[i][j + 1] - 2, lcs[i + 1][j] - 2, ))

    i = m - 1
    j = n - 1
    common_l1 = []
    common_l2 = []
    common_l1.insert(0, l1[i])
    common_l2.insert(0, l2[j])

    while 1:
        if i == 0 and j == 0:
            break
        if l1[i] == l2[j]:
            if lcs[i - 1][j - 1] + 1 > lcs[i - 1][j] - 2 and lcs[i - 1][j - 1] + 1 > lcs[i][j - 1] - 2:
                i = i - 1
                j = j - 1
                common_l1.insert(0, l1[i])
                common_l2.insert(0, l2[j])
                print(1)
            else:
                if lcs[i][j + 1] > lcs[i + 1][j]:
                    i = i - 1
                    common_l1.insert(0, l1[i])
                    common_l2.insert(0, empty_slot)
                    # common_l1 = u"%s%s" % (l1[i], common_l1)
                    # common_l2 = u"%s%s" % ('-', common_l2)

                else:
                    j = j - 1
                    common_l1.insert(0, empty_slot)
                    common_l2.insert(0, l2[j])
                    # common_l1 = u"%s%s" % ('-', common_l1)
                    # common_l2 = u"%s%s" % (l2[j], common_l2)

        else:
            if lcs[i - 1][j - 1] + 1 > lcs[i - 1][j] - 2 and lcs[i - 1][j - 1] + 1 > lcs[i][j - 1] - 2:
                i = i - 1
                j = j - 1
                common_l1.insert(0, l1[i])
                common_l2.insert(0, l2[j])
                # common_l1 = u"%s%s" % (l1[i], common_l1)
                # common_l2 = u"%s%s" % (l2[j], common_l2)

            else:
                if lcs[i][j + 1] > lcs[i + 1][j]:
                    i = i - 1
                    common_l1.insert(0, l1[i])
                    common_l2.insert(0, empty_slot)
                    # common_l1 = u"%s%s" % (l1[i], common_l1)
                    # common_l2 = u"%s%s" % ('-', common_l2)

                else:
                    j = j - 1
                    common_l1.insert(0, empty_slot)
                    common_l2.insert(0, l2[j])
                    # common_l1 = u"%s%s" % ('-', common_l1)
                    # common_l2 = u"%s%s" % (l2[j], common_l2)
    return common_l1, common_l2


def Needleman_Wunsch_others(str1, str2):
    # 字符串为空则返回
    if str1 == '' or str2 == '':
        return ''
    # 字符串长度
    m = len(str1)
    n = len(str2)
    # 初始化
    lcs = [[i * (-2)] for i in range(0, m + 1)]
    lcs[0] = [j * (-2) for j in range(0, n + 1)]
    #
    for i in range(m):
        for j in range(n):
            lcs[i + 1].append(
                max(lcs[i][j] + (1 if str1[i] == str2[j] else -1), lcs[i][j + 1] - 2, lcs[i + 1][j] - 2, )
            )
    # for i in range(m+1):
    # print lcs[i]
    i = m - 1
    j = n - 1
    common_substr1 = u''
    common_substr2 = u''
    common_substr1 = u"%s%s" % (str1[i], common_substr1)
    common_substr2 = u"%s%s" % (str2[j], common_substr2)
    # 回溯
    while True:
        if i == 0 and j == 0:
            break
        if str1[i] == str2[j]:
            if lcs[i - 1][j - 1] + 1 > lcs[i - 1][j] - 2 and lcs[i - 1][j - 1] + 1 > lcs[i][j - 1] - 2:
                i = i - 1
                j = j - 1
                common_substr1 = u"%s%s" % (str1[i], common_substr1)
                common_substr2 = u"%s%s" % (str2[j], common_substr2)
                print(1)
            else:
                if lcs[i][j + 1] > lcs[i + 1][j]:
                    i = i - 1
                    common_substr1 = u"%s%s" % (str1[i], common_substr1)
                    common_substr2 = u"%s%s" % ('-', common_substr2)

                else:
                    j = j - 1
                    common_substr1 = u"%s%s" % ('-', common_substr1)
                    common_substr2 = u"%s%s" % (str2[j], common_substr2)

        else:
            if lcs[i - 1][j - 1] + 1 > lcs[i - 1][j] - 2 and lcs[i - 1][j - 1] + 1 > lcs[i][j - 1] - 2:
                i = i - 1
                j = j - 1
                common_substr1 = u"%s%s" % (str1[i], common_substr1)
                common_substr2 = u"%s%s" % (str2[j], common_substr2)

            else:
                if lcs[i][j + 1] > lcs[i + 1][j]:
                    i = i - 1
                    common_substr1 = u"%s%s" % (str1[i], common_substr1)
                    common_substr2 = u"%s%s" % ('-', common_substr2)

                else:
                    j = j - 1
                    common_substr1 = u"%s%s" % ('-', common_substr1)
                    common_substr2 = u"%s%s" % (str2[j], common_substr2)
    return common_substr1, common_substr2


if __name__ == '__main__':
    print(Needleman_Wunsch("AGCACACA", "ACACTA"))
    pass
