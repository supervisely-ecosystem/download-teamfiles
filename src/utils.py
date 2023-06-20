import os
import zipfile
import tarfile

from tqdm import tqdm


def unpack_if_archive(path: str) -> str:
    if os.path.isdir(path):
        return path

    extraction_path = os.path.splitext(path)[0]

    if zipfile.is_zipfile(path):
        os.makedirs(extraction_path, exist_ok=True)

        with zipfile.ZipFile(path, "r") as zip_ref:
            total_files = len(zip_ref.infolist())
            
            for file in tqdm(iterable=zip_ref.infolist(), total=total_files, unit="file"):
                zip_ref.extract(file, extraction_path)

            return extraction_path

    if tarfile.is_tarfile(path):
        os.makedirs(extraction_path, exist_ok=True)

        with tarfile.open(path, "r") as tar_ref:
            total_files = len(tar_ref.getnames())
            
            for file in tqdm(iterable=tar_ref.getnames(), total=total_files, unit="file"):
                tar_ref.extract(file, extraction_path)

            return extraction_path

    return path