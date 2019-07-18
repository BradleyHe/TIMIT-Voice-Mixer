# Dual Voice Mixer for TIMIT Dataset
This project is intended to be used in conjunction with the [Pytorch implementation](https://github.com/AzizCode92/Listen-Attend-and-Spell-Pytorch) of LAS and test the LAS model's recognition ability when background noise is introduced. The TIMIT dataset is modified to generate voices with background noise that can be tested with a trained LAS model.

## Setup
### TIMIT
- Move the files in mix_timit to the LAS Pytorch directory.

- TIMIT dataset folder must be in the same directory as timit_preprocess.sh and mixer.py

- Run timit_preprocess.sh (should convert NIST .WAV to RIFF .wav)

- Run mixer.py

	- TIR and gender mixing can be adjusted by editing their respective lists

- Run timit\_preproccess\_mixed.py

	- Adjust TIR and gender list accordingly

- Run test\_timit\_mixed.py to generate phoneme error rate results

## Requirements
- pysox: Mixes audio files

- SoX: Converts NIST to RIFF and a requirement for pysox

- NumPy: Calculates target-to-interference ratio

- pandas: Saves testing data in .csv format
