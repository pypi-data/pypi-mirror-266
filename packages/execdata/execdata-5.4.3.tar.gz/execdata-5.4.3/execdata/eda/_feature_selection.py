'''
Date         : 2023-01-17 10:33:06
Author       : BDFD,bdfd2005@gmail.com
Github       : https://github.com/bdfd
LastEditTime : 2023-11-13 11:06:34
LastEditors  : BDFD
Description  : 
FilePath     : \execdata\eda\_feature_selection.py
Copyright (c) 2023 by BDFD, All Rights Reserved. 
'''
import numpy as np
import pandas as pd


def sort_categorical_feature(categorical_features):
    if isinstance(categorical_features, list):
        categorical_features = categorical_features
        categorical_features.sort()
        # print(type(categorical_features))
    else:
        categorical_features = list(categorical_features)
        categorical_features = categorical_features
        categorical_features.sort()
        # print(type(categorical_features))
    return categorical_features


def drop_columns(df, del_columns_list):
    if isinstance(del_columns_list, str):
        del_columns_list = [del_columns_list]
    elif isinstance(del_columns_list, list):
        del_columns_list = del_columns_list
    else:
        return print("input is not list or str! please redo the function with correct parameter.")
    for column in del_columns_list:
        df = df.drop(column, axis=1)
    return df


def column_not_drop(df, save_columns_list):
    if isinstance(save_columns_list, str):
        save_columns_list = [save_columns_list]
    elif isinstance(save_columns_list, list):
        save_columns_list = save_columns_list
    else:
        return print("input is not list or str! please redo the function with correct parameter.")
    column_to_drop_list = [
        col for col in df.columns if col not in save_columns_list]
    column_to_drop_list = sort_categorical_feature(column_to_drop_list)
    print("The dropped column list are:", column_to_drop_list)
    df = drop_columns(df, column_to_drop_list)
    return df
