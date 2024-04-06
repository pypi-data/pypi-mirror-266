from __future__ import annotations
from dataclasses import field
from multiprocessing.sharedctypes import Value
from typing import Dict, List, Union
from copy import deepcopy
import re


def user_opts_handler(obj: dict):
    stack = []
    for key, value in obj.items():
        stack.append((key, value))

    def getNext():
        path, data = stack.pop()
        return path, data

    def pushData(start_path: str, newData: dict):
        for key, value in newData.items():
            stack.append((f"{start_path}.{key}", value))

    def shouldStop():
        return len(stack) <= 0

    return getNext, pushData, shouldStop

def base_opt_handler(opts: dict):
    base_opts = deepcopy(opts)
    
    def pathGet(dictionary: dict, path: str):
        #按照[ . ]切割字符串，因为会有空值和数字字符串，要进行一下判断
        if ']' not in path:
            path = re.sub(r'([^.]+)', r'\1'+'[0]', path, count=1)
        path_list = re.split('[\[,\],.]',path)

        try:
            path_list.remove('')
        except ValueError:
            pass

        len_path_list = len(path_list)

        for num, item in enumerate(path_list):
            if item.isdigit():
                item = int(item)
            if num == len_path_list - 1:
                dictionary_last = dictionary
            try:
                dictionary = dictionary[item]
            except KeyError:
                return False, dictionary, item
                
        return True, dictionary_last, item

    def try_update(path: str, data):
        dictionary = base_opts
        isdict, dictionary, item = pathGet(dictionary, path)
        #如果路径不存在 或 存在，但是data不是一个字典，直接新增，返回True
        
        if not isinstance(data, dict):
            dictionary[item] = data
            return True
        #如果路径存在，且data是字典，则不更新，返回False
        else:
            if isdict:
                return False
            else:
                dictionary[item] = data
                return True
    def get_opts():
        return base_opts
    
    return try_update, get_opts

def merge_user_options(base_opts: Dict, user_opts: Dict):
    
    getNext, pushData, shouldStop = user_opts_handler(user_opts)
    try_update, get_opts = base_opt_handler(base_opts)

    while not shouldStop():
        path, data = getNext()

        if not try_update(path, data):
            pushData(path, data)
        
    return get_opts()