import argparse
import cv2
import json
import os
from PIL import Image


import pdb
def make_video(input_dir, output_file):
    images = [f for f in os.listdir(input_dir) if f.endswith('.png')]
    index_list = [int(f.split(".")[0].split("_")[-1]) for f in images]
    # sort images by index
    images = [x for _, x in sorted(zip(index_list, images))]
    images = [os.path.join(input_dir, f) for f in images]
    # read images as frames
    frames = [cv2.imread(f) for f in images]
    # write frames to video
    out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'mp4v'), 1, (frames[0].shape[1], frames[0].shape[0]))
    for frame in frames:
        out.write(frame)
    out.release()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_save_dir", type=str, default="/Users/liuyichen/Documents/repo/browser-use/outputs/test_all_claudesonnet_debug", help="The directory to save the data")
    parser.add_argument("--output_dir", type=str, default="/Users/liuyichen/Documents/repo/browser-use/outputs/test_all_claudesonnet_debug_visualization", help="The directory to save the output")
    parser.add_argument("--filter_false_positive", action="store_true", help="Whether to filter false positive")
    return parser.parse_args()

def main():
    args = parse_args()
    data_save_dir = args.data_save_dir
    output_dir = args.output_dir
    filter_false_positive = args.filter_false_positive

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    total_score = 0
    total_count = 0

    test_output_file = os.path.join(data_save_dir, "test_output.jsonl")
    with open(test_output_file, "r") as f:
        for line in f:
            test_output = json.loads(line)
            raw_output_dir = os.path.join(data_save_dir, f"debug_{test_output["unique_id"]}")
            if not os.path.exists(raw_output_dir):
                print(f"Skipping {raw_output_dir} because it does not exist")
                continue
            total_count += 1
            total_score += test_output["score"]
            if filter_false_positive:
                if test_output["score"]:
                    continue
            print(f"Making video for {test_output["unique_id"]}. Score: {test_output["score"]}")
            # assume only one instance
            instance_dir = os.listdir(os.path.join(raw_output_dir, "browser_temp"))
            if len(instance_dir) != 1:
                for instance in instance_dir:
                    screenshot_dir = os.path.join(raw_output_dir, "browser_temp", instance, "screenshots")
                    if os.path.exists(screenshot_dir):
                        instance_dir = instance
                        break
            else:
                instance_dir = instance_dir[0]
            screenshot_dir = os.path.join(raw_output_dir, "browser_temp", instance_dir, "screenshots")
            make_video(screenshot_dir, os.path.join(output_dir, f"{test_output["unique_id"]}.mp4"))
            if total_count >= 5:
                break
            # print(f"Made video for {test_output["unique_id"]}")
    print(f"Total score: {total_score}, Total count: {total_count}, Average score: {total_score / total_count}")

if __name__ == "__main__":
    main()