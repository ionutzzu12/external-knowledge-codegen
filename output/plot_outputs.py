
import re
import matplotlib.pyplot as plt

file0 = "orig-train"
file1_1 = "orig-train-renamed_fs"
file1_2 = "orig-train-renamed_fs2"
file1_3 = "orig-train-renamed_fs-15patience"
# file1_4 = "orig-big_vocab"

# file2 = "05func-train-shuffle"
file2_1 = "05func-train-shuffle-dev200"
file2_2 = "05func-train-shuffle-dev200-10patience"
file2_3 = "05func-train-shuffle-dev200-15patience"

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
    plt.plot(range(len(ys)), ys, label=fname)


if __name__ == "__main__":

    # files = [file1, file2, file3, file4]
    # files = [file0, file1, file1_2, file1_3, file2, file2_5]
    files = [file0, file1_3, file1_1, file1_2, file2_1, file2_2, file2_3]

    do_what = PLOT_LOSS

    for f in files:
        draw(f, do_what)
    plt.legend()
    plt.show()
