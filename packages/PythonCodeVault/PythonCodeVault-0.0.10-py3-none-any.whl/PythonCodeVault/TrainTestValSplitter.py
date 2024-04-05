import os
from pathlib import Path
from tqdm import tqdm
import random
import shutil


def ClassificationSplitterPercent(base_dir = './data', folders = ['Pass', 'Fail'], splits = [70,20,10], extension = 'png', random_seed = None):
    
    """
    Splits two directories (e.g. Fail & Pass) into Train and Test.

    Parameters
    ----------
    base_dir: str
        Base directory containing the Label directories

    folders: list of str
        containing Label folder names

    splits: list
        containing splits in percent -> [train, test, val]
        0 means split will not be created
        -1 means split contains remaining percent

    extension: str
        extension of the files to be read in
    
    random_seed: int
        random seed for reproduction
        if not wanted -> none

        
    Structure of given Base Folder should be like:

        Base
        │
        └─── Label0
        │    │   file01.txt
        │    │   ...
        │   
        └─── Label1
        │    │   file11.txt
        │    │   ...
        │   
        └─── Label2
            │   file21.txt
            │   ...
    """

    if sum(splits) != 100 and -1 not in splits: raise Exception('Sum of percentages has to be 100')
    if splits.count(-1) > 1: raise Exception('Only one -1 alowed in splits')

    # splits_percent exists and contains -1:
    if -1 in splits:
        idx = splits.index(-1)
        splits[idx] = 100 - (sum(splits) + 1)

    # src folder
    base_dir = os.path.abspath(base_dir)

    val = True
    if splits[2] == 0:
        val = False
    
    # dest folders
    split_dir = os.path.join(base_dir, 'split')
    if os.path.exists(split_dir):
        shutil.rmtree(split_dir)
    Path(split_dir).mkdir(exist_ok=True)
    Path(os.path.join(split_dir, 'Train')).mkdir(exist_ok=True)
    Path(os.path.join(split_dir, 'Test')).mkdir(exist_ok=True)
    if val:
        Path(os.path.join(split_dir, 'Val')).mkdir(exist_ok=True)

    train_dest_folders = [os.path.join(split_dir, 'Train', label) for label in folders]
    test_dest_folders = [os.path.join(split_dir, 'Test', label) for label in folders]
    if val:
        val_dest_folders = [os.path.join(split_dir, 'Val', label) for label in folders]

    for new_folder in train_dest_folders: Path(new_folder).mkdir()
    for new_folder in test_dest_folders: Path(new_folder).mkdir()
    if val:
        for new_folder in val_dest_folders: Path(new_folder).mkdir()


    for folder in folders:
        src_folder = os.path.join(base_dir, folder)

        shuffled_filenames = [file for file in os.listdir(src_folder) if file.endswith(extension)]
        if random_seed:
            random.Random(random_seed).shuffle(shuffled_filenames)
        else:
            random.Random().shuffle(shuffled_filenames)

        train_size = int(len(shuffled_filenames) * splits[0] / 100) + 1
        test_size = int(len(shuffled_filenames) * splits[1] / 100)

        train_filenames = shuffled_filenames[:train_size]
        test_filenames = shuffled_filenames[train_size:train_size+test_size]
        if val:
            val_filenames = shuffled_filenames[train_size+test_size:]

        for filename in train_filenames:
            src_file_path = os.path.join(base_dir, folder, filename)
            dest_file_path = os.path.join(split_dir, 'Train', folder, filename)
            shutil.copy(src_file_path, dest_file_path)
        
        for filename in test_filenames:
            src_file_path = os.path.join(base_dir, folder, filename)
            dest_file_path = os.path.join(split_dir, 'Test', folder, filename)
            shutil.copy(src_file_path, dest_file_path)

        if val:
            for filename in val_filenames:
                src_file_path = os.path.join(base_dir, folder, filename)
                dest_file_path = os.path.join(split_dir, 'Val', folder, filename)
                shutil.copy(src_file_path, dest_file_path)


