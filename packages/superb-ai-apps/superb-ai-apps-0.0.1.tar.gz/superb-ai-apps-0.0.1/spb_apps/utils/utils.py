import json
import os
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from directory_tree import display_tree


def separate_batches(image_batch_size: int, to_batch_list: list):
    image_paths = []
    number_of_iteration = len(to_batch_list) // image_batch_size + 1
    for i in range(number_of_iteration):
        start = i * image_batch_size
        end = (
            (i + 1) * image_batch_size
            if (i + 1) * image_batch_size < len(to_batch_list)
            else False
        )
        if end is False:
            subset_image_paths = to_batch_list[start:]
        else:
            subset_image_paths = to_batch_list[start:end]
        image_paths.append(subset_image_paths)

    return image_paths


def read_info_from_zip_yolo(dataset_file: str):
    try:
        second_level_folders = set()
        expected_second_level_folders = ["images", "labels"]
        image_extensions = ["jpg", "jpeg", "png", "bmp"]
        classes_txt = None

        with ZipFile(dataset_file, "r") as zip_file:
            name_list = zip_file.namelist()

            file_list = [
                f
                for f in name_list
                if "__MACOSX" not in f and "DS_Store" not in f
            ]

            top_level_folder = os.path.commonprefix(file_list)

            if top_level_folder:  # top_level/images/0001.jpg
                for item in file_list:
                    if item.count("/") == 2 and item.endswith("/"):
                        second_level_folders.add(item.split("/")[1])

                    elif item.count("/") == 1 and item.endswith("classes.txt"):
                        classes_txt = item

                image_path_list = [
                    f
                    for f in file_list
                    if f.split("/")[-1].split(".")[-1].lower()  # check ext
                    in image_extensions
                    and f.split("/")[-2] == expected_second_level_folders[0]
                ]

                annotation_path_list = [
                    f
                    for f in file_list
                    if f.split("/")[-2] == expected_second_level_folders[1]
                    and f.endswith(".txt")
                ]

            else:  # images/0001.jpg
                for item in file_list:
                    if item.count("/") == 1:
                        second_level_folders.add(item.split("/")[0])
                    elif item.count("/") == 0 and item.endswith("classes.txt"):
                        classes_txt = item

                image_path_list = [
                    f
                    for f in file_list
                    if f.split("/")[-1].split(".")[-1].lower()
                    in image_extensions
                    and f.split("/")[-2] == expected_second_level_folders[0]
                ]

                annotation_path_list = [
                    f
                    for f in file_list
                    if "/" in f
                    and f.endswith(".txt")
                    and f.split("/")[-2] == expected_second_level_folders[1]
                ]

            if set(second_level_folders) != set(expected_second_level_folders):
                if len(second_level_folders) == 0:
                    raise Exception(
                        "Required folders, 'images' and 'labels' are missing in your zip file."
                    )
                # images 폴더만 있는 경우
                elif (
                    expected_second_level_folders[0] in second_level_folders
                    and expected_second_level_folders[1]
                    not in second_level_folders
                ):
                    raise Exception(
                        "Required folder, 'labels', is missing in your zip file."
                        f"Your zip file includes {str(second_level_folders)[1:-1]}."
                    )
                # labels 폴더만 있는 경우
                elif (
                    expected_second_level_folders[0]
                    not in second_level_folders
                    and expected_second_level_folders[1]
                    in second_level_folders
                ):
                    raise Exception(
                        "Required folder, 'images', is missing in your zip file."
                        f"Your zip file includes {str(second_level_folders)[1:-1]}."
                    )

            if not classes_txt:
                raise Exception(
                    "Required file, 'classes.txt' is missing in your zip file."
                )

            if len(image_path_list) == 0:
                raise Exception(
                    "The 'images' folder contains no image files with valid formats (PNG, JPEG, JPG, BMP)."
                )

            if len(annotation_path_list) == 0:
                raise Exception(
                    "The 'labels' folder contains no label files with valid formats (txt)."
                )

            zip_file.extractall(path=Path(dataset_file).parent)

        return image_path_list, annotation_path_list, classes_txt

    except BadZipFile as e:
        file_name = dataset_file.split("/")[-1]
        raise Exception(f"[Invalid zip file] '{file_name}' {e}.")

    except Exception as e:
        print("[Zip File]")
        with ZipFile(dataset_file, "r") as zip_file:
            zip_file.extractall(path=Path(dataset_file).parent)
            display_tree(str(Path(dataset_file).parent), max_depth=2)
        print("")
        raise Exception(f"[Invalid zip file] {e}")
