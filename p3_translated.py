import os
import argparse
import json
import logging
import time
from googletrans import Translator
from retrying import retry
from multiprocessing import Pool
from functools import partial

"""
Commands:
python3 p3_translated.py --path file_path --split train --size 1000
python3 p3_translated.py --path file_path --split validation --size 100
"""

translator = Translator(proxies={'http': 'http://localhost:8118'})

logging.basicConfig(filename='/tmp/p3_translated.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

# Need to automatic check if incompleted task list exists or not 
# Or to run the whole original task list

def read_json(task_name, split):
    with open(f'p3_{task_name}_{split}.jsonl', 'r') as json_file:
        json_list = list(json_file)

    data_list = []
    for json_str in json_list:
        data_list.append(list(json.loads(json_str).values()))
    return data_list

# List of translated object to list of translated text string
def to_list_text(mylist):
    res_texts = []
    for i in range(len(mylist)):
        res_texts.append(mylist[i].text)
    return res_texts

# Divide small chunks
def divide_chunks(mylist, n): 
  # looping till length l
  for i in range(0, len(mylist), n):
    yield mylist[i:i + n]

# Convert list to dict 
def list_to_dict(mylist):
    title = ['inputs', 'targets']
    return dict(zip(title, mylist))

def save_translated_json(mydict, task_name, split):
    # save json translated file test
    json_object = json.dumps(mydict, indent=2, ensure_ascii=False)

    # Writing to .jsonl
    with open(f'p3_translated_{task_name}_{split}.jsonl', "w", encoding='utf-8') as outfile:
        outfile.write(json_object)

@retry(wait_fixed=7000)
def translate_list_str(task_name, translator, list_str):
    translated = []
    try:
        translated = translator.translate(list_str, src='en', dest='vi')
    except Exception as err:
        logger.error(err)
        print(f'Exception occured when translating: {task_name}')
        print(f"Exception occurred for sentence: {list_str}")
        # Write error list that stores sentences that exception occurred
        with open(f'{task_name}_error_sentences.txt', 'a+') as fp:
            fp.write("%s\n" %list_str)
            print(f'Write {task_name} error sentences successuflly!')
    return translated

def translate_chunks(task_name, list_chunks):
    translated_chunks = []
    for i in range(len(list_chunks)):
        translated_chunk = []
        for j in range(len(list_chunks[i])):
            translated_chunk.append(translate_list_str(task_name=task_name, translator=translator, list_str=list_chunks[i][j]))
        translated_list_chunk = []
        for j in range(len(translated_chunk)):
            translated_list_chunk.append(to_list_text(translated_chunk[j]))
        translated_list_dict_chunk = []
        for j in range(len(translated_list_chunk)):
            translated_list_dict_chunk.append(list_to_dict(translated_list_chunk[j]))
        translated_chunks.append(translated_list_dict_chunk)
    return translated_chunks

def dir_path(string):
    if os.path.exists(string):
        return string
    else:
        raise NotADirectoryError(string)

def parse_args():
    parser = argparse.ArgumentParser(description='Translate dataset')
    parser.add_argument(
        '--path',
        default='task_list.txt',
        type=dir_path
    )
    parser.add_argument(
        '--split',
        default='train',
        help='define split')
    # chunk size = 1000 when split train
    # chunk size = 100 when split validation
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    with open(args.path, 'r+') as f:
        files = f.readlines()
    TASK_LIST = []
    for i in range(len(files)):
        files[i] = files[i].rstrip("\n")
        TASK_LIST.append(files[i])
    FINISHED_TASK_LIST = []

    for task_name in TASK_LIST:
        try:
            data = read_json(task_name, args.split)
            data_size = len(data)
            data_chunks = list(divide_chunks(data, int(data_size / 16)))
            print(f'Starting translation task: {task_name}...')
            pool_chunks = (data_chunks[0:2], data_chunks[2:4],data_chunks[4:6], data_chunks[6:8], data_chunks[8:10], data_chunks[10:12], data_chunks[12:14], data_chunks[14:])
            with Pool(8) as pool:
                # translated length: len = 5 corresponds to 8 chunks (corresponds to 8 cores)
                # translated_list_1: chunk 0, 2, 4, 6, 8, 10, 12, 14, (16)
                # translated_list_2: chunk 1, 3, 5, 7, 9, 11, 13, 15
                translated_list_1, translated_list_2 = zip(*pool.map(partial(translate_chunks, task_name), pool_chunks))
                # report a message
                print('Done translation translated.')

            save_translated_json(translated_list_1, task_name, args.split)
            save_translated_json(translated_list_2, task_name, args.split)
        
            # if translated successful add this task_name to the translated list
            FINISHED_TASK_LIST.append(task_name)

        except Exception as err:
            # if Exception occurs, write the rest of the list to the task_list file
            print(f'Exception when translating task name: {task_name}')
            logger.error(err)
            print("Writing log. Continue to translate... ")

    # remove finished tasks in the original task list
    for task_name in FINISHED_TASK_LIST:
        TASK_LIST.remove(task_name)
    # Write again incompleted task list        
    with open(f'incompleted_{args.split}_task_list.txt', 'w') as ft:
        for task_name in TASK_LIST:
            ft.write("%s\n" %task_name)
        print(f'Write incompleted {args.split} task list after translating')
    
    # write translated list to file
    with open(f'{args.split}_translated_list.txt', 'a+') as fp:
        for task_name in FINISHED_TASK_LIST:
            fp.write("%s\n" %task_name)
        print(f'Write {args.split} translated_list successuflly!')

if __name__ == '__main__':
    main()








