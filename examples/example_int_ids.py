import os

import numpy as np
from astropy.io import fits
from scipy.signal import find_peaks

from rascal.calibrator import Calibrator
from rascal.atlas import Atlas
from rascal import util

# Load the LT SPRAT data
base_dir = os.path.dirname(os.path.abspath(__file__))
spectrum2D = fits.open(
    os.path.join(base_dir, "data_int_ids/int20180101_01355922.fits.fz")
)[1].data

# Collapse into 1D spectrum between row 110 and 120
spectrum = np.flip(spectrum2D.mean(1), 0)

# Identify the peaks
peaks, _ = find_peaks(spectrum, prominence=10, distance=5, threshold=None)
peaks = util.refine_peaks(spectrum, peaks, window_width=5)

# Initialise the calibrator
c = Calibrator(peaks, spectrum=spectrum)
c.plot_arc()
c.set_hough_properties(
    num_slopes=10000,
    range_tolerance=500.0,
    xbins=200,
    ybins=200,
    min_wavelength=2500.0,
    max_wavelength=4600.0,
)
c.set_ransac_properties(sample_size=8, top_n_candidate=10)

atlas = Atlas(
    elements=["Cu", "Ne", "Ar"],
    min_intensity=5,
    pressure=80000.0,
    temperature=285.0,
    range_tolerance=500,
)
c.set_atlas(atlas)

c.do_hough_transform()

# Run the wavelength calibration
(
    best_p,
    matched_peaks,
    matched_atlas,
    rms,
    residual,
    peak_utilisation,
    atlas_utilisation,
) = c.fit(max_tries=100, fit_deg=4)

# Plot the solution
c.plot_fit(
    best_p, spectrum, plot_atlas=True, log_spectrum=False, tolerance=5.0
)

# Show the parameter space for searching possible solution
c.plot_search_space()

print("Stdev error: {} A".format(residual.std()))
print("Peaks utilisation rate: {}%".format(peak_utilisation * 100))
print("Atlas utilisation rate: {}%".format(atlas_utilisation * 100))
