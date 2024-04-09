# darwin_fiftyone

Provides an integration between Voxel51 and V7 Darwin. This enables Voxel51 users to send subsets of their datasets to Darwin for annotation and review. The annotated data can then be imported back into Voxel51.

This integration is currently in beta.

## Example Usage

To illustrate, let's upload all files from the zoo dataset "quickstart" into a Darwin dataset named "quickstart-example". If the dataset doesn't already exist in Darwin, it will be created.

```python
import fiftyone.zoo as foz
dataset = foz.load_zoo_dataset("quickstart", dataset_name="quickstart-example")

#If video annotation
dataset.ensure_frames()

dataset.annotate(
    "annotation_job_key",
    label_field="ground_truth",
    atts=["iscrowd"],
    launch_editor=True,
    backend="darwin",
    dataset_slug="quickstart-example",
    external_storage="example-darwin-storage-slug",
    base_url="https://darwin.v7labs.com/api/v2/teams",
)
```

**Note**: You will have to use the `ensure_frames()` method on the dataset/view if you are annotating videos. You must also ensure that the label_field begins with `frames.` e.g. `frames.detections`

After the annotations and reviews are completed in Darwin, you can fetch the updated data as follows:

```python
dataset.load_annotations("annotation_job_key")
```

## API

In addition to the standard arguments provided by dataset.annotate(), we also support:

- `backend=darwin`, Indicates that the Darwin backend is being used.
- `atts`, Specifies attribute subannotations to be added in the labelling job
- `dataset_slug`, Specifies the name of the dataset to use or create on Darwin.
- `external_storage`, Specifies the sluggified name of the Darwin external storage and indicates that all files should be treated as external storage

## Checking Status

You can check the status of your V7 Darwin dataset by calling the `check_status()` method

```python
results = dataset.load_annotation_results(anno_key)
results.check_status()
```

## Configuration

To integrate with the Darwin backend:

1. Install the backend:

```bash
pip install .
```

2. Configure voxel51 to use it.

```bash
cat ~/.fiftyone/annotation_config.json
```

```json
{
  "backends": {
    "darwin": {
      "config_cls": "darwin_fiftyone.DarwinBackendConfig",
      "api_key": "d8mLUXQ.**********************"
    }
  }
}
```

**Note**: Replace the api_key placeholder with a valid API key generated from Darwin.

## Supported Annotation Types

The integration currently supports bounding boxes, polygons (closed polylines), keypoints, and tags (classification). It also supports attributes, text, instance ids, and properties subtypes.

Future development work will focus on the addition of annotation and subannotation types. Do reach out if you have suggestions.

## TODO
- Support for read only external data storage
- Support for mask and keypoint skeleton types