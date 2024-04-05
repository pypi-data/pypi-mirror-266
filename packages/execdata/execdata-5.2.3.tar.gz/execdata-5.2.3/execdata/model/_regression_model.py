import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import median_absolute_error
import seaborn as sns


def reg_model(model, X_train, y_train, X_test, y_test):
    # Initial the Variables
    CV = []
    train_scores = []
    test_scores = []

    # Training model
    model.fit(X_train, y_train)

    # score of train set
    train_model_score = model.score(X_train, y_train)
    train_scores.append(round(train_model_score, 2))
    y_pred_train = model.predict(X_train)

    # score of test set
    test_model_score = model.score(X_test, y_test)
    test_scores.append(round(test_model_score, 2))
    y_pred_test = model.predict(X_test)

    # train set using Cross validation
    cross_val = cross_val_score(model, X_train, y_train, cv=5)
    cv_mean = cross_val.mean()
    CV.append(round(cv_mean, 2))

    # Printing results
    print("Train score :", round(train_model_score, 2))
    print("Test score :", round(test_model_score, 2))
    print("Train CV scores :", cross_val)
    print("Train CV mean :", round(cv_mean, 2))
    print("Mean absolute error for train :",
          mean_absolute_error(y_train, y_pred_train))
    print("Median absolute error for train :",
          median_absolute_error(y_train, y_pred_train))
    print("Mean absolute error for test :",
          mean_absolute_error(y_test, y_pred_test))
    print("Median absolute error for test :",
          mean_absolute_error(y_test, y_pred_test))

    # Plotting Graphs
    # Residual Plot of train data
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].set_title('Residual Plot of Train samples')
    sns.distplot((y_train[:100]-y_pred_train[:100]), hist=False, ax=ax[0])
    ax[0].set_xlabel('y_train - y_pred_train')

    # Y_test vs Y_train scatter plot
    ax[1].set_title('y_test vs y_pred_test')
    ax[1].scatter(x=y_test[:100], y=y_pred_test[:100])
    ax[1].set_xlabel('y_test')
    ax[1].set_ylabel('y_pred_test')

    plt.show()
