import numpy as np


def IoU(mask_ref, mask_pred):
    intersection = np.logical_and(mask_ref, mask_pred)
    union = np.logical_or(mask_ref, mask_pred)
    iou = np.sum(intersection) / np.sum(union)

    true_positive = np.sum(np.logical_and(mask_ref, mask_pred))
    false_negative = np.sum(np.logical_and(mask_ref, np.logical_not(mask_pred)))
    false_positive = np.sum(np.logical_and(np.logical_not(mask_ref), mask_pred))

    tpr = true_positive / (true_positive + false_negative)
    ppv = true_positive / (true_positive + false_positive)

    return iou, tpr, ppv