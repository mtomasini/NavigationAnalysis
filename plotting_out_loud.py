import pandas as pd
import matplotlib.pyplot as plt

from plotting import plot_towing, plot_towing_by_weight, plot_towing_by_orientation

towing_data = pd.read_excel("towing_data.ods", engine="odf", header=0)
towing_data

plot_towing_by_orientation(towing_data, "Enora", 2)

plt.show()