import os

import numpy as np
from matplotlib import pyplot as plt, colors
from matplotlib.cm import ScalarMappable
from matplotlib.ticker import LogLocator, LogFormatter
from matplotlib.tri import Triangulation

from examples.contact_sensitivity.sensitivity_model_contact import get_rectangular_matrix_from_upper_triu


def generate_tornado_plot(sim_obj, labels, prcc: np.ndarray, p_val, filename: str, title=None):
    """
    Generate a tornado plot to visualize the Partial Rank Correlation Coefficient (PRCC) values.
    """
    prcc = np.round(prcc, 3)
    ys = range(len(labels))[::-1]

    p_val_colors = ['green', 'yellow', 'red']
    thresholds = [0, 0.01, 0.1, 1]
    cmap = colors.ListedColormap(p_val_colors)
    norm = colors.BoundaryNorm(boundaries=thresholds, ncolors=cmap.N, clip=True)

    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, orientation='vertical', shrink=0.7, pad=0.02, ax=plt.gca())
    cbar.set_label('p-values')

    # Plot the bars one by one
    for y, value in zip(ys, prcc):
        facecolor = cmap(norm((p_val[len(prcc) - 1 - y])))
        plt.broken_barh(
            [(value if value < 0 else 0, abs(value))],
            (y - 0.4, 0.8),
            facecolors=[facecolor, facecolor],
            edgecolors=['black', 'black'],
            linewidth=1,
        )

        if value != 0:
            x = (value / 2) if np.abs(value) >= 0.2 else (- np.sign(value) * 0.1)
        else:
            x = -0.1
        plt.text(x, y - 0.01, str(value), va='center', ha='center')

    plt.axvline(0, color='black')

    # Position the x-axis on the top, hide all the other spines (=axis lines)
    axes = plt.gca()  # (gca = get current axes)
    axes.spines['left'].set_visible(False)
    axes.spines['right'].set_visible(False)
    axes.spines['bottom'].set_visible(False)
    axes.xaxis.set_ticks_position('top')

    # Display age groups next to y axis

    plt.yticks(ys, labels)

    # Set the portion of the x- and y-axes to show
    plt.xlim(-1.1, 1.1)
    plt.ylim(-1, len(labels))

    if title is not None:
        plt.title(title)
    plot_path = os.path.join(sim_obj.folder_name, f"prcc_plots/prcc_tornado_plot_{filename}.pdf")
    plt.savefig(plot_path, format="pdf", bbox_inches='tight')
    plt.show()


def get_age_groups():
    return [f'{5 * age_start}-{5 * age_start + 5}' if 5 * age_start != 75 else '75+' for age_start in range(16)]


def construct_triangle_grid(n_age):
    # vertices of the little squares
    xv, yv = np.meshgrid(np.arange(-0.5, n_age), np.arange(-0.5, n_age))
    # centers of the little square
    xc, yc = np.meshgrid(np.arange(0, n_age), np.arange(0, n_age))
    x = np.concatenate([xv.ravel(), xc.ravel()])
    y = np.concatenate([yv.ravel(), yc.ravel()])
    triangles_prcc = [(i + j * (n_age + 1), i + 1 + j * (n_age + 1),
                       i + (j + 1) * (n_age + 1))
                      for j in range(n_age) for i in range(n_age)]
    triangles_p = [(i + 1 + j * (n_age + 1), i + 1 + (j + 1) *
                    (n_age + 1),
                    i + (j + 1) * (n_age + 1))
                   for j in range(n_age) for i in range(n_age)]
    triang = [Triangulation(x, y, triangles, mask=None)
              for triangles in [triangles_prcc, triangles_p]]
    return triang


def get_prcc_and_p_values(n_age, prcc_vector, p_values):
    prcc_mtx = np.array(get_rectangular_matrix_from_upper_triu(
        rvector=prcc_vector,
        matrix_size=n_age))
    p_values_mtx = np.array(get_rectangular_matrix_from_upper_triu(
        rvector=p_values,
        matrix_size=n_age))
    values = np.array([prcc_mtx, p_values_mtx])
    return values


def plot_prcc_p_values_as_heatmap(n_age, prcc_vector, p_values, filename_to_save, plot_title):
    p_value_cmap = colors.ListedColormap(['Orange', 'red', 'darkred'])
    cmaps = ["Greens", p_value_cmap]

    log_norm = colors.LogNorm(vmin=1e-3, vmax=1e0)  # used for p_values
    norm = plt.Normalize(vmin=0, vmax=1)  # used for PRCC_values

    fig, ax = plt.subplots()
    triang = construct_triangle_grid(n_age=n_age)
    mask = get_prcc_and_p_values(n_age=n_age, prcc_vector=prcc_vector, p_values=p_values)
    images = [ax.tripcolor(t, np.ravel(val), cmap=cmap, ec="white")
              for t, val, cmap in zip(triang,
                                      mask, cmaps)]

    fig.colorbar(images[0], ax=ax, shrink=0.7, aspect=20 * 0.7)  # for the prcc values
    cbar_pval = fig.colorbar(images[1], ax=ax, shrink=0.7, aspect=20 * 0.7, pad=0.1)

    images[1].set_norm(norm=log_norm)
    images[0].set_norm(norm=norm)

    locator = LogLocator()
    formatter = LogFormatter()
    cbar_pval.locator = locator
    cbar_pval.formatter = formatter
    cbar_pval.update_normal(images[1])

    ax.set_xticks(range(n_age))
    ax.set_yticks(range(n_age))
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    ax.set(frame_on=False)
    plt.gca().grid(which='minor', color='gray', linestyle='-', linewidth=1)
    ax.margins(x=0, y=0)
    ax.set_aspect('equal', 'box')
    plt.tight_layout()
    plt.title(plot_title, y=1.03, fontsize=25)
    plt.title(plot_title, y=1.03, fontsize=25)
    plt.savefig(filename_to_save, format="pdf",
                bbox_inches='tight')
    plt.show()
    plt.close()
