import os
from datetime import datetime
from pathlib import Path

import magic

from komodo.proto.generated.collection_pb2 import File
from komodo.shared.utils.digest import get_file_digest_full, get_text_digest_short
from komodo.store.proto_utils import convert_proto_to_dict


def file_details(filepath):
    path = Path(filepath)
    guid = get_text_digest_short(str(path.absolute()))
    checksum = get_file_digest_full(filepath)

    file = File(guid=guid, path=str(path))
    stat = path.stat()
    file.name = path.stem
    file.size = stat.st_size
    file.magic = magic.from_file(filepath, mime=True)
    file.checksum = checksum
    file.created_at = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
    file.modified_at = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    return file


def file_details_dict(filepath):
    return convert_proto_to_dict(file_details(filepath))


if __name__ == "__main__":
    print(os.curdir)
    for f in os.listdir(os.curdir):
        d = file_details(f)
        m = convert_proto_to_dict(d)
        print(m)
