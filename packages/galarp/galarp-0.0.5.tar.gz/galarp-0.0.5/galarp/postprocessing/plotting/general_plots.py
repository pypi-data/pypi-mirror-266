from astropy import units as u
import numpy as np
import os

from .. import utils            # TODO This is horrible, but it works for now. Refactor the top-level utils file.

from matplotlib import pyplot as plt


__all__ = ["get_orbit_data", "k3d_plot", "plot_orbits", "plot_density", "plot_density_3ax"]

def get_orbit_data(o):
    pos, vel = o.pos, o.vel

    x, y, z = pos.xyz.value
    x, y, z = x.T, y.T, z.T

    vx, vy, vz = vel.d_xyz.to(u.km / u.s).value
    vx, vy, vz = vx.T, vy.T, vz.T

    return x, y, z, vx, vy, vz


def k3d_plot(
    orbit_containers,
    bgcolor=0,
    particle_color=0xFFFFFF,
    outname="test_out/orbits.html",
    duration=20,
    transpose=False,
    size=0.1,
    alpha=0.5,
):
    import k3d

    colors = [0xFFFFFF, 0x3387FF, 0xFF3333]

    wind = orbit_containers[0].metadata["WIND"].vector.to(u.km / u.s).value
    wind = np.array([wind[1], wind[0], wind[2]])
    wind /= np.sqrt(np.sum(wind**2))
    wind_length = 2
    wind_x0, wind_y0, wind_z0 = 0, 0, 0

    ell_xs, ell_ys, ell_zs = utils.ellipse_coords(0, 0, 10, 10, 0)

    plot = k3d.plot(
        fps=60,
        axes_helper=0,
        grid_visible=False,
        background_color=0,
    )

    for i, container in enumerate(orbit_containers):
        orbits = container.data

        pos = orbits.pos

        p_x, p_y, p_z = pos.xyz.value
        if transpose:
            p_x, p_y, p_z = p_x.T, p_y.T, p_z.T

        #vmin, vmax = -20, 20

        # v_z[v_z > vmax] = vmax
        # v_z[v_z < vmin] = vmin

        particles = k3d.points(
            np.vstack([p_x[0], p_y[0], p_z[0]]),
            point_size=size,
            color=colors[i],
            opacity=alpha,
        )
        plot += particles

        n_points = p_x.shape[0]

        t_int = np.arange(0, n_points, 1)
        t_sub = np.linspace(0, duration, n_points)

        particles.positions = {
            str(t): np.vstack([p_x[t_int[i]], p_y[t_int[i]], p_z[t_int[i]]]).T
            for i, t in enumerate(t_sub)
        }

    plot += k3d.line(np.vstack([ell_xs, ell_ys, ell_zs]).T, color=0xFFFFFF)

    plot += k3d.line(
        (
            [
                wind_x0,
                wind_x0 + wind[0] * wind_length,
                wind_y0,
                wind_y0 + wind[1] * wind_length,
                wind_z0,
                wind_z0 + wind[2] * wind_length,
            ]
        ),
        color=particle_color,
    )
    plot.display()

    with open(outname, "w") as fp:
        fp.write(plot.get_snapshot())


def plot_orbits(
    data,
    wind=None,
    shadow=None,
    plot_dir="plots/",
    R_plot=15,
    zrange=(-5, 15),
    title=None,
    plot_title="orbits",
):
    os.makedirs(plot_dir, exist_ok=True)

    fig, ax = plt.subplots(1, 3, figsize=(12, 5))

    pos = data.pos

    x, y, z = pos.xyz
    x, y, z = x.T, y.T, z.T

    for i in range(len(x)):
        ax[0].plot(x[i], y[i], color="Grey", alpha=0.3)
        ax[1].plot(x[i], z[i], color="Grey", alpha=0.3)
        ax[2].plot(y[i], z[i], color="Grey", alpha=0.3)

    ax[0].set_xlim(-R_plot, R_plot)
    ax[0].set_ylim(-R_plot, R_plot)
    ax[1].set_xlim(-R_plot, R_plot)
    ax[1].set_ylim(zrange[0], zrange[1])
    ax[2].set_xlim(-R_plot, R_plot)
    ax[2].set_ylim(zrange[0], zrange[1])

    utils.plot_disk(ax, 10)
    if wind is not None:
        utils.plot_wind_vector(
            wind.vector.value,
            ax,
            length=1,
            loc=(-R_plot + 1, -R_plot + 1, zrange[0] + 1),
            color="black",
        )

    if shadow is not None:
        shadow.plot_shadow(ax=ax)

    if title is not None:
        plt.suptitle(title)

    plt.tight_layout()
    if plot_dir is not None:
        plt.savefig(f"{plot_dir}{title}.pdf")
    else:
        plt.show()



