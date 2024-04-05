import tensorflow as tf
import requests as re
from psutil import virtual_memory
import json
import time

from os import environ, getenv
from os.path import exists
from typing import Tuple

import deepview.datastore as ds
from deepview.converter.plugin_api.datasets.core import BaseDataset
from deepview.converter.plugin_api.datasets.core import \
    RequestFieldError, RemoteResponseError


class BaseClassificationDataset(BaseDataset):
    def __init__(self, datastore, input_shape, batch_size):
        super(BaseClassificationDataset, self).__init__(
            datastore=datastore,
            input_shape=input_shape,
            batch_size=batch_size,
            sparse=False)

    def cache_on_memory(self, num_samples):
        num_bytes = 2 * num_samples * \
                    self.input_shape[0] * self.input_shape[1] * 3
        return virtual_memory().available > num_bytes

    @tf.function
    def process_test_data(self, x_sample, y_sample):
        float_image = tf.cast(x_sample, tf.float32)
        aug_img = tf.numpy_function(func=self.preprocess_input, inp=[
            float_image], Tout=tf.float32)
        label = tf.one_hot(y_sample, self.get_num_classes())
        return aug_img, label

    @tf.function
    def tf_fetch_sample(self, instance_id):
        return tf.numpy_function(func=self.load_instance,
                                 inp=[instance_id],
                                 Tout=tf.uint8)

    def build_train_dataset(self):
        dataset = super(BaseClassificationDataset,
                        self).build_tf_iterator("train")
        return dataset.batch(self.batch_size)


class RemoteDatastoreClassificationDataset(BaseClassificationDataset):
    def __init__(self, datastore, input_shape, batch_size):
        super(RemoteDatastoreClassificationDataset, self).__init__(
            datastore=datastore,
            input_shape=input_shape,
            batch_size=batch_size)
        self.number_of_threads = 16

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

    def read_annotations(self, grouping):
        url = '{}/v1/annotations?group={}'.format(self.datastore, grouping)
        response = re.get(url)
        if response.status_code != 200:
            raise RemoteResponseError(response.text, response.status_code)

        try:
            image_info = json.loads(response.text)
            return [x['id'] for x in image_info]
        except Exception as e:
            raise RequestFieldError('id') from e

    def load_instance(self, instance_id):
        while True:
            url = '{}/v1/samples/{}'.format(self.datastore, instance_id)
            params = {
                'crop': 1,
                'height': self.input_shape[0],
                'width': self.input_shape[1],
                'ignore_aspect': 1
            }
            response = re.get(url, params=params)
            if response.status_code == 200:
                break
            else:
                time.sleep(0.1)
        image = tf.image.decode_image(response.content, channels=3)
        return image


class LocalDatastoreClassificationDataset(BaseClassificationDataset):
    """
    This class implements a local fast-path connection to the datastore.  On
    construction it will attempt to open the local datastore project as
    returned by the Datastore HTTP API at /v1/project.

    Note:
        This class should only be used when the datastore is actually available
        locally and ensuring that the path returned by /v1/project is, in fact,
        the same project opened by the Datastore server.
    """

    def __init__(self,
                 datastore: str,
                 input_shape: Tuple[int, int, int],
                 batch_size: int):
        """
        Args:
            datastore: the URI to the datastore server.
            input_shape: the model's input shape to which the dataset must be
                adapted.
            batch_size: the batch size to be used for training.

        Raises:
            FileNotFoundError: The path refered to by ``/v1/project`` is not a
                valid project file.
            PermissionError: Insufficient priviledges to open the project file
                referenced by ``/v1/project``
            ConnectionError: Failed to connect to datastore to retrieve the
                ``/v1/project`` JSON
            RemoteResponseError: Datastore returned an invalid JSON object for
                ``/v1/project``
            RequestFieldError: Datastore ``/v1/project`` response is missing a
                required field.
        """
        super(LocalDatastoreClassificationDataset, self).__init__(
            datastore=datastore,
            input_shape=input_shape,
            batch_size=batch_size)
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

        if 'DATASTORE_PROFILER' in environ:
            ds.start_profiler(
                getenv('DATASTORE_PROFILER'),
                getenv('DATASTORE_PROFILER_MODE', 'CPU'))

        if not exists(self.project_path):
            raise FileNotFoundError(
                'Project file not found: %s' % self.project_path)
        self.project = ds.open_project(self.project_path)

    def __del__(self):
        if 'DATASTORE_PROFILER' in environ:
            ds.stop_profiler()

    def is_batched(self):
        return False

    def get_labels(self):
        return self.project.labels()

    def read_annotations(self, grouping):
        return self.project.annotation_ids_with_grouping(grouping)

    def load_instance(self, instance_id):
        resize = (self.input_shape[1], self.input_shape[0])
        data = self.project.sample(instance_id, resize)
        image = tf.image.decode_image(data.getvalue(), channels=3)
        return image
