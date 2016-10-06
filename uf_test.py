# Import necessary libraries.
import numpy
import pyart
import matplotlib as pl

# Load supercell test file.

uf_test = pyart.io.read_uf('corrected_vel_173943ARMOR.uf')
uf_test.info('compact')

# Intialize display class for radar.

uf_test_display = pyart.graph.RadarDisplay(uf_test)

# This displays the PPI scan.
uf_test_display.plot('reflectivity')

pl.pyplot.show()


