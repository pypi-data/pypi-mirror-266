import os
import subprocess
import uuid
import hashlib



def get_checksum(path):

    if not os.path.isfile(path) or not os.path.exists(path):
        return None

    sha256_hash = hashlib.sha256()
    with open(path,"rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_size(path):

    if not os.path.isfile(path) or not os.path.exists(path):
        return 0

    statinfo = os.stat(path)
    return statinfo.st_size


def get_consistent_uuid(text):
    # https://stackoverflow.com/questions/41186818/how-to-generate-a-random-uuid-which-is-reproducible-with-a-seed-in-python

    for n in range(0, 10):
        m = hashlib.md5()
        m.update((text + " " * n).encode("utf-8"))
        new_uuid = uuid.UUID(m.hexdigest())
        if str(new_uuid)[0] == "0":
            continue
        else:
            break

    assert str(new_uuid)[0] != "0"
    return new_uuid
