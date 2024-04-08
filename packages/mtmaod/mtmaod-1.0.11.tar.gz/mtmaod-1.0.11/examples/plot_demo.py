from mtmaod.plot import density_chart
import numpy as np


if __name__ == "__main__":
    x = np.arange(0, 2, 0.01)
    y = np.arange(0, 2, 0.01)

    # Note: if use non-GUI backend, then save_path must be specified
    # from mtmaod import mpl
    # mpl.use("Agg")

    # save path
    density_chart(x=x, y=y, save_path="demo_scatter.png", type="scatter", bins=25, dpi=300)
    density_chart(x=x, y=y, save_path="demo_pcolormesh.png", type="grid", bins=10, dpi=300, style="single_bold")
    density_chart(x=x, y=y, save_path="demo_kernels.png", type="kernels", dpi=300)

    # show in GUI
    density_chart(x=x, y=y, type="kernels", dpi=300)
