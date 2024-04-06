# استدعاء المكتبات
def PyPDF2():
    import PyPDF2
    return PyPDF2

def Translator():
    from googletrans import Translator
    from langdetect import detect

    return Translator

def openai():
    import openai

    return openai

def BeautifulSoup():
    from bs4 import BeautifulSoup
    return BeautifulSoup

def requests():
    import requests
    return requests

def time():
    import time
    return time

def os():
    import os
    return os

# global defs
def wait(wait_time: int = 1):
    import time

    time.sleep(wait_time)

def clear():
    """
    مسح الطَّرَفِيَّة
    """

    import os

    os.system("cls")

def detect_lang(text: str, detectOrSrc: int = 0):
    from googletrans import Translator
    from langdetect import detect
    
    try:
        if detectOrSrc == 0: return detect(text)
        else: return Translator().translate(text).src
    except:
        return 404

def rangeNum(num, range_or_while_method = 0):
    """
    ```
    rangeNum(3)

    ==> [0, 1, 2]
    ```
    """
    
    if range_or_while_method == 0:
        return list(range(num))
    else:
        res = []

        i = 0
        while i < num:
            res.append(i)
            i += 1

        return res

# file defs
def filesIn(folder_path: str = "./"):
    import os

    return os.listdir(folder_path)

def rename_file(file_path: str, new_name: str):
    import os

    os.rename(file_path, new_name)

def saveFile(data, file_path: str, encoding: str = "utf-8", save_mode = "w"):
    with open(file_path, save_mode, encoding=encoding) as output_file:
        output_file.write(data)

def readFile(file_path: str, errorAs = 404, errorOnly: int = 0, encoding: str = "utf-8"):
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            data = file.read()
            return data
    except Exception as error:
        if errorOnly == 0:
            return errorAs
        else:
            return error

def readJSON(file_path: str, errorAs = 404, errorOnly: int = 0, encoding: str = "utf-8"):
    import json

    try:
        with open(file_path, 'r', encoding=encoding) as file:
            data = json.load(file)
            return data
    except Exception as error:
        if errorOnly == 0:
            return errorAs
        else:
            return error

def saveJson(data: dict, file_path: str, indent: int = 4, encoding: str = "utf-8", save_mode = "w"):
    import json

    with open(file_path, save_mode, encoding=encoding) as output_file:
        json.dump(data, output_file, indent=indent, ensure_ascii=False)

def savePdf(merger, output_file_path, encoding = "utf-8"):
    with open(output_file_path, "wb", encoding=encoding) as output_file:
        merger.write(output_file)

def copy_file(file_path: str, new_file_path: str = None):
    import shutil

    if new_file_path is None:
        new_file_path = f"{file_path} - Copy"

    shutil.copy(file_path, new_file_path)

def move_file(file_path: str, new_folder_path: str = None):
    """
    دالة لاقتصاص الملف وارساله لمكان آخر\n\n

    مثال
    ------------
    ```
    file_path = "file.txt"
    new_folder_path = "./folder"
    ```
    """

    import shutil

    shutil.move(file_path, new_folder_path)

def delete_file(file_path):
    import os

    os.remove(file_path)

def delete_folder(folder_path):
    import shutil

    shutil.rmtree(folder_path)

# arr defs
def equalArr(arr: list, dimensions: int = 0): # arr1 = arr2
    """
    equalArr
    -----------------
    عند عمل مصفوفة واستنساخها:
    ```
    arr1 = [1, 2, 3]
    arr2 = arr1
    ```
    فإن أي تعديل تقوم به على المصفوفة الثانية يُغيّر أيضا في المصفوفة الأولى،
    ولهذا جاءت هذه الدالة: لتقوم باستنساخ المصفوفة بدون مشاكل، فقط عليك ان تدخل عدد ابعاد المصفوفة\n\n

    والفرق بين هذه الدالة وعمل: arr1.copy()\n
    هو التحكم في عدد الأبعاد التي تريد استنساخها

    ```
    
    ...
    ```

    مثلا:
    ------
    ```
    [1, 2, 3] # هذه المصفوفة لديها بُعد واحد
    [[1], [2], [3], 4] # هذه المصفوفة لديها بُعدان
    ```
    وهكذا\n
    وإذا كنت لا تعرف أبعاد المصفوفة أو تريد استنساخها بالكامل مهما كان عدد أبعادها أدخل صفر

    ```
    
    ...
    ```
    
    مثال:
    -----------
    ```
    arr1 = [1, 2, 3]
    arr2 = equalArr(arr1, 1) # أو equalArr(arr1, 0) إذا كنت تريد استنساخها مهما كان عدد أبعادها

    arr2.append(4) # إضافة رقم 4 للمصفوفة الثانية

    print(arr1) # ==> [1, 2, 3]
    print(arr2) # ==> [1, 2, 3, 4]
    ```
    """
    res = []

    if type(arr) == list:
        if dimensions > 0:
            i = 0
            while i < len(arr):
                if dimensions == 1:
                    res.append(arr[i])
                elif dimensions > 1 and type(arr[i]) == list:
                    res.append([])
                    res[i] = equalArr(arr[i], dimensions-1)
                else: # في حالة الخطأ
                    res.append(arr[i])
                
                i += 1
        else:
            i = 0
            while i < len(arr):
                if type(arr[i]) == list:
                    res.append([])
                    res[i] = equalArr(arr[i], 0)
                else:
                    res.append(arr[i])
                
                i += 1

    return res

