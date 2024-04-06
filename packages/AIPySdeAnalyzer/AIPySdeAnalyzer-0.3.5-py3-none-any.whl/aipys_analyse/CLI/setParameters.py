import os
import shutil
import h5py
from pathlib import Path
import numpy as np
import argparse
import pdb

# Assuming the 'default_parameters.h5' file is located directly inside the package folder
#default_parameters_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'default_parameters.h5')
default_parameters_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'parameters.h5')
# Determine the user's home configuration path
user_parameters_path = os.path.join(Path.home(), '.AIPyS', 'parameters.h5') # save the parameter file to .AIPyS folder. 

def ensure_user_parameters():
    """Ensure the user has their own copy of parameters.h5; if not, create it."""
    if not os.path.exists(user_parameters_path):
        os.makedirs(os.path.dirname(user_parameters_path), exist_ok=True)
        shutil.copy(default_parameters_path, user_parameters_path)
        print(f'Created a personal parameters file at {user_parameters_path}')


def update_auto_parameters(parameter_updates,user_parameters_path):
    '''
    this function is used for updating h5 file based on results
    e.g. intercept and slope from model build
    '''
    with h5py.File(user_parameters_path, 'r+') as hdf:
        for key, value in parameter_updates.items():
            if key in hdf:
                value = 'None' if value is None else value
                if isinstance(value, str):
                    hdf[key][()] = np.array(value, dtype=h5py.special_dtype(vlen=str))
                else:
                    hdf[key][...] = value
            else:
                # If the key does not exist in the HDF5 file, create a new dataset.
                if isinstance(value, str):
                    dt = h5py.special_dtype(vlen=str)
                    hdf.create_dataset(key, data=np.array(value, dtype=dt), dtype=dt)
                else:
                    hdf.create_dataset(key, data=value)
                print(f"'{key}' added to or updated in the HDF5 file with value: {value}")



def update_user_parameters(parameter_updates):
    """Example function to update parameters in the user's parameters.h5 file."""
    ensure_user_parameters()  # Ensure the user copy exists
    #pdb.set_trace()
    with h5py.File(user_parameters_path, 'r+') as hdf:
        for key, value in parameter_updates.items():
            if key in hdf:
                value = 'None' if value is None else value
                if isinstance(value, str):
                    hdf[key][()] = np.array(value, dtype=h5py.special_dtype(vlen=str))
                else:
                    hdf[key][...] = value
            else:
                # If the key does not exist in the HDF5 file, create a new dataset.
                if isinstance(value, str):
                    dt = h5py.special_dtype(vlen=str)
                    hdf.create_dataset(key, data=np.array(value, dtype=dt), dtype=dt)
                else:
                    hdf.create_dataset(key, data=value)
                print(f"'{key}' added to or updated in the HDF5 file with value: {value}")

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle

# def read_user_parameters():
#     """Example function to read parameters from the user's parameters.h5 file."""
#     ensure_user_parameters()  # Ensure the user copy exists
#     with h5py.File(user_parameters_path, 'r') as hdf:
#         # Read and return parameters as needed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This program provides a command-line interface for updating, adding, or displaying parameters stored in a .h5 file. It's designed to manage experimental parameters for bioinformatics or genetic studies,enabling users to easily modify values such as target numbers, gene counts, target plasmid ratios, and more. Whether you're adjusting the setup for a new experiment or reviewing configurations for an ongoing study, this tool simplifies parameter management without the need to manually edit files.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--targetNum', type=int, help="Specifies the target number.")
    parser.add_argument('--geneNum', type=int, help="Specifies the number of genes.")
    parser.add_argument('--effectSgRNA', type=int, help="Specifies the number of effective sgRNAs.")
    parser.add_argument('--tpRatio', type=int, help="The target plasmid ratio, indicating the balance between target and control.")
    parser.add_argument('--n', type=int, help="Expected negative binomial rate (mu) for the distribution.")
    parser.add_argument('--p', type=float, help="Dispersion (alpha) of the negative binomial distribution.")
    parser.add_argument('--low', type=int, help="Specifies the lower limit.")
    parser.add_argument('--high', type=int, help="Specifies the upper limit.")
    parser.add_argument('--size', type=int, help="The total sum of the master (M) sample before generating H_0.")
    parser.add_argument('--FalseLimits', nargs=2, type=float, help="A tuple indicating the minimum and maximum viral particles per cell. e.g., --FalseLimits 0.01 0.5")
    parser.add_argument('--ObservationNum', nargs=2, type=int, help="The number of observations and their standard deviation to generate. e.g., --ObservationNum 70 3")
    
    args = parser.parse_args()
   
    # Construct the dictionary from provided CLI arguments
    # Exclude 'h5_file' from update_dict, as it's not a parameter to store but the file path
    update_dict = {k: v for k, v in vars(args).items() if k != 'h5_file' and v is not None}
    #pdb.set_trace()
    # Update or add parameters in the H5 file
    update_user_parameters(update_dict)