def plot_density(xyz, gridsize=40, outname=None, **kwargs):
    """ Generate hexbin plots of the x-y and x-z particle densities.

    Args:
        gridsize (int): Number of bins in the hexbin plots.
        outname (str): Filename for saving the output plot. Will just run plt.show() if None.
    """
    figsize = kwargs.get("figsize", (8, 5))
    Rmax = kwargs.get("Rmax", 15)
    zmax = kwargs.get("zmax", 3)
    cmap = kwargs.get("cmap", "inferno")

    x, y, z = xyz
    lim = (-Rmax * 1.1, Rmax * 1.1)
    gridsize_z = int(gridsize * zmax / Rmax)

    fig, ax = plt.subplots(1, 2, figsize=figsize)

    hist1 = ax[0].hexbin(x, y, bins="log", cmap=cmap, gridsize=gridsize)
    hist2 = ax[1].hexbin(x, z, bins="log", cmap=cmap, gridsize=(gridsize, gridsize_z))
    
    for axis in ax.flatten():
        axis.set(xlim=lim, ylim=lim)

    ax[0].set_xlabel("x [kpc]")
    ax[0].set_ylabel("y [kpc]")
    ax[1].set_xlabel("x [kpc]")
    ax[1].set_ylabel("z [kpc]")

    plt.colorbar(mappable=hist1, ax=ax[0], location="top")
    plt.colorbar(mappable=hist2, ax=ax[1], location="top")

    plt.tight_layout()
    
    if outname is not None:
        plt.savefig(outname)
    else:
        plt.show()


def plot_density_3ax(xyz, gridsize=40, outname=None, **kwargs):
    """ Generate hexbin plots for all 3 principle axes of the particle densities.

    Args:
        gridsize (int): Number of bins in the hexbin plots.
        outname (str): Filename for saving the output plot. Will just run plt.show() if None.
    """
    figsize = kwargs.get("figsize", (12, 5))
    Rmax = kwargs.get("Rmax", 15)
    zmax = kwargs.get("zmax", 3)
    cmap = kwargs.get("cmap", "inferno")

    x, y, z = xyz
    lim = (-Rmax * 1.1, Rmax * 1.1)
    gridsize_z = int(gridsize * zmax / Rmax)

    fig, ax = plt.subplots(1, 3, figsize=figsize)

    hist1 = ax[0].hexbin(x, y, bins="log", cmap=cmap, gridsize=gridsize)
    hist2 = ax[1].hexbin(x, z, bins="log", cmap=cmap, gridsize=(gridsize, gridsize_z))
    hist3 = ax[2].hexbin(y, z, bins="log", cmap=cmap, gridsize=(gridsize, gridsize_z))

    for axis in ax.flatten():
        axis.set(xlim=lim, ylim=lim)

    ax[0].set_xlabel("x [kpc]")
    ax[0].set_ylabel("y [kpc]")
    ax[1].set_xlabel("x [kpc]")
    ax[1].set_ylabel("z [kpc]")
    ax[2].set_xlabel("y [kpc]")
    ax[2].set_ylabel("z [kpc]")

    plt.colorbar(mappable=hist1, ax=ax[0], location="top")
    plt.colorbar(mappable=hist2, ax=ax[1], location="top")
    plt.colorbar(mappable=hist3, ax=ax[2], location="top")

    plt.tight_layout()
    
    if outname is not None:
        plt.savefig(outname)
    else:
        plt.show()