'''
Date         : 2023-11-02 12:47:29
Author       : BDFD,bdfd2005@gmail.com
Github       : https://github.com/bdfd
LastEditTime : 2024-04-05 11:44:47
LastEditors  : <BDFD>
Description  : 
FilePath     : \execdata\graph\_data_analysis_graph.py
Copyright (c) 2023 by BDFD, All Rights Reserved. 
'''
from tabulate import tabulate
import seaborn as sns
import matplotlib.pyplot as plt
import math


def top_correlation(df, target_feature, top_feature_number=10, correlation_boundary=0.05):
    # Get Correlation of "Churn" with other variables:
    plt.figure(figsize=(20, 20))
    df.corr()[target_feature].sort_values(ascending=False).plot(kind='bar')

    # Calculate the correlation with the target variable and sort by values
    correlations = []
    for column in df.columns:
        if column != target_feature:
            correlation = df[target_feature].corr(df[column])
            if abs(correlation) > correlation_boundary:
                correlation = round(correlation, 2)
                correlations.append((column, correlation))

    # top_feature_number = 10 #default value
    # Sort the correlations by values and select the top 10
    correlations.sort(key=lambda x: abs(x[1]), reverse=True)
    top_features = correlations[:top_feature_number]

    # Extract column name
    top_feature_column_names = [item[0] for item in top_features]
    top_feature_column_names = top_feature_column_names + [target_feature]
    # print(column_names)

    # Display the top 12 feature correlations as a table
    headers = ["Feature", "Abs Cor"]
    table = tabulate(correlations, headers=headers, tablefmt="github")

    print(
        f"Feature Correlations (sorted by absolute values):")
    print(
        f"Top 10 feature and target feature list:", top_feature_column_names)
    print(table)

    return top_feature_column_names


def categorical_numerical_feature_vs_target_graph(df, categorical_numerical_feature_list, target_feature):
    figsize = math.ceil(math.sqrt(len(categorical_numerical_feature_list)))
    fig = plt.figure(figsize=(18, 15))
    gs = fig.add_gridspec(figsize, figsize)
    gs.update(wspace=0.5, hspace=0.25)
    for i in range(figsize):
        for j in range(figsize):
            num = 0
            num = i * figsize + j
            if num < len(categorical_numerical_feature_list):
                print(i, j)
                # print('number is', num)
                # print('number is', len(categorical_numerical_feature_list))
                ax = fig.add_subplot(gs[i, j])
                background_color = "#ffe6e6"
                color_palette = ["#800000", "#8000ff",
                                 "#6aac90", "#5833ff", "#da8829"]
                fig.patch.set_facecolor(background_color)
                print(categorical_numerical_feature_list[num])
                ax.set_facecolor(background_color)
                ax.grid(color='#000000', linestyle=':',
                        axis='y', zorder=0,  dashes=(1, 5))
                sns.countplot(
                    ax=ax, data=df, x=categorical_numerical_feature_list[num], palette=color_palette)
                ax.set_xlabel(
                    categorical_numerical_feature_list[num], fontsize=14, fontweight='bold', fontfamily='serif', color="#000000")
                ax.set_ylabel(target_feature, fontsize=14,
                              fontweight='bold', fontfamily='serif', color="#000000")