def allIndexInArr(arr: list, item): # 1D arr=[10,20,30,40,30], item=30 ==> [2,4]
    """
    ```
    arr = [10, 20, 30, 40, 30]
    item = 30
    
    ==> [2, 4]
    ```
    """

    allIndex = []

    i = 0
    while i < len(arr):
        if arr[i] == item:
            allIndex.append(i)
        i += 1

    return allIndex

def inArr(arr: list, item): # ==> True, False
    """
    ==> True || False
    """

    return item in arr

def onSide(arr: list, item, greater: int = 1, startFrom: bool = 0, multi_items: bool = False, want_items: bool = False): # 2D arr=[1,1,1,3,2,2,2,1,2,2], item=2, greater=1 ==> [ [4,5,6], [8,9] ] ==> [ indexArr ]
    """
    هذه الدالة تقوم بإرجاع اماكن العناصر الموضوعين بجانب بعضهم\n
    arr: المصفوفة\n
    item: العنصر الذي تريده\n
    greater: عدد العناصر التي تريد أن يكونوا بجانب بعضهم + 1 (greater: أكبر)\n
    start_from: مكان البدء (ادخل الفهرس)\n
    multi_items: هل تريد حساب أكثر من عنصر؟\n
    want_items: هل تريد ارجاع العناصر أيضا مع الفهرس؟\n\n

    مثال
    ---------
    ```
    arr=[1,1,1,3,2,2,2,1,2,2]
    item=2
    greater=1
    
    ==> [ [4,5,6], [8,9] ]
    ==> [     الفهرس     ]
    ```
    """

    finalArr = []
    onceArr = []
    finalItemsArr = []
    onceItemsArr = []
    
    i = startFrom
    while i < len(arr):
        if arr[i] == item or (type(item) == list and multi_items == True and (arr[i] in item)):
            onceArr.append(i)
            onceItemsArr.append(arr[i])
        else:
            if len(onceArr) > greater:
                finalArr.append(onceArr)
                finalItemsArr.append(onceItemsArr)

            onceArr = []
            onceItemsArr = []
        i += 1

    if len(onceArr) > greater:
        finalArr.append(onceArr)
        finalItemsArr.append(onceItemsArr)
        
        onceArr = []
        onceItemsArr = []
    

    if want_items == 0:
        return finalArr
    else:
        return [finalItemsArr, finalArr]

def fillArr(arr: list, fill, fromNum: int = -1, toNum: int = -1): # arr=["⬜","⬜","⬜"], fill="🟩", from=0,to=1 ==> ["🟩","🟩","⬜"] #
    """
    ```
    arr = ["⬜","⬜","⬜"]
    fill = "🟩"
    fromNum = 0
    toNum = 1
    ```

    ==> ["🟩","🟩","⬜"]
    """

    arr = equalArr(arr)

    if fromNum == -1:
        fromNum = 0
    if toNum == -1:
        toNum = len(arr)-1

    if fromNum < len(arr) and toNum < len(arr):
        i = fromNum
        while i < toNum+1:
            arr[i] = fill
            i += 1

    return arr

def removeFromArr(arr: list, index: int = -1, txt = "", minusOne: int = 0):
    newArr = []
    i = 0
    if (index > -1) or (index <= -1 and minusOne != 0):
        while i < len(arr):
            if i != index%len(arr):
                newArr.append(arr[i])
            i += 1
    else:
        counter = 0
        while i < len(arr):
            if arr[i] != txt or (arr[i] == txt and counter == 1):
                newArr.append(arr[i])
        
            if counter == 0 and arr[i] == txt:
                counter = 1
            
            i += 1
        
    return newArr

def RemoveDuplicates(arr: list, removeOriginalItem: int = 0, spicificItem: int = -1, item = None):
    arr = equalArr(arr)
    
    i = 0
    continu = 1
    while i < len(arr) and (spicificItem == -1 or (spicificItem != -1 and continu == 1)):
        allInd = []
        if spicificItem == -1:
            allInd = allIndexInArr(arr, arr[i])
        else:
            allInd = allIndexInArr(arr, item)
        
        if len(allInd) > 1:
            e = len(allInd)-1
            while e > 0:
                arr = removeFromArr(arr, allInd[e])
                if spicificItem != -1:
                    continu = 0
                e -= 1
                    
            if removeOriginalItem > 0:
                arr = removeFromArr(arr, allInd[0])
                i -= 1
                    
        i += 1
            
    return arr

