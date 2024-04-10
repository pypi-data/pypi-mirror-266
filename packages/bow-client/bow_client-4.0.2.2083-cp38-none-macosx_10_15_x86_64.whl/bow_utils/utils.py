# -*- coding: utf-8 -*-
# Copyright (c) 2023, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: Daniel Camilleri <daniel.camilleri@bow.ltd>

import logging
import time
import types
from collections import OrderedDict

import numpy
import numpy as np
from functools import partial

import bow_utils as bow_data
import cv2
from typing import Union, Tuple, Any, Optional, List

from google.protobuf.internal import enum_type_wrapper

HEAD_RIGHT = 1.0
HEAD_LEFT = -1.0
HEAD_UP = 1.0
HEAD_DOWN = -1.0
BODY_FORWARD = 1.0
BODY_BACKWARD = -1.0
BODY_LEFT = -1.0
BODY_RIGHT = 1.0
BODY_CLOCKWISE = 1.0
BODY_ANTICLOCKWISE = -1.0


def create_logger(name, level) -> logging.Logger:
    logger = logging.getLogger(name)
    if not len(logger.handlers):
        formatter = logging.Formatter('[ %(levelname)-5s - {:10} ] %(asctime)s - %(message)s'.format(name))
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)

        logger.addHandler(ch)
        logger.setLevel(level)

    return logger


log = create_logger("BowUtils", logging.INFO)
discover_log = create_logger("DiscoverModalities", logging.INFO)
dummy_log = create_logger("DummyModality", logging.INFO)
encode_log = create_logger("Encoder", logging.INFO)
decode_log = create_logger("Decoder", logging.INFO)

# # Connection struct definitions
emotions_list = ["angry", "fear", "sad", "happy", "surprised", "neutral"]
audio_backends = ["alsa", "wasapi", "dsound", "winmm", "pulse", "jack", "coreaudio",
                  "sndio", "audio4", "oss", "opensl", "openal", "sdl"]


def get_motor_dict() -> dict:
    ret = OrderedDict()
    ret["head_left_right"] = 0.0
    ret["head_up_down"] = 0.0
    ret["head_roll"] = 0.0
    ret["body_forward"] = 0.0
    ret["body_sideways"] = 0.0
    ret["body_rotate"] = 0.0
    ret["tracking_left_arm"] = -1.0
    ret["tracking_right_arm"] = -1.0
    return ret


class RobotAction:
    def __init__(self):
        self.data = None
        self.modality = None


class ImageSampleHelper:
    def __init__(self,
                 source=None,  # type: (Optional[str])
                 shape=None,  # type: (Optional[np.ndarray])
                 image=None,  # type: (Optional[np.ndarray])
                 image_type=bow_data.ImageSample.ImageTypeEnum.RGB,  # type: (Optional[bow_data.ImageSample.ImageTypeEnum])
                 transform=None,  # type: (Optional[bow_data.Transform])
                 compression=bow_data.ImageSample.CompressionFormatEnum.RAW,  # type: (Optional[bow_data.ImageSample.CompressionFormatEnum])
                 designation=bow_data.StereoDesignationEnum.NONE,  # type: (Optional[bow_data.ImageSample.StereoDesignationEnum])
                 hfov=90,  # type: (Optional[int])
                 vfov=0    # type: (Optional[int])
                 ) -> None:
        pass
        self.source = source
        self.shape = shape
        self.image = image
        self.image_type = image_type
        self.transform = transform
        self.compression = compression
        self.stereo_designation = designation
        self.hfov = hfov
        self.vfov = vfov
        self.new_data_flag = False

    def from_proto(self, image_sample: bow_data.ImageSample) -> bool:
        try:
            npimage = np.frombuffer(image_sample.Data, np.uint8).reshape(
                [int(image_sample.DataShape[1] * 3 / 2), image_sample.DataShape[0]])
            npimage = cv2.cvtColor(npimage, cv2.COLOR_YUV2RGB_I420)

            self.source = image_sample.Source
            self.shape = image_sample.DataShape
            self.image = npimage
            self.image_type = image_sample.ImageType
            self.transform = image_sample.Transform
            self.compression = image_sample.Compression
            self.stereo_designation = image_sample.Designation
            self.hfov = image_sample.HFOV
            self.vfov = image_sample.VFOV
            self.new_data_flag = image_sample.NewDataFlag
            return True
        except Exception as e:
            log.error("Error importing image from proto: " + str(e))
            return False

    def to_proto(self) -> bow_data.ImageSample:
        return bow_data.ImageSample(
            Source=self.source,
            Data=self.image.tostring(),
            DataShape=self.shape,
            Compression=self.compression,
            ImageType=self.image_type,
            Transform=self.transform,
            Designation=self.stereo_designation,
            HFOV=self.hfov,
            VFOV=self.vfov,
            NewDataFlag=self.new_data_flag,
        )

    def encode_image(self, image: numpy.array) -> None:
        self.shape = [image.shape[1], image.shape[0], image.shape[2]]
        self.image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV_I420)
        self.new_data_flag = True


