
import re
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import numpy as np
import pandas as pd

file1 = "orig-train"
file2 = "10func-train"

file3 = "10func-train2"
# file4 = "03func-train-wrong_eval"
# file5 = "03func-train-unfinished"
file7 = "03func-train"

PLOT_LOSS = 1
PLOT_SCORE = 2


def draw(fname, dowhat):
    with open('out-' + fname + '.txt') as file:
        content = file.readlines()
        content = [x.strip() for x in content]
        ys = []

        if dowhat == PLOT_SCORE:
            for line in content:
                xs = re.findall("corpus_bleu: 0.[0-9]+", line)
                # xs = re.findall("'exact_match': 0.[0-9]+", line)
                assert len(xs) < 2, len(xs)

                if xs:
                    ys.append(float(xs[0].split(' ')[1]))
        if dowhat == PLOT_LOSS:
            for line in content:
                if 'loss=' in line:
                    ps = line.split('loss=')
                    ys.append(float(ps[1]))

    print(ys)
    x_new = range(len(ys))
    y_new = pd.Series(ys).rolling(10, min_periods=10).mean()

    plt.plot(x_new, y_new, label=fname)


if __name__ == "__main__":
    files = [file1, file2, file3, file7]
    do_what = PLOT_SCORE

    for f in files:
        draw(f, do_what)
    plt.legend()
    plt.show()
