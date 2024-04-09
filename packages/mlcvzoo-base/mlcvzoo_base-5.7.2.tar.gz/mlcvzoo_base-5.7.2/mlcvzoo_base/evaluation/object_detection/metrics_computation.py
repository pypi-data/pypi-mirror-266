# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

import copy
import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
from tqdm import tqdm

from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.evaluation.object_detection.data_classes import (
    CONFUSION_MATRIX_DICT_TYPE,
    CONFUSION_MATRIX_TYPE,
    DEFAULT_FLOAT_VALUE,
    DEFAULT_INT_VALUE,
    EVALUATION_LIST_TYPE,
    METRIC_DICT_TYPE,
    METRIC_IMAGE_INFO_TYPE,
    MetricImageInfo,
    ODEvaluationComputingData,
    ODMetrics,
    ODModelEvaluationMetrics,
)
from mlcvzoo_base.evaluation.object_detection.structs import BBoxSizeTypes
from mlcvzoo_base.evaluation.object_detection.utils import (
    compute_max_bounding_box,
    generate_metric_table,
    get_bbox_size_type,
)
from mlcvzoo_base.third_party.py_faster_rcnn.voc_ap import voc_ap

logger = logging.getLogger(__name__)


class MetricsComputation:
    """
    Main class for handling the evaluation of object detection models.
    """

    iou_thresholds_ap_50_95: List[float] = [
        0.5,
        0.55,
        0.6,
        0.65,
        0.7,
        0.75,
        0.8,
        0.85,
        0.9,
        0.95,
    ]

    def __init__(
        self,
        model_specifier: str,
        classes_id_dict: Optional[Dict[int, str]],
        iou_thresholds: List[float],
        gt_annotations: List[BaseAnnotation],
        predicted_bounding_boxes_list: List[List[BoundingBox]],
        mapper: Optional[AnnotationClassMapper] = None,
    ):
        self.model_specifier = model_specifier
        self.iou_thresholds: List[float] = iou_thresholds
        self.dataset_length: int = len(gt_annotations)

        self.class_identifier_list: List[ClassIdentifier] = []
        self._classes_id_dict = classes_id_dict
        if self._classes_id_dict is not None:
            logger.warning(
                "DEPRECATED: The parameter classes_id_dict is deprecated and will"
                "be removed in future versions, please use mapper instead"
            )
            for class_id, class_name in self._classes_id_dict.items():
                self.class_identifier_list.append(
                    ClassIdentifier(class_id=class_id, class_name=class_name)
                )
        else:
            if mapper is not None:
                self.mapper = mapper
                self.class_identifier_list = self.mapper.create_class_identifier_list()
            else:
                raise ValueError(
                    "Either the parameter 'mapper' or the parameter 'classes_id_dict'(DEPRECATED) "
                    "has to be provided "
                )

        # Remove duplicates
        self.class_identifier_list = list(dict.fromkeys(self.class_identifier_list))

        self._all_predicted_annotations_dict: Dict[int, Dict[str, List[BaseAnnotation]]] = {
            i: {} for i in range(self.dataset_length)
        }
        self._all_gt_annotations_dict: Dict[int, Dict[str, List[BaseAnnotation]]] = {
            i: {} for i in range(self.dataset_length)
        }

        self.model_metrics: ODModelEvaluationMetrics = ODModelEvaluationMetrics(
            model_specifier=self.model_specifier
        )
        self.computing_data: ODEvaluationComputingData = ODEvaluationComputingData()

        process_bar = tqdm(
            zip(gt_annotations, predicted_bounding_boxes_list),
            desc=f"Compute metrics",
        )

        # TODO: Convert to batch-processing
        for index, (gt_annotation, predicted_bounding_boxes) in enumerate(process_bar):
            _ = self.__update_from_prediction(
                index=index,
                gt_annotation=gt_annotation,
                predicted_bounding_boxes=predicted_bounding_boxes,
            )

    @property
    def classes_id_dict(self) -> Optional[Dict[int, str]]:
        logger.warning(
            "DEPRECATED: The attribute 'classes_id_dict' is deprecated"
            "and will be removed in future versions"
        )
        return self._classes_id_dict

    @property
    def all_predicted_annotations(self) -> EVALUATION_LIST_TYPE:
        logger.warning(
            "DEPRECATED: The attribute 'all_predicted_annotations' is deprecated"
            "and will be removed in future versions"
        )
        return [[]]

    @property
    def all_gt_annotations(self) -> EVALUATION_LIST_TYPE:
        logger.warning(
            "DEPRECATED: The attribute 'all_gt_annotations' is deprecated"
            "and will be removed in future versions"
        )
        return [[]]

    def get_metrics_dict(self) -> METRIC_DICT_TYPE:
        return self.model_metrics.metrics_dict

    def get_metrics_image_info_dict(
        self,
    ) -> METRIC_IMAGE_INFO_TYPE:
        return self.model_metrics.metrics_image_info_dict

    @staticmethod
    def get_overall_ap(metrics_dict: METRIC_DICT_TYPE, iou_threshold: float) -> float:
        """
        Calculate AP metric over every class specific AP metric for bounding boxes of all sizes.

        Args:
            metrics_dict: The dictionary that stores the relevant metric data, which is the
                          basis for the calculation
            iou_threshold: The iou threshold for which the AP metric should be computed

        Returns:
            The computed overall AP metric
        """

        if iou_threshold in metrics_dict:
            class_metrics = metrics_dict[iou_threshold][BBoxSizeTypes.BBOX_ALL]
        else:
            raise ValueError(
                "Can not compute overall AP for iou-threshold=%s, "
                "no data is given in the metrics-dict.",
                iou_threshold,
            )

        ap_list: List[float] = [class_metric.AP for class_metric in class_metrics.values()]
        return sum(ap_list) / len(ap_list)

    @staticmethod
    def compute_average_ap(model_metrics: ODModelEvaluationMetrics) -> float:
        """
        Compute the average of the AP metric for every
        overall AP (average over all classes) of all iou-thresholds
        in the metrics_dict.

        Args:
            model_metrics: The model-metrics for which to compute the average ap

        Returns:
            The computed average AP metric
        """
        ap_list: List[float] = [
            MetricsComputation.get_overall_ap(
                metrics_dict=model_metrics.metrics_dict,
                iou_threshold=iou_threshold,
            )
            for iou_threshold in model_metrics.metrics_dict.keys()
        ]
        return sum(ap_list) / len(ap_list)

    @staticmethod
    def get_ap_50_95(model_metrics: ODModelEvaluationMetrics) -> float:
        """
        Compute the COCO mAP metric which is defined as the AP
        metric for the iou-thresholds = [0.5, 0.55, ..., 0.95].

        Args:
            model_metrics: The model-metrics for which to compute the COCO mAP

        Returns:
            The computed COCO mAP
        """
        return sum(
            [
                MetricsComputation.get_overall_ap(
                    metrics_dict=model_metrics.metrics_dict, iou_threshold=iou
                )
                for iou in MetricsComputation.iou_thresholds_ap_50_95
            ]
        ) / len(MetricsComputation.iou_thresholds_ap_50_95)

    @staticmethod
    def get_ap_50(model_metrics: ODModelEvaluationMetrics) -> float:
        """
        Compute the AP50 metric which is defined as the AP
        metric for the iou-threshold=0.5

        Args:
            model_metrics: The model-metrics for which to compute the COCO mAP

        Returns:
            The computed AP50
        """

        return MetricsComputation.get_overall_ap(
            metrics_dict=model_metrics.metrics_dict, iou_threshold=0.5
        )

    def __reset_main_dictionaries(
        self,
    ) -> None:
        for class_identifier in self.class_identifier_list:
            self.model_metrics.metrics_image_info_dict[str(class_identifier)] = dict()

        for bbox_size_type in BBoxSizeTypes.get_values_as_list(class_type=BBoxSizeTypes):
            self.computing_data.gt_counter_dict[bbox_size_type] = dict()

            for class_identifier in self.class_identifier_list:
                self.computing_data.gt_counter_dict[bbox_size_type][str(class_identifier)] = 0

        for iou_thresh in self.iou_thresholds:
            self.model_metrics.metrics_dict[iou_thresh] = dict()
            self.computing_data.valid_precisions[iou_thresh] = dict()

            for bbox_size_type in BBoxSizeTypes.get_values_as_list(class_type=BBoxSizeTypes):
                self.model_metrics.metrics_dict[iou_thresh][bbox_size_type] = dict()
                self.computing_data.valid_precisions[iou_thresh][bbox_size_type] = list()

                # TODO: Make None to state that now data has been computed?
                for class_identifier in self.class_identifier_list:
                    self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][
                        str(class_identifier)
                    ] = ODMetrics()

    def __reset_computing_dictionaries(self) -> None:
        for iou_thresh in self.iou_thresholds:
            self.computing_data.false_positives_dict[iou_thresh] = dict()
            self.computing_data.true_positives_dict[iou_thresh] = dict()
            self.computing_data.detected_annotations[iou_thresh] = list()
            self.computing_data.scores[iou_thresh] = dict()

            for bbox_size in BBoxSizeTypes.get_values_as_list(class_type=BBoxSizeTypes):
                self.computing_data.false_positives_dict[iou_thresh][bbox_size] = np.zeros((0,))
                self.computing_data.true_positives_dict[iou_thresh][bbox_size] = np.zeros((0,))

                self.computing_data.scores[iou_thresh][bbox_size] = np.zeros((0,))

    def compute_metrics(
        self,
    ) -> ODModelEvaluationMetrics:
        """
        Compute MAP Metrics

        return: the metrics dictionary in the form of:
                1st key: iou-threshold
                2nd key: type of the size of the bounding-box
                3rd key: class-name
                Value: The computed metrics

                Dict[IOU_THRESHOLD][BBoxSizeTypes.BBOX_SIZE_TYPE][CLASS_NAME] = ODMetrics
        """

        self.__reset_main_dictionaries()

        # process get_bounding_boxes and annotations
        for class_identifier in self.class_identifier_list:
            self.__reset_computing_dictionaries()

            self.__fill_computing_data(
                class_id=class_identifier.class_id,
                class_name=class_identifier.class_name,
                class_identifier=class_identifier,
            )

            self.__compute_metrics(class_identifier=class_identifier)

        for iou_threshold in self.iou_thresholds:
            metric_table = generate_metric_table(
                metrics_dict=self.model_metrics.metrics_dict,
                iou_threshold=iou_threshold,
            )
            logger.debug(
                "Metrics for IOU-Threshold '%s': \n%s" % (iou_threshold, metric_table.table)
            )

        return ODModelEvaluationMetrics(
            model_specifier=self.model_specifier,
            metrics_dict=self.get_metrics_dict(),
            metrics_image_info_dict=self.get_metrics_image_info_dict(),
        )

    def __update_from_prediction(
        self,
        index: int,
        gt_annotation: BaseAnnotation,
        predicted_bounding_boxes: List[BoundingBox],
    ) -> BaseAnnotation:
        """
        Update the main computing attributes given the information from the ground truth
        annotation and predicted bounding boxes at the dataset index.

        Args:
            index: The index of the dataset where to update the data
            gt_annotation: The ground truth information for the given index (data item)
            predicted_bounding_boxes: The predicted bounding boxes for this index (data item)

        Returns:
            The annotation object created on the basis of the ground truth data and the predicted
            bounding boxes
        """

        logger.debug(
            "Get metrics for annotation: \n"
            "  - image-path:       %s\n"
            "  - image-annotation: %s",
            gt_annotation.image_path,
            gt_annotation.annotation_path,
        )

        self._all_gt_annotations_dict = MetricsComputation.__update_annotation_data_dict(
            class_identifier_list=self.class_identifier_list,
            all_annotations_dict=self._all_gt_annotations_dict,
            index=index,
            new_annotation=gt_annotation,
        )

        predicted_annotation = BaseAnnotation(
            image_path=gt_annotation.image_path,
            annotation_path=gt_annotation.annotation_path,
            image_shape=gt_annotation.image_shape,
            classifications=[],
            bounding_boxes=predicted_bounding_boxes,
            segmentations=[],
            image_dir=gt_annotation.image_dir,
            annotation_dir=gt_annotation.annotation_dir,
            replacement_string=gt_annotation.replacement_string,
        )

        self._all_predicted_annotations_dict = MetricsComputation.__update_annotation_data_dict(
            class_identifier_list=self.class_identifier_list,
            all_annotations_dict=self._all_predicted_annotations_dict,
            index=index,
            new_annotation=predicted_annotation,
        )

        return predicted_annotation

    @staticmethod
    def __update_annotation_data_dict(
        class_identifier_list: List[ClassIdentifier],
        all_annotations_dict: Dict[int, Dict[str, List[BaseAnnotation]]],
        index: int,
        new_annotation: BaseAnnotation,
    ) -> Dict[int, Dict[str, List[BaseAnnotation]]]:
        """
        Update annotation information in the given 'all_annotations' list at the given index
        based on the annotation data given by 'new_annotation'.

        Args:
            class_identifier_list: List of class identifier for which to update the annotation
                                   data
            all_annotations_dict: The dictionary to update
            index: int, index of entry (image) which annotations should be updated
            new_annotation: BaseAnnotation object, holding the new annotation information

        Returns:
            The updated all_annotations_dict

        """

        if len(new_annotation.get_bounding_boxes(include_segmentations=True)) == 0:
            # No update necessary
            return all_annotations_dict

        # Gather (BoundingBox / Annotation) data for each class-id.
        # This is needed to be able to compute detailed metrics
        # for each class-id.
        for class_identifier in class_identifier_list:
            # Have to find all bounding-boxes for a specific class-id.
            # In order to have access to the information about the image-path,
            # we need to store an annotation object, rather than a single bounding-box.
            # Despite the fact that for the metric calculation itself the bounding-box
            # information is enough.
            # For purposes like: draw/log all false-positive bounding-boxes for specific
            # images we need to have the information about the image-path
            #   => therefore use BaseAnnotation and not BoundingBox alone
            all_annotations_dict[index][str(class_identifier)] = []
            for b in new_annotation.get_bounding_boxes(include_segmentations=True):
                if b.class_id == class_identifier.class_id:
                    metric_annotation = BaseAnnotation(
                        image_path=new_annotation.image_path,
                        annotation_path=new_annotation.annotation_path,
                        image_shape=new_annotation.image_shape,
                        classifications=[],
                        bounding_boxes=[
                            BoundingBox(
                                class_identifier=b.class_identifier,
                                model_class_identifier=b.model_class_identifier,
                                score=b.score,
                                box=b.box,
                                difficult=False,
                                occluded=False,
                                background=False,
                                content="",
                            )
                        ],
                        segmentations=[],
                        image_dir=new_annotation.image_dir,
                        annotation_dir=new_annotation.annotation_dir,
                        replacement_string=new_annotation.replacement_string,
                    )

                    all_annotations_dict[index][str(class_identifier)].append(metric_annotation)

        return all_annotations_dict

    def __update_tp_fp_data(
        self,
        is_true_positive: bool,
        iou_thresh: float,
        bbox_size_type: str,
    ) -> None:
        if is_true_positive:
            tp_value = 1
            fp_value = 0
        else:
            tp_value = 0
            fp_value = 1

        # Update dictionary for overall mAP computation
        self.computing_data.true_positives_dict[iou_thresh][BBoxSizeTypes.BBOX_ALL] = np.append(
            self.computing_data.true_positives_dict[iou_thresh][BBoxSizeTypes.BBOX_ALL],
            tp_value,
        )
        self.computing_data.false_positives_dict[iou_thresh][BBoxSizeTypes.BBOX_ALL] = np.append(
            self.computing_data.false_positives_dict[iou_thresh][BBoxSizeTypes.BBOX_ALL],
            fp_value,
        )

        # Update dictionary for size specific mAP computation
        self.computing_data.true_positives_dict[iou_thresh][bbox_size_type] = np.append(
            self.computing_data.true_positives_dict[iou_thresh][bbox_size_type],
            tp_value,
        )
        self.computing_data.false_positives_dict[iou_thresh][bbox_size_type] = np.append(
            self.computing_data.false_positives_dict[iou_thresh][bbox_size_type],
            fp_value,
        )

    def __update_computation_dictionaries(
        self,
        bounding_box: BoundingBox,
        iou_thresh: float,
        unmatched_gt_bounding_boxes: List[BoundingBox],
    ) -> List[BoundingBox]:
        bbox_size_type: str = get_bbox_size_type(bounding_box.box)

        # if the ground truth data for this image indicates that nothing has to be detected,
        # indicate this box as False-Positive right away!
        if len(unmatched_gt_bounding_boxes) == 0:
            self.__update_tp_fp_data(
                is_true_positive=False,
                iou_thresh=iou_thresh,
                bbox_size_type=bbox_size_type,
            )
        else:
            max_overlap, assigned_gt_bounding_box = compute_max_bounding_box(
                bounding_box=bounding_box, gt_bounding_boxes=unmatched_gt_bounding_boxes
            )

            # If max-overlap fulfills given threshold
            # the detected box is treated as TP, otherwise as FP
            if (
                max_overlap
                >= iou_thresh
                # and
                # if this bounding_box has not already been assigned as valid,
                # treat it as true positive, otherwise as false positive
                # assigned_bounding_box not in self.detected_annotations[iou_thresh]
            ):
                unmatched_gt_bounding_boxes.remove(assigned_gt_bounding_box)

                # NOTE: In order to have correct metrics, the size of a true positive
                #       bounding box is the same as for the matching ground truth bounding box
                bbox_size_type = get_bbox_size_type(assigned_gt_bounding_box.box)

                # Update as True-Positive
                self.__update_tp_fp_data(
                    is_true_positive=True,
                    iou_thresh=iou_thresh,
                    bbox_size_type=bbox_size_type,
                )
            else:
                # Update as False-Positive
                self.__update_tp_fp_data(
                    is_true_positive=False,
                    iou_thresh=iou_thresh,
                    bbox_size_type=bbox_size_type,
                )

        # append the score of the current bounding-box to the overall  scores list
        self.computing_data.scores[iou_thresh][BBoxSizeTypes.BBOX_ALL] = np.append(
            self.computing_data.scores[iou_thresh][BBoxSizeTypes.BBOX_ALL],
            bounding_box.score,
        )

        # append the score of the current bounding-box to the size specific scores list
        self.computing_data.scores[iou_thresh][bbox_size_type] = np.append(
            self.computing_data.scores[iou_thresh][bbox_size_type], bounding_box.score
        )

        return unmatched_gt_bounding_boxes

    def __update_false_positive_metric_info(
        self,
        ground_truth_annotation: Optional[BaseAnnotation],
        predicted_annotation: BaseAnnotation,
        bounding_box: BoundingBox,
        class_identifier: ClassIdentifier,
    ) -> None:
        # Build an annotation based on the ground truth data and the given
        # bounding boxes
        false_positive_annotation = BaseAnnotation(
            image_path=predicted_annotation.image_path,
            annotation_path=predicted_annotation.annotation_path,
            image_shape=predicted_annotation.image_shape,
            classifications=[],
            bounding_boxes=[bounding_box],
            segmentations=[],
            image_dir=predicted_annotation.image_dir,
            annotation_dir=predicted_annotation.annotation_dir,
            replacement_string=predicted_annotation.replacement_string,
        )

        # save FP annotation to metric_image_info_dict
        if (
            predicted_annotation.image_path
            not in self.model_metrics.metrics_image_info_dict[str(class_identifier)]
        ):
            # The predicted annotation is a FP, therefore store it in a dict so that
            # it can be logged to tensorboard after the evaluation has finished
            self.model_metrics.metrics_image_info_dict[str(class_identifier)][
                predicted_annotation.image_path
            ] = MetricImageInfo(
                ground_truth_annotation=ground_truth_annotation,
                false_positive_annotation=false_positive_annotation,
                false_negative_annotation=None,
            )
        else:
            # Update FP annotation object that belongs to the given image-path
            if (
                self.model_metrics.metrics_image_info_dict[str(class_identifier)][
                    predicted_annotation.image_path
                ].false_positive_annotation
                is not None
            ):
                # If their already is an annotation object present, append this bounding box
                # NOTE: the mypy error 'Item "None" of "Optional[BaseAnnotation]" has no
                #       attribute "bounding_boxes' can be ignored. It is checked by the
                #       above query operation. Somehow mypy does not gets that
                self.model_metrics.metrics_image_info_dict[str(class_identifier)][
                    predicted_annotation.image_path
                ].false_positive_annotation.bounding_boxes.append(  # type: ignore
                    bounding_box
                )

            # REMARK: false_positive_annotation of
            #         self.model_metrics.metrics_image_info_dict[class_name]
            #         [predicted_annotation.image_path]
            #         can't be None here. This would only be the case if a MetricImageInfo
            #         object would be inserted with
            #           MetricImageInfo(
            #             ground_truth_annotation=ground_truth_annotation,
            #             false_positive_annotation=None,
            #             false_negative_annotation=false_negative_annotation,
            #           )
            #         Since the false negative annotations will be updated after the false
            #         positive annotations are already set, we always have an
            #         false_positive_annotation present here.

    def __update_false_negative_metric_info(
        self,
        ground_truth_annotation: BaseAnnotation,
        iou_unmatched_gt_bounding_boxes: List[BoundingBox],
        class_identifier: ClassIdentifier,
    ) -> None:
        """
        Update the false_negative_annotation entry of model_metrics.metrics_image_info_dict
        for the given class_name and the image path of the given ground truth annotation.

        Args:
            ground_truth_annotation:
            iou_unmatched_gt_bounding_boxes:
            class_identifier:

        Returns:

        """

        false_negative_annotation = BaseAnnotation(
            image_path=ground_truth_annotation.image_path,
            annotation_path=ground_truth_annotation.annotation_path,
            image_shape=ground_truth_annotation.image_shape,
            classifications=[],
            bounding_boxes=iou_unmatched_gt_bounding_boxes,
            segmentations=[],
            image_dir=ground_truth_annotation.image_dir,
            annotation_dir=ground_truth_annotation.annotation_dir,
            replacement_string=ground_truth_annotation.replacement_string,
        )

        if (
            ground_truth_annotation.image_path
            not in self.model_metrics.metrics_image_info_dict[str(class_identifier)]
        ):
            self.model_metrics.metrics_image_info_dict[str(class_identifier)][
                ground_truth_annotation.image_path
            ] = MetricImageInfo(
                ground_truth_annotation=ground_truth_annotation,
                false_positive_annotation=None,
                false_negative_annotation=false_negative_annotation,
            )
        else:
            self.model_metrics.metrics_image_info_dict[str(class_identifier)][
                ground_truth_annotation.image_path
            ].false_negative_annotation = false_negative_annotation

    def __get_gt_annotation(
        self, dataset_index: int, class_identifier: ClassIdentifier
    ) -> Tuple[Optional[BaseAnnotation], List[BoundingBox]]:
        # annotation object for gathering all ground truth bounding boxes for this image
        ground_truth_annotation: Optional[BaseAnnotation] = None

        unmatched_gt_bounding_boxes: List[BoundingBox] = []

        if not str(class_identifier) in self._all_gt_annotations_dict[dataset_index]:
            return ground_truth_annotation, unmatched_gt_bounding_boxes

        # Iterate over all ground-truth annotations that containing bounding-box
        # information for this image (dataset_index) and the given class-id
        for gt_annotation in self._all_gt_annotations_dict[dataset_index][str(class_identifier)]:
            unmatched_gt_bounding_boxes.extend(
                gt_annotation.get_bounding_boxes(include_segmentations=True)
            )

            for bounding_box in gt_annotation.get_bounding_boxes(include_segmentations=True):
                # increase bounding-box ground-truth counter for overall count
                # and the specific bounding-box size count

                self.computing_data.gt_counter_dict[BBoxSizeTypes.BBOX_ALL][
                    str(class_identifier)
                ] += 1

                self.computing_data.gt_counter_dict[get_bbox_size_type(bounding_box.box)][
                    str(class_identifier)
                ] += 1

            # Initialize/update an overall ground_truth annotation that contains all
            # data for this image and class-id
            if ground_truth_annotation is None:
                ground_truth_annotation = copy.deepcopy(gt_annotation)
            else:
                ground_truth_annotation.bounding_boxes.extend(
                    gt_annotation.get_bounding_boxes(include_segmentations=True)
                )

        return ground_truth_annotation, unmatched_gt_bounding_boxes

    def __fill_computing_data(
        self,
        class_id: Optional[int],
        class_name: Optional[str],
        class_identifier: Optional[ClassIdentifier] = None,
    ) -> None:
        if class_identifier is None:
            if class_id is not None:
                logger.warning(
                    "DEPRECATED: The parameter class_id is deprecated "
                    "and will be removed in future versions, please use the parameter "
                    "'class_identifier' instead"
                )

                if class_name is not None:
                    logger.warning(
                        "DEPRECATED: The parameter class_id is deprecated "
                        "and will be removed in future versions, please use the parameter "
                        "'class_identifier' instead"
                    )
                else:
                    class_name = self.mapper.map_annotation_class_id_to_model_class_name(
                        class_id=class_id
                    )
            else:
                if class_name is not None:
                    logger.warning(
                        "DEPRECATED: The parameter class_id is deprecated "
                        "and will be removed in future versions, please use the parameter "
                        "'class_identifier' instead"
                    )

                    class_id = self.mapper.map_annotation_class_name_to_model_class_id(
                        class_name=class_name
                    )
                else:
                    raise ValueError("TODO")

            class_identifier = ClassIdentifier(class_id=class_id, class_name=class_name)

        process_bar = tqdm(
            range(self.dataset_length),
            desc=f"Compute metrics for class-identifier: {class_identifier}",
        )

        # Iterate over all image indices
        for dataset_index in process_bar:
            (
                ground_truth_annotation,
                unmatched_gt_bounding_boxes,
            ) = self.__get_gt_annotation(
                dataset_index=dataset_index, class_identifier=class_identifier
            )

            for iou_thresh in self.iou_thresholds:
                # Iterate over all predicted annotations for this image and class-id
                iou_unmatched_gt_bounding_boxes = copy.deepcopy(unmatched_gt_bounding_boxes)

                if str(class_identifier) in self._all_predicted_annotations_dict[dataset_index]:
                    for predicted_annotation in self._all_predicted_annotations_dict[
                        dataset_index
                    ][str(class_identifier)]:
                        for bounding_box in predicted_annotation.get_bounding_boxes(
                            include_segmentations=True
                        ):
                            iou_unmatched_gt_bounding_boxes = (
                                self.__update_computation_dictionaries(
                                    bounding_box=bounding_box,
                                    iou_thresh=iou_thresh,
                                    unmatched_gt_bounding_boxes=iou_unmatched_gt_bounding_boxes,
                                )
                            )

                            # The bounding_box is a FP
                            if self.computing_data.false_positives_dict[iou_thresh][
                                BBoxSizeTypes.BBOX_ALL
                            ][-1]:
                                self.__update_false_positive_metric_info(
                                    ground_truth_annotation=ground_truth_annotation,
                                    predicted_annotation=predicted_annotation,
                                    bounding_box=bounding_box,
                                    class_identifier=class_identifier,
                                )

                    # There are ground truth annotations which haven't been matched,
                    # this states that the box is a false negative
                    if (
                        str(class_identifier) in self._all_gt_annotations_dict[dataset_index]
                        and len(
                            self._all_gt_annotations_dict[dataset_index][str(class_identifier)]
                        )
                        > 0
                        and len(iou_unmatched_gt_bounding_boxes) > 0
                        and ground_truth_annotation is not None
                    ):
                        self.__update_false_negative_metric_info(
                            ground_truth_annotation=ground_truth_annotation,
                            iou_unmatched_gt_bounding_boxes=iou_unmatched_gt_bounding_boxes,
                            class_identifier=class_identifier,
                        )

    def __compute_and_update_metrics_step(
        self,
        class_identifier: ClassIdentifier,
        iou_thresh: float,
        bbox_size_type: str,
        num_annotations: int,
        true_positives: np.ndarray,  # type: ignore[type-arg]
        false_positives: np.ndarray,  # type: ignore[type-arg]
    ) -> None:
        # compute recall and precision
        recall_values = true_positives / num_annotations
        precision_values = true_positives / np.maximum(
            true_positives + false_positives, np.finfo(np.float64).eps
        )

        # compute average precision
        # NOTE: mypy error 'Call to untyped function "close" in typed context' can be ignored
        ap = voc_ap(rec=recall_values, prec=precision_values, use_07_metric=False)  # type: ignore

        if len(true_positives) > 0:
            tp = int(true_positives[-1])

            if tp > num_annotations:
                print("TP not valid")

            rc = tp / num_annotations
        else:
            tp = DEFAULT_INT_VALUE
            rc = DEFAULT_FLOAT_VALUE

        if len(false_positives) > 0:
            fp = int(false_positives[-1])
        else:
            fp = DEFAULT_INT_VALUE

        try:
            pr = tp / (fp + tp)
        except ZeroDivisionError:
            pr = DEFAULT_FLOAT_VALUE

        try:
            f1 = 2 * (pr * rc) / (pr + rc)
        except ZeroDivisionError:
            f1 = DEFAULT_FLOAT_VALUE

        fn = num_annotations - tp

        self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][
            str(class_identifier)
        ] = ODMetrics(TP=tp, FP=fp, FN=fn, PR=pr, RC=rc, F1=f1, AP=ap, COUNT=num_annotations)

    def __compute_metrics(self, class_identifier: ClassIdentifier) -> None:
        # TODO: Is this mAP computation? - separate from rest !
        for iou_thresh in self.iou_thresholds:
            for bbox_size_type in BBoxSizeTypes.get_values_as_list(class_type=BBoxSizeTypes):
                num_annotations = self.computing_data.gt_counter_dict[bbox_size_type][
                    str(class_identifier)
                ]

                if num_annotations == 0.0:
                    continue

                # sort by score
                # TODO: CHECK NEGATIVE SIGN!!!
                indices = np.argsort(-self.computing_data.scores[iou_thresh][bbox_size_type])

                false_positives = self.computing_data.false_positives_dict[iou_thresh][
                    bbox_size_type
                ][indices]

                true_positives = self.computing_data.true_positives_dict[iou_thresh][
                    bbox_size_type
                ][indices]

                # compute false positives and true positives
                false_positives = np.cumsum(false_positives)
                true_positives = np.cumsum(true_positives)

                self.__compute_and_update_metrics_step(
                    class_identifier=class_identifier,
                    iou_thresh=iou_thresh,
                    bbox_size_type=bbox_size_type,
                    num_annotations=num_annotations,
                    true_positives=true_positives,
                    false_positives=false_positives,
                )

                if (
                    self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][
                        str(class_identifier)
                    ].FP
                    != -1
                    and self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][
                        str(class_identifier)
                    ].TP
                    != -1
                ):
                    self.computing_data.valid_precisions[iou_thresh][bbox_size_type].append(
                        self.model_metrics.metrics_dict[iou_thresh][bbox_size_type][
                            str(class_identifier)
                        ].AP
                    )

    @staticmethod
    def match_false_negatives_and_false_positives(
        metrics_image_info_dict: METRIC_IMAGE_INFO_TYPE,
        iou_threshold: float,
    ) -> Tuple[METRIC_IMAGE_INFO_TYPE, CONFUSION_MATRIX_TYPE]:
        """


        Args:
            metrics_image_info_dict:
            iou_threshold:

        Returns:

        """

        logger.warning(
            "DEPRECATED: The method 'match_false_negatives_and_false_positives' is "
            "deprecated and will be removed in future versions"
        )

        confusion_matrix: CONFUSION_MATRIX_TYPE = [
            [0 for _ in metrics_image_info_dict.keys()] for _ in metrics_image_info_dict.keys()
        ]
        classes_name_dict: Dict[str, int] = {}
        for class_identifier_str in metrics_image_info_dict.keys():
            class_identifier: ClassIdentifier = ClassIdentifier.from_str(
                class_identifier_str=class_identifier_str
            )
            classes_name_dict[str(class_identifier)] = class_identifier.class_id

        # Build a dict for reverse look up, where the keys are image paths.
        # This is needed to fill the confusion matrix per image.
        image_metrics_info_dict: Dict[str, Dict[str, MetricImageInfo]] = {}
        for class_identifier_str in metrics_image_info_dict.keys():
            for image_path, metric_image_info in metrics_image_info_dict[
                class_identifier_str
            ].items():
                if image_path not in image_metrics_info_dict:
                    image_metrics_info_dict[image_path] = {}

                if class_identifier_str not in image_metrics_info_dict[image_path]:
                    image_metrics_info_dict[image_path][class_identifier_str] = metric_image_info

        result_metrics_image_info_dict = copy.deepcopy(metrics_image_info_dict)

        for image_path in image_metrics_info_dict.keys():
            class_identifiers = [
                ClassIdentifier.from_str(class_identifier_str=class_identifier_str)
                for class_identifier_str in image_metrics_info_dict[image_path].keys()
            ]

            for class_identifier in class_identifiers:
                other_class_identifiers = copy.deepcopy(class_identifiers)
                other_class_identifiers.remove(class_identifier)

                class_img_metrics_info = image_metrics_info_dict[image_path][str(class_identifier)]
                if class_img_metrics_info.false_negative_annotation:
                    class_fn_bounding_boxes = (
                        class_img_metrics_info.false_negative_annotation.bounding_boxes
                    )

                    for fn_bounding_box in class_fn_bounding_boxes:
                        for other_class_identifier in other_class_identifiers:
                            other_class_img_metrics_info = image_metrics_info_dict[image_path][
                                str(other_class_identifier)
                            ]

                            if other_class_img_metrics_info.false_positive_annotation:
                                other_class_fp_bounding_boxes = (
                                    other_class_img_metrics_info.false_positive_annotation.bounding_boxes
                                )

                                (
                                    max_overlap,
                                    assigned_fp_bounding_box,
                                ) = compute_max_bounding_box(
                                    bounding_box=fn_bounding_box,
                                    gt_bounding_boxes=other_class_fp_bounding_boxes,
                                )

                                if max_overlap > iou_threshold:
                                    confusion_matrix[classes_name_dict[str(class_identifier)]][
                                        classes_name_dict[str(other_class_identifier)]
                                    ] += 1
                                    annotation_path = (
                                        class_img_metrics_info.false_negative_annotation.annotation_path
                                    )
                                    image_shape = (
                                        class_img_metrics_info.false_negative_annotation.image_shape
                                    )
                                    image_dir = (
                                        class_img_metrics_info.false_negative_annotation.image_dir
                                    )
                                    annotation_dir = (
                                        class_img_metrics_info.false_negative_annotation.annotation_dir
                                    )
                                    replacement_string = (
                                        class_img_metrics_info.false_negative_annotation.replacement_string
                                    )

                                    class_img_metrics_info.false_negative_annotation.bounding_boxes.remove(
                                        fn_bounding_box
                                    )
                                    other_class_img_metrics_info.false_positive_annotation.bounding_boxes.remove(
                                        assigned_fp_bounding_box
                                    )

                                    result_metrics_image_info_dict = MetricsComputation.__change_matched_bbox_attribute(
                                        metrics_image_info_dict=result_metrics_image_info_dict,
                                        image_path=image_path,
                                        annotation_path=annotation_path,
                                        class_identifier=class_identifier,
                                        other_class_identifier=other_class_identifier,
                                        image_shape=image_shape,
                                        image_dir=image_dir,
                                        annotation_dir=annotation_dir,
                                        replacement_string=replacement_string,
                                        fn_bounding_box=fn_bounding_box,
                                        assigned_fp_bounding_box=assigned_fp_bounding_box,
                                        class_img_metrics_info=class_img_metrics_info,
                                        other_class_img_metrics_info=other_class_img_metrics_info,
                                    )

                            if other_class_img_metrics_info.false_positive_annotation:
                                if (
                                    len(
                                        other_class_img_metrics_info.false_positive_annotation.bounding_boxes
                                    )
                                    == 0
                                ):
                                    other_class_img_metrics_info.false_positive_annotation = None

                if class_img_metrics_info.false_negative_annotation:
                    if len(class_img_metrics_info.false_negative_annotation.bounding_boxes) == 0:
                        class_img_metrics_info.false_negative_annotation = None

        return result_metrics_image_info_dict, confusion_matrix

    @staticmethod
    def match_false_negatives_and_false_positives_as_dict(
        metrics_image_info_dict: METRIC_IMAGE_INFO_TYPE,
        iou_threshold: float,
    ) -> Tuple[METRIC_IMAGE_INFO_TYPE, CONFUSION_MATRIX_DICT_TYPE]:
        """


        Args:
            metrics_image_info_dict:
            iou_threshold:

        Returns:

        """

        confusion_matrix: CONFUSION_MATRIX_DICT_TYPE = {
            k2: {k1: 0 for k1 in metrics_image_info_dict.keys()}
            for k2 in metrics_image_info_dict.keys()
        }

        # Build a dict for reverse look up (reverse of metrics_image_info_dict),
        # where the keys are image paths. This is needed to fill the confusion matrix per image.
        # 1st key: Image Path
        # 2nd key: Class Identifier as string
        # value: The MetricImageInfo for this image path and class name
        image_metrics_info_dict: Dict[str, Dict[str, MetricImageInfo]] = {}
        for class_identifier_str in metrics_image_info_dict.keys():
            for image_path, metric_image_info in metrics_image_info_dict[
                class_identifier_str
            ].items():
                if image_path not in image_metrics_info_dict:
                    image_metrics_info_dict[image_path] = {}

                if class_identifier_str not in image_metrics_info_dict[image_path]:
                    image_metrics_info_dict[image_path][class_identifier_str] = metric_image_info

        result_metrics_image_info_dict = copy.deepcopy(metrics_image_info_dict)

        for image_path in image_metrics_info_dict.keys():
            class_identifiers: List[ClassIdentifier] = [
                ClassIdentifier.from_str(class_identifier_str=c)
                for c in image_metrics_info_dict[image_path].keys()
            ]

            for class_identifier in class_identifiers:
                other_class_identifiers: List[ClassIdentifier] = copy.deepcopy(class_identifiers)
                other_class_identifiers.remove(class_identifier)

                class_img_metrics_info = image_metrics_info_dict[image_path][str(class_identifier)]
                if class_img_metrics_info.false_negative_annotation:
                    class_fn_bounding_boxes = (
                        class_img_metrics_info.false_negative_annotation.bounding_boxes
                    )

                    for fn_bounding_box in class_fn_bounding_boxes:
                        for other_class_identifier in other_class_identifiers:
                            other_class_img_metrics_info = image_metrics_info_dict[image_path][
                                str(other_class_identifier)
                            ]

                            if other_class_img_metrics_info.false_positive_annotation:
                                other_class_fp_bounding_boxes = (
                                    other_class_img_metrics_info.false_positive_annotation.bounding_boxes
                                )

                                (
                                    max_overlap,
                                    assigned_fp_bounding_box,
                                ) = compute_max_bounding_box(
                                    bounding_box=fn_bounding_box,
                                    gt_bounding_boxes=other_class_fp_bounding_boxes,
                                )

                                if max_overlap > iou_threshold:
                                    confusion_matrix[str(class_identifier)][
                                        str(other_class_identifier)
                                    ] += 1
                                    annotation_path = (
                                        class_img_metrics_info.false_negative_annotation.annotation_path
                                    )
                                    image_shape = (
                                        class_img_metrics_info.false_negative_annotation.image_shape
                                    )
                                    image_dir = (
                                        class_img_metrics_info.false_negative_annotation.image_dir
                                    )
                                    annotation_dir = (
                                        class_img_metrics_info.false_negative_annotation.annotation_dir
                                    )
                                    replacement_string = (
                                        class_img_metrics_info.false_negative_annotation.replacement_string
                                    )

                                    class_img_metrics_info.false_negative_annotation.bounding_boxes.remove(
                                        fn_bounding_box
                                    )
                                    other_class_img_metrics_info.false_positive_annotation.bounding_boxes.remove(
                                        assigned_fp_bounding_box
                                    )

                                    result_metrics_image_info_dict = MetricsComputation.__change_matched_bbox_attribute(
                                        metrics_image_info_dict=result_metrics_image_info_dict,
                                        image_path=image_path,
                                        annotation_path=annotation_path,
                                        class_identifier=class_identifier,
                                        other_class_identifier=other_class_identifier,
                                        image_shape=image_shape,
                                        image_dir=image_dir,
                                        annotation_dir=annotation_dir,
                                        replacement_string=replacement_string,
                                        fn_bounding_box=fn_bounding_box,
                                        assigned_fp_bounding_box=assigned_fp_bounding_box,
                                        class_img_metrics_info=class_img_metrics_info,
                                        other_class_img_metrics_info=other_class_img_metrics_info,
                                    )

                            if other_class_img_metrics_info.false_positive_annotation:
                                if (
                                    len(
                                        other_class_img_metrics_info.false_positive_annotation.bounding_boxes
                                    )
                                    == 0
                                ):
                                    other_class_img_metrics_info.false_positive_annotation = None

                if class_img_metrics_info.false_negative_annotation:
                    if len(class_img_metrics_info.false_negative_annotation.bounding_boxes) == 0:
                        class_img_metrics_info.false_negative_annotation = None

        return result_metrics_image_info_dict, confusion_matrix

    @staticmethod
    def __change_matched_bbox_attribute(
        metrics_image_info_dict: METRIC_IMAGE_INFO_TYPE,
        image_path: str,
        annotation_path: str,
        class_identifier: ClassIdentifier,
        other_class_identifier: ClassIdentifier,
        image_shape: Tuple[int, int],
        image_dir: str,
        annotation_dir: str,
        replacement_string: str,
        fn_bounding_box: BoundingBox,
        assigned_fp_bounding_box: BoundingBox,
        class_img_metrics_info: MetricImageInfo,
        other_class_img_metrics_info: MetricImageInfo,
    ) -> METRIC_IMAGE_INFO_TYPE:
        if class_img_metrics_info.false_negative_matched_false_positive_annotation is not None:
            class_img_metrics_info.false_negative_matched_false_positive_annotation.bounding_boxes.append(
                fn_bounding_box
            )
        else:
            class_img_metrics_info.false_negative_matched_false_positive_annotation = (
                BaseAnnotation(
                    image_path=image_path,
                    annotation_path=annotation_path,
                    image_shape=image_shape,
                    classifications=[],
                    bounding_boxes=[fn_bounding_box],
                    segmentations=[],
                    image_dir=image_dir,
                    annotation_dir=annotation_dir,
                    replacement_string=replacement_string,
                )
            )

        if (
            other_class_img_metrics_info.false_negative_matched_false_positive_annotation
            is not None
        ):
            other_class_img_metrics_info.false_negative_matched_false_positive_annotation.bounding_boxes.append(
                assigned_fp_bounding_box
            )

        else:
            other_class_img_metrics_info.false_negative_matched_false_positive_annotation = (
                BaseAnnotation(
                    image_path=image_path,
                    annotation_path=annotation_path,
                    image_shape=image_shape,
                    classifications=[],
                    bounding_boxes=[assigned_fp_bounding_box],
                    segmentations=[],
                    image_dir=image_dir,
                    annotation_dir=annotation_dir,
                    replacement_string=replacement_string,
                )
            )

        metrics_image_info_dict[str(class_identifier)][image_path] = class_img_metrics_info
        metrics_image_info_dict[str(other_class_identifier)][
            image_path
        ] = other_class_img_metrics_info

        return metrics_image_info_dict
