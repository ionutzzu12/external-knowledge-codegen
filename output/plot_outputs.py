
import re
import matplotlib.pyplot as plt

file0 = "orig-train"
file00 = "orig-train-no_copy"
file01 = "orig-train-bert"
file02 = "orig-train-bert-long_run"
# file1_1 = "orig-train-renamed_fs"
# file1_2 = "t1-train-renamed_fs-patience10-renamed_bleu_metric"
# file1_3 = "orig-train-renamed_fs-15patience"
# file1_4 = "t1-train-renamed_fs-patience5-renamed_bleu_metric"

# file2 = "05func-train-shuffle"
# file2_1 = "05func-train-shuffle-dev200"
# file2_2 = "05func-train-shuffle-dev200-10patience"
# file2_3 = "t0-funcs5-renamed_fs-patience15-renamed_bleu_metric"
file2_4 = "t1-funcs10-renamed_fs-patience10-renamed_bleu_metric"
# file2_5 = "t1-funcs10-renamed_fs-patience10-renamed_bleu_metric-last_state"

file3_1 = 't3-funcs15-renamed_fs-patience7-renamed_bleu_metric-last_state'
file3_2 = 't4-funcs25-renamed_fs-patience7-renamed_bleu_metric-last_cell'
file3_3 = 't5-funcs25-renamed_fs-patience7-renamed_bleu_metric-last_cell-just_train_set_funcs'

# file2 = "10func-train"
# file3 = "10func-train2"
# file4 = "03func-train"

# file3 = "10func-train2"
# file4 = "03func-train"

PLOT_LOSS = 1
PLOT_SCORE = 2


def draw(fname, dowhat):
    with open('out-' + fname + '.txt') as file:
        content = file.readlines()
        content = [x.strip() for x in content]
        ys = []

        if dowhat == PLOT_SCORE:
            for line in content:
                xs = re.findall("'corpus_bleu': 0.[0-9]+", line)
                # xs = re.findall("'exact_match': 0.[0-9]+", line)
                assert len(xs) < 2, len(xs)

                if xs:
                    ys.append(float(xs[0].split(' ')[1]))
        if dowhat == PLOT_LOSS:
            for line in content:
                if 'loss=' in line:
                    ps = line.split('loss=')
                    ys.append(float(ps[1])/100)

    print(ys)
    plt.plot(range(len(ys)), ys, label=fname)


if __name__ == "__main__":

    # files = [file1, file2, file3, file4]
    # files = [file0, file1, file1_2, file1_3, file2, file2_5]
    # files = [file1_1, file1_2, file1_3, file1_4, file2_2, file2_4, file2_5, file3_1, file3_2, file3_3]
    files = [file0, file00, file01, file02, file2_4]  # , file3_1, file3_2, file3_3]

    do_what = PLOT_SCORE
    # do_what = PLOT_LOSS

    for f in files:
        draw(f, do_what)

    plt.legend()
    plt.show()
