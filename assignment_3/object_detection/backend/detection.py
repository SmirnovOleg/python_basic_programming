import cv2 as cv
import sys
import numpy as np
import os.path


class YOLOv3DetectionModel:
    conf_threshold = 0.2  # Confidence threshold
    nms_threshold = 0.4  # Non-maximum suppression threshold
    input_width = 416  # Width of network's input image
    input_height = 416  # Height of network's input image

    def __init__(self):
        classes_file = "coco.names"
        with open(classes_file, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')

        # Give the configuration and weight files for the model and load the network using them.
        model_configuration = "yolov3.cfg"
        model_weights = "yolov3.weights"
        self.model = cv.dnn.readNetFromDarknet(model_configuration, model_weights)
        self.model.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
        self.model.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

    def run_detection(self, input_file, output_file):
        if not os.path.isfile(input_file):
            print("Input image file ", input_file, " doesn't exist")
            sys.exit(1)

        cap = cv.VideoCapture(input_file)
        has_frame, frame = cap.read()
        if not has_frame:
            print("Frame doesn't exist")
            cap.release()

        # Create a 4D blob from a frame.
        blob = cv.dnn.blobFromImage(frame, 1 / 255, (self.input_width, self.input_height), [0, 0, 0], 1, crop=False)

        # Sets the input to the network
        self.model.setInput(blob)

        # Runs the forward pass to get output of the output layers
        outs = self.model.forward(self.__get_outputs_names())

        # Remove the bounding boxes with low confidence
        self.__postprocess(frame, outs)

        # Write the frame with the detection boxes
        cv.imwrite(output_file, frame.astype(np.uint8))

    # Draw the predicted bounding box
    def __draw_pred(self, frame, class_id, conf, left, top, right, bottom):
        # Draw a bounding box.
        cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)
        label = '%.2f' % conf

        # Get the label for the class name and its confidence
        if self.classes:
            assert (class_id < len(self.classes))
            label = '%s:%s' % (self.classes[class_id], label)

        # Display the label at the top of the bounding box
        label_size, base_line = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top = max(top, label_size[1])
        cv.rectangle(frame,
                     (left, top - round(1.5 * label_size[1])),
                     (left + round(1.5 * label_size[0]), top + base_line),
                     (255, 255, 255), cv.FILLED)
        cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)

    # Remove the bounding boxes with low confidence using non-maxima suppression
    def __postprocess(self, frame, outs):
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]

        # Scan through all the bounding boxes output from the network and keep only the
        # ones with high confidence scores. Assign the box's class label as the class with the highest score.
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > self.conf_threshold:
                    center_x = int(detection[0] * frame_width)
                    center_y = int(detection[1] * frame_height)
                    width = int(detection[2] * frame_width)
                    height = int(detection[3] * frame_height)
                    left = int(center_x - width / 2)
                    top = int(center_y - height / 2)
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])

        # Perform non maximum suppression to eliminate redundant overlapping boxes with
        # lower confidences.
        indices = cv.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)
        for idx in indices:
            box = boxes[idx[0]]
            left, top, width, height = box[0], box[1], box[2], box[3]
            self.__draw_pred(frame, class_ids[idx[0]], confidences[idx[0]], left, top, left + width, top + height)

    # Get the names of the output layers
    def __get_outputs_names(self):
        # Get the names of all the layers in the network
        layers_names = self.model.getLayerNames()
        # Get the names of the output layers, i.e. the layers with unconnected outputs
        return [layers_names[i[0] - 1] for i in self.model.getUnconnectedOutLayers()]
