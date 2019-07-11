# Dual Voice Mixer for TIMIT Dataset
This project is intended to be used in conjunction with the [Pytorch implementation](https://github.com/AzizCode92/Listen-Attend-and-Spell-Pytorch) of LAS and test the LAS model's recognition ability when background noise is introduced. The TIMIT dataset is modified by the included python script to generate voices with background noise that can be tested with a trained LAS model.

## Setup
- TIMIT dataset folder must be in the same directory as timit_preprocess.sh and mixer.py
- Run timit_preprocess.sh
- Run mixer.py after all .WAV files have been converted to .wav files

## Requirements
- pysox: Mixes audio files
- SoX: Converts .WAV to .wav and a requirement for pysox
- NumPy: Calculates target-to-interference ratio
