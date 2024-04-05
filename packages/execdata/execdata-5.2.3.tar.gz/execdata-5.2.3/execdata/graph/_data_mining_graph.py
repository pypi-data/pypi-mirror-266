'''
Date         : 2023-11-09 16:43:01
Author       : BDFD,bdfd2005@gmail.com
Github       : https://github.com/bdfd
LastEditTime : 2023-11-10 12:56:01
LastEditors  : BDFD
Description  : 
FilePath     : \execdata\analysis_graph\_data_mining_graph.py
Copyright (c) 2023 by BDFD, All Rights Reserved. 
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def missing_value_analysis(df, miss_rate=5):
    # Total missing values
    missing_value = df.isnull().sum()

    # Percentage of missing values
    missing_value_percentage = 100 * df.isnull().sum() / df.shape[0]

    avaiable_value_for_analysis = df.count()

    # Make a table with the results
    missing_value_table = pd.concat(
        [missing_value, missing_value_percentage, avaiable_value_for_analysis], axis=1)

    # Rename the columns
    mis_val_table_rename_columns = missing_value_table.rename(
        columns={0: 'Miss_Values', 1: 'Miss_Rate', 2: 'Available_Value'})

    # Sort the table by percentage of missing descending
    missing_value_analysis_table = mis_val_table_rename_columns[
        mis_val_table_rename_columns.iloc[:, 1] != 0].reset_index().sort_values(
        'Miss_Rate', ascending=False).round(2)

    # Print some summary information
    print("Your selected dataframe has " + str(df.shape[1]) + " columns.\n"
          "There are " + str(missing_value_analysis_table.shape[0]) +
          " columns that have missing values.")

    fig = plt.figure(figsize=(18, 6))
    plt.bar(np.arange(missing_value_analysis_table.shape[0]), list(
        missing_value_analysis_table.Miss_Rate.values), align='center', color=['red', 'green', 'yellow', 'steelblue'])

    plt.title('Histogram of Variables Missing Value Percentage')
    plt.xlabel('Missing Feature')
    plt.ylabel('Percentage of Value Missing')
    # 添加x轴标签，并旋转90度
    plt.xticks(np.arange(missing_value_analysis_table.shape[0]), list(
        missing_value_analysis_table['index']))
    plt.xticks(rotation=90)
    # # 添加数值显示
    for x, y in enumerate(list(missing_value_analysis_table.Miss_Rate.values)):
        plt.text(x, y+0.12, '{}'.format(y), ha='center', rotation=90)
    plt.ylim([0, 100])

    plt.show()
    # Return the dataframe with missing information
    print(missing_value_analysis_table)
    filtered_df = missing_value_analysis_table[missing_value_analysis_table['Miss_Rate'] > miss_rate]
    delete_column_name_list = filtered_df['index'].tolist()
    # print(delete_column_name_list)
    return delete_column_name_list
