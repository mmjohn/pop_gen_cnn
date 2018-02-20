import keras
from keras.preprocessing import sequence
import numpy as np
from matplotlib import pyplot as plt
import sys
import json
from sklearn.neighbors import NearestNeighbors


#model magic below. just a json string that specifies model structure
json_str = '{"backend": "tensorflow", "keras_version": "2.0.6", "config": [{"config": {"arguments": {}, "output_shape": null, "mode": "concat", "concat_axis": -1, "output_shape_type": "raw", "mode_type": "raw", "name": "merge_3", "dot_axes": -1, "output_mask_type": "raw", "output_mask": null, "layers": [{"config": [{"config": {"kernel_constraint": null, "dtype": "float32", "bias_constraint": null, "activity_regularizer": null, "dilation_rate": [1], "filters": 1250, "padding": "valid", "trainable": true, "batch_input_shape": [null, 418, 50], "bias_regularizer": null, "kernel_regularizer": null, "strides": [1], "activation": "relu", "kernel_initializer": {"config": {"scale": 1.0, "mode": "fan_avg", "distribution": "uniform", "seed": null}, "class_name": "VarianceScaling"}, "kernel_size": [2], "use_bias": true, "name": "conv1d_16", "bias_initializer": {"config": {}, "class_name": "Zeros"}}, "class_name": "Conv1D"}, {"config": {"kernel_constraint": null, "bias_constraint": null, "activity_regularizer": null, "dilation_rate": [1], "filters": 256, "trainable": true, "padding": "valid", "bias_regularizer": null, "kernel_regularizer": null, "strides": [1], "activation": "relu", "kernel_initializer": {"config": {"scale": 1.0, "mode": "fan_avg", "distribution": "uniform", "seed": null}, "class_name": "VarianceScaling"}, "kernel_size": [2], "use_bias": true, "name": "conv1d_17", "bias_initializer": {"config": {}, "class_name": "Zeros"}}, "class_name": "Conv1D"}, {"config": {"name": "average_pooling1d_11", "pool_size": [2], "trainable": true, "strides": [2], "padding": "valid"}, "class_name": "AveragePooling1D"}, {"config": {"name": "dropout_16", "rate": 0.25, "trainable": true}, "class_name": "Dropout"}, {"config": {"kernel_constraint": null, "bias_constraint": null, "activity_regularizer": null, "dilation_rate": [1], "filters": 256, "trainable": true, "padding": "valid", "bias_regularizer": null, "kernel_regularizer": null, "strides": [1], "activation": "relu", "kernel_initializer": {"config": {"scale": 1.0, "mode": "fan_avg", "distribution": "uniform", "seed": null}, "class_name": "VarianceScaling"}, "kernel_size": [2], "use_bias": true, "name": "conv1d_18", "bias_initializer": {"config": {}, "class_name": "Zeros"}}, "class_name": "Conv1D"}, {"config": {"name": "average_pooling1d_12", "pool_size": [2], "trainable": true, "strides": [2], "padding": "valid"}, "class_name": "AveragePooling1D"}, {"config": {"name": "dropout_17", "rate": 0.25, "trainable": true}, "class_name": "Dropout"}, {"config": {"name": "flatten_6", "trainable": true}, "class_name": "Flatten"}], "class_name": "Sequential"}, {"config": [{"config": {"kernel_constraint": null, "dtype": "float32", "bias_constraint": null, "bias_initializer": {"config": {}, "class_name": "Zeros"}, "units": 64, "kernel_initializer": {"config": {"scale": 1.0, "mode": "fan_avg", "distribution": "uniform", "seed": null}, "class_name": "VarianceScaling"}, "trainable": true, "batch_input_shape": [null, 418], "bias_regularizer": null, "kernel_regularizer": null, "name": "dense_10", "activation": "relu", "use_bias": true, "activity_regularizer": null}, "class_name": "Dense"}, {"config": {"name": "dropout_18", "rate": 0.1, "trainable": true}, "class_name": "Dropout"}], "class_name": "Sequential"}]}, "class_name": "Merge"}, {"config": {"kernel_constraint": null, "bias_constraint": null, "bias_initializer": {"config": {}, "class_name": "Zeros"}, "units": 256, "kernel_initializer": {"config": {"scale": 1.0, "mode": "fan_avg", "distribution": "uniform", "seed": null}, "class_name": "VarianceScaling"}, "trainable": true, "bias_regularizer": null, "kernel_regularizer": null, "activation": "relu", "name": "dense_11", "use_bias": true, "activity_regularizer": null}, "class_name": "Dense"}, {"config": {"kernel_constraint": null, "bias_constraint": null, "bias_initializer": {"config": {}, "class_name": "Zeros"}, "units": 1, "kernel_initializer": {"config": {"stddev": 0.05, "mean": 0.0, "seed": null}, "class_name": "RandomNormal"}, "trainable": true, "bias_regularizer": null, "kernel_regularizer": null, "activation": "linear", "name": "dense_12", "use_bias": true, "activity_regularizer": null}, "class_name": "Dense"}], "class_name": "Sequential"}'


