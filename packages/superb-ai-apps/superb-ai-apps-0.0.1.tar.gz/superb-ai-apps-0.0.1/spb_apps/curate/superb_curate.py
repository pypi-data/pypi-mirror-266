import json
import os
import time
from pathlib import Path
from timeit import default_timer as timer
from typing import List, Tuple
from uuid import uuid4

import requests
import spb_curate
from spb_curate.error import ConflictError

from spb_apps.utils.utils import separate_batches

SLEEP_INTERVAL = 5  # time in seconds to wait between loop iterations


class SuperbCurate(object):
    def __init__(
        self,
        team_name: str,
        access_key: str,
        dataset_name: str = "",
        slice_name: str = "",
        is_dev: bool = False,
    ):
        """
        Initializes the SuperbCurate class with team, dataset, and slice details.
        Optionally sets the environment to development mode.

        :param team_name: Name of the team
        :param access_key: Access key for authentication
        :param dataset_name: Name of the dataset (optional)
        :param slice_name: Name of the slice within the dataset (optional)
        :param is_dev: Flag to set the environment to development mode (optional)
        """
        self.team_name: str = team_name  # Team name
        self.access_key: str = access_key  # Access key for authentication
        self.dataset_name: str = dataset_name  # Dataset name (optional)
        # Set global variables in spb_curate module for team name and access key
        spb_curate.team_name = self.team_name
        spb_curate.access_key = self.access_key
        # Set API base URL to development environment if in development mode
        if is_dev:
            spb_curate.api_base = "https://api.dev.superb-ai.com"

        # Attempt to fetch the dataset if a dataset name is provided
        if len(dataset_name) > 0:
            try:
                self.dataset = spb_curate.fetch_dataset(name=dataset_name)
            except ConflictError:
                # Notify the user if the dataset does not exist and needs to be created
                print(
                    f"Dataset does not exist, Creating Dataset {dataset_name}"
                )
                self.dataset = spb_curate.create_dataset(
                    name=dataset_name, description="Demo dataset."
                )
        # Attempt to fetch the slice from the dataset if a slice name is provided
        if len(slice_name) > 0:
            self.slice = self.dataset.fetch_slice(
                name=slice_name
            )  # Fetch the slice

    def curate_prep_images(self, images_path: list) -> List[spb_curate.Image]:
        """
        This will prep local images for Superb Curate by creating a list of
        Superb Curate images.

        Args:
            images_path (list): list of paths to upload

        Returns:
            List[spb_curate.Image]: list of curate images to upload
        """
        curate_images: List[spb_curate.Image] = []
        for image in images_path:
            curate_images.append(
                spb_curate.Image(
                    key=image.split("/")[-1],
                    source=spb_curate.ImageSourceLocal(asset=image),
                    metadata={},
                )
            )

        return curate_images

    def curate_upload_images(self, image_path: list):
        """
        Uploads images in batches to the dataset.

        Args:
            image_path (list): List of image paths to upload.
        """
        # Separate images into batches of 500
        seperated_images = separate_batches(
            image_batch_size=500, to_batch_list=image_path
        )
        total_loops = len(seperated_images)  # Total number of batches
        for idx, sep_images in enumerate(seperated_images, start=1):
            # Prepare images for upload
            curate_images = self.curate_prep_images(images_path=sep_images)
            # Create bulk image import job
            image_import_job = spb_curate.Image.create_bulk(
                dataset_id=self.curate_dataset["id"], images=curate_images
            )

            print(f"created an image import job: ({idx}/{total_loops})")
            start_time = timer()  # Start timing the upload process

            while True:
                # Fetch the current status of the import job
                image_import_job = spb_curate.Job.fetch(
                    id=image_import_job["id"]
                )
                print(
                    f"job progress: {image_import_job['progress']}", end="\r"
                )

                # Check if the job is complete
                if image_import_job["status"] == "COMPLETE":
                    # Print any failure details if present
                    if image_import_job["result"]["fail_detail"]:
                        print(image_import_job["result"]["fail_detail"])
                        print(image_import_job["fail_reason"])
                    break  # Exit the loop if job is complete

                if image_import_job["status"] == "FAILED":
                    if image_import_job["result"]["fail_detail"]:
                        print(
                            "[INFO] Fail detail: ",
                            image_import_job["result"]["fail_detail"],
                        )
                        print(
                            "[INFO] Fail reason: ",
                            image_import_job["fail_reason"],
                        )
                    break
                time.sleep(
                    SLEEP_INTERVAL
                )  # Wait before checking the status again

            print(
                f"total time: {timer() - start_time}"
            )  # Print total upload time

    def curate_prep_annotations(self, annotation: list) -> List:
        """
        Prepares annotations for upload by creating a list of spb_curate.Annotation objects.

        Args:
            annotation (list): List of dictionaries containing annotation details.

        Returns:
            List[spb_curate.Annotation]: List of prepared annotations for upload.
        """
        curate_annotations: List[spb_curate.Annotation] = []
        for anno in annotation:
            meta = anno.get(
                "metadata", {"iscrowd": 0}
            )  # Safely get metadata or default
            curate_annotations.append(
                spb_curate.Annotation(
                    image_key=anno[
                        "data_key"
                    ],  # Key of the image being annotated
                    annotation_class=anno[
                        "class_name"
                    ],  # Class of the annotation
                    annotation_type=anno[
                        "annotation_type"
                    ],  # Type of annotation (e.g., bounding box, segmentation)
                    annotation_value=anno[
                        "annotation"
                    ],  # The actual annotation data
                    metadata=meta,
                )
            )

        return curate_annotations

    def curate_upload_annotations(
        self,
        annotation_list: list,
    ):
        """
        Uploads annotations in batches to the dataset.

        Args:
            annotation_list (list): List of annotations to upload. Format is a
                                    list of dicts that are made up of "class_name", "annotation", "data_key", "annotation_type", "metadata" (optional)
        """
        # Separate annotations into batches of 500 for upload
        seperated_images = separate_batches(
            image_batch_size=500, to_batch_list=annotation_list
        )
        for idx, sep_annotations in enumerate(seperated_images, start=1):
            # Prepare annotations for upload
            # Create bulk annotation import job
            annotation_import_job = spb_curate.Annotation.create_bulk(
                dataset_id=self.curate_dataset[
                    "id"
                ],  # Dataset ID to upload annotations to
                annotations=sep_annotations,  # Prepared annotations for upload
            )

            while True:
                # Fetch the current status of the annotation import job
                annotation_import_job = spb_curate.Job.fetch(
                    id=annotation_import_job["id"]
                )

                print(
                    f"[INFO] {(idx-1) * 500 + annotation_import_job['progress']} / {len(annotation_list)} labels updated"
                )

                if annotation_import_job["status"] == "COMPLETE":
                    # Check for and print any failure details if present
                    if annotation_import_job["result"]["fail_detail"]:
                        print(
                            "[INFO] Fail detail: ",
                            annotation_import_job["result"]["fail_detail"],
                        )
                        print(
                            "[INFO] Fail reason: ",
                            annotation_import_job["fail_reason"],
                        )
                    break  # Exit the loop if job is complete

                if annotation_import_job["status"] == "FAILED":
                    if annotation_import_job["result"]["fail_detail"]:
                        print(
                            "[INFO] Fail detail: ",
                            annotation_import_job["result"]["fail_detail"],
                        )
                        print(
                            "[INFO] Fail reason: ",
                            annotation_import_job["fail_reason"],
                        )
                    break
                time.sleep(
                    SLEEP_INTERVAL
                )  # Wait before checking the status again

    def get_width_height(self, data_key: str) -> Tuple[int, int]:
        """
        Fetches the width and height of an image using its data key.

        Args:
            data_key (str): The unique identifier for the image.

        Returns:
            Tuple[int, int]: A tuple containing the width and height of the image.
        """
        image = self.dataset.fetch_images(key=data_key)[0]
        meta = image["metadata"]
        width, height = meta["_width"], meta["_height"]
        return width, height

    def download_image(self, data_key: str, download_path: str):
        """
        Downloads an image from the dataset using its data key.
        """
        image_url = self.dataset.fetch_images(
            key=data_key, include_image_url=True
        )[0]["image_url"]
        try:
            response = requests.get(image_url)
            response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX/5XX
            with open(download_path, "wb") as f:
                f.write(response.content)
            print(f"[INFO] Image downloaded successfully: {download_path}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to download image: {e}")

    def bbox_setting(
        self, data_key: str, class_name: str, annotation: list
    ) -> spb_curate.Annotation:
        """
        Creates a bounding box annotation for a given image.

        Args:
            data_key (str): The unique identifier for the image.
            class_name (str): The class name associated with the bounding box.
            annotation (list): A list containing the x, y coordinates, width, and height of the bounding box.

        Returns:
            spb_curate.Annotation: An Annotation object representing the bounding box.
        """
        bounding_box = spb_curate.BoundingBox(
            raw_data={
                "x": annotation[0],
                "y": annotation[1],
                "width": annotation[2],
                "height": annotation[3],
            },
        )
        bbox_annotation = spb_curate.Annotation(
            image_key=data_key,
            annotation_class=class_name,
            annotation_type="box",
            annotation_value=bounding_box,
            metadata={},
        )

        return bbox_annotation
