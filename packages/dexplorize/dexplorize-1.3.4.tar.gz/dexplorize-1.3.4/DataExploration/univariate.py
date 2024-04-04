import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Entropy Based - Supervised
def compute_entropy(data):
  u_class, counts = np.unique(data, return_counts=True)
  prob = counts / len(data)
  entropy = -np.sum(prob * np.log2(prob))
  return entropy

def best_split(attr1, attr2):
  entropy = float('inf')
  splits =  None
  left_gsplit = right_gsplit = 0
  
  for value in np.unique(attr1):
    left_val = attr1 <= value
    right_val = attr1 > value
    
    left_entr = compute_entropy(attr2[left_val])
    right_entr = compute_entropy(attr2[attr1 > value])
    total_entr = (len(attr2[left_val]) / len(attr2)) * left_entr + (len(attr2[right_val]) / len(attr2)) * right_entr
    
    if total_entr < entropy:
      entropy = total_entr
      splits = value
      left_gsplit = left_entr
      right_gsplit = right_entr
      
  return splits, left_gsplit, right_gsplit
      
      

def entropy(attr1, attr2, bins):
  
  splits = []
  info_gain = []
  left_gsplit = right_gsplit = 0  
  
  for x in range(bins):
    BS, LE, RE = best_split(attr1, attr2)
    
    if BS is None:
      break
    splits.append(BS)
    info_gains = compute_entropy(attr2) - ((len(attr1[attr1 <= BS]) / len(attr1)) * LE + (len(attr1[attr1 > BS]) / len(attr1)) * RE)
    info_gain.append(info_gains)
    attr1 = np.where(attr1 <= BS, np.nan, attr1)
    
  return splits, info_gain


def entropy_based(data1, target, bins):
  splits, info_gain = entropy(data1, target, bins)
  entr = compute_entropy(target)
  gain = max(info_gain)
  split_val = entr - gain
  print(f'Entropy: {entr:.3f}') 
  print(f'Entropy given best split: {split_val:.3f}')
  print(f'Information gain: {gain:.3f}')
  print(f'Best split bins <= {min(splits):.3f} and > {max(splits):.3f}')

# Equal Width Based - Unsupervised
def equal_width(data, bins):
    width = (max(data) - min(data)) / bins
    boundaries = [min(data) + x * width for x in range(1, bins)]
    bin = np.split(np.sort(data), np.searchsorted(np.sort(data), boundaries))
    return bin
    
def ewidth_bin(data, bins):
	ew = equal_width(data, bins)
	for x, bin in enumerate(ew):
		print(f'Bin: {x+1}: {bin}')

def ewidth_plot(data):
  ew1 = [f'{x[0]} - {x[-1]}' for x in data]
  ew2 = [sum(x) for x in data]
    
  plt.bar(ew1, ew2)
  plt.xlabel('Values')
  plt.ylabel('Width')
  plt.show()
        

# Equal Frequency Based - Unsupervised
def equal_freq(data, bins):
    freq = sorted(data)
    size = len(data) // bins
    boundaries = [freq[x * size] for x in range(1, bins)]
    bin = np.split(freq, np.searchsorted(freq, boundaries))
    return bin

def efreq_bin(data, bins):
  ef = equal_freq(data, bins)
  for x, bin in enumerate(ef):
	  print(f'Bin: {x+1}: {bin}')

def  efreq_plot(data):
    ef1 = [f'{x[0]} - {x[-1]}' for x in data]
    ef2 = [sum(x) for x in data]

    plt.bar(ef1, ef2)
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.show()

# Encoding - Binary
def binary_encoding(data, values):
    encode = pd.get_dummies(data[values])
    encoded = encode.astype(int)
    return encoded

def target_encoding(data, values, attr):
  combine = pd.concat([attr, binary_encoding(data, values)], axis=1)
  return combine

# Missing Values - Imputation
def impute_values(data):
  find_missing = data.columns[data.isna().any()].tolist()
  
  for values in find_missing:
    random_values = data[values].dropna().sample(data[values].isnull().sum(), random_state=0)
    random_values.index = data[data[values].isnull()].index
    data.loc[data[values].isnull(), values] = random_values
    
  return data

# Categorical Variables
def pie_chart(data):
  val, val_counts = [], []
  for x in set(data):
    val.append(x)
    val_counts.append(data.count(x))
  
  plt.pie(val_counts, labels=val, autopct='%1.1f%%', startangle=140)
  plt.axis('equal')
  plt.title('Pie Chart')
  plt.show()

def bar_chart(data):
  series = pd.Series(data)
  val_count = series.value_counts()
  value_count.plot(kind='bar')
  plt.xlabel('Categories')
  plt.ylabel('Counts')
  plt.title('Bar Chart')
  plt.show()

# Numerical Variables
def describe(data):
  minimum = min(data)
  maximum = max(data)
  means = sum(data) / len(data)
  
  sort_data = sorted(data)
  length = len(data)
  if length % 2 == 0:
    medians = (sort_data[length // 2 - 1] + sort_data[length // 2]) / 2
  else:
    medians = sort_data[length // 2]
  
  freq = {}
  for x in data:
    freq[x] = freq.get(x, 0) + 1
    
  modes = max(freq, key=freq.get)
  data_range = np.ptp(data)
  data_qntles = np.percentile(data, [25, 50, 75])
  data_var = np.var(data)
  data_std = np.std(data)
  data_cov = (data_std / np.mean(data)) * 100

  print('-'*40)
  print('Statistical Measure')
  print('-'*40)
  print(f'Min:     {minimum}')
  print(f'Max:     {maximum}')
  print(f'Mean:    {means}')
  print(f'Median:  {medians}')
  print(f'Mode:    {modes}')
  print('-'*40)
  print(f'Range:            {data_range}')
  print(f'Quantiles:        {data_qntles}')
  print(f'Variance:         {data_var}')
  print(f'STDev:            {data_std}')
  print(f'CoVar:            {data_range}')
  print('-'*40)
  
def hist_bar(data, bins):
  plt.hist(data, bins=bins, color='green', edgecolor='black')
  plt.xlabel('Data Values')
  plt.ylabel('Frequency')
  plt.title('Histogram')
  plt.show()