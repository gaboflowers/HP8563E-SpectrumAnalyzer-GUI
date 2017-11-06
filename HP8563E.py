import visa
import re
import numpy as np

string_delimiters = re.compile("( ! | \$ | \% | & | ' | / |\
					: | = | \@ | \\ | \| | < | > | { | } )") 

class HP8563E:
	
	def __init__(self,**kwargs):
		self.res_mgr = visa.ResourceManager()
		self.res = self._get_GPIB_resources()
		self.inst = None
		
		key_args = kwargs.keys()
		known_params = ["fast"]
		if "fast" in key_args:
			if kwargs["fast"]:
				self.fast_init()
		if any([s not in known_params for s in key_args]):
			for s in [s for s in key_args if s not in key_args]:
				print "Careful. Unknown parameter","'"+s+"'"
	
	def _get_GPIB_resources(self):
		return [s for s in self.res_mgr.list_resources()\
					if s.startswith("GPIB")]
			
	def get_resources(self):
		return self.res
		
	def refresh_resources(self):
		self._get_GPIB_resources()
		
	def set_instrument(self,x):
		self.inst = self.res_mgr.open_resource(x)
	
	def _check_init_inst(self):
		return None
		if self.inst is None:
			raise IOError("Instrument not initialised.")
	
	def is_initialized(self):
		return self.inst is not None
	
	def fast_init(self):
		try:
			self.set_instrument(self.get_resources()[0])
		except IndexError:
			raise IOError("No instruments found")
			
	def write(self, x):
		self._check_init_inst()
		
		self.inst.write(x)
	
	def read(self):
		self._check_init_inst()
		
		self.inst.read()
	
	def query(self,x):
		self._check_init_inst()
		
		return self.inst.query(x)
	
	#-------------------- utils
	def _not_valid(self, option, parameter):
		raise ValueError("'"+str(option)+"' not valid\
								for parameter '"+parameter+"'")
								
	def _float_or_str_result(self, result, output_type):
		if output_type == float:
			return float(result)
		elif output_type == str:
			return result
		else:
			self._not_valid(output_type,"output_type")
			
	#-------------------- commands
	
	
	def get_id(self):
		self._check_init_inst()
		
		return self.query("ID?")
	
	def set_toReset(self):
		self._check_init_inst()
		
		self.write("PRESET")
		
	def set_title(self, title):
		self._check_init_inst()
		
		title = re.sub(string_delimiters,"",title)
		command = "TITLE @"+title+"@"
		self.write(command)
	
	#-- #Frequency
	
	#------->CF
	def get_centerFreq(self, output_type=float):
		self._check_init_inst()
		
		result = self.query("CF?")
		return self._float_or_str_result(result, output_type)
	
	def set_centerFreq(self,new_freq):
		self._check_init_inst()
		
		self.write("CF "+str(new_freq))
	
	get_CF = get_centerFreq
	set_CF = set_centerFreq
	#------->FA
	def get_startFreq(self, output_type=float):
		self._check_init_inst()
		
		result = self.query("FA?")
		return self._float_or_str_result(result, output_type)
	
	def set_startFreq(self,new_freq):
		self._check_init_inst()
		
		self.write("FA "+str(new_freq))
	
	get_FA = get_startFreq
	set_FA = set_startFreq
	#------->FB
	def get_stopFreq(self, output_type=float):
		self._check_init_inst()
		
		result = self.query("FB?")
		return self._float_or_str_result(result, output_type)
	
	def set_stopFreq(self,new_freq):
		self._check_init_inst()
		
		self.write("FB "+str(new_freq))
	
	get_FB = get_stopFreq
	set_FB = set_stopFreq
	#-- #Span
	
	#------->SP
	def get_span(self, output_type=float):
		self._check_init_inst()
		
		result = self.query("SP?")
		return self._float_or_str_result(result, output_type)
	
	def set_span(self,new_freq):
		self._check_init_inst()
		
		self.write("SP "+str(new_freq))
	
	get_SP = get_span
	set_SP = set_span
	
	#------->FS
	def set_fullSpan(self):
		self._check_init_inst()
		
		self.write("FS")
		
	#--- #Amplitude
	#------->RL
	def get_refLevel(self):
		self._check_init_inst()
		result = self.query("RL?").strip()
		
		return result
		
	#------->LN/LG
	def get_isLinearOrLog(self):
		self._check_init_inst()
		lg = self.query("LG?").strip()
		if lg == "0":
			return "LN"
		else:
			return "LG"
	
	def get_LG(self):
		self._check_init_inst()
		return self.query("LG?").strip()
		
	def set_linear(self):
		self._check_init_inst()
		self.write("LN")
		
	def set_log(self, value=""):
		'''
		value only in [1,2,5,10]
		'''
		self._check_init_inst()
		self.write("LG "+str(value))
		
	#-- #Sweep
	
	#------->ST
	def get_sweepTime(self, output_type=float):
		self._check_init_inst()
		
		result = self.query("ST?")
		return self._float_or_str_result(result, output_type)
	
	def set_sweepTime(self,time="530ms"):
		self._check_init_inst()
		
		self.write("ST "+str(time))
	
	get_ST = get_sweepTime
	set_ST = set_sweepTime
	#------->Sweep Mode
	def set_sweepMode(self, mode="CONT"):
		self._check_init_inst()
		
		mode = mode.upper()
		if mode.startswith("CONT"):
			self.write("CONTS")
		elif mode.startswith("SING") or mode.startswith("SNG") or mode == "SGL":
			self.write("SNGLS")
		else:
			self._not_valid(mode,"mode")
	
	#-- #Bandwidth
	
	#------->VB
	def get_videoBW(self, output_type=float):
		self._check_init_inst()
		
		result = self.query("VB?")
		return self._float_or_str_result(result, output_type)
	
	def set_videoBW(self,bw="1MHZ"):
		self._check_init_inst()
		
		self.write("VB "+str(bw))
	
	get_VB = get_videoBW
	set_VB = set_videoBW
	#------->RB
	def get_resBW(self, output_type=float):
		self._check_init_inst()
		
		result = self.query("RB?")
		return self._float_or_str_result(result, output_type)
	
	def set_resBW(self,bw="1MHZ"):
		self._check_init_inst()
		
		self.write("RB "+str(bw))
		
	#------->VAVG	
	def set_videoAvg(self,option="OFF"):
		self._check_init_inst()
		
		if type(option) == bool:
			if option: option = "ON"
			else: option = "OFF"
		self.write("VAVG "+option)
	
	set_VAVG = set_videoAvg
	#------->VBR
	def get_videoResRatio(self, output_type):
		self._check_init_inst()
		
		result = self.query("VBR?")
		return self._float_or_str_result(result, output_type)
	
	def set_videoResRatio(self,ratio="1"):
		self._check_init_inst()
		
		self.write("VBR "+str(ratio))
	
	get_VBR = get_videoResRatio
	set_VBR = get_videoResRatio
	
	############## Data
	# ---- AUNITS
	def get_ampUnits(self):
		self._check_init_inst()
		
		result = self.query("AUNITS?")
		return result.strip()
		
	# ---- TDF
	def get_traceDataFormat(self):
		self._check_init_inst()
		
		result = self.query("TDF?")
		return result.strip()
	
	def set_TDF_Meas(self):
		self._check_init_inst()
		
		self.write("TDF M")
		
	def set_TDF_Param(self):
		self._check_init_inst()
		
		self.write("TDF P")

	get_TDF = get_traceDataFormat
	
	# Data
	def get_trace(self):
		self._check_init_inst()
		
		if self.get_traceDataFormat() != "P":
			print "Warning: Data not in parameter units."
			print "		Do [HP].set_TDF_Param()"
		raw = self.query("TRA?").strip().split(",")
		return np.array(map(float, raw))		
		
		