def sumArr(arr: list, fromNum: int = -1, toNum: int = -1): # arr=[1,2,3], fromNum=0, toNum=1 ==> 1+2 = 3
    """
    ```
    arr=[1, 2, 3]
    fromNum = 0
    toNum = 1
    
    ==> 1+2 = 3
    ```
    """
    
    sum = 0
    if fromNum > -1 and toNum > -1:
        toNum += 1
    elif fromNum > -1 and toNum < 0:
        toNum = len(arr)
    elif fromNum < 0 and toNum < 0:
        fromNum = 0
        toNum = len(arr)
        
    while fromNum < toNum:
        sum += arr[fromNum]
        fromNum += 1
    
    return sum

def minusArr(arr: list): # [1,4,5,8,7] ==> [3,1,3,-1]
    """
    ```
    arr = [1, 4, 5, 8, 7]
    
    ==> [3, 1, 3, -1]
    ```
    """

    res = []

    i = 1
    while i < len(arr):
        res.append(arr[i] - arr[i-1])
        i += 1
    
    return res

def makeColumnArr(arr: list, column: int = 0): # convert column in 2D arr to arr
    """
    تحويل العمود في المصفوفة ثنائية الأبعاد إلى مصفوفة منفصلة
    """
    
    arrLen = len(arr)
    columnArr = []

    i = 0
    while i < arrLen:
        if column < len(arr[i]): columnArr.append(arr[i][column])
        i += 1

    return columnArr

def convertRowToCol(arr: list, columnArr: list, column: int = 0): # Col ==> column, columnArr ==> row
    """
    تحويل المصفوفة أحادية الأبعاد إلى عمود في مصفوفة ثنائية الأبعاد
    """
    
    i = 0
    while i < len(columnArr):
        arr[i][column] = columnArr[i]
        i += 1
    
    return arr

def addArr(fromArr: list, toArr: list): # fromArr=[4,5,6], toArr=[1,2,3] ==> [1,2,3,4,5,6]
    """
    إضافة مصفوفة إلى أخرى\n

    مثال
    -------
    ```
    fromArr=[4, 5, 6]
    toArr=[1, 2, 3]
    
    ==> [1, 2, 3, 4, 5, 6]
    ```
    """
    
    toArr = equalArr(toArr)
    for x in fromArr:
        toArr.append(x)

    return toArr

def delArr(smallArr: list, bigArr: list): # smallArr = [4,5,6], bigArr=[1,2,3,4,5,6] ==> [1,2,3]
    """
    إلغاء مصفوفة من أخرى\n

    مثال
    ------------
    ```
    smallArr = [4,5,6]
    bigArr=[1,2,3,4,5,6]
    
    ==> [1,2,3]
    ```
    """
    
    smallArr = equalArr(smallArr)
    bigArr = equalArr(bigArr)

    for x in smallArr:
        if inArr(bigArr, x):
            bigArr = removeFromArr(bigArr, -1, x)
    
    return bigArr

def sliceArr(arr: list, fromNum: int = 0, toNum: int = 0): # arr=[10,20,30,40,50], fromNum=1, toNum=3 ==> [20,30,40]
    """
    ```
    arr = [10, 20, 30, 40, 50]
    fromNum = 1
    toNum = 3
    
    ==> [20, 30, 40]
    ```
    """
    
    newArr = []

    i = fromNum
    while i <= toNum:
        newArr.append(arr[i])
        i += 1
    
    return newArr

def reverseArr(arr: list): # arr=[1,2,3] ==> [3,2,1]
    """
    عكس المصفوفة

    مثال
    ---------
    ```
    arr=[1, 2, 3]
    
    ==> [3, 2, 1]
    ```
    """

    return arr[::-1]

def search2D(arr: list, item, column: int = 0): # ==> [index]
    """
    البحث عن عنصر في مصفوفة ثنائية الأبعاد عن طريق العمود
    """

    res = []
    ind = []

    i = 0
    while i < len(arr):
        if arr[i][column] == item:
            res.append(arr[i])
            ind.append(i)
        i += 1

    return [res, ind]

def convert2D(arr: list): # ==> 1D, convert 2D to 1D, arr=[ [1,2,3], [4,5,6], [7,8,9] ] ==> [1,2,3,4,5,6,7,8,9]
    """
    تحويل المصفوفة ثنائية الأبعاد إلى أحادية الأبعاد\n

    مثال
    -----------
    ```
    arr=[ [1,2,3], [4,5,6], [7,8,9] ]
    
    ==> [1,2,3,4,5,6,7,8,9]
    ```
    """

    newArr = []

    i = 0
    while i < len(arr):
        if type(arr[i]) == list:
            e = 0
            while e < len(arr[i]):
                newArr.append(arr[i][e])
                e += 1
        else:
            newArr.append(arr[i])
        i += 1

    return newArr

