
import re
import matplotlib.pyplot as plt

file1 = "orig-train"
file2 = "10func-train"

file3 = "10func-train2"
file4 = "03func-train"

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
    files = [file1, file2, file3, file4]
    do_what = PLOT_SCORE

    for f in files:
        draw(f, do_what)
    plt.legend()
    plt.show()
