"""! @package bow_client
This is the documentation for the bow_client module.

This module provides an interface for the BOW python SDK which allows you to connect to and interact with robots running a BOW driver.
"""

# -*- coding: utf-8 -*-
# Copyright (c) 2023, Bettering Our Worlds (BOW) Ltd.
# All Rights Reserved
# Author: Daniel Camilleri <daniel.camilleri@bow.ltd>

import bow_utils
from bow_utils import ImageSampleHelper
from lib_client import animus_client as bow_client
import logging
from typing import Union, Tuple, Any, List, Optional

## A logging.Logger object created to write information about this BOW client to the logs and terminal.
log = bow_utils.create_logger("BOWClient", logging.INFO)
_bow_messages_version = "v1.1.20"
_bow_core_version = "v4.0.2.1509"
_bow_client_version = "v4.0.2.2081"
_sdk_version = "v2.1.0.3077"
_sdk_build_date = "2024-04-05-16:38:58-UTC"

# Setup default audio parameters for the inbuilt audio player
# Backends = ["alsa", "wasapi", "dsound", "winmm", "pulse", "jack", "coreaudio",
#                   "sndio", "audio4", "oss", "opensl", "openal", "sdl"]
# SampleRate
# Channels
# packets transmitted per second
# sizeinframes - leave true

## Gets the SDK version information.
# Gets the version of the bow client and animus core libraries.
# @return **str**: A version string in the form:
# @code
# [ INFO  - BOWClient  ] 2023-10-06 23:17:21,537 - b'BOW Client                     version v3.2.1.1683 \nBOW Core                       version v3.2.1.1201\nBuilt with AnimusMessages v0.10.31 on 2023-08-24-14:13:43-UTC \nCopyright (C) 2023 Bettering Our Worlds (BOW) Ltd. - All Rights Reserved\n'
# b'BOW Client                     version v3.2.1.1683 \nBOW Core                       version v3.2.1.1201\nBuilt with AnimusMessages v0.10.31 on 2023-08-24-14:13:43-UTC \nCopyright (C) 2023 Bettering Our Worlds (BOW) Ltd. - All Rights Reserved\n'
# @endcode
def version() -> str:
    version_string = bow_client.VersionGo()
    log.info(version_string)
    return version_string

