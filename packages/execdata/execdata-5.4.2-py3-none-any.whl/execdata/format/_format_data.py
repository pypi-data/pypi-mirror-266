'''
Date         : 2023-01-17 10:33:06
Author       : BDFD,bdfd2005@gmail.com
Github       : https://github.com/bdfd
LastEditTime : 2023-11-30 12:37:47
LastEditors  : BDFD
Description  : 
FilePath     : \execdata\format\_format_data.py
Copyright (c) 2023 by BDFD, All Rights Reserved. 
'''
import execdata as exe
import pandas as pd


def fill_zeros(num, full_position=2):
    # exe.format.convint(num)
    result = str(num).zfill(full_position)
    return result


def concat_transformed_df(df, concat_df, drop_columns_list):
    # usually combine use with after transform_label_encoder and transform_one_hot_encode
    result_df = []
    new_df = df.drop(columns=drop_columns_list)
    result_df = pd.concat([new_df, concat_df], axis=1)
    return result_df


def concat_inversed_df(df, reverted_df, transformed_df):
    # usually combine use with after inverse_label_encoder and inverse_one_hot_encode
    drop_columns_list = transformed_df.columns.tolist()
    result_df = []
    new_df = df.drop(columns=drop_columns_list)
    result_df = pd.concat([new_df, reverted_df], axis=1)
    return result_df
