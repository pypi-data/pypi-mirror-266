import bow_data_common_pb2 as _bow_data_common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Lidar(_message.Message):
    __slots__ = ["Data", "Start", "End", "AngularResolution", "TemporalResolution", "Transform", "NewDataFlag"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    ANGULARRESOLUTION_FIELD_NUMBER: _ClassVar[int]
    TEMPORALRESOLUTION_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    NEWDATAFLAG_FIELD_NUMBER: _ClassVar[int]
    Data: _containers.RepeatedScalarFieldContainer[float]
    Start: float
    End: float
    AngularResolution: float
    TemporalResolution: float
    Transform: _bow_data_common_pb2.Transform
    NewDataFlag: bool
    def __init__(self, Data: _Optional[_Iterable[float]] = ..., Start: _Optional[float] = ..., End: _Optional[float] = ..., AngularResolution: _Optional[float] = ..., TemporalResolution: _Optional[float] = ..., Transform: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., NewDataFlag: bool = ...) -> None: ...

class Range(_message.Message):
    __slots__ = ["Data", "Min", "Max", "FOV", "SensorType", "OperationType", "Transform"]
    class SensorTypeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        Distance: _ClassVar[Range.SensorTypeEnum]
        Proximity: _ClassVar[Range.SensorTypeEnum]
    Distance: Range.SensorTypeEnum
    Proximity: Range.SensorTypeEnum
    class OperationTypeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        Ultrasound: _ClassVar[Range.OperationTypeEnum]
        Infrared: _ClassVar[Range.OperationTypeEnum]
        Mechanical: _ClassVar[Range.OperationTypeEnum]
    Ultrasound: Range.OperationTypeEnum
    Infrared: Range.OperationTypeEnum
    Mechanical: Range.OperationTypeEnum
    DATA_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    FOV_FIELD_NUMBER: _ClassVar[int]
    SENSORTYPE_FIELD_NUMBER: _ClassVar[int]
    OPERATIONTYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    Data: float
    Min: float
    Max: float
    FOV: float
    SensorType: Range.SensorTypeEnum
    OperationType: Range.OperationTypeEnum
    Transform: _bow_data_common_pb2.Transform
    def __init__(self, Data: _Optional[float] = ..., Min: _Optional[float] = ..., Max: _Optional[float] = ..., FOV: _Optional[float] = ..., SensorType: _Optional[_Union[Range.SensorTypeEnum, str]] = ..., OperationType: _Optional[_Union[Range.OperationTypeEnum, str]] = ..., Transform: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ...) -> None: ...

class IMU(_message.Message):
    __slots__ = ["Gyro", "Acc", "Orientation", "Transform"]
    GYRO_FIELD_NUMBER: _ClassVar[int]
    ACC_FIELD_NUMBER: _ClassVar[int]
    ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    Gyro: _bow_data_common_pb2.Vector3
    Acc: _bow_data_common_pb2.Vector3
    Orientation: _bow_data_common_pb2.Vector3
    Transform: _bow_data_common_pb2.Transform
    def __init__(self, Gyro: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ..., Acc: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ..., Orientation: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ..., Transform: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ...) -> None: ...

class GPS(_message.Message):
    __slots__ = ["Latitude", "Longitude", "Elevation", "Time"]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    ELEVATION_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    Latitude: float
    Longitude: float
    Elevation: float
    Time: str
    def __init__(self, Latitude: _Optional[float] = ..., Longitude: _Optional[float] = ..., Elevation: _Optional[float] = ..., Time: _Optional[str] = ...) -> None: ...

class Compass(_message.Message):
    __slots__ = ["Mag", "Transform"]
    MAG_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    Mag: _bow_data_common_pb2.Vector3
    Transform: _bow_data_common_pb2.Transform
    def __init__(self, Mag: _Optional[_Union[_bow_data_common_pb2.Vector3, _Mapping]] = ..., Transform: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ...) -> None: ...

class Light(_message.Message):
    __slots__ = ["Data", "Min", "Max", "Unit", "Transform"]
    class LightUnitEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        Lux: _ClassVar[Light.LightUnitEnum]
        Undefined: _ClassVar[Light.LightUnitEnum]
    Lux: Light.LightUnitEnum
    Undefined: Light.LightUnitEnum
    DATA_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    Data: float
    Min: float
    Max: float
    Unit: Light.LightUnitEnum
    Transform: _bow_data_common_pb2.Transform
    def __init__(self, Data: _Optional[float] = ..., Min: _Optional[float] = ..., Max: _Optional[float] = ..., Unit: _Optional[_Union[Light.LightUnitEnum, str]] = ..., Transform: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ...) -> None: ...

class ExteroceptionSample(_message.Message):
    __slots__ = ["Lidar", "Range", "Imu", "Gps", "Compass", "Env", "Light"]
    LIDAR_FIELD_NUMBER: _ClassVar[int]
    RANGE_FIELD_NUMBER: _ClassVar[int]
    IMU_FIELD_NUMBER: _ClassVar[int]
    GPS_FIELD_NUMBER: _ClassVar[int]
    COMPASS_FIELD_NUMBER: _ClassVar[int]
    ENV_FIELD_NUMBER: _ClassVar[int]
    LIGHT_FIELD_NUMBER: _ClassVar[int]
    Lidar: _containers.RepeatedCompositeFieldContainer[Lidar]
    Range: _containers.RepeatedCompositeFieldContainer[Range]
    Imu: _containers.RepeatedCompositeFieldContainer[IMU]
    Gps: GPS
    Compass: Compass
    Env: _bow_data_common_pb2.Environment
    Light: _containers.RepeatedCompositeFieldContainer[Light]
    def __init__(self, Lidar: _Optional[_Iterable[_Union[Lidar, _Mapping]]] = ..., Range: _Optional[_Iterable[_Union[Range, _Mapping]]] = ..., Imu: _Optional[_Iterable[_Union[IMU, _Mapping]]] = ..., Gps: _Optional[_Union[GPS, _Mapping]] = ..., Compass: _Optional[_Union[Compass, _Mapping]] = ..., Env: _Optional[_Union[_bow_data_common_pb2.Environment, _Mapping]] = ..., Light: _Optional[_Iterable[_Union[Light, _Mapping]]] = ...) -> None: ...
