import os


def create_name(path):
    return str(os.path.basename(path).split('.')[0])