def encode_audio(proto: bow_data.AudioSample, data: np.array, sample_rate: int, channels: int) -> None:
    proto.SampleRate = sample_rate
    proto.Channels = channels
    proto.Data = data.tostring()
    proto.NumSamples = int(len(data) / channels)


def decode_data(sample: bow_data.DataMessage) -> (Union[
            ImageSampleHelper,
            List[ImageSampleHelper],
            bow_data.AudioSample,
            List[bow_data.AudioSample],
            bow_data.MotorSample,
            bow_data.ProprioceptionSample,
            bow_data.StringSample,
            bow_data.BlobSample,
            bow_data.Float32Array,
            bow_data.Int64Array,
            None,
    ]):

    if sample.data_type == bow_data.DataMessage.IMAGE:
        image_samples = bow_data.ImageSamples().FromString(sample.data)
        image_list = []
        for im in image_samples.Samples:
            new_pyimage = ImageSampleHelper()
            success = new_pyimage.from_proto(im)
            if success:
                image_list.append(new_pyimage)
        return image_list

    elif sample.data_type == bow_data.DataMessage.AUDIO:
        audio_samples = bow_data.AudioSamples().FromString(sample.data)
        audio_list = []
        for frame in audio_samples.Samples:
            audio_list.append(frame)
        return audio_list

    elif sample.data_type == bow_data.DataMessage.STRING:
        return bow_data.StringSample().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.FLOAT32ARR:
        return bow_data.Float32Array().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.INT64ARR:
        return bow_data.Int64Array().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.COMMAND:
        return bow_data.Command().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.MOTOR:
        return bow_data.MotorSample().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.BLOB:
        return bow_data.BlobSample().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.PROPRIOCEPTION:
        return bow_data.ProprioceptionSample().FromString(sample.data)

    elif sample.data_type == bow_data.DataMessage.TACTILE:
        tactile_samples = bow_data.TactileSamples().FromString(sample.data)
        tactile_list = []
        for frame in tactile_samples.Samples:
            tactile_list.append(frame)
        return tactile_list

    else:
        decode_log.info("decoding {} datatype unhandled".format(sample.data_type))
        return None


