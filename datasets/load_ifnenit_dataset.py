from __future__ import print_function, division

import os
import warnings

import numpy as np
from PIL import Image
from torch.utils.data import Dataset

from scripts.data_transformations import process_ifnedit_data

warnings.filterwarnings("ignore")

class IfnEnitDataset(Dataset):

    def __init__(self, cf, train=True, transform=None, data_idx= np.arange(1), complement_idx=False):
        """
        Args:
            dir_tru (string): Directory with all the GT files.
            dir_bmp (string): Directory with all the BMP images.
            transform (callable, optional): Optional transform to be applied
            on a sample.
            data_idx: numpy.ndarray as a vector ([1, 4, 5,...])  containing the idx
            used to select the set, if none is presented, idx's will be generated 
            randomly according to split_percentage. To generate the testing set, 
            the data_idx generated by the train_set should be passed to the class 
            constructor of the test_set. 
            complement_idx: generate the set from the complement of data_idx
        """
        self.cf = cf
        self.dir_bmp = cf.dataset_path_IFN
        self.dir_tru = cf.gt_path_IFN
        self.train = train  # training set or test set
        self.transform = transform
        self.word_id = []
        self.word_str = []
        self.phoc_word = []

        aux_word_id = []
        aux_word_str = []
        aux_phoc_word = []

        process_ifnedit_data(cf, aux_phoc_word, aux_word_id, aux_word_str)
        
        len_data = len(aux_word_id)
        if len(data_idx) == 1:  # this is safe as the lowest is one, when nothing is passed
            np.random.seed(cf.rnd_seed_value)
            data_idx = np.sort(np.random.choice(len_data, size=int(len_data * cf.split_percentage), replace=False) )
            
        if complement_idx:
            all_idx = np.arange(0, len_data)
            data_idx = np.sort( np.setdiff1d(all_idx, data_idx, assume_unique=False) )


        for idx in data_idx:
            self.phoc_word.append(aux_phoc_word[idx])
            self.word_id.append(aux_word_id[idx])
            self.word_str.append(aux_word_str[idx])
            
        self.len_phoc = len(self.phoc_word[0])
        self.data_idx = data_idx
        
    def num_classes(self):
        return len(self.phoc_word[0])
        
        
    def __len__(self):
        return len(self.word_id)
       
        
    def __getitem__(self, idx):
        img_name = os.path.join(self.dir_bmp, self.word_id[idx] + '.bmp')
        data = Image.open(img_name)
        if not(self.cf.H_ifn_scale ==0): # resizing just the height            
            data = data.resize((data.size[0], self.cf.H_ifn_scale), Image.ANTIALIAS)
            #    data.show()
            
        # Convert data to numpy array
        data = np.array(data.getdata(),
                    np.uint8).reshape(data.size[1], data.size[0], 1)
        if self.transform:
            data = self.transform(data)
        

        target = self.phoc_word[idx]
        word_str = self.word_str[idx]

        return data, target, word_str
    
    
    
# temp_idx = np.sort(temp_idx)
#            test_idx = []
#            prev_num = -1
#            for idx in range(train_idx.shape[0]):
#                if idx != 0:
#                    prev_num = train_idx[idx - 1]
#                while train_idx[idx] != prev_num + 1:
#                    prev_num = prev_num + 1
#                    test_idx.append(prev_num)
#            test_idx = np.sort(test_idx)
        
#
#        Choose the training or the testing indexes
#        if self.train:
#            data_idx = train_idx
#        else:
#            data_idx = test_idx