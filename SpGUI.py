import Tkinter as tk
import tkMessageBox
import tkFileDialog
import ttk
import time
import sys
import HP8563E as hp
import PlotFrame as pf
from Utils import Utils
import os

class InstrumentWindow(tk.Toplevel):
	def __init__(self, parent):
		tk.Toplevel.__init__(self)
		self.parent = parent
		self.title("Select instrument")
		self.f = tk.Frame(self)
		self.f.pack(padx=5, pady=10)
		self.label_top = tk.Label(self.f, text="Look in the following list"+
											  " the\nGPIB address of your instrument")
		self.label_top.pack()
		
		self.hp = self.parent.hp
		self.selected = "None"
		
		self.resources = self.hp.get_resources()
		self.instrument_list(self.resources)
		
		self.label_bottom = tk.Label(self.f, text="Currently selected: "+self.selected)
		
		tk.Button(self.f,text="Pick instrument", command=self.set_instrument).pack()
		
	def instrument_list(self, values):
		#self.inst_var = tk.StringVar()
		#print "self.inst_var ", type(self.inst_var), repr(self.inst_var)
		self.listbox = tk.Listbox(self.f)
		self.listbox.pack()
		for inst in values:
			self.listbox.insert(tk.END, inst)
		
	def set_instrument(self):
		index_selected = self.listbox.curselection()
		selected_inst = self.listbox.get(index_selected)
		print selected_inst,type(selected_inst),repr(selected_inst)
		self.hp.set_instrument(selected_inst)
		self.selected = selected_inst
		
		self.instrument_initialSetup()
		
		self.destroy()
		
	def instrument_initialSetup(self):
		if self.hp.get_FA() < 0:
			self.hp.set_FA("0 Hz")
	
class Menubar(tk.Menu):
	def __init__(self, parent, mainWindow, *args, **kwargs):
		tk.Menu.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		
		#drop menu file
		self.dp_menu_file = tk.Menu(self, tearoff=0)
		self.dp_menu_file.add_command(label="Load CSV and plot",\
									command=mainWindow.data_handler.load_data )
		self.dp_menu_file.add_separator()
		self.dp_menu_file.add_command(label="Save data (.csv)",\
									command=lambda : mainWindow.data_handler.save_data() )
		self.dp_menu_file.add_command(label="Save plot image",\
									command=lambda : mainWindow.data_handler.save_plot() )
		
		#drop menu inst
		self.dp_menu_inst = tk.Menu(self, tearoff=0)
		self.dp_menu_inst.add_command(label="Select Instrument",\
									command=lambda : InstrumentWindow(mainWindow))
		self.dp_menu_inst.add_separator()
		self.dp_menu_inst.add_command(label="Frequency & Amplitude",\
									command=lambda : self.create_FreqBrowserWindow(mainWindow) )
		self.dp_menu_inst.add_command(label="Bandwidth",\
									command=lambda : self.create_BandWidthWindow(mainWindow) )
		self.dp_menu_inst.add_command(label="Sweep",\
									command=lambda : self.create_SweepWindow(mainWindow) )
		self.dp_menu_inst.add_separator()
		self.dp_menu_inst.add_command(label="TEST",\
									command=lambda : self.create_TestWindow(mainWindow) )
									
		#drop menu meas
		self.dp_menu_meas = tk.Menu(self, tearoff=0)
		self.dp_menu_meas.add_command(label="Get Single Measurement",\
									command=lambda : mainWindow.data_handler.plot_trace() )
		self.dp_menu_meas.add_command(label="Get Continuous Measurement",\
									command=lambda : self.create_ContMeasWindow(mainWindow) )
									
		self.add_cascade(label="File", menu=self.dp_menu_file)		
		self.add_cascade(label="Instrument", menu=self.dp_menu_inst)
		self.add_cascade(label="Measurement", menu=self.dp_menu_meas)
	
	def create_FreqBrowserWindow(self, mainWindow):
		mainWindow.freqBrowser_window = FreqBrowserWindow(mainWindow.parent, mainWindow)
		mainWindow.freqBrowser_window.lift()
		
	def create_BandWidthWindow(self, mainWindow):
		mainWindow.bandWidthBrowser_window = BandWidthWindow(mainWindow.parent, mainWindow)
		mainWindow.bandWidthBrowser_window.lift()
		
	def create_SweepWindow(self, mainWindow):
		mainWindow.sweep_window = SweepWindow(mainWindow.parent, mainWindow)
		mainWindow.sweep_window.lift()
	
	def create_ContMeasWindow(self, mainWindow):
		mainWindow.contMeas_window = ContMeasWindow(mainWindow.parent, mainWindow)
		mainWindow.contMeas_window.lift()
	
	def create_TestWindow(self, mainWindow):
		mainWindow.test_window = TestWindow(mainWindow.parent, mainWindow)
		mainWindow.test_window.lift()
		
