import h5py
import numpy as np
import os
import shutil
from pathlib import Path
import argparse

params = {
    "targetNum": 5,
    "geneNum": 100,
    "effectSgRNA": 4,
    "tpRatio": 40,
    "n": 10,
    "p": 0.1,
    "low": 1,
    "high": 5,
    "size": 1_000,
    "FalseLimits": (0.01,0.5),
    "ObservationNum": (10,3)
    }

# Specify the HDF5 file name
filename = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'parameters.h5')
user_parameters_path = os.path.join(Path.home(), '.AIPyS', 'parameters.h5')

def parametersGnert():
    # Open a new HDF5 file
    with h5py.File(filename, 'w') as hdf:
        # Iterate through dictionary items and save them to the HDF5 file
        for key, value in params.items():
            # Convert None values to a recognizable string, as NoneType can't be directly stored
            if value is None:
                value = 'None'
            # Check if value needs to be stored as a string
            if isinstance(value, str):
                dt = h5py.special_dtype(vlen=str)  # special dtype for variable-length strings
                dset = hdf.create_dataset(key, (1,), dtype=dt)
                dset[0] = value
            else:
                # Directly store if the value is numeric
                hdf.create_dataset(key, data=value)
    print(f"Parameters saved to {filename}")

def resetParameters():
    if not os.path.exists(user_parameters_path):
        #if missing creat
        os.makedirs(os.path.dirname(user_parameters_path), exist_ok=True)
        shutil.copy(filename, user_parameters_path)
        print(f'Created a personal parameters file at {user_parameters_path}')
    else:
        #reset
        parametersGnert()
        shutil.copy(filename, os.path.join(Path.home(), '.AIPyS'))
        print(f'personal parameters reset at file at {user_parameters_path}')

def display_parameters():
    """Read and display parameters from the user's parameters.h5 file."""
    with h5py.File(user_parameters_path, 'r') as hdf:
        print("Current parameters stored in the H5 file:")
        for key in hdf.keys():
            print(f"{key}: {hdf[key][()]}")

def main():
    parser = argparse.ArgumentParser(description='Manage parameters file', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('action', choices=['generate', 'reset', 'display'],
                        help="generate: Create a new parameters file with default values."
                             "reset: Reset the parameters file to default values."
                             "display: Show current values in the parameters file.")
    args = parser.parse_args()
    
    if args.action == 'generate':
        parametersGnert()
    elif args.action == 'reset':
        resetParameters()
    elif args.action == 'display':
        display_parameters()
    else:
        raise ValueError("Unknown action. Available actions: generate, reset, display")

if __name__ == "__main__":
    main()