import math
import ntpath

class Utils:
	def __init__(self, *args, **kwargs):
		pass
		
	def long_to_autoScale(self, value):
		print "ltaS value=",repr(value)
		out = float(value)
		if out > 1:
			length = len(str(int(float(value))))
			
			if "." in str(value): # wrong?
				length -= 1
			
			if length >= 9:
				out = out/10**9
				return (str(out), "G")
			elif length >= 6:
				out = out/10**6
				return (str(out), "M")
			elif length >= 3:
				out = out/10**3
				return (str(out), "K")
			else:
				return (str(out), "")
		elif out == 0:
			return (str(out), "")
		else:
			exp = abs(math.log10(float(value)))
			if exp <= 2:
				out = out*(10**3)
				return (str(out), "")
			elif exp <= 5:
				out = out*(10**6)
				return (str(out), "m")
			elif exp <= 8:
				out = out*(10**9)
				return (str(out), "u")
			else:
				raise ValueError("Value "+str(value)+" too small")
				
			
	def long_to_units(self, value, units):
		'''
		Ex.: long_to_units(30000, "Hz") -> "30 KHz"
		     long_to_units(3000000, "V") -> "3 MV"
		'''
		(num, mag) = self.long_to_autoScale(value)
		return num+" "+mag+units
		
	def long_to_freq(self, value):
		return long_to_units(value,"Hz")
		
	def long_to_scale(self, value, scale):
		out = float(value)
		
		if scale == "G":
			return str(out/10**9)
		elif scale == "M":
			return str(out/10**6)
		elif scale == "K":
			return str(out/10**3)
		elif scale == "":
			return str(out)
		elif scale == "m":
			return str(out*(10**3))
		elif scale == "u":
			return str(out*(10**6))
		else:
			raise ValueError("SI prefix '"+str(scale)+"' not recognized")
	
	# https://stackoverflow.com/questions/8384737/extract-file-name-from-path-no-matter-what-the-os-path-format
	def path_leaf(self, path):
		head, tail = ntpath.split(path)
		return tail or ntpath.basename(head)