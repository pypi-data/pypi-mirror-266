# This module defines global config for use in the Huggingface Remote Schema Retrival package.
# text-to-image: BETA MODE (Auto Serialization/Deserialization logic needs to be added in the sagemaker-python-sdk)
SUPPORTED_TASKS = ['question-answering', 'automatic-speech-recognition', 'fill-mask', 'text-to-image']
PATH_TO_HF_TASKS_NPM = 'huggingface/node_modules/@huggingface/tasks/src/tasks'
SAMPLE_AUDIO = 'sample.flac'
SAMPLE_IMAGE = 'png-truncated.png'
PATH_TO_SAMPLE_AUDIO = 'huggingface/sample_data/audio'
PATH_TO_SAMPLE_IMAGE = 'huggingface/sample_data/image'