def sort_min_diff(amat):
    '''this function takes in a SNP matrix with indv on rows and returns the same matrix with indvs sorted by genetic similarity.
    this problem is NP-hard, so here we use a nearest neighbors approx.  it's not perfect, but it's fast and generally performs ok.
    assumes your input matrix is a numpy array'''
    mb = NearestNeighbors(len(amat), metric='manhattan').fit(amat)
    v = mb.kneighbors(amat)
    smallest = np.argmin(v[0].sum(axis=1))
    return amat[v[1][smallest]]

def convert_01_to_neg1_1(amat):
    '''convert standard binary 0/1 ms SNP matrix to -1/1 SNP matrix. B/c weights & biases are drawn from a distribution with mean=0
    choosing -1/1 (which is also mean=0) tends to help in training. assumes your input matrix is a numpy array'''
    return (amat*-2+1)*-1 

def rsquare(x,y):
    return np.corrcoef(x,y)[0][1]**2  #r-squared

def rmse(x,y):
    return np.sqrt(np.mean((x-y)**2))

s = json.load(open('ldhat.data/validate.data.LD.json'))

xtest = []
postest = []
ytest = []
maxL = 0
idx = 0
for pos, theta_rho, str_mat in s:
    postest.append(np.array(pos))
    nm = []
    for i in str_mat:
        nm.append([float(j) for j in i])
    nm = convert_01_to_neg1_1(sort_min_diff(np.array(nm))).T
    #print nm.shape
    xtest.append(nm)
    ytest.append(theta_rho)
    if nm.shape[1] > maxL: maxL = nm.shape[1]
    if not idx % 100: print idx
    idx+=1
print maxL

postest = np.array(postest)
xtest = np.array(xtest)

# xtemp = []
# for i in xtest:
#     v = sequence.pad_sequences(i, maxlen=418, padding='post')
#     xtemp.append(v)
#     
# xtest = np.array(xtemp)
xtest = sequence.pad_sequences(xtest, maxlen=418, padding='post')
postest = sequence.pad_sequences(postest, maxlen=418, padding='post', value=-1., dtype='float32')
ytest_rho = np.array([i[1] for i in ytest])
thetas=[i[0] for i in ytest]

#print postest

mean_test = 4.78757605959  #use training data mean ln(rho)   np.mean(np.log(ytest_rho))
print mean_test

mod = keras.models.model_from_json(json_str)
mod.load_weights('merge.mod.weights')


pred = mod.predict([xtest,postest])
plt.hist(pred, bins=24)
plt.show()

pred = np.exp([i[0]+mean_test for i in pred])

print map(len, (thetas, pred, ytest_rho))
print 'r-squared', rsquare(pred, ytest_rho), 'rmse', rmse(pred, ytest_rho)
q = {}
outfile = open('test.data.results.csv', 'w')
outfile.write('index,theta,num_sites,predict_rho,real_rho\n')
idx = 1
for i,j,k, p in zip(thetas, pred, ytest_rho, postest):
    if i not in q: q[i] = []
    q[i].append((j,k))
    num_sites = len([iiii for iiii in p if iiii >= 0])
    outfile.write(','.join(map(str, [idx, i, num_sites, j, k]))+'\n')
    idx+=1
for i in q: print i, len(q[i])
outfile.close()

idx=1
for i in sorted(q):
    plt.subplot(2,3,idx)
    pred, real = [n[0] for n in q[i]], [n[1] for n in q[i]]
    plt.scatter(real, pred, alpha=.3)
    r = rsquare(np.array(real), np.array(pred))
    plt.title('theta = '+str(i)+' r2:'+str(round(r,2)))
    idx+=1
plt.show()


d = []
for i in sorted(q):
    resid = [p-r for p,r in q[i]]
    d.append(resid)
