# Hi-Fi TTS Phone Duration Extractor

This is the phone duration extractor for Hi-Fi TTS dataset. The scripts are modified from the LJSpeech data processing scripts provided in [NEMO](https://github.com/NVIDIA/NeMo/tree/main/scripts/dataset_processing/ljspeech).

## Reorgnize dataset

```
python reorganize_hifitts.py --hifitts_dir=datasets/hi_fi_tts_v0 --reorg_hifitts_dir=datasets/hifitts_reorg
```

## Extract duration

```
./extract_hifitts_phonemes_and_durs.sh datasets/hifitts_reorg
```

The extracted phone durations will be saved to ```alignments``` dir.
