# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

""" Post-processing functions."""

import os
import numpy as np
import json
import cv2
from PIL import Image
import supervision as sv

__all__ = [
    "save_detection_images",
    "save_crop_images",
    "save_detection_json",
    "save_detection_classification_json",
]


# !!! Output paths need to be optimized !!!
def save_detection_images(results, output_dir):
    """
    Save detected images with bounding boxes and labels annotated.

    Args:
        results (list or dict):
            Detection results containing image ID, detections, and labels.
        output_dir (str):
            Directory to save the annotated images.
    """
    box_annotator = sv.BoxAnnotator(thickness=4, text_thickness=4, text_scale=2)
    os.makedirs(output_dir, exist_ok=True)

    with sv.ImageSink(target_dir_path=output_dir, overwrite=True) as sink:
        if isinstance(results, list):
            for entry in results:
                annotated_img = box_annotator.annotate(
                    scene=np.array(Image.open(entry["img_id"]).convert("RGB")),
                    detections=entry["detections"],
                    labels=entry["labels"],
                )
                sink.save_image(
                    image=cv2.cvtColor(annotated_img, cv2.COLOR_RGB2BGR), image_name=entry["img_id"].rsplit(os.sep, 1)[1]
                )
        else:
            annotated_img = box_annotator.annotate(
                scene=np.array(Image.open(results["img_id"]).convert("RGB")),
                detections=results["detections"],
                labels=results["labels"],
            )
            sink.save_image(
                image=cv2.cvtColor(annotated_img, cv2.COLOR_RGB2BGR), image_name=results["img_id"].rsplit(os.sep, 1)[1]
            )


# !!! Output paths need to be optimized !!!
def save_crop_images(results, output_dir):
    """
    Save cropped images based on the detection bounding boxes.

    Args:
        results (list):
            Detection results containing image ID and detections.
        output_dir (str):
            Directory to save the cropped images.
    """
    assert isinstance(results, list)
    os.makedirs(output_dir, exist_ok=True)
    with sv.ImageSink(target_dir_path=output_dir, overwrite=True) as sink:
        for entry in results:
            for i, (xyxy, _, _, cat, _) in enumerate(entry["detections"]):
                cropped_img = sv.crop_image(
                    image=np.array(Image.open(entry["img_id"]).convert("RGB")), xyxy=xyxy
                )
                sink.save_image(
                    image=cv2.cvtColor(cropped_img, cv2.COLOR_RGB2BGR),
                    image_name="{}_{}_{}".format(
                        int(cat), i, entry["img_id"].rsplit(os.sep, 1)[1]
                    ),
                )


def save_detection_json(results, output_dir, categories=None, exclude_category_ids=[]):
    """
    Save detection results to a JSON file.

    Args:
        results (list):
            Detection results containing image ID, bounding boxes, category, and confidence.
        output_dir (str):
            Path to save the output JSON file.
        categories (list, optional):
            List of categories for detected objects. Defaults to None.
        exclude_category_ids (list, optional):
            List of category IDs to exclude from the output. Defaults to []. Category IDs can be found in the definition of each models.
    """
    json_results = {"annotations": [], "categories": categories}
    with open(output_dir, "w") as f:
        for r in results:

            # Category filtering
            img_id = r["img_id"]
            category = r["detections"].class_id

            bbox = r["detections"].xyxy.astype(int)[~np.isin(category, exclude_category_ids)]
            confidence =  r["detections"].confidence[~np.isin(category, exclude_category_ids)]
            category = category[~np.isin(category, exclude_category_ids)]

            if not all([x in exclude_category_ids for x in category]):
                json_results["annotations"].append(
                    {
                        "img_id": img_id,
                        "bbox": bbox.tolist(),
                        "category": category.tolist(),
                        "confidence": confidence.tolist(),
                    }
                )

        json.dump(json_results, f, indent=4)


def save_detection_classification_json(
    det_results, clf_results, output_path, det_categories=None, clf_categories=None
):
    """
    Save classification results to a JSON file.

    Args:
        det_results (list):
            Detection results containing image ID, bounding boxes, detection category, and confidence.
        clf_results (list):
            classification results containing image ID, classification category, and confidence.
        output_dir (str):
            Path to save the output JSON file.
        det_categories (list, optional):
            List of categories for detected objects. Defaults to None.
        clf_categories (list, optional):
            List of categories for classified objects. Defaults to None.
    """

    json_results = {
        "annotations": [],
        "det_categories": det_categories,
        "clf_categories": clf_categories,
    }

    with open(output_path, "w") as f:
        counter = 0
        for det_r in det_results:
            clf_categories = []
            clf_confidence = []
            for i in range(counter, len(clf_results)):
                clf_r = clf_results[i]
                if clf_r["img_id"] == det_r["img_id"]:
                    clf_categories.append(clf_r["class_id"])
                    clf_confidence.append(clf_r["confidence"])
                    counter += 1
                else:
                    break

            json_results["annotations"].append(
                {
                    "img_id": str(det_r["img_id"]),
                    "bbox": [
                        [int(x) for x in sublist]
                        for sublist in det_r["detections"].xyxy.astype(int).tolist()
                    ],
                    "det_category": [
                        int(x) for x in det_r["detections"].class_id.tolist()
                    ],
                    "det_confidence": [
                        float(x) for x in det_r["detections"].confidence.tolist()
                    ],
                    "clf_category": [int(x) for x in clf_categories],
                    "clf_confidence": [float(x) for x in clf_confidence],
                }
            )
        json.dump(json_results, f)