plt.boxplot(d)
plt.xticks(range(1,6), map(str, sorted(q)))
plt.show()


#now try same model at interpolation in the big gap in Ne we created

a = np.load('gap.ld.data.npz')
ytest, xtest, postest = [a[i] for i in [ 'ytest', 'xtest', 'postest']]
xtest = sequence.pad_sequences(xtest, maxlen=418, padding='post')
postest = sequence.pad_sequences(postest, maxlen=418, padding='post', value=-1., dtype='float32')
ytest_rho = np.array([i[1] for i in ytest])
thetas=[i[0] for i in ytest]
mean_test = 4.78757605959  #use training data mean ln(rho)  np.mean(np.log(ytest_rho))
print mean_test

pred = mod.predict([xtest,postest])
plt.hist(pred, bins=24)
plt.show()

pred = np.exp([i[0]+mean_test for i in pred])

print map(len, (thetas, pred, ytest_rho))
print 'r-squared', rsquare(pred, ytest_rho), 'rmse', rmse(pred, ytest_rho)

q = {}
idx = 1
for i,j,k, p in zip(thetas, pred, ytest_rho, postest):
    if i not in q: q[i] = []
    q[i].append((j,k))
    num_sites = len([iiii for iiii in p if iiii >= 0])
    idx+=1

for i in sorted(q): print i, len(q[i])


idx = 1
for i in sorted(q):
    plt.subplot(2, 2, idx)
    pred, real = [n[0] for n in q[i]], [n[1] for n in q[i]]
    plt.scatter(real, pred, alpha=.3)
    r = rsquare(np.array(real), np.array(pred))
    plt.title('theta = '+str(i)+' r2:'+str(round(r,2)))
    idx+=1

plt.show()

json_str = '{"backend": "tensorflow", "class_name": "Sequential", "config": [{"class_name": "Merge", "config": {"output_shape": null, "arguments": {}, "layers": [{"class_name": "Sequential", "config": [{"class_name": "Conv1D", "config": {"dtype": "float32", "activation": "relu", "bias_regularizer": null, "trainable": true, "use_bias": true, "batch_input_shape": [null, 418, 50], "kernel_regularizer": null, "bias_initializer": {"class_name": "Zeros", "config": {}}, "bias_constraint": null, "activity_regularizer": null, "kernel_initializer": {"class_name": "VarianceScaling", "config": {"scale": 1.0, "mode": "fan_avg", "distribution": "uniform", "seed": null}}, "name": "conv1d_1", "kernel_size": [2], "strides": [1], "dilation_rate": [1], "padding": "valid", "filters": 1250, "kernel_constraint": null}}, {"class_name": "Conv1D", "config": {"filters": 256, "strides": [1], "activation": "relu", "bias_regularizer": null, "trainable": true, "use_bias": true, "kernel_regularizer": null, "bias_constraint": null, "bias_initializer": {"class_name": "Zeros", "config": {}}, "activity_regularizer": null, "kernel_initializer": {"class_name": "VarianceScaling", "config": {"scale": 1.0, "mode": "fan_avg", "distribution": "uniform", "seed": null}}, "name": "conv1d_2", "dilation_rate": [1], "padding": "valid", "kernel_size": [2], "kernel_constraint": null}}, {"class_name": "AveragePooling1D", "config": {"padding": "valid", "name": "average_pooling1d_1", "strides": [2], "pool_size": [2], "trainable": true}}, {"class_name": "Dropout", "config": {"rate": 0.25, "trainable": true, "name": "dropout_1"}}, {"class_name": "Conv1D", "config": {"filters": 256, "strides": [1], "activation": "relu", "bias_regularizer": null, "trainable": true, "use_bias": true, "kernel_regularizer": null, "bias_constraint": null, "bias_initializer": {"class_name": "Zeros", "config": {}}, "activity_regularizer": null, "kernel_initializer": {"class_name": "VarianceScaling", "config": {"scale": 1.0, "mode": "fan_avg", "distribution": "uniform", "seed": null}}, "name": "conv1d_3", "dilation_rate": [1], "padding": "valid", "kernel_size": [2], "kernel_constraint": null}}, {"class_name": "AveragePooling1D", "config": {"padding": "valid", "name": "average_pooling1d_2", "strides": [2], "pool_size": [2], "trainable": true}}, {"class_name": "Dropout", "config": {"rate": 0.25, "trainable": true, "name": "dropout_2"}}, {"class_name": "Flatten", "config": {"trainable": true, "name": "flatten_1"}}]}, {"class_name": "Sequential", "config": [{"class_name": "Dense", "config": {"dtype": "float32", "kernel_constraint": null, "bias_regularizer": null, "trainable": true, "use_bias": true, "kernel_regularizer": null, "bias_constraint": null, "bias_initializer": {"class_name": "Zeros", "config": {}}, "activity_regularizer": null, "kernel_initializer": {"class_name": "VarianceScaling", "config": {"scale": 1.0, "mode": "fan_avg", "distribution": "uniform", "seed": null}}, "units": 64, "name": "dense_1", "batch_input_shape": [null, 418], "activation": "relu"}}, {"class_name": "Dropout", "config": {"rate": 0.1, "trainable": true, "name": "dropout_3"}}]}], "dot_axes": -1, "concat_axis": -1, "output_mask_type": "raw", "output_mask": null, "output_shape_type": "raw", "mode_type": "raw", "name": "merge_1", "mode": "concat"}}, {"class_name": "Dense", "config": {"kernel_constraint": null, "bias_regularizer": null, "trainable": true, "use_bias": true, "kernel_regularizer": null, "bias_initializer": {"class_name": "Zeros", "config": {}}, "bias_constraint": null, "activity_regularizer": null, "kernel_initializer": {"class_name": "VarianceScaling", "config": {"scale": 1.0, "mode": "fan_avg", "distribution": "uniform", "seed": null}}, "units": 256, "name": "dense_2", "activation": "relu"}}, {"class_name": "Dense", "config": {"kernel_constraint": null, "bias_regularizer": null, "trainable": true, "use_bias": true, "kernel_regularizer": null, "bias_initializer": {"class_name": "Zeros", "config": {}}, "bias_constraint": null, "activity_regularizer": null, "kernel_initializer": {"class_name": "RandomNormal", "config": {"stddev": 0.05, "mean": 0.0, "seed": null}}, "units": 1, "name": "dense_3", "activation": "linear"}}], "keras_version": "2.0.6"}'