## The Robot class.
# Each instance represents a robot connection. You can have multiple robots connected, each with their own class to allow for multiple synchronised robot control.
class Robot:

    ## The Robot class initialiser.
    # The constructor accepts the robot details obtained from get_robots()
    # @param robot_details **bow_utils.GetRobotsProtoReply.robots[]**: Obtained from get_robots().
    def __init__(self, robot_details):

        self.robot_details = robot_details
        self.robot_id = self.robot_details.robot_id

    ## Starts a connection with the robot.
    # This method starts a peer to peer connection with the robot using the robot details previously passed in to the constructor.
    # @return **bow_utils.Error**: Where error.Success is a boolean, True indicates a successful connection. If error.Success is False you can inspect error.Description for more information.
    def connect(self) -> bow_utils.Error:
        log.info("Connecting with robot {}".format(self.robot_details.name))

        connect_request = bow_utils.ChosenRobotProto(
            chosenOne=self.robot_details
        ).SerializeToString()

        return bow_utils.Error().FromString(
            bow_client.Connect(connect_request, len(connect_request))
        )

    ## Opens a channel for the given modality.
    # Opens a channel between the robot and client, over which data for the chosen modality is transmitted.
    # @param modality_name **str**: The name of the modality channel you wish to open. Available options are specific to the robot but can be vision, audition, proprioception, motor, voice, speech or tactile.
    # @return **bow_utils.Error**: Where error.Success is a boolean, True indicates a successful open. If error.Success is False you can inspect error.Description for more information.
    def open_modality(self, modality_name: str) -> bow_utils.Error:
        log.info("Opening {} modality".format(modality_name))

        open_modality_request = bow_utils.OpenModalityProto(
            modalityName=modality_name,
            fps=30
        ).SerializeToString()

        return bow_utils.Error().FromString(
            bow_client.OpenModality(self.robot_id.encode(), open_modality_request, len(open_modality_request))
        )

    ## Sends data on an open modality channel.
    # This sends a sample of data of the correct type over the open modality channel to the robot.
    # @param modality_name **str**: The name of the modality channel you wish to send data on.
    # @param sample **bow_utils.MotorSample**, **bow_utils.AudioSamples**, **bow_utils.StringSample**:
    # @return **bow_utils.Error**: Where error.Success is a boolean, True indicates a successful send. If error.Success is False you can inspect error.Description for more information.
    def set_modality(self, modality_name: str, sample: Union[
        ImageSampleHelper,
        List[ImageSampleHelper],
        bow_utils.AudioSample,
        bow_utils.AudioSamples,
        List[bow_utils.AudioSample],
        bow_utils.TactileSamples,
        bow_utils.TactileSample,
        List[bow_utils.TactileSample],
        bow_utils.ProprioceptionSample,
        bow_utils.MotorSample,
        bow_utils.StringSample,
        bow_utils.BlobSample,
        bow_utils.Int64Array,
        bow_utils.Float32Array,
        bow_utils.Command,
        str,
        List[float],
        List[int]]
                     ) -> bow_utils.Error:

        # Sample is validated in validate_encode_databefore being transmitted
        dtype, data, data_len = bow_utils.encode_data(sample)
        if dtype is not None:
            return bow_utils.Error().FromString(
                bow_client.SetModality(self.robot_id.encode(), modality_name.encode(), dtype, data, data_len)
            )
        else:
            error = bow_utils.Error()
            error.Success = False
            error.Code = -1
            error.Description = "Failed to encode data"
            return error

    ## @brief Reads data from an open modality channel.
    # This reads a data sample from the robot on the named open modality channel.
    # @param modality_name **str**: The name of the modality channel you wish to receive data on.
    # @param blocking **bool**: Optional parameter, if True, function will block until data is received from the robot.
    # @return **bow_utils.ProprioceptionSample**, **List[bow_utils.AudioSample]**, **List[bow_utils.ImageSampleHelper]**, **List[utils.TactileSample]**: type depends on the chosen modality.
    def get_modality(self,
                     modality_name: str,
                     blocking: Optional[bool] = False
                     ) -> Tuple[Union[List[ImageSampleHelper],
                                List[bow_utils.AudioSample],
                                List[bow_utils.TactileSample],
                                bow_utils.MotorSample,
                                bow_utils.ProprioceptionSample,
                                bow_utils.StringSample,
                                bow_utils.BlobSample,
                                bow_utils.Float32Array,
                                bow_utils.Int64Array,
                                None],
                                bow_utils.Error]:
        get_result = bow_client.GetModality(self.robot_id.encode(), modality_name.encode(), int(bool(blocking)))
        sample = bow_utils.GetModalityProto().FromString(get_result)

        if not sample.error.Success:
            return None, sample.error

        new_sample = bow_utils.decode_data(sample.sample)
        if new_sample is None:
            sample.error.Success = False
            sample.error.Code = -1
            return None, sample.error

        return new_sample, sample.error

    ## Closes an open modality channel.
    # This closes the named open modality channel.
    # @param modality_name **str**: The name of the modality channel you wish to close.
    # @return **bow_utils.Error**: Where error.Success is a boolean, True indicates a successful closure. If error.Success is False you can inspect error.Description for more information.
    def close_modality(self, modality_name: str) -> bow_utils.Error:
        log.info("Closing {} modality".format(modality_name))
        return bow_utils.Error().FromString(
            bow_client.CloseModality(self.robot_id.encode(), modality_name.encode())
        )

    ## Close the connection to the robot.
    # This closes the peer to peer connection between client and robot.
    # @return **bow_utils.Error**: Where error.Success is a boolean, True indicates a successful disconnection. If error.Success is False you can inspect error.Description for more information.
    def disconnect(self) -> bow_utils.Error:
        log.info("Disconnecting from {}".format(self.robot_details.name))
        return bow_utils.Error().FromString(
            bow_client.Disconnect(self.robot_id.encode())
        )

## Quick connect function to simplify process of connecting to a robot and opening modalities.
# Quick connect talks to the system tray application to login, get a list of robots, connect to the robot chosen via the system tray and open the requested channels.
# @param pylog **logging.Logger**: Can be created with bow_util.create_logger(). A logging object which enables the SDK to output useful information about your robot and robot connection to the terminal.
# @param modalities **List[str]**: A list of the modalities you wish to open on the robot. Modalities are specific to the robot but can be vision, audition, proprioception, motor, voice, speech and tactile.
# @return Robot: Returns an instance of the Robot class, which represents the connected robot. Returns None if no connection made.
# @return **bow_utils.Error**: Where error.Success is a boolean, True indicates a successful connection. If error.Success is False you can inspect error.Description for more information.
def quick_connect(pylog: logging.Logger,
                  modalities: List[str],
                  verbose: bool = True,
                  audio_params: bow_utils.AudioParams = bow_utils.AudioParams(
                    Backends=[""],
                    SampleRate=16000,
                    Channels=1,
                    SizeInFrames=True,
                    TransmitRate=30)
                  ) -> Tuple[Union[Robot, None], bow_utils.Error]:

    # audio_params = bow_utils.AudioParams(
    #     Backends=[""],
    #     SampleRate=16000,
    #     Channels=1,
    #     SizeInFrames=True,
    #     TransmitRate=30
    # )

    setup_result = setup(audio_params, pylog.name, verbose)
    if not setup_result.Success:
        return None, setup_result

    login_result = login_user("", "", True)
    if login_result.Success:
        pylog.info("Logged in")
    else:
        return None, login_result

    get_robots_result = get_robots(False, False, True)
    if not get_robots_result.localSearchError.Success:
        pylog.error(get_robots_result.localSearchError.Description)

    if not get_robots_result.remoteSearchError.Success:
        pylog.error(get_robots_result.remoteSearchError.Description)

    if len(get_robots_result.robots) == 0:
        pylog.info("No Robots found")
        close_client_interface()
        return None, bow_utils.Error(Success=False, Code=62, Description="No Robots Found")

    chosen_robot_details = get_robots_result.robots[0]

    myrobot = Robot(chosen_robot_details)
    connected_result = myrobot.connect()
    if not connected_result.Success:
        pylog.error("Could not connect with robot {}".format(myrobot.robot_details.robot_id))
        close_client_interface()
        return None, connected_result

    all_robot_modalities = (list(chosen_robot_details.robot_config.input_modalities)
                            + list(chosen_robot_details.robot_config.output_modalities))
    print(all_robot_modalities)
    for modality in modalities:
        if modality in all_robot_modalities:
            open_result = myrobot.open_modality(modality)
            if not open_result.Success:
                pylog.error(f"Failed to open {modality} modality: {open_result.Description}")
        else:
            pylog.warning(f"{modality} modality is not available for the chosen robot. Modality ignored")

    err = bow_utils.Error()
    err.Success = True
    err.Code = 0
    err.Description = ""
    return myrobot, err