def encode_data(sample: Union[
                                ImageSampleHelper,
                                List[ImageSampleHelper],
                                bow_data.AudioSample,
                                bow_data.AudioSamples,
                                List[bow_data.AudioSample],
                                bow_data.TactileSamples,
                                bow_data.TactileSample,
                                List[bow_data.TactileSample],
                                bow_data.ProprioceptionSample,
                                bow_data.MotorSample,
                                bow_data.StringSample,
                                bow_data.BlobSample,
                                bow_data.Int64Array,
                                bow_data.Float32Array,
                                bow_data.Command,
                                str,
                                List[float],
                                List[int]]
                ):
    encoded_dtype=None
    encoded_sample=None
    if isinstance(sample, list):
        if isinstance(sample[0], float):
            encoded_sample = bow_data.Float32Array(Data=sample).SerializeToString()
            encoded_dtype = bow_data.DataMessage.FLOAT32ARR

        elif isinstance(sample[0], int):
            encoded_sample = bow_data.Int64Array(Data=sample).SerializeToString()
            encoded_dtype = bow_data.DataMessage.INT64ARR

        elif isinstance(sample[0], ImageSampleHelper):
            image_samples = bow_data.ImageSamples()
            for s in sample:
                image_samples.Samples.append(s.to_proto())

            encoded_sample = image_samples.SerializeToString()
            encoded_dtype = bow_data.DataMessage.IMAGE

        elif isinstance(sample[0], bow_data.AudioSamples):
            audio_samples = bow_data.AudioSamples()
            for s in sample:
                audio_samples.Samples.append(s)

            encoded_sample = audio_samples.SerializeToString()
            encoded_dtype = bow_data.DataMessage.AUDIO

        elif isinstance(sample[0], bow_data.TactileSamples):
            tactile_samples = bow_data.TactileSamples()
            for s in sample:
                tactile_samples.Samples.append(s)

            encoded_sample = tactile_samples.SerializeToString()
            encoded_dtype = bow_data.DataMessage.AUDIO

        else:
            encode_log.error("list of {} data type is unsupported".format(type(sample[0])))
            return None, None, 0

    elif isinstance(sample, ImageSampleHelper):
        image_samples = bow_data.ImageSamples()
        image_samples.Samples.append(sample.to_proto())

        encoded_sample = image_samples.SerializeToString()
        encoded_dtype = bow_data.DataMessage.IMAGE

    elif isinstance(sample, bow_data.AudioSample):
        audio_samples = bow_data.AudioSamples()
        audio_samples.Samples.append(sample)

        encoded_sample = audio_samples.SerializeToString()
        encoded_dtype = bow_data.DataMessage.AUDIO

    elif isinstance(sample, str):
        encoded_sample = bow_data.StringSample(Data=sample).SerializeToString()
        encoded_dtype = bow_data.DataMessage.STRING

    elif isinstance(sample, bow_data.MotorSample):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.MOTOR

    elif isinstance(sample, bow_data.BlobSample):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.BLOB

    elif isinstance(sample, bow_data.ProprioceptionSample):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.PROPRIOCEPTION

    elif isinstance(sample, bow_data.TactileSample):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.TACTILE

    elif isinstance(sample, bow_data.Command):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.COMMAND

    elif isinstance(sample, bow_data.Int64Array):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.INT64ARR

    elif isinstance(sample, bow_data.Float32Array):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.FLOAT32ARR

    elif isinstance(sample, bow_data.StringSample):
        encoded_sample = sample.SerializeToString()
        encoded_dtype = bow_data.DataMessage.STRING

    else:
        encode_log.error("{} data type is unsupported".format(type(sample)))
        return None, None, 0

    # type: (Tuple[Optional[bow_utils.DataMessage.DataType], Optional[str], int])
    return encoded_dtype, encoded_sample, len(encoded_sample)