s = json.load(open('ldhat.data/validate.data.LD.json'))

xtest = []
postest = []
ytest = []
maxL = 0
idx = 0
for pos, theta_rho, str_mat in s:
    postest.append(np.array(pos))
    nm = []
    for i in str_mat:
        nm.append([float(j) for j in i])
    nm = convert_01_to_neg1_1(sort_min_diff(np.array(nm))).T
    #print nm.shape
    xtest.append(nm)
    ytest.append(theta_rho)
    if nm.shape[1] > maxL: maxL = nm.shape[1]
    if not idx % 100: print idx
    idx+=1
#print maxL

postest = np.array(postest)
xtest = np.array(xtest)

# xtemp = []
# for i in xtest:
#     v = sequence.pad_sequences(i, maxlen=418, padding='post')
#     xtemp.append(v)
#     
# xtest = np.array(xtemp)
xtest = sequence.pad_sequences(xtest, maxlen=418, padding='post')
postest = sequence.pad_sequences(postest, maxlen=418, padding='post', value=-1., dtype='float32')
ytest_rho = np.array([i[1] for i in ytest])
thetas=[i[0] for i in ytest]

z = ytest_rho <= 500
ytest_rho, xtest, postest = ytest_rho[z], xtest[z], postest[z]
#print postest

mean_test = 4.25091521168  #use training data mean ln(rho)   np.mean(np.log(ytest_rho))
print mean_test

mod = keras.models.model_from_json(json_str)
mod.load_weights('low.rho.only.merge.mod.weights')

pred = mod.predict([xtest,postest])
plt.hist(pred, bins=24)
plt.show()

pred = np.exp([i[0]+mean_test for i in pred])


print 'r-squared', rsquare(pred, ytest_rho), 'rmse', rmse(pred, ytest_rho)
q = {}
outfile = open('low.row.test.data.results.csv', 'w')
outfile.write('index,predict_rho,real_rho\n')
idx = 1
for j,k, p in zip(pred, ytest_rho, postest):
    if i not in q: q[i] = []
    q[i].append((j,k))
    #num_sites = len([iiii for iiii in p if iiii >= 0])
    outfile.write(','.join(map(str, [idx, j, k]))+'\n')
    idx+=1
for i in q: print i, len(q[i])
outfile.close()
