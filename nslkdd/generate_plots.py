"""
===========================================
Realisation plotting for data check
===========================================

In order to understand the data more, it will visualise 20% dataset for every properties.

It usually takes about 250 seconds (4 minutes)
"""
print (__doc__)

import datetime
import math
import numpy as np
from sklearn import mixture
import matplotlib
import matplotlib.mlab
import matplotlib.pyplot as plt
from matplotlib import gridspec
import copy

from data import model
import preprocessing

def generate_realisation_plots(df, headers, min_sample=1000, min_covariance=0.001, title="", gmms=None):
    discretes = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attemped', 'num_root', 'num_file_creation', 'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count', 'srv_count', 'dst_host_count', 'dst_host_srv_count']
    for hi, key in enumerate(headers):
        print "generating " + title + " figure for " + str(key) + " ..."
        fig, ax = plt.subplots()
#        ax.autoscale_view()
        ax.grid(True)
        plt.title(key + " " + str(len(df)))
        plt.ylabel(key + " (logscale)")

        minval = min(df[key])
        maxval = max(df[key])
        margin = 0 #(maxval-minval) / 20.0

        # gmm fitting
        clf = gmms[hi]
#        clf = mixture.GMM(n_components=3, covariance_type='full', min_covar=min_covariance, n_init=3)
#        clf.fit(df[key])
#        m1, m2, m3 = clf.means_
#        w1, w2, w3 = clf.weights_
#        c1, c2, c3 = clf.covars_

        # show realisation
        plt.subplot(3, 1, 1)
        plt.xlabel(key)
        plt.ylabel("count")

        xs = range(len(df[key]))
        plt.scatter(xs, df[key])

        # show hist
        plt.subplot(3, 1, 2)
        plt.xlabel(key)
        plt.ylabel("count")

        binwidth = -1
        if key in discretes :
            binwidth = int(abs(maxval - minval + 1)) * 2
        else :
            binwidth = 10 * 2
        histdist = df[key].hist()
#        histdist = plt.hist(df[key], binwidth, normed=1, facecolor='b')

        # show GMM
        plt.subplot(3, 1, 3)
        plt.xlabel(key)
        plt.ylabel('prob')

        gmm_sample = min_sample
        x = histdist
        xs = np.linspace(minval-margin,maxval+margin,gmm_sample)

        # gmm draw
        yss = [0]*len(xs)
        colors = ['r','g','b','c','black']
        for mi, _ in enumerate(clf.means_) :
            m1 = clf.means_[mi]
            c1 = clf.covars_[mi]
            w1 = clf.weights_[mi]

            ys = [matplotlib.mlab.normpdf(x,m1,np.sqrt(c1))[0]*w1 for x in xs]
            for yi,y in enumerate(ys) :
                yss[yi] = yss[yi] + y
        plt.plot(xs,yss,color='y', lw=5)

        for mi, _ in enumerate(clf.means_) :
            m1 = clf.means_[mi]
            c1 = clf.covars_[mi]
            w1 = clf.weights_[mi]

            ys = [matplotlib.mlab.normpdf(x,m1,np.sqrt(c1))[0]*w1 for x in xs]
            plt.plot(xs,ys,color=colors[mi], lw=1)

        # save and close
        fig.savefig("./plots/" +key+"_" + title + ".png")
        plt.close()

if __name__ == '__main__':
    import sys
    import time

    if sys.version_info < (2, 7) or sys.version_info >= (3, 0):
        print ("Requires Python 2.7.x")
        exit()
    del sys

    headerfile = './data/kddcup.names'
    datafile = './data/KDDTrain+_20Percent.txt'

    datasize = None
    start = time.time()

    # plot for abnormal
    df, headers, gmms = preprocessing.get_preprocessed_data(datasize,headerfile,datafile)
    headers.remove('attack')
    headers.remove('difficulty')

    normal_gmm = gmms[0]
    abnormal_gmm = gmms[1]

    df_train = copy.deepcopy(df)
    df_train = df_train[(df_train["attack"] != 11)] # only select for normal data
    df_train.drop('attack',1,inplace=True) # remove useless 
    df_train.drop('difficulty',1,inplace=True) # remove useless 
    df_train.reset_index(drop=True)
    generate_realisation_plots(df_train, headers, min_sample=len(df_train), title="abnormal", gmms=abnormal_gmm)

    # plot for normal
    df_train = copy.deepcopy(df)
    df_train = df_train[(df_train["attack"] == 11)] # only select for normal data
    df_train.drop('attack',1,inplace=True) # remove useless 
    df_train.drop('difficulty',1,inplace=True) # remove useless 
    df_train.reset_index(drop=True)
    df_train.reset_index(drop=True)
    generate_realisation_plots(df_train, headers, min_sample=len(df_train), title="normal", gmms=normal_gmm)

    elapsed = (time.time() - start)
    print "[histogram] done in %s seconds" % (elapsed)