def discover_modalities(driver_class: Any) -> [List[str], List[str]]:
    method_list = [func for func in dir(driver_class) if
                   callable(getattr(driver_class, func)) and not func.startswith("__")]

    init_modalities = [m.replace("_initialise", "") for m in method_list if "_initialise" in m]
    close_modalities = [m.replace("_close", "") for m in method_list if "_close" in m]
    set_modalities = [m.replace("_set", "") for m in method_list if "_set" in m]
    get_modalities = [m.replace("_get", "") for m in method_list if "_get" in m]

    # After getting lists for init close set and get,
    # find modalities that are present in init, close and get or set.
    modalities_dict = OrderedDict()

    input_modalities = []
    output_modalities = []
    for priority, mod in enumerate(init_modalities):
        if mod in close_modalities:
            if mod in set_modalities:
                modalities_dict[mod] = ["input", priority]
                input_modalities.append(mod)
            elif mod in get_modalities:
                modalities_dict[mod] = ["output", priority]
                output_modalities.append(mod)
            else:
                discover_log.warning("{} Modality incomplete. No set or get method".format(mod))
        else:
            discover_log.warning("{} Modality incomplete. No close method".format(mod))

    return input_modalities, output_modalities


class EmptyHelperClass(object):
    def __init__(self):
        pass


class DummyModality(object):
    def __init__(self, name):
        self.name = name

    def open(self):
        dummy_log.error("{} modality is not implemented for this robot. Cannot open()".format(self.name))
        return False

    def get(self):
        dummy_log.error("{} modality is not implemented for this robot. Cannot get()".format(self.name))
        return None

    def set(self):
        dummy_log.error("{} modality is not implemented for this robot. Cannot set()".format(self.name))
        pass

    def close(self):
        dummy_log.error("{} modality is not implemented for this robot. Cannot close()".format(self.name))
        pass


def check_function(func, devmode):
    if not devmode:
        return True

    if isinstance(func, types.MethodType) or isinstance(func, types.FunctionType) or isinstance(func, partial):
        return True
    else:
        return False


class FpsLag:
    def __init__(self, log: logging.Logger, modality_name:str, interval=128) -> None:
        self.count = 0
        self.interval = interval
        self.cumulative_lag = 0
        self.fps_startt = time.time()
        self.name = modality_name
        self.log = log
        self.average_fps = 0
        self.average_lag = 0

    def increment(self, send_timestamp=None) -> bool:
        self.count += 1
        if send_timestamp is not None:
            self.cumulative_lag += time.time() - send_timestamp

        if self.count == self.interval:
            endt = time.time()
            self.average_fps = self.interval / (endt - self.fps_startt)
            if send_timestamp is not None:
                self.average_lag = self.cumulative_lag / self.interval
                self.log.info("{} - {:.2f} fps ------ {:.2f} lag".format(self.name.capitalize(),
                                                                         self.average_fps, self.average_lag))
            else:
                self.log.info("{} - {:.2f} fps ".format(self.name.capitalize(), self.average_fps))

            self.fps_startt = endt
            self.count = 0
            self.cumulative_lag = 0
            return True
        return False


class PeriodicSampler:
    def __init__(self, name, periodic_function, rate, devmode, success_callback=None):
        self._name = name
        self._periodic_function = periodic_function
        self.requested_rate = rate

        if check_function(success_callback, devmode):
            self._success_callback = success_callback
        else:
            raise ValueError("Callback must be a function")

        self._result = None
        self._run_flag = True
        self.log = create_logger(name="Sample Loop".format(self._name), level=logging.INFO)
        self.perf = FpsLag(log=self.log, modality_name=self._name, interval=128)

    def run(self):
        rate_delay = 1.0 / self.requested_rate

        self.log.info("Started {} sampling loop".format(self._name))

        average_fps = -1
        while self._run_flag:
            time.sleep(rate_delay)

            self._result = self._periodic_function()

            if self._result is not None:
                self._success_callback(self._result, average_fps)
                if self.perf.increment():
                    rate_delay += 1.0 / self.requested_rate - 1.0 / self.perf.average_fps

                    # samp_log.info("{} - {:.2f} fps".format(self._name.capitalize(), average_fps))

                    if rate_delay < 0:
                        rate_delay = 0

        self.log.info("{} sampling loop stopped".format(self._name.capitalize()))

    @property
    def result(self):
        """
        Returns:
            Result of the function.
        """
        return self._result

    def stop(self):
        self._run_flag = False
