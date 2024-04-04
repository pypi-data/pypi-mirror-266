import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Numeric to Numeric
def scatter_plot(data, col1, col2):
    x = data[col1]
    y = data[col2]
    N = 3
    
    colors = np.random.rand(N)
    plt.scatter(x, y, color=colors, alpha=0.5)
    plt.xlabel(col1)
    plt.ylabel(col2)
    plt.title('Scatter Plot')
    plt.show()

def linear_corr(data, col1, col2):
    x = data[col1]
    y = data[col2]
    m, b = np.polyfit(x, y, 1)
    
    plt.plot(x, m*x+b, color='red', linestyle='-')
    plt.scatter(x, y)
    plt.xlabel(col1)
    plt.ylabel(col2)
    plt.title('Linear Correlation')
    plt.show()

# Categorical to Categorical  
def stacked_column(data, val1, val2):
    cat_data = data.groupby([val1, val2]).size().reset_index(name='count')
    cat_data =cat_data.pivot(index=val2, columns=val1, values='count').fillna(0)
    cat_data = cat_data.div(cat_data.sum(axis=1), axis=0) * 100
    cat_data.plot(kind='bar', stacked=True)
    plt.xlabel(val2)
    plt.ylabel(val1)
    plt.title('Stacked Column Chart')
    plt.show()

# Numerical to Categorical 
def line_chart(data, attr, num):
    data_err = data.groupby(attr)[num].agg(['mean', 'sem'])
    x = np.arange(len(data_err))
    y = data_err['mean']
    std_error = data_err['sem']
    fig, ax = plt.subplots()
    
    ax.errorbar(x, y, yerr=std_error, capsize=4)
    ax.set_xticks(x)
    ax.set_xticklabels(data_err.index)
    ax.set_xlabel(attr)
    ax.set_ylabel(num)
    ax.set_title('Line Chart w/ Error Bars')
    plt.show()