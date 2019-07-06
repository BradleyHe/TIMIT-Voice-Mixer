# Dual Voice Mixer for TIMIT Dataset

This project is intended to be used in conjunction with the [Pytorch implementation](https://github.com/AzizCode92/Listen-Attend-and-Spell-Pytorch) of LAS and test the LAS model's recognition ability when background noise is introduced. The TIMIT dataset is modified by the included python script to generate voices with background noise that can be tested with a trained LAS model.

## Setup

The TIMIT dataset must be initially preprocessed by the timit_preprocess.sh script included in the Pytorch implementation. Afterwards, the python script can be run on the TIMIT dataset. Generated test folders can be individually tested by editing the test_source_path in timit_preprocess.py and preprocessing it again.

## Requirements
- SoX
- pysox
- NumPy
