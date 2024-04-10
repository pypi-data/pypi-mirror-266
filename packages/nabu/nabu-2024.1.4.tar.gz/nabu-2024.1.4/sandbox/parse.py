from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

steps_to_measure = [
    "Reading data",
    "Applying flat-field",
    "Applying double flat-field",
    "Applying CCD corrections",
    "Performing phase retrieval",
    "Performing unsharp mask",
    "Taking logarithm",
    "Building sinograms",
    "Removing rings on sinograms",
    "Reconstruction",
    "Computing histogram",
    "Saving data"
]

def parse_reconstruction(lines, separator=" - "):
    def extract_timestamp(line):
        timestamp = line.split(separator)[0]
        return datetime.strptime(timestamp, "%d-%m-%Y %H:%M:%S")

    def extract_current_step(line):
        return line.split(separator)[-1]

    current_step = extract_current_step(lines[0])
    t1 = extract_timestamp(lines[0])

    res = {}
    for line in lines[1:]:
        line = line.strip()
        if len(line.split(separator)) == 1:
            continue
        timestamp = line.strip().split(separator)[0]
        t2 = datetime.strptime(timestamp, "%d-%m-%Y %H:%M:%S")

        res.setdefault(current_step, [])
        res[current_step].append((t2 - t1).seconds)

        t1 = t2
        current_step = extract_current_step(line)

    return res


def parse_logfile(fname, separator=" - "):
    with open(fname, "r") as f:
        lines = f.readlines()

    start_text = "Going to reconstruct slices"
    end_text = "Merging reconstructions to"

    rec_log_bounds = []
    for i, line in enumerate(lines):
        if start_text in line:
            start_line = i
        if end_text in line:
            rec_log_bounds.append((start_line, i))


    results = {}
    for bounds in rec_log_bounds:
        start, end = bounds
        results[start] = {}
        res = parse_reconstruction(lines[start:end], separator=separator)
        for step in steps_to_measure:
            if step in res:
                results[start][step] = {
                    "n": len(res[step]),
                    "mean": np.mean(res[step]),
                    "min": np.min(res[step]),
                    "max": np.max(res[step]),
                    "std": np.std(res[step])
                }
    return results



# https://matplotlib.org/stable/gallery/lines_bars_and_markers/horizontal_barchart_distribution.html#sphx-glr-gallery-lines-bars-and-markers-horizontal-barchart-distribution-py
def survey(results, category_names, colormap="tab10"):
    """
    Parameters
    ----------
    results : dict
        A mapping from question labels to a list of answers per category.
        It is assumed all lists contain the same number of entries and that
        it matches the length of *category_names*.
    category_names : list of str
        The category labels.
    """
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap(colormap)(
        # np.linspace(0.15, 0.85, data.shape[1])
        np.linspace(0., 1, data.shape[1])
    )

    fig, ax = plt.subplots(figsize=(9.2, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels, widths, left=starts, height=0.5,
                        label=colname, color=color)

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        ax.bar_label(rects, label_type='center', color=text_color)
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')

    return fig, ax



def plot_results(results, colormap="tab10"):
    # This assumes that the processing steps are always the same between runs!
    plot_values = {}
    for i, result in enumerate(results.values()):
        categories = result.keys()
        plot_values["Run %d" % (i + 1)] = [v["mean"] for v in result.values()]
    fig, ax = survey(plot_values, categories, colormap=colormap)
    plt.show()



