#!/usr/bin/env pythoin
#!coding=utf-8

import matplotlib as mpl  
mpl.use('Agg')                 
import matplotlib.pyplot as plt
import math

def draw(x_nums, y_nums):

    fig = plt.figure(dpi=128, figsize=(10, 6))

    plt.plot(x_nums, y_nums, c='red')

    #plt.xlim([0, 1])
    #plt.ylim([0, 1])

    plt.xscale("log")
    plt.xlim([1e-3, 1])
    plt.ylim([-0.01, 1.01])
    #plt.xlabel('FPR')
    #plt.ylabel('TPR')
    #plt.title("NAME")
    plt.legend(loc="best")
    plt.grid(True)
    plt.show()

    plt.title("false positve rate and recognition rate", fontsize=24)
    plt.xlabel('false positve rate', fontsize=16)
    plt.ylabel("recognition rate", fontsize=16)

    plt.tick_params(axis='both', which='major', labelsize=16)

    fig.savefig('falsePositiveRate_recognitionRate.png', bbox_inches='tight')

if __name__ == "__main__":
    x_nums = [0.0034, 0.0042, 0.0059, 0.0076, 0.0084, 0.0093, 0.0093, 0.0093, 0.0093, 0.0835, 0.6644, 1]
    y_nums = [0.1857, 0.2724, 0.5296, 0.6245, 0.7071, 0.7418, 0.7714, 0.7898, 0.8102, 0.8714, 0.8867, 0.8878]

    draw(x_nums, y_nums)