def rotate2DArr(arr: list, numR: int = 1): # numR ==> num of right turns
    arr = equalArr(arr, 2)
    
    a = 0
    while a < numR:
        res = []

        i = 0
        while i < len(arr[0]):
            res.append(makeColumnArr(arr, i)[::-1])
            i += 1
        
        arr = res
        a += 1
    
    return arr

def insertInArr(arr: list, itemToInsert, itemIndex: int = 0, isMultiItems: int = 0): # arr=[1,3,4], itemToInsert=2 ==> [1,2,3,4]
    """
    ```
    arr=[1,3,4]
    itemToInsert = 2
    itemIndex = 1

    ==> [1,2,3,4]
    ```
    """

    arr = equalArr(arr)
    res = []

    i = 0
    while i < len(arr):
        if i == itemIndex:
            if isMultiItems == 0: res.append(itemToInsert)
            elif type(itemToInsert) == list:
                e = 0
                while e < len(itemToInsert):
                    res.append(itemToInsert[e])
                    e += 1
        res.append(arr[i])
        i += 1

    return res

def convertTxt(text: str): # convert text to code, "5 + 7" ==> 12
    """
    تحويل النص لشيفرة\n

    مثال
    -----------------
    ```
    "5 + 7" ==> 12
    ```
    """
    
    try:
        return eval(text)
    except Exception as e:
        print("حدث خطأ في التحويل:", e)
        return None

def searchIn_decodeNum(arr: list, search_key, equalOrContain: int = 0): # arr=["n1", "o1", "n2"], search_key="n" ==> [0, 2] => [index]
    """
    ```
    arr=["n1", "o1", "n2"]
    search_key = "n"
    
    ==> [0, 2]
    ==> [فهرس]
    ```
    """
    
    arr = equalArr(arr)
    result = []
    
    newArr = []
    i = 0
    while i < len(arr):
        newArr.append(decodeNum(arr[i]))
        for index, item in enumerate(newArr[i]):
            newArr[i][index] = str(item)

        if (equalOrContain == 0 and search_key in newArr[i]) or (equalOrContain == 1 and search_key in "".join(newArr[i])):
            result.append(i)
        i += 1

    return result

def searchInObjArr(arr: list, key_want_search: str, value_want_search): # [ {"id": 1, "num": 453}, {"id": 2, "num": 734} ], id == 1 ==> [  [ {"id": 1, "num": 453} ], [0]  ]
    """
    ```
    [ {"id": 1, "num": 453}, {"id": 2, "num": 734} ]
    key_want_search = "id"
    value_want_search = 1
    
    ==> [  [ {"id": 1, "num": 453} ], [0]  ]
    ```
    """

    res = []
    ind = []
    for i, item in enumerate(arr):
        if type(item) == dict:
            if key_want_search in item:
                if item[key_want_search] == value_want_search:
                    res.append(item)
                    ind.append(i)
    
    return [res, ind]

# object {} defs
def equalObject(the_object: dict, dimensions: int = 0): # the_object1 = the_object2
    """
    equalObject
    -----------------
    عند عمل قاموس واستنساخه:
    ```
    obj1 = {"number": 1}
    obj2 = obj1
    ```
    فإن أي تعديل تقوم به على القاموس الثاني يُغيّر أيضا في القاموس الأول،
    ولهذا جاءت هذه الدالة: لتقوم باستنساخ القاموس بدون مشاكل، فقط عليك ان تدخل عدد ابعاد القاموس\n\n

    والفرق بين هذه الدالة وعمل: obj1.copy()\n
    هو التحكم في عدد الأبعاد التي تريد استنساخها

    ```
    
    ...
    ```

    مثلا:
    ------
    ```
    {"number": 1} # هذا القاموس لديه بُعد واحد
    {"number": {"number2": 2}} # هذا القاموس لديه بُعدان
    ```
    وهكذا\n
    وإذا كنت لا تعرف أبعاد القاموس أو تريد استنساخه بالكامل مهما كان عدد أبعاده أدخل صفر

    ```
    
    ...
    ```
    
    مثال:
    -----------
    ```
    obj1 = {"numbers":  {"n1": 1, "n2": 2, "n3": 3}  } # القاموس الأول لديه بُعدان
    obj2 = equalObject(obj1, 2) # أو equalObject(obj1, 0) إذا كنت تريد استنساخه مهما كان عدد أبعاده

    obj2["numbers"]["n4"] = 4 # إضافة رقم 4 للقاموس الثاني

    print(obj1) # ==> {"numbers": {"n1": 1, "n2": 2, "n3": 3}}
    print(obj2) # ==> {"numbers": {"n1": 1, "n2": 2, "n3": 3, 4}}
    ```
    """
    
    res = {}
    if type(the_object) == dict:
        if dimensions > 0:
            for key in the_object:
                item = the_object[key]
                if dimensions == 1:
                    res[key] = item
                elif dimensions > 1 and type(item) == dict:
                    res[key] = equalObject(item, dimensions-1)
                else: # في حالة الخطأ
                    res[key] = item
        else:
            for key in the_object:
                item = the_object[key]
                if type(item) == dict:
                    res[key] = equalObject(item, 0)
                else:
                    res[key] = item                

    return res