def ClassificationSplitterAbsolute(base_dir = './data', folders = ['Pass', 'Fail'], splits = [[70,20,10],[35,20,5]], extension = 'png', random_seed = None):
    
    """
    Splits two directories (e.g. Fail & Pass) into Train and Test.

    Parameters
    ----------
    base_dir: str
        Base directory containing the Label directories

    folders: list of str
        containing Label folder names

    splits: list
        containing splits for each label in absolute amount -> [[train, test, val], [train, test, val]]
        0 means split will not be created
        -1 means split contains remaining percent

    extension: str
        extension of the files to be read in
    
    random_seed: int
        random seed for reproduction
        if not wanted -> none

        
    Structure of given Base Folder should be like:

        Base
        │
        └─── Label0
        │    │   file01.txt
        │    │   ...
        │   
        └─── Label1
        │    │   file11.txt
        │    │   ...
        │   
        └─── Label2
            │   file21.txt
            │   ...
    """

    # List Files of folders:
    files_dict = {}
    for folder in folders:
        files_dict[folder] = [file for file in os.listdir(os.path.join(base_dir, folder)) if file.endswith(extension)]
        if random_seed:
            random.Random(random_seed).shuffle(files_dict[folder])
        else:
            random.Random().shuffle(files_dict[folder])

    # Replace -1:
    for i in range(len(splits)):
        if splits[i].count(-1) > 1: raise Exception('Only one -1 alowed in per split')
        if -1 in splits[i]:
            split = splits[i]
            index = split.index(-1)
            split[index] = len(files_dict[folders[i]]) - (sum(split) + 1)
            splits[i] = split 
 
    # Errors:
    if len(folders) != len(splits): raise Exception('Length of folders and splits dont match')
    
    for i in range(len(folders)):
        if len(files_dict[folders[i]]) != sum(splits[i]):
            raise Exception(f'Number of files in {folders[i]} and {splits[i]} dont match')
    
    for split in splits: 
        if split[0] == 0 or split[1] == 0: raise Exception('0 not allowed')
    
    val_values = [split[2] for split in splits]
    val = True
    if 0 in val_values:
        if sum(val_values) != 0:
            raise Exception('Validation either all have to be zero or given size')
        val = False
        
    # dest folders
    split_dir = os.path.join(base_dir, 'split')
    if os.path.exists(split_dir):
        shutil.rmtree(split_dir)
    Path(split_dir).mkdir(exist_ok=True)
    Path(os.path.join(split_dir, 'Train')).mkdir(exist_ok=True)
    Path(os.path.join(split_dir, 'Test')).mkdir(exist_ok=True)
    if val:
        Path(os.path.join(split_dir, 'Val')).mkdir(exist_ok=True)

    train_dest_folders = [os.path.join(split_dir, 'Train', label) for label in folders]
    test_dest_folders = [os.path.join(split_dir, 'Test', label) for label in folders]
    if val:
        val_dest_folders = [os.path.join(split_dir, 'Val', label) for label in folders]

    for new_folder in train_dest_folders: Path(new_folder).mkdir()
    for new_folder in test_dest_folders: Path(new_folder).mkdir()
    if val:
        for new_folder in val_dest_folders: Path(new_folder).mkdir()

    for i in range(len(folders)):
        folder, split = folders[i], splits[i]
        filenames = files_dict[folder]
        train_size, test_size = split[0], split[1]

        train_filenames = filenames[:train_size]
        test_filenames = filenames[train_size:train_size+test_size]
        if val:
            val_filenames = filenames[train_size+test_size:]

        for filename in train_filenames:
            src_file_path = os.path.join(base_dir, folder, filename)
            dest_file_path = os.path.join(split_dir, 'Train', folder, filename)
            shutil.copy(src_file_path, dest_file_path)
        
        for filename in test_filenames:
            src_file_path = os.path.join(base_dir, folder, filename)
            dest_file_path = os.path.join(split_dir, 'Test', folder, filename)
            shutil.copy(src_file_path, dest_file_path)

        if val:
            for filename in val_filenames:
                src_file_path = os.path.join(base_dir, folder, filename)
                dest_file_path = os.path.join(split_dir, 'Val', folder, filename)
                shutil.copy(src_file_path, dest_file_path)
