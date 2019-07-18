import numpy as np
import sox
import os
import shutil
import random
import sys

test_dir = ''
new_test_dir = ''
categories = ['FF', 'MM', 'MF', 'FM']
TIR = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
dialects = ['DR1', 'DR2', 'DR3', 'DR4', 'DR5', 'DR6', 'DR7', 'DR8']

if len(sys.argv) != 2:
	print('Usage: python3 mixer.py <timit directory>')
timit_path = sys.argv[1]

#############################################

def calculate_tir(target, interference):
  return 10 * np.log10(target ** 2 / interference ** 2) 

def tir_factor(ratio, target, interference):
	return 10 ** ((ratio - calculate_tir(target, interference)) / 20)

def match_voices(target_key, target_len, interf_key, interf_len):
	matched = {}

	for target in range(len(target_len) - 1, -1, -1):
		interf = len(interf_len) - 1

		if(target_len[target] > interf_len[interf]):
			matched[target_key[target]] = interf_key[interf]
			continue;

		while target_len[target] < interf_len[interf] and interf > 0:
			interf -= 1

		matched[target_key[target]] = interf_key[random.randint(interf + 1, len(interf_len) - 1)] 
	return matched

def mix_voices(target, interf, factor):
	# build trimmed version of interference audio
	if not os.path.exists('trimmed/{}'.format(interf)):
		os.makedirs('trimmed/{}'.format(interf))
	tfn.build(file2, 'trimmed/{}.wav'.format(interf))

	# mix target audio file and trimmed interference together
	cbn.build([file1, 'trimmed/{}.wav'.format(interf)], '{}/{}.wav'.format(new_test_dir, target), 
							'mix', [1, 1 / factor])

	# copy over corresponding training info
	shutil.copy('{}/{}.PHN'.format(test_dir, target), 
							'{}/{}'.format(new_test_dir, target[:5]))
	shutil.copy('{}/{}.TXT'.format(test_dir, target), 
							'{}/{}'.format(new_test_dir, target[:5]))
	shutil.copy('{}/{}.WRD'.format(test_dir, target), 
							'{}/{}'.format(new_test_dir, target[:5]))
	print('Target {}.wav mixed with interf {}.wav with TIR {}'.format(target, interf, ratio))

#############################################

cbn = sox.Combiner()
cbn.set_input_format(file_type=['wav', 'wav'])

for ratio in TIR:
	for category in categories:
		print('Mixing {} with TIR {}'.format(category, ratio))
		for dialect in dialects:
			test_dir = '{}/TEST/{}'.format(timit_path, dialect)
			new_test_dir = '{}/TEST_{}_{}/{}'.format(timit_path, ratio, category, dialect)

			tfn = sox.Transformer()
			speakers = os.listdir(test_dir)
			interf_speakers = []

			# stratify speakers
			for speaker in list(speakers):
				if speaker[0] != category[0]:
					speakers.remove(speaker)
					interf_speakers.append(speaker)
			
			lengths = {}
			interf_lengths = {}

			tfn.silence(location=-1)

			# get lengths of trimmed audio files
			for speaker in speakers:
					for file in os.listdir('{}/{}'.format(test_dir, speaker)):
						if not file.endswith('.wav'):
							continue
						lengths['{}/{}'.format(speaker, file[:-4])] = float(tfn.stat('{}/{}/{}'.format(test_dir, speaker, file))['Length (seconds)'])

			# get lengths of opposite gender if needed
			if category == 'MF' or category == 'FM':
				for speaker in interf_speakers:
					for file in os.listdir('{}/{}'.format(test_dir, speaker)):
						if not file.endswith('.wav'):
							continue
						interf_lengths['{}/{}'.format(speaker, file[:-4])] = float(tfn.stat('{}/{}/{}'.format(test_dir, speaker, file))['Length (seconds)'])

			sorted_names = sorted(lengths, key=lengths.get)
			interf_sorted_names = sorted(interf_lengths, key=interf_lengths.get)
			sorted_lengths = sorted(lengths.values())
			interf_sorted_lengths = sorted(interf_lengths.values())

			if category == 'MM' or category == 'FF':
				for x in range(0, len(lengths)):
					tfn.clear_effects()
					tfn.silence(location=-1)

					# random file with larger trimmed length than target
					# we want to trim the interference voice to be the same length as the target
					# if we are at the last voice, we can just mix it with the previous one.
					if x < len(lengths) - 1: 
						rand_index = random.randint(x + 1, len(lengths) - 1)
					else:
						rand_index = x - 1

					speaker1 = sorted_names[x].split('/')[0]
					speaker2 = sorted_names[rand_index].split('/')[0]
					file1 = '{}/{}.wav'.format(test_dir, sorted_names[x])
					file2 = '{}/{}.wav'.format(test_dir, sorted_names[rand_index])

					tfn.trim(0, sorted_lengths[x])

					if not os.path.exists('{}/{}'.format(new_test_dir, speaker1)):
						os.makedirs('{}/{}'.format(new_test_dir, speaker1))

					rms1 = sox.file_info.stat(file1)['RMS     amplitude']
					rms2 = sox.file_info.stat(file2)['RMS     amplitude']
					factor = tir_factor(ratio, rms1, rms2)

					mix_voices(sorted_names[x], sorted_names[rand_index], factor)
					shutil.rmtree('trimmed')

			elif category == 'MF' or category == 'FM':
				matched = match_voices(sorted_names, sorted_lengths, interf_sorted_names, interf_sorted_lengths)

				for key1, key2 in matched.items():
					tfn.clear_effects()
					tfn.silence(location=-1)
					tfn.trim(0, lengths[key1])

					speaker1 = key1.split('/')[0]
					speaker2 = key2.split('/')[0]
					file1 = '{}/{}.wav'.format(test_dir, key1)
					file2 = '{}/{}.wav'.format(test_dir, key2)

					if not os.path.exists('{}/{}'.format(new_test_dir, speaker1)):
						os.makedirs('{}/{}'.format(new_test_dir, speaker1))

					rms1 = sox.file_info.stat(file1)['RMS     amplitude']
					rms2 = sox.file_info.stat(file2)['RMS     amplitude']
					factor = tir_factor(ratio, rms1, rms2)

					mix_voices(key1, key2, factor)
					shutil.rmtree('trimmed')
		print()
	print()
print("DONE")