def getObjectKeys(the_object: dict): # {"h1": "text", "h2": "text2"} ==> ["h1", "h2"]
    """
    ```
    the_object = {"h1": "text", "h2": "text2"}
    
    ==> ["h1", "h2"]
    ```
    """
    
    keys = []
    for key in the_object:
        keys.append(key)
    
    return keys

def addToObject(the_object: dict, key: str, want_to_add): # {"name": "about"}, "name", "about" ==> {"name": "about", "name 2": "about"}
    """
    ```
    the_object = {"name": "about"}
    key = "name"
    value = "about"
    
    ==> {"name": "about", "name 2": "about"}
    ```
    """

    the_object = equalObject(the_object)
    if len(searchIn_decodeNum(getObjectKeys(the_object), key, 1)) > 0:
        the_object[f"{key} {len(searchIn_decodeNum(getObjectKeys(the_object), key, 1))+1}"] = want_to_add
    else:
        the_object[key] = want_to_add

    return the_object

def key_index(the_object: dict, key: str):
    """
    مثال
    -----------
    ```
    the_object = {"number 1": 10, "number 2": 20, "number 3": 30}
    key = "number 3"

    ==> 2
    ```
    
    مثال 2
    -----------
    ```
    the_object = {"number 1": 10, "number 2": 20, "number 3": 30}
    key = "number 5"

    ==> -1
    ```
    """
    
    if key in the_object:
        for i, item in enumerate(the_object.keys()):
            if key == item:
                return i
    else:
        return -1

def delete_key(the_object: dict, key: str): # {"n1":10, "n2":20, "n3":30}, key = "n1" ==> {"n2":20, "n3":30}
    """
    مثال
    ----------
    ```
    the_object = {"number 1": 10, "number 2": 20, "number 3": 30}
    key = "number 1"
    ==> {"number 2": 20, "number 3": 30}\n\n
    ```

    مثال 2
    ----------
    ```
    the_object = {"number 1": 10, "number 2": 20, "number 3": 30}
    key = ["number 1", "number 2"]
    ==> {"number 3": 30}
    ```
    """

    the_object = equalObject(the_object)

    if type(key) == str:
        if key in the_object: the_object.pop(key)
    elif type(key) == list:
        for item in key:
            the_object = delete_key(the_object, item)

    return the_object

def insert_key(the_object: dict, i: int, key: str, value = None, change_value: bool = False):
    """
    مثال
    -----------
    ```
    the_object = {"num1": 10, "num3": 30}
    i = 1
    key = "num2"
    value = 20

    ==> {"num1": 10, "num2": 20, "num3": 30}
    ```

    مثال 2
    -----------
    ```
    the_object = {"num1": 10, "num3": 30, "num2": 20}
    i = 1
    key = "num2"

    ==> {"num1": 10, "num2": 20, "num3": 30}
    ```

    مثال 3
    -----------
    ```
    the_object = {"num1": 10, "num3": 30, "num2": 50}
    i = 1
    key = "num2"
    value = 20
    change_value = True

    ==> {"num1": 10, "num2": 20, "num3": 30}
    ```
    """

    tmp_list = list(the_object.items())
    if change_value and key in the_object:
        tmp_list.remove((key, the_object[key]))

    return {**dict(tmp_list[:i]), key: value, **dict(tmp_list[i:])}

def change_key(the_object: dict, old_key: str, new_key: str): # {"number 1": 10, "number 5": 20, "number 3": 30}, "number 5", "number 2" ==> {"number 1": 10, "number 2": 20, "number 3": 30} #
    """
    ```
    the_object = {"number 1": 10, "number 5": 20, "number 3": 30}
    old_key = "number 5"
    new_key = "number 2"

    ==> {"number 1": 10, "number 2": 20, "number 3": 30}
    ```
    """

    the_object = equalObject(the_object)

    if old_key in the_object and new_key not in the_object:
        value = the_object[old_key]
        key_ind = key_index(the_object, old_key)

        the_object = delete_key(the_object, old_key)
        the_object = insert_key(the_object, key_ind, new_key, value)
    
    return the_object

# json defs
def combine_json_files(files_names: list, output_file_path: str, indent: int = 4, encoding: str = "utf-8"):
    combined_data = {}

    # قراءة محتوى كل ملف وإضافة المعلومات إلى القاموس
    for file_name in files_names:
        data = readFile(file_name, encoding)
        combined_data.update(data)

    # حفظ الملف
    saveJson(combined_data, output_file_path, indent, encoding)

