import numpy as np
import matplotlib.pyplot as plt
from nabu.estimation.tilt import CameraTilt
import fabio

def BOLD(x):
    pass


def nabu_align():
    with fabio.open('/tmp/bl/scan0001/edgetwinmic_0000.h5') as f:
        flat = f.data
    with fabio.open('/tmp/bl/scan0002/edgetwinmic_0000.h5') as f:
        dark = f.data
    with fabio.open('/tmp/bl/scan0003/edgetwinmic_0000.h5') as f:
        proj0 = f.data
    with fabio.open('/tmp/bl/scan0003/edgetwinmic_0001.h5') as f:
        proj180 = f.data
    radio0 = (proj0.astype(float) - dark.astype(float)) / (
            flat.astype(float) - dark.astype(float)
    )
    radio180 = (proj180.astype(float) - dark.astype(float)) / (
            flat.astype(float) - dark.astype(float)
    )
    radio180_flip = np.fliplr(radio180.copy())
    tilt_calc = CameraTilt()
    # enable calculation results plotting
    tilt_calc.verbose = True
    plt.subplot(1, 2, 1)
    plt.imshow(radio0)
    plt.subplot(1, 2, 2)
    plt.imshow(radio180_flip)
    plt.show()
    pixel_cor, camera_tilt = tilt_calc.compute_angle(radio0, radio180_flip)#, method="fft-polar")
    print("CameraTilt: pixel_cor = %f" % pixel_cor)
    pos_cor = 0.0003632 * pixel_cor

    print(BOLD(f"Lateral alignment position correction in mm: {-pos_cor:>10.5f}"))
    print(
        BOLD(
            f"Camera tilt in deg : {camera_tilt:35.5f}\n"
        )
    )

    input("Press any key")
    plt.close("all")

if __name__ == "__main__":
    nabu_align()
