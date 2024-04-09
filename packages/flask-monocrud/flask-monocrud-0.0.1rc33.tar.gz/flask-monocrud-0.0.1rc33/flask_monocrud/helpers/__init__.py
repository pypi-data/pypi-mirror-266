import os
import shutil
import inspect
import yaml

from .get_by_dot import getByDot
from .to_class import to_class


def from_config(key):
    config = yaml.load(open("config/config.yaml", "r"), Loader=yaml.FullLoader)
    return getByDot(config, key)


def copy_folder_contents(source_folder_relative, destination_folder):
    # Get the absolute path of the directory containing this script
    package_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path of the source folder relative to the package directory
    source_folder = os.path.join(package_dir, source_folder_relative)

    # Make sure the source folder exists
    if not os.path.exists(source_folder):
        print(f"Source folder '{source_folder}' does not exist.")
        return

    # Make sure the destination folder exists, if not create it
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Iterate over each item in the source folder
    for item in os.listdir(source_folder):
        source_item = os.path.join(source_folder, item)
        destination_item = os.path.join(destination_folder, item)

        # If the item is a file, copy it to the destination
        if os.path.isfile(source_item):
            shutil.copy2(source_item, destination_item)
            print(f"File '{item}' copied to '{destination_folder}'")
        # If the item is a directory, recursively copy its contents
        elif os.path.isdir(source_item):
            shutil.copytree(source_item, destination_item)
            print(f"Folder '{item}' copied to '{destination_folder}'")