def uncombine_json_file(combined_file_path: str, indent: int = 4, encoding: str = "utf-8", files: str = 'f"{key}.json"'):
    # قراءة الملف
    combined_data = readFile(combined_file_path, encoding)

    # حفظ الملفات
    for key in combined_data:
        saveJson({key:combined_data[key]}, eval(files), indent, encoding)

# pdf defs
def combine_pdf_files(files_names: list, output_file_path: str, encoding: str = "utf-8"):
    import PyPDF2

    merger = PyPDF2.PdfMerger()

    for pdf in files_names:
        merger.append(pdf)

    savePdf(merger, output_file_path, encoding)

# text defs
def decodeNum(text: str): # r2 ==> ["r", 2]
    res = []
    tmp = ""
    nums = "0123456789"

    i = 0
    while i < len(text)-1:
        tmp += text[i]
        if text[i] not in nums:
            if text[i+1] in nums:
                res.append(tmp)
                tmp = ""
        else:
            if text[i+1] not in nums:
                res.append(int(tmp))
                tmp = ""
        i += 1

    tmp += text[i]
    if text[i] in nums: res.append(int(tmp))
    if text[i] not in nums: res.append(tmp)
    tmp = ""

    return res

def right(text: str, amount: int):
    return text[-amount:]

def left(text: str, amount: int):
    return text[:amount]

def mid(text: str, offset: int, amount: int):
    return text[offset:offset+amount]

def split(text: str, splitter: str | list[str] = ""):
    """
    هذه الدالة تقسم النص
    """
    
    res = []
    if splitter == "":
        for char in text:
            res.append(char)
    else:
        if type(splitter) == str:
            res = text.split(splitter)
        elif type(splitter) == list:
            if splitter == []:
                res = text
            else:
                for splitter_item in splitter:
                    if res == []:
                        res.append(split(text, splitter_item))
                    else:
                        res_len = len(res)
                        res_i = res_len-1
                        while res_i >= 0:
                            res = convert2D(res)
                            res_item = res[res_i]

                            res[res_i] = split(res_item, splitter_item)
                            res = convert2D(res)

                            res_i -= 1

    return res

def removeSpaces(text: str): # إلغاء   المسافات
    """
    إلغاء   المسافات
    """
    
    text = " ".join(RemoveDuplicates(text.split(" "), 1, 1, ""))
    text = " ".join(removeFromArr(text.split(" "), -1, ""))
    return text.strip()

def replaceText(text: str, replArr: list): # text = "hello word!", replArr = [ ["word", "world"], ["!", "."] ] ==> "hello world."
    """
    ```
    text = "hello word!"
    replArr = [ ["word", "world"], ["!", "."] ]
    ```
    \n\n
    ==> "hello world."
    """
    
    i = 0
    while i < len(replArr):
        text = text.replace(replArr[i][0], replArr[i][1])
        i += 1

    return text

# num defs
def makeZeroNum(num: str | int, cells_num: int = 3, zero: str = "0"):
    """
    num = "10"
    cells_num = 4
    ==> "0010"
    """

    num = str(num)
    if cells_num > len(num):
        for item in rangeNum(cells_num - len(num)):
            num = zero + num
    
    return num

# separate defs
def separate_text(text: str, splitter: list = ["."], joiner: str = "\n", stripping: str = 0, delete_splitter: int = 0): # "line1.line2" ==> "line1.\nline2"
    """
    text = "line1.line2"
    splitter = ["."] # بعد النقطة ضع سطرًا جديدًا
    joiner = "\n"

    ==> "line1.\nline2"
    """
    
    if type(splitter) == list:
        for item in splitter:
            tmp = text.split(item)
            if stripping == 1:
                for tmp_i, tmpItem in enumerate(tmp): tmp[tmp_i] = tmpItem.strip()
            
            if delete_splitter == 0: text = f"{item}{joiner}".join(tmp)
            else: text = joiner.join(tmp)
    else:
        tmp = text.split(str(splitter))
        if stripping == 1:
            for tmp_i, tmpItem in enumerate(tmp): tmp[tmp_i] = tmpItem.strip()
        
        if delete_splitter == 0: text = f"{splitter}{joiner}".join(tmp)
        else: text = joiner.join(tmp)
    
    return text

def separate_arr(arr: list, splitter: list = ["."], joiner: str = "\n", stripping: str = 0, delete_splitter: int = 0):
    new_arr = []

    for item in arr:
        if type(item) == str:
            new_arr.append(separate_text(item, splitter, joiner, stripping, delete_splitter))
        elif type(item) == list:
            new_arr.append(separate_arr(item, splitter, joiner, stripping))
        elif type(item) == dict:
            new_arr.append(separate_obj(item, splitter, joiner, stripping))
        else:
            new_arr.append(item)
    
    return new_arr

