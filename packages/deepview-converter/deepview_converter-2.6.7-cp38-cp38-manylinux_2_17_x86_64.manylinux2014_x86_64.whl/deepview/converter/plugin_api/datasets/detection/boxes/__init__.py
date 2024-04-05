import tensorflow as tf
import requests as re
import numpy as np
from psutil import virtual_memory
import json
import random
from os.path import exists
from time import perf_counter_ns

import deepview.datastore as ds
from deepview.converter.plugin_api.datasets.core import BaseDataset
from deepview.converter.plugin_api.datasets.core import \
    RequestFieldError, RemoteResponseError


def retrieve_page(url, params):
    response = re.get(url, params=params)
    if response.status_code != 200:
        raise RemoteResponseError(response.text, response.status_code)
    image_info = json.loads(response.text)
    return [x['id'] for x in image_info]


class BaseDetectionDataset(BaseDataset):
    def __init__(self, datastore, input_shape, batch_size, max_detections):
        super(BaseDetectionDataset, self).__init__(datastore=datastore,
                                                   input_shape=input_shape,
                                                   batch_size=batch_size,
                                                   sparse=False)
        self.max_detections = max_detections

    def cache_on_memory(self, num_samples):
        num_bytes = 2 * num_samples * (
                self.input_shape[0] * self.input_shape[1] * 3 +
                16 * self.max_detections)
        return virtual_memory().available >= num_bytes

    def init_labels(self):
        super().init_labels()
        self.labels = ['Background'] + self.labels

    @tf.function
    def tf_fetch_sample(self, instance_id):
        return tf.numpy_function(
            func=self.load_instance,
            inp=[instance_id],
            Tout=tf.uint8)

    def build_train_dataset(self):
        dataset = super(BaseDetectionDataset, self).build_tf_iterator("train")
        return dataset.batch(self.batch_size)


class RemoteDatastoreDetectionDataset(BaseDetectionDataset):
    def __init__(self, datastore, input_shape, batch_size, max_detections):
        super(RemoteDatastoreDetectionDataset, self).__init__(
            datastore=datastore,
            input_shape=input_shape,
            batch_size=batch_size,
            max_detections=max_detections)

    def get_image(self, image_id):
        url = '%s/v1/images/%d' % (self.datastore, image_id)
        params = {
            'height': self.input_shape[0],
            'width': self.input_shape[1]
        }
        while True:
            response = re.get(url, params=params)
            if response.status_code == 429:
                continue
            if response.status_code != 200:
                raise RemoteResponseError(response.text, response.status_code)
            image = tf.image.decode_jpeg(response.content, 3)
            return image

    def get_image_annotations(self, image_id, width, height):
        url = '%s/v1/annotations?image_id=%d' % (self.datastore, image_id)

        while True:
            response = re.get(url)
            if response.status_code == 429:
                continue
            if response.status_code != 200:
                raise RemoteResponseError(response.text, response.status_code)

            annotations = json.loads(response.text)
            annotations = random.sample(annotations, self.max_detections) \
                if len(annotations) > self.max_detections else annotations

            boxes, labels = [], []
            for index, annotation in enumerate(annotations):
                labels.append(self.labels.index(annotation['label']))

                if None in [
                    annotation['x'],
                    annotation['y'],
                    annotation['width'],
                    annotation['height']]:
                    bbox = [0.0, 0.0, 1.0, 1.0]
                else:
                    bbox = [
                        annotation['x'] / width,
                        annotation['y'] / height,
                        (annotation['x'] + annotation['width']) / width,
                        (annotation['y'] + annotation['height']) / height
                    ]
                boxes.append(bbox)

            if len(annotations) == 0:
                raise RuntimeError("Empty annotation list for image id: %d"
                                   % image_id)

            boxes = np.array(boxes)
            boxes = np.clip(boxes, 0.0, 1.0)
            # We must return a tuple of types which are correctly recognized by
            # TensorFlow: tf.float32, tf.int32, tf.int32
            return (tf.cast(boxes, tf.float32),
                    tf.cast(labels, tf.int32),
                    tf.cast(boxes.shape[0], tf.int32))

    def is_batched(self):
        return False

    def get_labels(self):
        url = self.datastore + '/v1/labels'
        response = re.get(url)
        if response.status_code != 200:
            raise RemoteResponseError(response.text, response.status_code)
        try:
            labels = json.loads(response.text)
            return [x['name'] for x in labels]
        except Exception as e:
            raise RequestFieldError('name') from e

    def get_num_samples(self, group):
        project_url = self.datastore + "/v1/project"
        response = re.get(project_url)
        if response.status_code != 200:
            raise RemoteResponseError(response.text, response.status_code)

        response_info = json.loads(response.text)
        if group == "train":
            num_samples = int(response_info["train_images"])
        else:
            num_samples = int(response_info["test_images"])
        return num_samples

    def read_annotations(self, grouping):
        num_samples = self.get_num_samples(grouping)

        url = self.datastore + '/v1/images'
        pages = int(num_samples / 1000)

        if pages < 1:
            return retrieve_page(url, {'group': grouping, 'tagged': 1})
        else:
            samples = []
            start = 0
            limit = 1000
            for i in range(pages + 1):
                params = {
                    'group': grouping,
                    'tagged': 1,
                    'limit': limit,
                    'offset': start}
                info_page = retrieve_page(url, params)
                samples += info_page
                start = 1000 * (i + 1)
                if num_samples - limit < 1000:
                    limit = num_samples - limit
            return samples

    def load_instance(self, instance_id):
        image = self.get_image(instance_id)
        return image


