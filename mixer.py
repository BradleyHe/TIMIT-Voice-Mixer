import numpy as np
import sox
import os
import shutil

def calculate_tir(target, interference):
  return 10 * np.log10(target ** 2 / interference ** 2) 

def tir_factor(ratio, target, interference):
	return 10 ** ((ratio - calculate_tir(target, interference)) / 20)

# categories = ["MF", "MM", "FF"]
# TIR = [0, 3, 6, 9, 12, 15]

# for now, I am testing only one specific case
categories = ['FF']
TIR = [3]
dialects = ['DR1', 'DR2', 'DR3', 'DR4', 'DR5', 'DR6', 'DR7']

cbn = sox.Combiner()
cbn.set_input_format(file_type=['wav', 'wav'])

# create mixed audio files for every combination of categories and TIR

# NOTE: mixed audio file MUST have the same length as the target audio file 
#	i.e. the interference voice must be shorter than the target voice. Very important

# shortest duration for test audio: 1.094437
# longest duration for test audio:: 7.57125

for ratio in TIR:
	for category in categories:
		if not os.path.exists('timit/TEST_{}_{}'.format(ratio, category)):
			os.makedirs('timit/TEST_{}_{}'.format(ratio, category))

		for dialect in dialects:
			# TESTING DR1 only
			if dialect != 'DR1':
				continue

			speakers = os.listdir('timit/TEST/{}'.format(dialect))

			# stratify speakers based on gender (if needed)
			if(category == 'MM' or category == 'FF'):
				for speaker in list(speakers):
					if speaker[0] != category[0]:
						speakers.remove(speaker)

			lengths = {}

			# populate dict with lengths of audio files
			if not lengths:
				for speaker in speakers:
						for file in os.listdir('timit/TEST/{}/{}'.format(dialect, speaker)):
							if not file.endswith('.wav'):
								continue
							lengths['{}/{}'.format(speaker, file.split('.')[0])] = sox.file_info.duration('timit/TEST/{}/{}/{}'.format(dialect, speaker, file))

			# mix voice with the voice that is the next smallest duration (to minimize amount of time in target audio that does not contain another voice)
			sorted_lengths = sorted(lengths.values())
			sorted_keys = sorted(lengths, key=lengths.get)

			for x in range(len(lengths) - 1, 1, -1):
				speaker = sorted_keys[x].split('/')[0]

				file1 = 'timit/TEST/{}/{}.wav'.format(dialect, sorted_keys[x])
				rms1 = sox.file_info.stat(file1)['RMS     amplitude']

				file2 = 'timit/TEST/{}/{}.wav'.format(dialect, sorted_keys[x - 1])
				rms2 = sox.file_info.stat(file2)['RMS     amplitude']

				factor = tir_factor(ratio, rms1, rms2)

				if not os.path.exists('timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, speaker)):
					os.makedirs('timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, speaker))

				# create audio file and copy over corresponding phoneme, word, and text files
				cbn.build([file1, file2], 'timit/TEST_{}_{}/{}/{}.wav'.format(ratio, category, dialect, sorted_keys[x]), 'mix', [1, 1 / factor])
				shutil.copy('timit/TEST/{}/{}.PHN'.format(dialect, sorted_keys[x]), 
										'timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, speaker))
				shutil.copy('timit/TEST/{}/{}.TXT'.format(dialect, sorted_keys[x]), 
										'timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, speaker))
				shutil.copy('timit/TEST/{}/{}.WRD'.format(dialect, sorted_keys[x]), 
										'timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, speaker))
				

# factor = tir_factor(ratio, rms1, rms2)
# print(calculate_tir(rms1, rms2 / factor))
# cbn.build(['test/SA1.wav', 'test/SA2.wav'], 'test/SA1_SA2/out{}.wav'.format(ratio), 'mix',  [1, 1 / factor])