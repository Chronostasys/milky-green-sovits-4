import os
import argparse
import re

from tqdm import tqdm
from random import shuffle
import json

config_template = json.load(open("configs/config.json"))

pattern = re.compile(r'^[\.a-zA-Z0-9_\/]+$')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_list", type=str, default="./filelists/train.txt", help="path to train list")
    parser.add_argument("--val_list", type=str, default="./filelists/val.txt", help="path to val list")
    parser.add_argument("--test_list", type=str, default="./filelists/test.txt", help="path to test list")
    parser.add_argument("--source_dir", type=str, default="./dataset/44k", help="path to source dir")
    args = parser.parse_args()
    
    train = []
    val = []
    test = []
    idx = 0
    spk_dict = {}
    spk_id = 0
    for speaker in tqdm(os.listdir(args.source_dir)):
        spk_dict[speaker] = spk_id
        spk_id += 1
        wavs = ["/".join([args.source_dir, speaker, i]) for i in os.listdir(os.path.join(args.source_dir, speaker))]
        for wavpath in wavs:
            if not pattern.match(wavpath):
                print(f"warning：文件名{wavpath}中包含非字母数字下划线，可能会导致错误。（也可能不会）")
        if len(wavs) < 10:
            print(f"warning：{speaker}数据集数量小于10条，请补充数据")
        wavs = [i for i in wavs if i.endswith("wav")]
        shuffle(wavs)
        train += wavs[2:-2]
        val += wavs[:2]
        test += wavs[-2:]

    shuffle(train)
    shuffle(val)
    shuffle(test)
            
    print("Writing", args.train_list)
    with open(args.train_list, "w") as f:
        for fname in tqdm(train):
            wavpath = fname
            f.write(wavpath + "\n")
        
    print("Writing", args.val_list)
    with open(args.val_list, "w") as f:
        for fname in tqdm(val):
            wavpath = fname
            f.write(wavpath + "\n")
            
    print("Writing", args.test_list)
    with open(args.test_list, "w") as f:
        for fname in tqdm(test):
            wavpath = fname
            f.write(wavpath + "\n")

    config_template["spk"] = spk_dict
    print("Writing configs/config.json")
    with open("configs/config.json", "w") as f:
        json.dump(config_template, f, indent=2)
