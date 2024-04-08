__all__ = ["MeterDigitsRecognizer"]

import os
import cv2
import numpy as np

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))


class MeterDigitsRecognizer:

    def __init__(self):
        self.net = cv2.dnn.readNetFromONNX(os.path.join(PACKAGE_DIR, "model.onnx"))
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    def run(self, digit_imgs):

        digits_batch = np.stack([
            np.transpose(cv2.resize(img, (20, 32), interpolation=cv2.INTER_LINEAR).astype(np.float32), (2, 0, 1))
            for img in digit_imgs
        ]) / 255.0
        self.net.setInput(digits_batch)
        outputs = self.net.forward()
        all_confidences = softmax(outputs, axis=1)
        predictions = np.argmax(all_confidences, axis=1)
        confidences = all_confidences[np.arange(len(predictions)), predictions]
        return predictions, confidences


def softmax(x, axis=None):
    x_max = np.amax(x, axis=axis, keepdims=True)
    exp_x_shifted = np.exp(x - x_max)
    return exp_x_shifted / np.sum(exp_x_shifted, axis=axis, keepdims=True)


if __name__ == "__main__":
    pass
