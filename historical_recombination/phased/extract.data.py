import numpy as np
from common import *
from gzip import GzipFile as gz
from sklearn.neighbors import NearestNeighbors


def sort_min_diff(amat):
    '''this function takes in a SNP matrix with indv on rows and returns the same matrix with indvs sorted by genetic similarity.
    this problem is NP-hard, so here we use a nearest neighbors approx.  it's not perfect, but it's fast and generally performs ok.
    assumes your input matrix is a numpy array'''
    mb = NearestNeighbors(len(amat), metric='manhattan').fit(amat)
    v = mb.kneighbors(amat)
    smallest = np.argmin(v[0].sum(axis=1))
    return amat[v[1][smallest]]

a = (i.strip().split('asdfasdfd') for i in gz('all.LD.sims.txt.gz'))

idx = 0
xvals, yvals = {},{}
seg_sites = {}
pos = {}
n = []
ctr = 0
true_idx = 0

for i in a:
    if 'segsites' in i[0]:
        seg_sites[true_idx] = int(i[0].split()[-1])
    if 'positions' in i[0]:
        pos[true_idx] = [float(jj) for jj in i[0].split()[1:]]
    if './ms' in i[0]:
        true_idx+=1
        idx = 0
        theta_line = i[0].split()
        ms_vals = map(float, [theta_line[4], theta_line[6]])
        yvals[true_idx] = np.array(ms_vals)
    if 5 < idx < 56:
        n.append(np.array(map(int, i[0]), dtype='int8'))
    if len(n) == 50:
        n = np.array(n)
        n = sort_min_diff(n)
        xvals[true_idx] =  n.T 
        idx = 0
        n = []
        if not true_idx % 100: print true_idx, len(xvals), len(yvals), min(xvals), max(xvals), min(yvals), max(yvals) #xvals[max(xvals)].shape, seg_sites[max(seg_sites)]
        #if len(xvals) != len(yvals):
        #    print true_idx, idx, len(xvals), len(yvals), xvals[-2].shape, yvals[-2], '*********'
    #print idx
    idx+=1
    #print xvals, yvals, seg_sites, pos

new_yvals_train, new_yvals_test = [], []
new_xvals_train, new_xvals_test = [], []
new_pos_train, new_pos_test = [], []

isect = set(xvals.keys()).intersection(yvals.keys()).intersection(pos.keys())
print 'intersect len', len(isect), min(isect), max(isect)

for i in sorted(seg_sites):
    if i in xvals and i in yvals and i in pos:
        if i < 200001:
            s = seg_sites[i]
            if s > 0 and yvals[i][0] > 3:
                new_pos_train.append(np.array(pos[i]))
                new_xvals_train.append(xvals[i])
                new_yvals_train.append(yvals[i])
        else:
            s = seg_sites[i]
            if s > 0 and yvals[i][0] > 3:
                new_pos_test.append(np.array(pos[i]))
                new_xvals_test.append(xvals[i])
                new_yvals_test.append(yvals[i])

#for s,i,j in zip(seg_sites, yvals, pos):
#    if s != 0:
#        new_yvals.append(i)
#        new_pos.append(j)


#yvals = np.array(new_yvals)
#xvals = np.array(xvals)
#print len(yvals), len(xvals)

max_size = 0
for i in new_xvals_test:
    if i.shape[0] > max_size: max_size = i.shape[0]
for i in new_xvals_train:
    if i.shape[0] > max_size: max_size = i.shape[0]
    
print "maxsize", max_size


np.savez_compressed('ld.data.npz', xtrain=new_xvals_train, xtest=new_xvals_test, 
                                   ytrain = new_yvals_train, ytest = new_yvals_test,
                                   postrain = new_pos_train, postest=new_pos_test)
#from json import dump
#dump(new_pos, open('LD.postions.json', 'w'))



