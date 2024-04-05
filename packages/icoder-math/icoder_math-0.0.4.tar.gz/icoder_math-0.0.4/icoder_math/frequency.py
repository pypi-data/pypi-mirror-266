
def all(data, index,listStatus, totalPeriod):
    """
        data: a list of dict\n
        index: index frequency\n
        listStatus: show list True/False\n
        totalPeriod: if index is not range = 0 else number split\n
        return : f , r , rd(%) , F , R , RD(%) , list=[...]
    """
    if totalPeriod == 0:
        return unPeriod(data, index,listStatus)
    else:
        return period(data, index, totalPeriod,listStatus)


def unPeriod(data, index,listStatus):
    range_list = {}
    total = len(data)
    for item in data:
        if item[index] not in range_list:
            range_list[item[index]] = {}
            range_list[item[index]]["list"] = []
        if listStatus:
            range_list[item[index]]["list"].append(item)
        else:
            range_list[item[index]]["list"]=[]
        range_list[item[index]]["f"] = len(range_list[item[index]]["list"])

    final = {}
    i = 0
    for key, item in range_list.items():
        if i not in final:
            f = item["f"]
            r = float("{:.2f}".format(float(item["f"]) / total))
            rd = int(r * 100)
            if i == 0:
                F = f
                R = r
                RD = rd
            else:
                F = float(final[i - 1]["F"]) + f
                R = float(final[i - 1]["R"]) + r
                RD = int(final[i - 1]["RD"]) + rd

            final[i] = {
                "index": key,
                "f": f,
                "r": r,
                "rd": rd,
                "F": F,
                "R": "{:.2f}".format(R),
                "RD": RD,
                "list": item["list"],
            }
            i += 1

    return final


def period(data, index, totalPeriod,listStatus):
    range_list = range(data, index, totalPeriod)
    total = len(data)
    for key, item in range_list.items():
        minnum = float(item["index"]["min"])
        maxnum = float(item["index"]["max"])
        itemlist = []
        remaining_data = []
        for value in data:
            if float(value[index]) >= minnum and float(value[index]) < maxnum:
                itemlist.append(value)
            else:
                remaining_data.append(value)
        data = remaining_data
        f=len(itemlist)
        r = float("{:.2f}".format(len(itemlist) / total))
        rd=int(r * 100)
        if key ==0 :
            F=f 
            R=r
            RD=rd
        else:
            F = range_list[key - 1]["F"] + f
            R = float(range_list[key - 1]["R"]) + r
            RD = int(range_list[key - 1]["RD"]) + rd
        if listStatus == False:
            itemlist=[]
        range_list[key] = {
            "index": {"min": minnum, "max": maxnum},
            "f": f,
            "r": r,
            "rd": rd,
            "F": F,
            "R": "{:.2f}".format(R),
            "RD": RD,
            "list": itemlist,
        }
    return range_list


def range(data, index, totalPeriod):
    max_num = float(max(data, key=lambda x: float(x[index]))[index])
    min_num = float(min(data, key=lambda x: float(x[index]))[index])
    r = float((max_num + 0.5) - (min_num - 0.5)) / totalPeriod
    i = 0
    range = {}
    current_num = min_num
    next_num = float("{:.2f}".format(current_num + r))
    while i < totalPeriod:
        range[i] = {
            "index": {
                "min": current_num,
                "max": next_num,
            },
            "list": [],
        }
        current_num = next_num
        next_num = float("{:.2f}".format(current_num + r))
        i += 1
    return range