class LocalDatastoreDetectionDataset(RemoteDatastoreDetectionDataset):
    def __init__(self, datastore, input_shape, batch_size, max_detections):
        super(LocalDatastoreDetectionDataset, self).__init__(
            datastore=datastore,
            input_shape=input_shape,
            batch_size=batch_size,
            max_detections=max_detections)
        if datastore.startswith('http://'):
            response = re.get(datastore + '/v1/project')
            if response.status_code != 200:
                raise RemoteResponseError(response.text, response.status_code)
            try:
                project_info = json.loads(response.text)
                self.project_path = project_info['path']
            except Exception as e:
                raise RequestFieldError('path') from e
        else:
            self.project_path = datastore

        if not exists(self.project_path):
            raise FileNotFoundError(
                'Project file not found: %s' % self.project_path)
        self.project = ds.open_project(self.project_path)

    def is_batched(self):
        return False

    def get_labels(self):
        return self.project.labels()

    def get_image(self, image_id):
        image = self.project.image_with_id(image_id)
        encoded_image = image.scaled(self.input_shape[1], self.input_shape[0])
        width, height = image.get_size()
        if 0 in (width, height):
            raise RuntimeError('Invalid image with zero width/height')
        image_data = tf.image.decode_image(encoded_image.getvalue(),
                                               channels=3)
        return image_data

    def get_image_annotations(self, image_id, width, height):
        labels = []
        boxes = []

        for label, box in self.project.annotations_with_image(image_id):
            labels.append(self.labels.index(label))
            if box is None:
                boxes.append([0.0, 0.0, 1.0, 1.0])
            else:
                boxes.append([
                    box[0] / width,
                    box[1] / height,
                    (box[0] + box[2]) / width,
                    (box[1] + box[3]) / height])

        if len(labels) == 0 or len(boxes) == 0:
            raise RuntimeError("Empty annotation list for image id: %d"
                               % image_id)

        boxes = np.array(boxes)
        boxes = np.clip(boxes, 0.0, 1.0)

        return (tf.cast(boxes, tf.float32),
                tf.cast(labels, tf.int32),
                tf.cast(boxes.shape[0], tf.int32))

    def get_num_samples(self, group):
        dur = perf_counter_ns()
        count = self.project.annotated_images_with_grouping_count(group)
        dur = perf_counter_ns() - dur
        print('Counted %d %s annotations in %d ms'
              % (count, group, dur // 1e6))
        return count

    def read_annotations(self, group):
        dur = perf_counter_ns()
        images = self.project.annotated_images_with_grouping(group)
        dur = perf_counter_ns() - dur
        print('Retrieved %d %s annotations in %d ms'
              % (len(images), group, dur // 1e6))
        return [x.image_id for x in images]
