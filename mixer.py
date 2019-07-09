import numpy as np
import sox
import os
import shutil

def calculate_tir(target, interference):
  return 10 * np.log10(target ** 2 / interference ** 2) 

def tir_factor(ratio, target, interference):
	return 10 ** ((ratio - calculate_tir(target, interference)) / 20)

# used when category is MF or FM
# matches as many target voices as possible with interference voices that are shorter in duration than them
def match_voices(target_key, target_len, interf_key, interf_len):
	matched = {}
	interf = len(interf_len) - 1

	for target in range(len(target_len) - 1, 0, -1):
		while target_len[target] < interf_len[interf]:
			interf -= 1
			if interf == -1:
				return matched

		matched[target_key[target]] = interf_key[interf] 
	return matched

# mixes two voices together
def mix_voices(tir, category, dialect, target, target_name, interf, interf_name, factor):
	file1 = 'timit/TEST/{}/{}/{}.wav'.format(dialect, target, target_name)
	file2 = 'timit/TEST/{}/{}/{}.wav'.format(dialect, interf, interf_name)

	# build trimmed version of interference audio
	if not os.path.exists('trimmed/{}'.format(interf)):
		os.makedirs('trimmed/{}'.format(interf))

	# although this is computationally expensive, it is required to save the trimmed file in order to mix it with the target.
	tfn.build(file2, 'trimmed/{}/{}.wav'.format(interf, interf_name))

	# mix target audio file and trimmed interference together
	cbn.build([file1, 'trimmed/{}/{}.wav'.format(interf, interf_name)], 'timit/TEST_{}_{}/{}/{}/{}.wav'.format(tir, category, dialect, target, target_name), 
							'mix', [1, 1 / factor])

	# copy over corresponding training info
	shutil.copy('timit/TEST/{}/{}/{}.PHN'.format(dialect, target, target_name), 
							'timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, target))
	shutil.copy('timit/TEST/{}/{}/{}.TXT'.format(dialect, speaker1, target_name), 
							'timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, target))
	shutil.copy('timit/TEST/{}/{}/{}.WRD'.format(dialect, speaker1, target_name), 
							'timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, target))

	print('Target {} mixed with interf {} with TIR {}'.format(file1, file2, ratio))

# for now, I am testing only one specific case
categories = ['FF', 'MM', 'FM', 'MF']
TIR = [9]
dialects = ['DR1', 'DR2', 'DR3', 'DR4', 'DR5', 'DR6', 'DR7', 'DR8']

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
		print(category)

		if not os.path.exists('timit/TEST_{}_{}'.format(ratio, category)):
			os.makedirs('timit/TEST_{}_{}'.format(ratio, category))

		for dialect in dialects:
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
			sorted_lengths = sorted(lengths.values())
			interf_sorted_lengths = sorted(interf_lengths.values())

			if category == 'MM' or category == 'FF':
				for x in range(len(lengths) - 1, 0, -1):
					speaker1 = sorted_keys[x].split('/')[0]
					speaker2 = sorted_keys[x - 1].split('/')[0]
					name1 = sorted_keys[x].split('/')[1]
					name2 = sorted_keys[x - 1].split('/')[1]
					file1 = 'timit/TEST/{}/{}/{}.wav'.format(dialect, speaker1, name1)
					file2 = 'timit/TEST/{}/{}/{}.wav'.format(dialect, speaker2, name2)

					if not os.path.exists('timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, speaker1)):
						os.makedirs('timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, speaker1))

					# mix voice with the voice that is the next smallest duration (to minimize amount of time in target audio that does not contain another voice)
					rms1 = sox.file_info.stat(file1)['RMS     amplitude']
					rms2 = sox.file_info.stat(file2)['RMS     amplitude']
					factor = tir_factor(ratio, rms1, rms2)

					mix_voices(ratio, category, dialect, speaker1, name1, speaker2, name2, factor)

					#NOTE: If you comment this line out, SoX will produce warning messages due to files being written over in this directory.
					shutil.rmtree('trimmed')

			elif category == 'MF' or category == 'FM':
				matched = match_voices(sorted_keys, sorted_lengths, interf_sorted_keys, interf_sorted_lengths)

				for key1, key2 in matched.items():
					speaker1 = key1.split('/')[0]
					speaker2 = key2.split('/')[0]
					name1 = key1.split('/')[1]
					name2 = key2.split('/')[1]
					file1 = 'timit/TEST/{}/{}/{}.wav'.format(dialect, speaker1, name1)
					file2 = 'timit/TEST/{}/{}/{}.wav'.format(dialect, speaker2, name2)

					if not os.path.exists('timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, speaker1)):
						os.makedirs('timit/TEST_{}_{}/{}/{}'.format(ratio, category, dialect, speaker1))

					# mix voice with the voice that is the next smallest duration (to minimize amount of time in target audio that does not contain another voice)
					rms1 = sox.file_info.stat(file1)['RMS     amplitude']
					rms2 = sox.file_info.stat(file2)['RMS     amplitude']
					factor = tir_factor(ratio, rms1, rms2)

					mix_voices(ratio, category, dialect, speaker1, name1, speaker2, name2, factor)

					#NOTE: If you comment this line out, SoX will produce warning messages due to files being written over in this directory.
					shutil.rmtree('trimmed')
		print()
	print()
print("DONE")