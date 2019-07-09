import numpy as np
import sox
import os
import shutil

def calculate_tir(target, interference):
  return 10 * np.log10(target ** 2 / interference ** 2) 

def tir_factor(ratio, target, interference):
	return 10 ** ((ratio - calculate_tir(target, interference)) / 20)

# categories = ["MF", "FM", "MM", "FF"]
# TIR = [0, 3, 6, 9, 12, 15]

# for now, I am testing only one specific case
categories = ['FF']
TIR = [3]
dialects = ['DR1', 'DR2', 'DR3', 'DR4', 'DR5', 'DR6', 'DR7']

cbn = sox.Combiner()
cbn.set_input_format(file_type=['wav', 'wav'])

# trim silence off of end of each audio file
tfn = sox.Transformer()
tfn.silence(location=-1)

# create mixed audio files for every combination of categories and TIR

# NOTE: mixed audio file MUST have the same length as the target audio file 
#	i.e. the interference voice must be shorter than the target voice. Very important

# shortest duration for test audio: 1.094437
# longest duration for test audio:: 7.57125

if not os.path.exists("trimmed"):
	os.makedirs('trimmed')

for ratio in TIR:
	for category in categories:
		if not os.path.exists('timit/TEST_{}_{}'.format(ratio, category)):
			os.makedirs('timit/TEST_{}_{}'.format(ratio, category))

		for dialect in dialects:
			# TESTING DR1 only
			if dialect != 'DR1':
				continue

			speakers = os.listdir('timit/TEST/{}'.format(dialect))
			interf_speakers = []

			# stratify speakers based on gender 
			for speaker in list(speakers):
				if speaker[0] != category[0]:
					speakers.remove(speaker)
					interf_speakers.append(speaker)
			
			lengths = {}
			interf_lengths = {}

			# get lengths of audio files
			if not lengths:
				for speaker in speakers:
						for file in os.listdir('timit/TEST/{}/{}'.format(dialect, speaker)):
							if not file.endswith('.wav'):
								continue
							# get duration of audio file with silence at end trimmed off
							lengths['{}/{}'.format(speaker, file.split('.')[0])] = tfn.stat('timit/TEST/{}/{}/{}'.format(dialect, speaker, file))['Length (seconds)']

				if category == 'MF' or category == 'FM':
					for speaker in interf_speakers:
						for file in os.listdir('timit/TEST/{}/{}'.format(dialect, speaker)):
							if not file.endswith('.wav'):
								continue
							# get duration of audio file with silence at end trimmed off
							interf_lengths['{}/{}'.format(speaker, file.split('.')[0])] = tfn.stat('timit/TEST/{}/{}/{}'.format(dialect, speaker, file))['Length (seconds)'] 

			sorted_keys = sorted(lengths, key=lengths.get)
			interf_sorted_keys = sorted(interf_lengths, key=interf_lengths.get)

			#iterate through target voices
			for x in range(len(lengths) - 1, 0, -1):
				speaker1 = ''
				speaker2 = ''
				name1 = ''
				name2 = ''
				file1 = ''
				file2 = ''

				# determine target and interf voices based on the category
				if category == 'MM' or category == 'FF':
					speaker1 = sorted_keys[x].split('/')[0]
					speaker2 = sorted_keys[x - 1].split('/')[0]
					name1 = sorted_keys[x].split('/')[1]
					name2 = sorted_keys[x - 1].split('/')[1]

					file1 = 'timit/TEST/{}/{}.wav'.format(dialect, sorted_keys[x])
					file2 = 'timit/TEST/{}/{}.wav'.format(dialect, sorted_keys[x - 1])

				# elif category == 'MF' or category == 'FM':
				# 	if category[0] == 'M':
				# 		speaker1 = sorted_keys[x].split('/')[0]

				if not os.path.exists('timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, speaker1)):
					os.makedirs('timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, speaker1))

				# mix voice with the voice that is the next smallest duration (to minimize amount of time in target audio that does not contain another voice)
				rms1 = sox.file_info.stat(file1)['RMS     amplitude']
				rms2 = sox.file_info.stat(file2)['RMS     amplitude']

				factor = tir_factor(ratio, rms1, rms2)

				# build trimmed version of interference audio
				if not os.path.exists('trimmed/{}'.format(speaker2)):
					os.makedirs('trimmed/{}'.format(speaker2))

				# although this is computationally expensive, it is required to save the trimmed file in order to mix it with the target.
				tfn.build('timit/TEST/{}/{}.wav'.format(dialect, sorted_keys[x - 1]), 'trimmed/{}/{}.wav'.format(speaker2, name2))

				# mix target audio file and trimmed interference together
				cbn.build([file1, 'trimmed/{}/{}.wav'.format(speaker2, name2)], 'timit/TEST_{}_{}/{}/{}/{}.wav'.format(ratio, category, dialect, speaker1, name1), 
										'mix', [1, 1 / factor])

				# copy over corresponding training info
				shutil.copy('timit/TEST/{}/{}/{}.PHN'.format(dialect, speaker1, name1), 
										'timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, speaker1))
				shutil.copy('timit/TEST/{}/{}/{}.TXT'.format(dialect, speaker1, name1), 
										'timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, speaker1))
				shutil.copy('timit/TEST/{}/{}/{}.WRD'.format(dialect, speaker1, name1), 
										'timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, speaker1))

				print('Target {} mixed with interf {} with TIR {}'.format(file1, file2, ratio))

				#NOTE: If you comment this line out, SoX will produce warning messages due to files being written over in this directory.
				shutil.rmtree('trimmed')

print("DONE")