# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.import json

from tqdm import tqdm
import glob
import argparse
import os
import subprocess
from concurrent.futures import ProcessPoolExecutor
from functools import partial

sox_path = "/usr/bin/sox"
target_sr = 22050

def convert_flac(path, out_path):
    subprocess.call([sox_path, path, out_path, "rate", str(target_sr)])

def process_item(flac_filepath, wav_filepath, transcript_filepath, transcript):
    convert_flac(flac_filepath, wav_filepath)
    with open(transcript_filepath, 'w', encoding='utf8') as f:
        f.write(transcript)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reorganize HiFi-TTS dataset for force alignment.")
    parser.add_argument('--hifitts_dir', required=True, default=None, type=str)
    parser.add_argument('--reorg_hifitts_dir', required=True, default=None, type=str)
    args = parser.parse_args()

    mainfest_list = glob.glob(os.path.join(args.hifitts_dir, '*.json'))

    if not os.path.exists(args.reorg_hifitts_dir):
        os.mkdir(args.reorg_hifitts_dir)

    wavs_dir = os.path.join(args.reorg_hifitts_dir, "wavs")
    if not os.path.exists(wavs_dir):
        os.mkdir(wavs_dir)
    
    executer = ProcessPoolExecutor(max_workers=8)
    futures = []

    for mainfest in mainfest_list:
        with open(mainfest) as f:
            lines = f.readlines()
        
        mainfest_name = os.path.basename(mainfest)
        speaker_dir = mainfest_name.split("_")[0] + "_" + mainfest_name.split("_")[2]
        speaker_path = os.path.join(wavs_dir, speaker_dir)

        if not os.path.exists(speaker_path):
            os.mkdir(speaker_path)

        for line in lines:
            data = json.loads(line)
            flac_audio_path = data["audio_filepath"]
            _, speaker, book, filename = flac_audio_path.split("/")
            book_dir = os.path.join(speaker_path, book)

            if not os.path.exists(book_dir):
                os.mkdir(book_dir)

            wav_filename = filename[:-5] + ".wav"
            transcript_filename = filename[:-5] + ".txt"

            wav_filepath = os.path.join(book_dir, wav_filename)
            transcript_filepath = os.path.join(book_dir, transcript_filename)

            flac_filepath = os.path.join(args.hifitts_dir, flac_audio_path)

            transcript = data["text_normalized"].lower()

            futures.append(executer.submit(partial(process_item, flac_filepath, wav_filepath, transcript_filepath, transcript)))

    for future in tqdm(futures):
        future.result()
