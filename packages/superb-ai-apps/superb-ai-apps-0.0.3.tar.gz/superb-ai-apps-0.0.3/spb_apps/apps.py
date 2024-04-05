from typing import Dict, List, Tuple

from spb_label import sdk as spb_label

from spb_apps.curate.superb_curate import SuperbCurate
from spb_apps.label.superb_label import SuperbLabel
from spb_apps.utils.converter import convert_yolo_bbox
from spb_apps.utils.utils import read_info_from_zip_yolo


class SuperbApps:
    """
    A class to manage and interact with Superb applications Label and Curate.
    """

    def __init__(
        self,
        team_name: str,
        access_key: str,
        platform: str,
        project_id: str = "",
        project_name: str = "",
        dataset_name="",
    ):
        """
        Initializes the SuperbApps instance with necessary details and clients based on the platform.

        Args:
            team_name (str): The name of the team.
            access_key (str): The access key for authentication.
            platform (list): A list of platforms to initialize (e.g., ['label', 'curate']).
            project_id (str, optional): The ID of the project for labeling. Defaults to "".
            dataset_name (str, optional): The name of the dataset for Curate. Defaults to "".
        """
        self.team_name = team_name
        self.access_key = access_key
        if platform == "label":
            self.client = SuperbLabel(
                team_name=team_name,
                access_key=access_key,
                project_id=project_id,
                project_name=project_name,
            )

            self.label_project_name = self.client.client._project.name
        if platform == "curate":
            self.client = SuperbCurate(
                team_name=team_name,
                access_key=access_key,
                dataset_name=dataset_name,
            )
        self.platform = platform

    def download_image_by_key(self, data_key: str, path: str = None):
        """
        Downloads an image by its data key.

        Args:
            data_key (str): The data key of the image to download.
            path (str, optional): The local file path where the image will be saved. Defaults to None.
        """
        if self.platform == "label":
            _, label = self.client.get_labels(data_key=data_key)
            self.client.download_image(label=label[0], path=path)
        if self.platform == "curate":
            self.client.download_image(data_key=data_key, download_path=path)

    def download_image_by_filter(
        self,
        tags: list = [],
        data_key: str = "",
        status: list = [],
        path: str = None,
    ):
        """
        Downloads images by applying filters such as tags, data key, and status.

        Args:
            tags (list, optional): A list of tags to filter images. Defaults to [].
            data_key (str, optional): A data key to filter images. Defaults to "".
            status (list, optional): A list of statuses to filter images. Defaults to [].
            path (str, optional): The local file path where the images will be saved. Defaults to None.
        """
        from concurrent.futures import ThreadPoolExecutor

        if self.platform == "label":

            def download(label):
                self.client.download_image(label=label, path=path)

            count, labels = self.client.get_labels(
                tags=tags, data_key=data_key, status=status
            )
            print(f"Downloading {count} data to {path}")
            if count > 50:
                with ThreadPoolExecutor(max_workers=4) as executor:
                    executor.map(download, labels)
            else:
                for label in labels:
                    download(label)
        else:
            print("Curate does not have filters")

    def get_width_height(
        self, data_hanler: spb_label.DataHandle = None, data_key: str = ""
    ) -> Tuple[int, int]:
        """
        Retrieves the width and height of an image based on its data key.

        This method supports both 'label' and 'curate' platforms. It fetches the image's dimensions
        by utilizing the respective client's method to get the width and height.

        Args:
            data_key (str): The unique identifier for the image.

        Returns:
            Tuple[int, int]: A tuple containing the width and height of the image.
        """
        if self.platform == "label":
            if data_hanler == None:
                print("Label takes data handler object from spb_label")
                return
            return self.client.get_width_height(label=data_hanler)
        if self.platform == "curate":
            if data_key == "":
                print("Curate takes data key")
                return
            return self.client.get_width_height(data_key=data_key)

    def get_labels(
        self,
        data_key: str = "",
        tags: list = [],
        assignees: list = [],
        status: list = [],
        all: bool = False,
    ) -> Tuple[int, List]:
        """
        Retrieves labels based on filters or all labels if specified.

        Args:
            data_key (str, optional): A data key to filter labels. Defaults to "".
            tags (list, optional): A list of tags to filter labels. Defaults to [].
            assignees (list, optional): A list of assignees to filter labels. Defaults to [].
            status (list, optional): A list of statuses to filter labels. Defaults to [].
            all (bool, optional): If True, retrieves all labels ignoring other filters. Defaults to False.

        Returns:
            Tuple[int, List]: A tuple containing the count of labels and a list of labels.
        """
        count, labels = self.label_client.get_labels(
            data_key=data_key,
            tags=tags,
            assignees=assignees,
            status=status,
            all=all,
        )

        return count, labels

    def change_project(self, project_name: str):
        """
        Changes the project context for the label client.

        Args:
            project_name (str): The name of the project to switch to.
        """
        self.label_client.client.set_project(name=project_name)
        self.label_project_name = self.label_client.client._project.name

    def get_label_interface(self) -> Dict:
        """
        Retrieves the label interface configuration.

        Returns:
            Dict: The label interface configuration.
        """
        lb_interface = self.label_client.client.project.label_interface
        return lb_interface

    def make_bbox(self, class_name: str, annotation: list, data_key: str = ""):
        """
        Creates a bounding box based on the specified platform ('label' or 'curate').

        Args:
            class_name (str): The class name associated with the bounding box.
            annotation (list): A list containing the x, y coordinates, width, and height of the bounding box.
            data_key (str, optional): The unique identifier for the image. Required for 'curate' platform.

        Returns:
            The result of the bounding box setting operation, which varies by platform.
            For 'label', it returns the result of `client.bbox_setting` with class_name and annotation.
            For 'curate', it additionally requires a data_key and returns the result of `client.bbox_setting` with data_key, class_name, and annotation.
            If the required data_key is not provided for 'curate', it prints a message and returns None.
        """
        if self.platform == "label":
            return self.client.bbox_setting(
                class_name=class_name, annotation=annotation
            )
        if self.platform == "curate":
            if data_key == "":
                print("To make a Curate bbox, you must provide a data_key.")
                return
            return self.client.bbox_setting(
                data_key=data_key, class_name=class_name, annotation=annotation
            )

    def upload_images(self, images_path: str, dataset_name: str = ""):
        """
        Uploads images to the specified platform ('label' or 'curate').

        For the 'label' platform, a dataset name must be specified. If not, an error message is printed.
        For the 'curate' platform, images are uploaded without needing a dataset name.

        Args:
            images_path (str): The path to the images to be uploaded.
            dataset_name (str, optional): The name of the dataset to upload the images to. Required for 'label' platform.

        Returns:
            The result of the image upload operation, which varies by platform.
            For 'label', it returns the result of `client.upload_image` with images_path and dataset_name.
            For 'curate', it returns the result of `client.curate_upload_images` with images_path.
            If the required dataset_name is not provided for 'label', it prints a message and returns None.
        """
        if self.platform == "label":
            if dataset_name == "":
                print("Must specify a dataset name when uploading to Label")
                return
            return self.client.upload_image(images_path, dataset_name)
        if self.platform == "curate":
            return self.client.curate_upload_images(images_path)

    def upload_annotations(
        self, data_key: str, annotations: list, format: str, classes: list = ""
    ):
        """
        Uploads annotations to the specified platform ('label' or 'curate') based on the provided format.

        For the 'label' platform and 'yolo' format, it converts YOLO annotations to the platform's format and uploads them.
        Requires a list of classes for 'yolo' format. If classes are not provided, it prints a message and returns None.

        Args:
            data_key (str): The unique identifier for the data to which the annotations belong.
            annotations (list): A list of annotations to be uploaded.
            format (str): The format of the annotations ('yolo', etc.).
            classes (list, optional): The list of classes associated with the annotations. Required for 'yolo' format.

        Returns:
            None. Prints a message if classes are not provided for 'yolo' format.
        """
        if self.platform == "label":
            _, label = self.client.get_labels(data_key=data_key)
            data_handler = label[0]
            if format == "yolo":
                if classes == "":
                    print(
                        "To upload yolo annotations, you must provide a classes."
                    )
                    return
                width, height = self.get_width_height(data_handler)
                converted_annotations = convert_yolo_bbox(
                    data_key, annotations, classes, width, height
                )
                if converted_annotations is not None:
                    self.client.upload_annotation(
                        data_handler, converted_annotations
                    )

    def read_yolo_zip(self, dataset_file: str):
        """
        Reads information from a YOLO formatted zip file.

        Args:
            dataset_file (str): The path to the YOLO formatted zip file.

        Returns:
            The information read from the zip file.
        """
        return read_info_from_zip_yolo(dataset_file)
