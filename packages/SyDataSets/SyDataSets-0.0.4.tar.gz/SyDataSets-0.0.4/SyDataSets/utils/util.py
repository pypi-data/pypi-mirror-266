import tarfile
import os
import uuid

#Decompress and delete files
def extract_tar_gz(tar_gz_file, destination_dir):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    with tarfile.open(tar_gz_file, 'r:gz') as tar:
        tar.extractall(path=destination_dir)
    os.remove(tar_gz_file)

#Generate a unique request id
def generate_token():
    token = uuid.uuid4()
    return str(token)
#Determine the data saving path
def get_absolute_path(user_input):
    if os.path.isabs(user_input):
        return user_input  
    else:
        return os.path.abspath(user_input)