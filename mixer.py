import numpy as np
import sox

test_dir = "timit/TEST"

categories = ["MF", "MM", "FF"]
TIR = [0, 3, 6, 9, 12, 15]

def calculate_tir(target, interference):
  return 10 * np.log10(target ** 2 / interference ** 2) 

def tir_factor(ratio, target, interference):
	return 10 ** ((ratio - calculate_tir(target, interference)) / 20)

rms1 = sox.file_info.stat('test/SA1.wav')['RMS     amplitude']
rms2 = sox.file_info.stat('test/SA2.wav')['RMS     amplitude']

# rms1 = sox.file_info.stat('test/SI943.wav')['RMS     amplitude']
# rms2 = sox.file_info.stat('test/SI2203.wav')['RMS     amplitude']

print(calculate_tir(rms1, rms2))

factor = tir_factor(0, rms1, rms2)

# tfn = sox.Transformer()
# tfn.vol(1 / factor, gain_type='amplitude')
# tfn.build('test/SA2.wav', 'test/out.wav')

cbn = sox.Combiner()

for ratio in TIR:
	factor = tir_factor(ratio, rms1, rms2)
	print(calculate_tir(rms1, rms2 / factor))

	cbn.build(['test/SA1.wav', 'test/SA2.wav'], 'test/SA1_SA2/out{}.wav'.format(ratio), 'mix',  [1, 1 / factor])
	# cbn.build(['test/SI943.wav', 'test/SI2203.wav'], 'test/SI943_SI2203/out{}.wav'.format(ratio), 'mix', [1, 1 / factor])
	
