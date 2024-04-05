import os
from io import BytesIO
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import uuid4

import phy_credit
import requests
from PIL import Image
from spb_label import sdk as spb_label
from spb_label.exceptions import ParameterException
from spb_label.utils import SearchFilter


class SuperbLabel(object):
    def __init__(
        self,
        team_name: str,
        access_key: str,
        project_id: str = "",
        project_name: str = "",
    ):
        """
        Initializes the SuperbLabel class with necessary details for operation.

        :param team_name: The name of the team.
        :param access_key: The access key for authentication.
        :param project_id: The ID of the project to be set for the client.
        """
        self.team_name = (
            team_name  # Assign the provided team name to an instance variable.
        )
        self.client = spb_label.Client(
            team_name=team_name,
            access_key=access_key,
            project_id=project_id if project_id else None,
            project_name=project_name if project_name else None,
        )

    def download_export(
        self,
        input_path: str,
        export_id: str,
    ):
        """
        Downloads an export from the server to a local path.

        :param input_path: The local file path where the export will be saved.
        :param export_id: The ID of the export to download.
        """
        print("[INFO] Checking for the export to be downloaded...")
        download_url = self.client.get_export(
            id=export_id
        ).download_url  # Retrieve the download URL for the export.
        r = requests.get(
            download_url
        )  # Make a GET request to the download URL.
        if r.status_code == 200:  # Check if the request was successful.
            print("Saving export to local path")
            Path(input_path).parents[0].mkdir(
                parents=True, exist_ok=True
            )  # Ensure the directory exists.
            with open(
                input_path, "wb"
            ) as f:  # Open the file in write-binary mode.
                f.write(
                    r.content
                )  # Write the content of the response to the file.
        else:
            print(
                f"Failed to download the file. Status code: {r.status_code}"
            )  # Log failure.

    def get_labels(
        self,
        data_key: str = "",
        tags: list = [],
        assignees: list = [],
        status: list = [],
        all: bool = False,
    ) -> Tuple[int, List]:
        """
        Retrieves labels based on provided filters or all labels if specified.

        :param data_key: Filter for specific data key.
        :param tags: Filter for specific tags.
        :param assignees: Filter for specific assignees.
        :param status: Filter for specific status.
        :param all: If True, ignores other filters and retrieves all labels.
        :return: A tuple containing the count of labels and a list of labels.
        """
        if all:  # If retrieving all labels.
            next_cursor = None
            count, labels, next_cursor = self.client.get_labels(
                cursor=next_cursor
            )  # Retrieve all labels.
        else:  # If using filters.
            filter = SearchFilter(
                project=self.client.project
            )  # Create a search filter.
            if data_key:
                filter.data_key_matches = data_key  # Set data key filter.
            if tags:
                filter.tag_name_all = tags  # Set tags filter.
            if assignees:
                filter.assignee_is_any_one_of = (
                    assignees  # Set assignees filter.
                )
            if status:
                filter.status_is_any_one_of = status  # Set status filter.
            next_cursor = None
            count, labels, next_cursor = self.client.get_labels(
                filter=filter, cursor=next_cursor
            )  # Retrieve filtered labels.

        return count, labels  # Return the count and list of labels.

    def download_image(self, label: spb_label.DataHandle, path: str = None):
        """
        Downloads an image associated with a label to a specified path.

        :param label: The label data handle containing the image to download.
        :param path: The local file path where the image will be saved. If None, defaults to the label's default path.
        """
        label.download_image(
            download_to=path
        )  # Download the image to the specified path.

    def get_width_height(self, label: spb_label.DataHandle) -> Tuple[int, int]:
        """
        Downloads an image associated with a label to a specified path, returns its width and height, and deletes the image.

        :param label: The label data handle containing the image to download.
        :return: A tuple containing the width and height of the downloaded image.
        """
        image_url = label.get_image_url()
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        width, height = img.size

        return width, height

    def bbox_setting(self, class_name: str, annotation: list):
        """
        Creates a bounding box setting for a given class name and annotation coordinates.

        :param class_name: The class name associated with the bounding box.
        :param annotation: A list containing the coordinates of the bounding box in the order [x, y, width, height].
        :return: A tuple containing the class name and a dictionary with the bounding box coordinates.
        """
        bbox = {
            "class_name": class_name,
            "annotation": {
                "coord": {
                    "x": annotation[0],
                    "y": annotation[1],
                    "width": annotation[2],
                    "height": annotation[3],
                }
            },
        }

        return bbox

    def upload_image(self, image_paths: list, dataset_name: str):
        for path in image_paths:
            try:
                self.client.upload_image(path, dataset_name)
            except ParameterException as e:
                print(f"[ERROR]: Uploading went wrong: {e}")

        return

    def upload_annotation(
        self, label: spb_label.DataHandle, annotations: list
    ):
        for anno in annotations:
            bbox = self.bbox_setting(anno[0], anno[1])
            label.add_object_label(bbox)
        label.update_info()

    def build_label_interface_from_yolo(
        self,
        dataset_file: str,
        class_file_path: str,
    ):
        existing_label_interface = self.client.label_interface
        if existing_label_interface:
            label_interface = phy_credit.imageV2.LabelInterface.from_dict(
                existing_label_interface
            )
            object_detection = phy_credit.imageV2.ObjectDetectionDef.from_dict(
                existing_label_interface.get("object_detection")
            )
        else:
            # get default label_interface and object_detection (json)
            label_interface = phy_credit.imageV2.LabelInterface.get_default()
            object_detection = (
                phy_credit.imageV2.ObjectDetectionDef.get_default()
            )

        # create class map from classes.txt and create label interface for project
        category_map = dict()
        with open(
            os.path.join(Path(dataset_file).parent, class_file_path), "r"
        ) as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            category_map[i] = line.rstrip("\n")
            bbox_suite_class_id = str(uuid4())
            bbox_suite_class_name = category_map[i]

            object_detection.add_box(
                name=bbox_suite_class_name, id=bbox_suite_class_id
            )

        label_interface.set_object_detection(object_detection=object_detection)
        print("[Classes]")
        for value in category_map.values():
            print(value, end=",")
        print("")
        print("")
        return label_interface, category_map