def separate_obj(obj: dict, splitter: list = ["."], joiner: str = "\n", stripping: int = 0, delete_splitter: int = 0):
    new_obj = {}

    for key in obj:
        item = obj[key]
        if type(item) == str:
            new_obj[key] = separate_text(item, splitter, joiner, stripping, delete_splitter)
        elif type(item) == list:
            new_obj[key] = separate_arr(item, splitter, joiner, stripping)
        elif type(item) == dict:
            new_obj[key] = separate_obj(item, splitter, joiner, stripping)
        else:
            new_obj[key] = item
    
    return new_obj

# translate defs
def translate_text(text, target_language: str ="en", not_langs: list = [], detectOrSrc: int = 0):
    from googletrans import Translator
    from langdetect import detect
    
    translator = Translator()

    if not_langs == []:
        if text:
            textArr = []
            for i in text.split("\n"):
                if i != "":
                    tmp = ""
                    try:
                        tmp = translator.translate(i, dest=target_language)
                        textArr.append(tmp.text)
                    except:
                        tmp = i
                        textArr.append(tmp)

            translation = "\n".join(textArr)
            return translation
    else:
        sentences = text.split(" ")
    
        fullArr = []
        fullArrInd = []
        tmpArr = []
        tmpInd = -1
        # ["hello", "اهلا"] ==> fullArr = [ ["hello"] ], fullArrInd = [ 0 ]
        detected_language = ""
        for i, item in enumerate(sentences):
            detected_language = detect_lang(item, detectOrSrc)
            if detected_language != 404:
                if detected_language not in not_langs:
                    tmpArr.append(item)
                    if tmpInd == -1: tmpInd = i
                elif i != 0 and len(tmpArr) > 0:
                    fullArr.append(tmpArr)
                    fullArrInd.append(tmpInd)
                    tmpArr = []
                    tmpInd = -1
            else:
                fullArr.append(item)
                fullArrInd.append(i)
                tmpArr = []
                tmpInd = -1
                detected_language = ""
        if detected_language not in not_langs and len(tmpArr) > 0:
            fullArr.append(tmpArr)
            fullArrInd.append(tmpInd)
            tmpArr = []
            tmpInd = -1
        
        for i, item in enumerate(fullArr):
            i = len(fullArr)-i-1
            for e in range(len(fullArr[i])):
                sentences = removeFromArr(sentences, fullArrInd[i])
            sentences.insert(fullArrInd[i], fullArr[i])

        for i, item in enumerate(sentences):
            if type(item) == list:
                tmpTransText = " ".join(item)
                tmpTrans = ""
                try: tmpTrans = translator.translate(tmpTransText, dest=target_language).text
                except: tmpTrans = tmpTransText
                sentences[i] = tmpTrans

        text = " ".join(sentences)
    
    return text

def translate_arr(arr, target_language: str ="en", not_langs: list = []):
    newArr = []
    for item in arr:
        if type(item) == str:
            newArr.append(translate_text(item, target_language, not_langs))
        elif type(item) == dict: # dict ==> {}
            newArr.append(translate_obj(item, target_language, not_langs))
        elif type(item) == list: # list ==> []
            newArr.append(translate_arr(item, target_language, not_langs))
        else:
            newArr.append(item)
        
    return newArr

def translate_obj(obj: dict, target_language: str = "en", not_langs: list = []):
    new_obj = {}

    for i in obj:
        if type(obj[i]) == str:
            new_obj[translate_text(i, target_language, not_langs)] = translate_text(obj[i], target_language, not_langs)
        elif type(obj[i]) == dict: # dict ==> {}
            new_obj[translate_text(i, target_language, not_langs)] = translate_obj(obj[i], target_language, not_langs)
        elif type(obj[i]) == list: # list ==> []
            new_obj[translate_text(i, target_language, not_langs)] = translate_arr(obj[i], target_language, not_langs)
        else:
            new_obj[translate_text(i, target_language, not_langs)] = obj[i]

    return new_obj

# decode html
def decode_html_in_text(text: str, tag: str = "img", attribute: str = "src", endTag: int = 0, delete_inner_html: int = 0):
    """
    مثال:
    --------------
    ```
    text = '<img src="the_link.com">'
    tag = "img"
    attribute = "src"
    endTag = 0
    delete_inner_html = 0 | 1
    ```

    ...\n
    النتيجة:
    ---
    the_link.com
    """

    import re

    if attribute != "":
        check = rf'<{tag} .*?{attribute}="([^"]*)".*?>'
        if endTag == 1: check += rf'.*?</{tag}>'
    else: # inner html
        check = rf'<{tag}.*?>'
        if delete_inner_html == 0:
            check += rf'([^"]*)'
        elif endTag == 1:
            check += rf'.*?'
        if endTag == 1: check += rf'</{tag}>'

    return re.sub(check, r"\1", text)

