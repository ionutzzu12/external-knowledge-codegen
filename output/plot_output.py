
import re
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import numpy as np
# import pandas as pd

file0 = "orig-train"
file10 = "orig-train-small_vocab"
file11 = "orig-train-small_vocab2"
file12 = "vanilla_dev200_func_renamed"
file20 = "5func-train-no_shuffle"
file22 = "5func-train-shuffle"
# file2 = "10func-train"
#
# file3 = "10func-train2"
# file4 = "03func-train-wrong_eval"
# file5 = "03func-train-last_state"
# file6 = "03func-train-last_cell"
# file7 = "03func-train"

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
    y_new = ys  # pd.Series(ys).rolling(10, min_periods=10).mean()

    plt.plot(x_new, y_new, label=fname)


if __name__ == "__main__":
    # files = [file1, file2, file3, file4, file5, file6, file7]
    files = [file0, file10, file11, file12, file20, file22]
    do_what = PLOT_SCORE

    for f in files:
        draw(f, do_what)
    plt.legend()
    plt.show()