## Configures variables required for a BOW client.
# This function sets up the audio sampling and playback settings, sets the folder name for the log files and otherwise initialises all the variables required for a BOW client.
# @param audio_params **bow_utils.AudioParams**: Configures the settings for the audio streams. Use None for default settings.
# @param logdir **str**: Name of the desired directory for logs. Should take logging.Logger.name.
# @param loglatency **bool**: Determines whether the latency of messages are reported in the log.
# @return **bow_utils.Error**: Where error.Success is a boolean, True indicates a successful setup. If error.Success is False you can inspect error.Description for more information.
def setup(audio_params: bow_utils.AudioParams, logdir: str, loglatency: bool) -> bow_utils.Error:
    if audio_params is None:
        audio_params = bow_utils.AudioParams(
            Backends=[""],
            SampleRate=16000,
            Channels=1,
            SizeInFrames=True,
            TransmitRate=20
        )

    setup_request = bow_utils.SetupClientProto(
        audio_params=audio_params,
        logDir=logdir,
        latencyLogging=loglatency,
    ).SerializeToString()
    return bow_utils.Error().FromString(
        bow_client.Setup(setup_request, len(setup_request))
    )

## Login to your BOW account.
# Login with your BOW username and password to initialise communication session and therefore communicate with robots associated with your account.
# If you have the System Tray application installed, then you can bypass entering your username and password by setting system_login to True which will login using the credentials used for the Systray application.
# @param username **str**: Your BOW username.
# @param password **str**: Your BOW password.
# @param system_login **bool**: True logs in using System Tray Application credentials, False uses provided credentials.
def login_user(username: str, password: str, system_login: bool) -> bow_utils.Error:
    log.info("Logging in user")

    login_request = bow_utils.LoginProto(
        username=username,
        password=password,
        systrayLogin=system_login
    ).SerializeToString()

    return bow_utils.Error().FromString(
        bow_client.LoginUser(login_request, len(login_request))
    )

## Get list of available robots.
# Returns the list of robots associated with your BOW account that are available on the local network or remotely.
# @param get_local **bool**: True to include robots on local network in search.
# @param get_remote **bool**: True to include robots available remotely in search.
# @param get_system **bool**: True returns the robot currently selected in the Systray.
# @return **bow_util.GetRobotsProtoReply**: This object consists of:
# **remoteSearchError** of type *bow_utils.Error*,
# **localSearchError** of type *bow_utils.Error* and
# **robots** an iterable containing the robot details for each robot detected. Each element can be passed to the Robot class constructor.
#
# **Example**
# @code
# get_robots_result = get_robots(False, False, True)
# chosen_robot_details = get_robots_result.robots[0]
# myrobot = Robot(chosen_robot_details)
# @endcode
def get_robots(get_local: bool, get_remote: bool, get_system: bool) -> bow_utils.GetRobotsProtoReply:
    get_robots_request = bow_utils.GetRobotsProtoRequest(
        getLocal=get_local,
        getRemote=get_remote,
        systrayRobot=get_system
    ).SerializeToString()

    return bow_utils.GetRobotsProtoReply().FromString(
        bow_client.GetRobots(get_robots_request, len(get_robots_request))
    )

## Closes your BOW client.
# This closes the BOW client, to restart a BOW client after closing, the setup function would need to be called again.
def close_client_interface() -> None:
    log.info("Bow Session closed")
    bow_client.CloseClientInterfaceGo()