def decode_html_in_arr(arr: list, tag: str = "img", attribute: str = "src", endTag: int = 0, delete_inner_html: int = 0):
    newArr = []
    for item in arr:
        if type(item) == list:
            newArr.append(decode_html_in_arr(item, tag, attribute, endTag, delete_inner_html))
        elif type(item) == dict:
            newArr.append(decode_html_in_obj(item, tag, attribute, endTag, delete_inner_html))
        elif type(item) == str:
            newArr.append(decode_html_in_text(item, tag, attribute, endTag, delete_inner_html))
        else:
            newArr.append(item)

    return newArr

def decode_html_in_obj(obj: dict, tag: str = "img", attribute: str = "src", endTag: int = 0, delete_inner_html: int = 0):
    newObj = {}
    for key in obj:
        item = obj[key]
        if type(item) == list:
            newObj[key] = decode_html_in_arr(item, tag, attribute, endTag, delete_inner_html)
        elif type(item) == dict:
            newObj[key] = decode_html_in_obj(item, tag, attribute, endTag, delete_inner_html)
        elif type(item) == str:
            newObj[key] = decode_html_in_text(item, tag, attribute, endTag, delete_inner_html)
        else:
            newObj[key] = item
    
    return newObj

# keyboard defs
def write(text: str, delay: float = 0, restore_state_after: bool = True, exact: bool | None = None):
    import keyboard

    keyboard.write(text, delay, restore_state_after, exact)

def press(hot_key):
    import keyboard

    keyboard.press(hot_key)

def unpress(hot_key):
    import keyboard

    keyboard.release(hot_key)

# mouse defs
def getMousePosition():
    import mouse

    return [mouse.get_position()[0], mouse.get_position()[1]]

def getMousePositions(saveKey: str ="g", breakKey: str ="0"):
    import keyboard

    all = []

    while True:
        if keyboard.is_pressed(saveKey):
            mouse_position = getMousePosition()
            item = input("what is it?\n")
            all.append([ item, mouse_position ])

        if keyboard.is_pressed(breakKey):
            break

    return all

def click():
    import mouse

    mouse.click()

def right_click():
    import mouse

    mouse.right_click()

def move(x: int, y: int, absolute: bool = True, duration: int = 0):
    import mouse

    mouse.move(x, y, absolute, duration)

# chatGPT
def chatGPT(user_question: str, api_key: str):
    import openai

    openai.api_key = api_key

    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {
                "role": "user",
                "content": user_question
            }
        ]
    )

    answer = response["choices"][0]["message"]["content"]
    return answer

# soup
def get_soup(link: str, wait: int = 0):
    from bs4 import BeautifulSoup
    import requests
    import time

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    with requests.Session() as session:
        try:
            result = session.get(link, headers=headers, timeout=10)
            time.sleep(wait)
            result.raise_for_status()  # رفع استثناء إذا كان هناك خطأ في الاستجابة
            src = result.content
            soup = BeautifulSoup(src, "lxml")
            return soup
        except requests.exceptions.RequestException as e:
            # print(f"Error: {e}")
            return None

def get_redirected_url(link: str): # bit.ly ==> link
    import requests

    # إجراء طلب GET للحصول على الصفحة الأولى
    response = requests.get(link)

    # التحقق من وجود عملية تحويل
    if response.history:
        # الحصول على الرابط النهائي بعد التحويل
        final_url = response.url
        return final_url
    else:
        return link

def innerText(item):
    return item.text

def innerHTML(item):
    return "".join(map(str, item.contents))

# selenium
def makeFirefoxDriver():
    from selenium import webdriver
    from selenium.webdriver.common.by import By

    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox()

    return driver

def driverToSoup(driver):
    from bs4 import BeautifulSoup

    return BeautifulSoup(driver.page_source, "html.parser")

# dataURL
def imageLink_to_dataurl(image_url, extension = "png", error = 404):
    import base64
    import requests

    # تنزيل الصورة من الرابط
    response = requests.get(image_url)
    
    # التحقق من أن الاستجابة صحيحة
    if response.status_code == 200:
        data_url = f'data:image/{extension};base64,' + base64.b64encode(response.content).decode('utf-8')
        return data_url
    else:
        return error

def videoFile_to_dataurl(video_path, error = 404):
    import base64

    try:
        # قراءة ملف الفيديو كتسلسل بيانات
        with open(video_path, "rb") as video_file:
            video_data = video_file.read()

        # تحويل التسلسل إلى base64
        video_base64 = base64.b64encode(video_data)

        # إنشاء Data URL
        data_url = "data:video/mp4;base64," + video_base64.decode('utf-8')

        return data_url
    except:
        return error

# done message
def doneMessage(want_clear: int = 1):
    if want_clear > 0: clear()
    print("Done.. Alhamdulillah")