class Statusbar(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		
class StatusBarIndicator:
    #pk=-1 -> pack side=LEFT;    0 -> fill=X;    1 -> side=RIGHT
    def __init__(self, frame, ancho,pk=-1):
        self.label = Label(frame, bd=2, relief=RIDGE, anchor=W, width=ancho)
        if pk == -1:
            self.label.pack(side=LEFT)
        elif pk == 0:
            self.label.pack(fill=X)
        else:
            self.label.pack(side=RIGHT)

    def set(self, texto):
        self.label.config(text=texto)

    def clear(self):
        self.label.config(text="")

		
class FreqBrowserWindow(tk.Toplevel):
	def __init__(self, parent, mainWindow, *args, **kwargs):
		'''
		if not mainWindow.hp.is_initialized():
			tkMessageBox.showerror("Error", "Instrument not initialized")
			return
			#pass
		'''
		tk.Toplevel.__init__(self, parent, *args, **kwargs)
		self.title("Frequency & Amplitude")
		#self.label_test = tk.Label(self, text="This is a test. Hallo Welt!")
		#self.label_test.pack()
		
		self.mainWindow = mainWindow
		
		self.hp = mainWindow.hp
		self.utils = Utils() #expressions
		
		#vars Freq
		self.var_freqType = tk.IntVar()
		
		self.var_FA = tk.StringVar()
		self.var_FB = tk.StringVar()
		self.var_scaleFA = tk.StringVar()
		self.var_scaleFB = tk.StringVar()
		
		self.var_CF = tk.StringVar()
		self.var_SP = tk.StringVar()
		self.var_scaleCF = tk.StringVar()
		self.var_scaleSP = tk.StringVar()
		
		self.populate_widgetsFreq()
		
		#vars Amp
		
		self.var_loglin = tk.IntVar()
		self.var_logdBDiv = tk.StringVar()
		
		self.populate_widgetsAmp()
	
	def populate_widgetsFreq(self):
		self.frameFreq = tk.LabelFrame(self,text="Frequency Browsing")
		self.frameFreq.pack(padx=5, pady=5)
		
		# Freq innerFrames
		self.frameFreqLeft = tk.Frame(self.frameFreq)
		self.frameFreqLeft.grid(row=0, column=0, padx=5)
		
		sep1 = ttk.Separator(self.frameFreq, orient="vertical")
		sep1.grid(row=0, column=1, sticky="ns")
		
		self.frameFreqRight = tk.Frame(self.frameFreq)
		self.frameFreqRight.grid(row=0, column=2, padx=5)
		
		# freq type selectors
		rad1 = tk.Radiobutton(self.frameFreqLeft, text="Start-Stop", variable=self.var_freqType, value=1)
		rad1.grid(row=0, column=0, columnspan=3)
		
		rad2 = tk.Radiobutton(self.frameFreqRight, text="Center-Span", variable=self.var_freqType, value=2	)
		rad2.grid(row=0, column=0, columnspan=3)
		
		self.var_freqType.set(1) #set default
		# Start/stop
		tk.Label(self.frameFreqLeft, text="Start Freq.").grid(row=1, column=0)
		self.fa = tk.Spinbox(self.frameFreqLeft, textvariable=self.var_FA, from_=0, to=10000, increment=0.1, width=6)
		self.fa.grid(row=1,column=1,pady=5)
		
		tk.Label(self.frameFreqLeft, text="Stop Freq.").grid(row=2, column=0)
		self.fb = tk.Spinbox(self.frameFreqLeft, textvariable=self.var_FB, from_=0, to=10000, increment=0.1, width=6)
		self.fb.grid(row=2,column=1,pady=5)
		
		self.magnitudes = tuple(["Hz","KHz","MHz","GHz"])
		self.scaleFA = ttk.Combobox(self.frameFreqLeft, textvariable=self.var_scaleFA, state='readonly', width=4)
		self.scaleFA['values'] = self.magnitudes
		self.scaleFA.grid(row=1,column=2,pady=5)
			
		self.scaleFB = ttk.Combobox(self.frameFreqLeft, textvariable=self.var_scaleFB, state='readonly', width=4)
		self.scaleFB['values'] = self.magnitudes
		self.scaleFB.grid(row=2,column=2,pady=5)
		
		# Center/span
		tk.Label(self.frameFreqRight, text="Center Freq.").grid(row=1, column=0)
		self.cf = tk.Spinbox(self.frameFreqRight, textvariable=self.var_CF, from_=0, to=10000, increment=0.1, width=7)
		self.cf.grid(row=1,column=1,pady=5)
		
		tk.Label(self.frameFreqRight, text="Span").grid(row=2, column=0)
		self.sp = tk.Spinbox(self.frameFreqRight, textvariable=self.var_SP, from_=0, to=10000, increment=0.1, width=7)
		self.sp.grid(row=2,column=1,pady=5)
		
		self.scaleCF = ttk.Combobox(self.frameFreqRight, textvariable=self.var_scaleSP, state='readonly', width=4)
		self.scaleCF['values'] = self.magnitudes
		self.scaleCF.current(0)
		self.scaleCF.grid(row=1,column=2,pady=5)
			
		self.scaleSP = ttk.Combobox(self.frameFreqRight, textvariable=self.var_scaleCF, state='readonly', width=4)
		self.scaleSP['values'] = self.magnitudes
		self.scaleSP.current(0)
		self.scaleSP.grid(row=2,column=2,pady=5)
		
		## Default values same as current
		self.update_freq_values()
		
		
		#EndFreq
		
		set_freq_button = tk.Button(self.frameFreq, text="Set Frequency Range", command=self.set_frequency )
		set_freq_button.grid(row=1, columnspan=3, pady=(5,10))
		
		# lowerbuttons
		sep2 = ttk.Separator(self.frameFreq, orient="horizontal")
		sep2.grid(row=2, column=0, columnspan=3, sticky="ew")
		
		self.frameFreqLower = tk.Frame(self.frameFreq)
		self.frameFreqLower.grid(row=3, column=0, pady=5)
		
		tk.Button(self.frameFreqLower, text="Full Span", command=self.set_fullSpan).grid(row=0,column=0)
	
	def update_freq_values(self):
		#Start-Stop
		curr_FA = self.hp.get_FA()
		(curr_valueFA, curr_scaleFA) = self.utils.long_to_autoScale(curr_FA)
		
		curr_FB = self.hp.get_FB()
		(curr_valueFB, curr_scaleFB) = self.utils.long_to_autoScale(curr_FB)
		
		self.fa.delete(0, tk.END)
		self.fb.delete(0, tk.END)
		
		self.fa.insert(0,curr_valueFA)
		self.fb.insert(0,curr_valueFB)
		
		index_combobox_FA = self.magnitudes.index(curr_scaleFA+"Hz")
		index_combobox_FB = self.magnitudes.index(curr_scaleFB+"Hz")
		
		self.scaleFA.current(index_combobox_FA)
		self.scaleFB.current(index_combobox_FB)
		
		#Center-Span
		curr_CF= self.hp.get_CF()
		(curr_valueCF, curr_scaleCF) = self.utils.long_to_autoScale(curr_CF)
		
		curr_SP = self.hp.get_SP()
		(curr_valueSP, curr_scaleSP) = self.utils.long_to_autoScale(curr_SP)
		
		self.cf.delete(0, tk.END)
		self.sp.delete(0, tk.END)
		
		self.cf.insert(0,curr_valueCF)
		self.sp.insert(0,curr_valueSP)
		
		index_combobox_CF = self.magnitudes.index(curr_scaleCF+"Hz")
		index_combobox_SP = self.magnitudes.index(curr_scaleSP+"Hz")
		
		self.scaleCF.current(index_combobox_CF)
		self.scaleSP.current(index_combobox_SP)
		
	def set_frequency(self):
		print "begin set_freq"
		type_freq = self.var_freqType.get()
		print "type_freq",type_freq
		if type_freq == 1: #start/stop
			fa = self.var_FA.get()
			units_fa = self.var_scaleFA.get()
			
			fb = self.var_FB.get()
			units_fb = self.var_scaleFB.get()
			
			self.hp.set_FA(fa+units_fa)
			self.hp.set_FB(fb+units_fb)
		elif type_freq == 2: #center/span
			cf = self.var_CF.get()
			units_cf = self.var_scaleCF.get()
			
			sp = self.var_SP.get()
			units_sp = self.var_scaleSP.get()
			
			self.hp.set_CF(cf+units_cf)
			self.hp.set_SP(sp+units_sp)
			
		self.update_freq_values()
	
	def set_fullSpan(self):
		self.hp.set_fullSpan()
		self.update_freq_values()
		
	def populate_widgetsAmp(self):
		self.frameAmp = tk.LabelFrame(self,text="Amplitude")
		self.frameAmp.pack(padx=5, pady=5)
		
		# Amp innerFrames
		self.frameAmpLeft = tk.Frame(self.frameAmp)
		self.frameAmpLeft.grid(row=0, column=0, padx=5)
		
		sep1 = ttk.Separator(self.frameAmp, orient="vertical")
		sep1.grid(row=0, column=1, sticky="ns")
		
		self.frameAmpRight = tk.Frame(self.frameAmp)
		self.frameAmpRight.grid(row=0, column=2, padx=5)
		
		# left frame
		tk.Label(self.frameAmpLeft, text = "Y-axis scale:").grid(row=0, column=0, pady=5)
		
		## log dB/div row
		rad_lg = tk.Radiobutton(self.frameAmpLeft, text="Log", variable=self.var_loglin, value=1,\
								command=self.update_loglin_values)
		rad_lg.grid(row=1, column=0, padx=5, pady=5)
		
		self.log_divs = tuple( map(str, [1,2,5,10]) )
		self.log_scale = ttk.Combobox(self.frameAmpLeft, textvariable=self.var_logdBDiv, state='readonly', width=5)
		self.log_scale['values'] = self.log_divs
		self.log_scale.grid(row=1, column=1, padx=(5,0), pady=5)
		
		tk.Label(self.frameAmpLeft, text="dB/div").grid(row=1, column=2, pady=5)
		
		## linear row
		rad_ln = tk.Radiobutton(self.frameAmpLeft, text="Linear", variable= self.var_loglin, value=2, \
								command=self.update_loglin_values)
		rad_ln.grid(row=2, column=0, padx=5, pady=5)
		
		## set defaults
		self.update_loglin_values()
		
	def update_loglin_values(self):
		log_or_lin = self.hp.get_isLinearOrLog()
		if log_or_lin == "LG":
			self.var_loglin.set(1)
			log_value = self.hp.get_LG()
			current_log = self.log_divs.index(log_value)
			self.log_scale.current(current_log)
		else:
			self.var_loglin.set(2)
		
	def set_loglin(self):
		type_loglin = self.var_loglin.get()
		
		if type_loglin == 1: #Log
			db_per_div = self.var_logdBDiv.get()
			self.hp.set_log(db_per_div)
		elif type_loglin == 2: #Lin
			self.hp.set_linear()
			
		self.update_loglin_values()

class BandWidthWindow(tk.Toplevel):
	def __init__(self, parent, mainWindow, *args, **kwargs):
		'''
		if not mainWindow.hp.is_initialized():
			tkMessageBox.showerror("Error", "Instrument not initialized")
			return
			#pass
		'''
		tk.Toplevel.__init__(self, parent, *args, **kwargs)
		self.title("Bandwidth")
		#self.label_test = tk.Label(self, text="This is a test. Hallo Welt!")
		#self.label_test.pack()
		
		self.mainWindow = mainWindow
		
		self.hp = mainWindow.hp
		self.utils = Utils() #expressions
		
		#vars BW		
		self.var_VBW = tk.StringVar()
		self.var_RBW = tk.StringVar()
		
		self.var_scaleVBW = tk.StringVar()
		self.var_scaleRBW = tk.StringVar()
		
		
		self.populate_widgetsBW()
	
	def populate_widgetsBW(self):
		self.frameBW = tk.LabelFrame(self,text="Measurement Bandwidth")
		self.frameBW.pack(padx=5, pady=5)
		
		# VBW & RBW
		tk.Label(self.frameBW, text="Video Bandwidth").grid(row=1, column=0)
		self.vbw = tk.Spinbox(self.frameBW, textvariable=self.var_VBW, from_=0, to=10000, increment=0.1, width=6)
		self.vbw.grid(row=1,column=1,pady=5)
		
		tk.Label(self.frameBW, text="Resolution Bandwidth").grid(row=2, column=0)
		self.rbw = tk.Spinbox(self.frameBW, textvariable=self.var_RBW, from_=0, to=10000, increment=0.1, width=6)
		self.rbw.grid(row=2,column=1,pady=5)
		
		self.magnitudes = tuple(["Hz","KHz","MHz","GHz"])
		self.scaleVBW = ttk.Combobox(self.frameBW, textvariable=self.var_scaleVBW, state='readonly', width=4)
		self.scaleVBW['values'] = self.magnitudes
		self.scaleVBW.grid(row=1,column=2,pady=5)
			
		self.scaleRBW = ttk.Combobox(self.frameBW, textvariable=self.var_scaleRBW, state='readonly', width=4)
		self.scaleRBW['values'] = self.magnitudes
		self.scaleRBW.grid(row=2,column=2,pady=5)
			
		## Default values same as current
		self.update_bw_values()
		
		#EndFreq
		set_vbw_button = tk.Button(self.frameBW, text="Set VBW", command=self.set_vbw )
		set_vbw_button.grid(row=1, column=3,padx=5)#, pady=(5,10))
		
		set_rbw_button = tk.Button(self.frameBW, text="Set RBW", command=self.set_rbw )
		set_rbw_button.grid(row=2, column=3,padx=5)#, pady=(5,10))
	
	def update_bw_values(self):
		# VBW & RBW
		curr_VBW = self.hp.get_videoBW()
		(curr_valueVBW, curr_scaleVBW) = self.utils.long_to_autoScale(curr_VBW)
		
		curr_RBW = self.hp.get_resBW()
		(curr_valueRBW, curr_scaleRBW) = self.utils.long_to_autoScale(curr_RBW)
		
		self.vbw.delete(0, tk.END)
		self.rbw.delete(0, tk.END)
		
		self.vbw.insert(0,curr_valueVBW)
		self.rbw.insert(0,curr_valueRBW)
		
		index_combobox_VBW = self.magnitudes.index(curr_scaleVBW+"Hz")
		index_combobox_RBW = self.magnitudes.index(curr_scaleRBW+"Hz")
		
		self.scaleVBW.current(index_combobox_VBW)
		self.scaleRBW.current(index_combobox_RBW)
		
	def set_vbw(self):
		vbw = self.var_VBW.get()
		units_vbw = self.var_scaleVBW.get()
		
		self.hp.set_VB(vbw+units_vbw)
			
		self.update_bw_values()
		
	def set_rbw(self):
		rbw = self.var_RBW.get()
		units_rbw = self.var_scaleRBW.get()
		
		self.hp.set_RB(rbw+units_rbw)
			
		self.update_bw_values()
		
class ContMeasWindow(tk.Toplevel):
	def __init__(self, parent, mainWindow, *args, **kwargs):
		if not mainWindow.hp.is_initialized():
			tkMessageBox.showerror("Error", "Instrument not initialized")
			return
			#pass
		tk.Toplevel.__init__(self, parent, *args, **kwargs)
		self.title("Continuous Measurement")
		#self.label_test = tk.Label(self, text="This is a test. Hallo Welt!")
		#self.label_test.pack()
		
		self.mainWindow = mainWindow
		
		self.hp = mainWindow.hp
		self.utils = Utils() #expressions
		
		
		self.var_fixedTimeParam = tk.StringVar() #radiobutton_check vars
		self.var_step = tk.StringVar()
		self.var_time = tk.StringVar()
		self.var_number = tk.StringVar()
		
	"""
	Do more
	"""
	def populate_widgetsOptions(self):
		self.frameFixed = tk.LabelFrame(self, "Predefine number of captures")
		
		tk.Radiobutton(self.frameFixed, text="Time Step", textvariable=self.var_fixedTimeParam, value="step").grid(row=0, column=0, pady=5)
		tk.Radiobutton(self.frameFixed, text="Time Interval", textvariable=self.var_fixedTimeParam, value="time").grid(row=1, column=0, pady=5)
		tk.Radiobutton(self.frameFixed, text="# of Captures", textvariable=self.var_fixedTimeParam, value="number").grid(row=2, column=0, pady=5)
		
		tk.Spinbox(self.frameFixed, textvariable=self.var_step, from_=0, to=10000, increment=0.1, width=6)
		tk.Spinbox(self.frameFixed, textvariable=self.var_time, from_=0, to=10000, increment=0.1, width=6)
		tk.Spinbox(self.frameFixed, textvariable=self.var_number, from_=1, to=10000, increment=1, width=6)

class SweepWindow(tk.Toplevel):
	def __init__(self, parent, mainWindow, *args, **kwargs):
		if not mainWindow.hp.is_initialized():
			tkMessageBox.showerror("Error", "Instrument not initialized")
			return
			pass
		tk.Toplevel.__init__(self, parent, *args, **kwargs)
		
		self.title("Sweep")
		
		self.mainWindow = mainWindow
		self.hp = mainWindow.hp
		
		if mainWindow.sweepMode is None:
			mainWindow.set_sweepMode("CONT")
			
		self.var = tk.StringVar()
		self.var.set(mainWindow.sweepMode)
		
		self.populate_widgetsSweepMode()
		
	def populate_widgetsSweepMode(self):
		self.frameSMode = tk.LabelFrame(self,text="Sweep Mode")
		self.frameSMode.pack(padx=5, pady=5)
		
		tk.Radiobutton(self.frameSMode, text="Continuous Sweep (CONTS)", variable=self.var, value="CONT",\
								indicatoron=0, command=self.update_sweepMode).grid(row=0,column=0)
		tk.Radiobutton(self.frameSMode, text="Single Sweep (SNGLS)", variable=self.var, value="SING",\
								indicatoron=0, command=self.update_sweepMode).grid(row=1,column=0)
	
	def update_sweepMode(self):
		var_value = self.var.get()
		self.hp.set_sweepMode(var_value)
		self.mainWindow.sweepMode = var_value
			
class TestWindow(tk.Toplevel):
	def __init__(self, parent, mainWindow, *args, **kwargs):
		if not mainWindow.hp.is_initialized():
			#tkMessageBox.showerror("Error", "Instrument not initialized")
			#return
			pass
		tk.Toplevel.__init__(self, parent, *args, **kwargs)
		self.title("TEST")
		
		self.mainWindow = mainWindow
		self.data_handler = mainWindow.data_handler
		
		
		self.var_n_of_caps = tk.StringVar()
		self.var_delay = tk.StringVar()
		
		tk.Label(self, text="No. of captures").grid(row=0, column=0)
		tk.Entry(self, textvariable=self.var_n_of_caps).grid(row=0, column=1)
		tk.Label(self, text="Delay").grid(row=1, column=0)
		tk.Entry(self, textvariable=self.var_delay).grid(row=1, column=1)
		
		tk.Button(self, text="Run test", command = self.runTest).grid(row=2, column=1)
		
	def runTest(self):
		
		n_of_caps = int(self.var_n_of_caps.get())
		delay = float(self.var_n_of_caps.get())
		"""
		self.data_handler.get_continuous_data(n_of_caps, delay)
		
		print "self.data_handler.data =", repr(self.data_handler.data)
		"""
		self.data_handler.TEST_continuous_data(n_of_caps, delay)
		
		print "data = ", repr(self.data_handler.data)
		
class Data:
	def __init__(self, parent):
		self.parent = parent
		self.hp = parent.hp
		self.plot_frame = parent.plot_frame
		self.data = None
		self.fa = None
		self.fb = None
		self.aunits = None
		
	def plot_trace_test(self):
		self.data = self.hp.get_trace()
		self.parent.plot_frame.set_data_TEST(self.data)
	

	def append_data(self, time):
		'''Assumes that all other required variables are already
		instantiated. To be used when saving continuous data.'''
		new_data = [time]
		new_data.extend(self.hp.get_trace())
		#print "self.data = ",repr(self.data)
		self.data.append(new_data)
	
		
	def get_continuous_data(self, number_of_captures, delay=0):
		self.get_params()
	
		old_sweepMode = self.sweepMode
		self.parent.set_sweepMode("SING")
		
		t_0 = time.time()
		print t_0
		self.get_data(update_params=False)
		
		self.plot_self_data()
		
		delta_t_2 = time.time() - t_0
		print "dt_", delta_t_2
		delay_justOnce = max(0, delay - delta_t_2)
		print "delay_jO", delay_justOnce
		#Desired delay between measurements has to account for the time
		#that takes acquiring the data from the Analyzer (and cannot be
		#negative).
		
		old_self_data = self.data
		first_meas = [0]
		first_meas.extend(old_self_data) #first value: time
		self.data = [first_meas] #now self.data is a list of measurements
		#self.data = [[0, d_1, ..., d_601], [t_2, d_2, ..., d_601], ... ]
		
		time.sleep(delay_justOnce)
		
		n = 1
		t_i_old = 0 # t_0 - t_0
		while n < number_of_captures:
			t_i = time.time() - t_0
			print "t_i", t_i
			
			self.append_data(t_i)
			
			delta_t = t_i - t_i_old
			print "delta_t", delta_t
			t_i_old = t_i
		
			print n, delta_t, "========="
			
			this_delay = max(0, delay - delta_t)
			print "this_delay", this_delay
			time.sleep(this_delay)
			
			n+=1
		
		print n,"captures -", self.data[-1][0],"seconds"
		
		self.parent.set_sweepMode(old_sweepMode)
	
	def TEST_continuous_data(self, number_of_captures, delay=0):
		self.get_params()
		
		t_0 = time.time()
		print "t_0 = ", t_0
		self.get_data(update_params=False)
		
		self.plot_self_data()
		
		delta_t_2 = time.time() - t_0
		print "dt_", delta_t_2
		delay_justOnce = max(0, delay - delta_t_2)
		print "delay_jO", delay_justOnce
		#Desired delay between measurements has to account for the time
		#that takes acquiring the data from the Analyzer (and cannot be
		#negative).
		
		old_self_data = self.data
		first_meas = [0]
		first_meas.extend(old_self_data) #first value: time
		self.data = [first_meas] #now self.data is a list of measurements
		#self.data = [[0, d_1, ..., d_601], [t_2, d_2, ..., d_601], ... ]
		
		time.sleep(delay_justOnce)
		
		n = 1
		t_i_old = 0 # t_0 - t_0
		while n < number_of_captures:
			t_i = time.time() - t_0
			print "t_i", t_i
			
			self.append_data(t_i)
			
			delta_t = t_i - t_i_old
			print "delta_t", delta_t
			t_i_old = t_i
		
			print n, delta_t, "========="
			
			this_delay = max(0, delay - delta_t)
			print "this_delay", this_delay
			time.sleep(this_delay)
			
			n+=1
		
		print n,"captures -", self.data[-1][0],"seconds"
		
	def get_params(self):
		self.hp.set_TDF_Param()
		
		self.fa = self.hp.get_startFreq()
		self.fb = self.hp.get_stopFreq()
		print "g_p fa=",repr(self.fa)
		print "g_p fb=",repr(self.fb)
		
		self.aunits = self.hp.get_ampUnits()
		
	def get_data(self, **kwargs):
		do_update = True
		try:
			do_update = kwargs['update_params']
		except KeyError:
			pass
		
		if do_update:
			self.get_params()
		
		self.data = self.hp.get_trace()
	
	def plot_trace(self):
		if not self.hp.is_initialized():
			tkMessageBox.showerror("Error", "Instrument not initialized.")
		else:
			self.get_data()
			
			print "TDF",repr(self.hp.get_traceDataFormat())			
			print "FA",self.fa
			print "FB",self.fb
			#print repr(self.data)
			
			self.plot_self_data()
			
	def plot_self_data(self):
			self.parent.plot_frame.set_plot_data(self.data, self.fa, self.fb, self.aunits)
	
	def load_data(self):
		loadfile = tkFileDialog.askopenfile(mode='r', title="Load CSV and plot", defaultextension=".csv",\
											filetypes=[("CSV","*.csv"), ("All files","*")])
		if loadfile is None:
			return
		str_data = loadfile.read().strip()
		
		
		n_rows = len(str_data.split("\n"))
		if n_rows == 1: 	#old version (one line)
			l_data = str_data.split(";")
			
			self.fa = l_data[0]
			del l_data[0]
			self.fb = l_data[0]
			del l_data[0]
			self.aunits = l_data[0]
			del l_data[0]
			self.data = l_data
		elif n_rows == 2 : #one measuerement
			l_header_data = str_data.split("\n")
			header = l_header_data[0].split(";")
			self.fa = header[0]
			self.fb = header[1]
			self.aunits = header[2]
			
			self.data = l_header_data[1].split(";")
		
		self.parent.plot_frame.set_plot_data(self.data, self.fa, self.fb, self.aunits)
		
	def save_data(self):
		if any([s is None for s in [self.data, self.fa, self.fb, self.aunits]]):
			tkMessageBox.showinfo("Error", "No data to be saved.")
		else:
			savefile = tkFileDialog.asksaveasfile(mode='w', defaultextension=".csv", title="Save data")
			if savefile is None or "":
				return
			str_header = str(self.fa) + ";" + str(self.fb) + ";" + str(self.aunits) + "\n"
			
			if type(self.data[0]) != list: #single measurement
				str_data = ";".join(map(str,self.data))
				
				savefile.write(str_header)
				savefile.write(str_data)
				savefile.close()
			else: #multiple measurements
				pass
	
	def save_plot(self):
		l_filetypes = [("Portable Network Graphics","*.png"), ("Scalable Vector Graphics", "*.svg"),\
						("Portable Document Format","*.pdf"), ("PostScript", "*.ps") ]
		savefilename = 	tkFileDialog.asksaveasfilename(title="Save plot image", filetypes=l_filetypes)	
		
		utils = Utils()
		if utils.path_leaf(savefilename).split() == "":
			return
			
		self.plot_frame.save_image(savefilename)
		
class MainWindow:
	def __init__(self, parent, fast=False):
		self.parent = parent
		parent.title("HP856E Spectrum Analyzer - Graphical User Interface (beta)")
		self.hp = hp.HP8563E()
		print "MainWindow's hp:",id(self.hp)
		self.statusbar = Statusbar(parent)
		
		self.plot_frame = pf.PlotFrame(parent, self)
		self.data_handler = Data(self)
		
		self.menubar = Menubar(parent, self)
		self.parent.config(menu = self.menubar)
		
		self.statusbar.pack(side="bottom", fill="x")
		#self.menubar.pack(side="top", fill="x")
		
		
		self.plot_frame.pack()
		
		##test
		#self.label_test = tk.Label(parent, text="This is a test. Hallo Welt!")
		#self.label_test.pack()
		##end/test
		
		self.lower_buttons = tk.Frame(parent)
		self.lower_buttons.pack()
		tk.Button(self.lower_buttons, text="(Test plot from Analyser)", command = self.data_handler.plot_trace_test ).pack(side=tk.LEFT)
		tk.Button(self.lower_buttons, text="Get Single Measurement from Analyser", command = self.data_handler.plot_trace ).pack(side=tk.LEFT)
			
		self.sweepMode = None
		
		self.freqBrowser_window = None
		self.bandWidth_window = None
		self.contMeas_window = None
		
		if fast:
			self.hp.fast_init()
		else:
			self.instrument_window = InstrumentWindow(self)
			self.instrument_window.lift()
			
	def set_sweepMode(self, newMode):
		self.hp.set_sweepMode(newMode)
		self.sweepMode = newMode
		
############################ --Run		
def start(args):
	root = tk.Tk()
	if os.name == "nt":
		root.iconbitmap(default='fav.ico')
	if "-f" in args:
		MainWindow(root, True)
	else:
		MainWindow(root)
	root.mainloop()

#########################3## --Autorun
if __name__ == '__main__':
	start(sys.argv[1:])
	#pass