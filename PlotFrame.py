import matplotlib
import Tkinter as tk
matplotlib.use('TkAgg')

import numpy as np
from Utils import Utils

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler


from matplotlib.figure import Figure as mpl_Figure

class PlotFrame(tk.Frame):
	def __init__(self, parent, mainWindow, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.mainWindow = mainWindow
		
		k = 1.5
		self.width = k*4.375
		self.height = k*2.75
		self.figure = mpl_Figure(figsize=(self.width, self.height), dpi=120, linewidth=0.1)
		self.plot = self.figure.add_subplot(111)
		
		self.test_x_axis = np.arange(1,602)
		self.x_axis = None
		
		self.canvas = FigureCanvasTkAgg(self.figure, master=self)
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
	
	def set_data_TEST(self, data):
		self.plot.plot(self.test_x_axis, data)
		self.canvas.draw()
		print "Plotted."
		
	def set_plot_data(self, data, fa, fb, aunits):
		utils = Utils()
		self.plot.cla()
		(value_FB, scale_FB) = utils.long_to_autoScale(fb)
		value_FB = float(value_FB)
		
		value_FA = utils.long_to_scale(fa, scale_FB)
		value_FA = float(value_FA)
		
		self.x_axis = np.linspace(value_FA,value_FB,601) # 8563E uses always 601 points of data
		
		
		self.plot.set_ylabel(aunits)
		self.plot.set_xlabel(scale_FB+"Hz")
		self.plot.plot(self.x_axis, data)
		
		self.canvas.draw()
		print "Plotted."
	
	def set_plot_data_only(self,data):
		self.plot.cla()
		
		self.plot.set_ylabel(aunits)
		self.plot.set_xlabel(scale_FB+"Hz")
		self.plot.plot(self.x_axis, data)
		
		self.canvas.draw()
		print "Fast plotted."
		
	def save_image(self, path):
		self.figure.savefig(path)
		