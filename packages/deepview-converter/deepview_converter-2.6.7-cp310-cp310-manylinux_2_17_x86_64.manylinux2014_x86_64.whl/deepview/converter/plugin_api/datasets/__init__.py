def get_cached_image_classification_dataset(arguments):
    try:
        from deepview.converter.plugin_api.datasets.classification.image \
            import LocalDatastoreClassificationDataset
        dataset = LocalDatastoreClassificationDataset(
            arguments['datastore_server'],
            arguments['input_shape'],
            arguments["batch_size"])
        dataset.init_dataset()
        return dataset
    except Exception as e:
        print('Unable to use fast-path connection to datastore:', e)

    from deepview.converter.plugin_api.datasets.classification.image \
        import RemoteDatastoreClassificationDataset
    dataset = RemoteDatastoreClassificationDataset(
        arguments['datastore_server'],
        arguments['input_shape'],
        arguments["batch_size"])
    dataset.init_dataset()
    return dataset


def get_cached_object_detection_dataset(arguments):
    try:
        from deepview.converter.plugin_api.datasets.detection.boxes \
            import LocalDatastoreDetectionDataset
        dataset = LocalDatastoreDetectionDataset(
            datastore=arguments['datastore_server'],
            input_shape=arguments['input_shape'],
            batch_size=arguments['batch_size'],
            max_detections=arguments['max_detections'])
        dataset.init_dataset()
        return dataset
    except Exception as e:
        print('Unable to use fast-path connection to datastore:', e)

    from deepview.converter.plugin_api.datasets.detection.boxes \
        import RemoteDatastoreDetectionDataset
    dataset = RemoteDatastoreDetectionDataset(
        datastore=arguments['datastore_server'],
        input_shape=arguments['input_shape'],
        batch_size=arguments['batch_size'],
        max_detections=arguments['max_detections'])
    dataset.init_dataset()
    return dataset


def get_cached_dataset(task, p_type, arguments):
    if task == "classification":
        if p_type == "image":
            return get_cached_image_classification_dataset(arguments)
        else:
            raise ValueError("Task ``{}`` is not supported yet !".format(
                p_type
            ))
    else:
        if task == 'detection':
            return get_cached_object_detection_dataset(arguments)
        else:
            raise ValueError("Task ``{}`` is not supported yet !".format(
                p_type
            ))
