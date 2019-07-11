import numpy as np
import sox

def calculate_tir(target, interference):
  return 10 * np.log10(target ** 2 / interference ** 2) 

def tir_factor(ratio, target, interference):
	return 10 ** ((ratio - calculate_tir(target, interference)) / 20)

cbn = sox.Combiner()
cbn.set_input_format(file_type=['wav', 'wav'])
tfn = sox.Transformer()

mrs1 = float(sox.file_info.stat('SI2023.wav')['RMS     amplitude'])
mrs2 = float(sox.file_info.stat('SI2149.wav')['RMS     amplitude'])

print(mrs1)
print(mrs2)

print('TIR = {}'.format(calculate_tir(mrs1, mrs2)))
tfn.vol(1 / tir_factor(9, mrs1, mrs2))
tfn.build('SI2149.wav', 'new.wav')

mrs2 = float(sox.file_info.stat('new.wav')['RMS     amplitude'])

print(mrs1)
print(mrs2)

print('TIR = {}'.format(calculate_tir(mrs1, mrs2)))