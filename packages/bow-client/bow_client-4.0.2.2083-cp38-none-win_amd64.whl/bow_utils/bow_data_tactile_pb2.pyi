import bow_data_common_pb2 as _bow_data_common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TactileSamples(_message.Message):
    __slots__ = ["Samples"]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    Samples: _containers.RepeatedCompositeFieldContainer[TactileSample]
    def __init__(self, Samples: _Optional[_Iterable[_Union[TactileSample, _Mapping]]] = ...) -> None: ...

class TactileSample(_message.Message):
    __slots__ = ["Source", "LocationTag", "Data", "DataShape", "TactileType", "Compression", "ClassifiedTexture", "FloatData", "Transform", "NewDataFlag"]
    class CompressionFormatEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        RAW: _ClassVar[TactileSample.CompressionFormatEnum]
    RAW: TactileSample.CompressionFormatEnum
    class TactileTypeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        UNDEFINED: _ClassVar[TactileSample.TactileTypeEnum]
        PRESSURE: _ClassVar[TactileSample.TactileTypeEnum]
        VIBRATION: _ClassVar[TactileSample.TactileTypeEnum]
        TEXTURE: _ClassVar[TactileSample.TactileTypeEnum]
        FORCE_FEEDBACK: _ClassVar[TactileSample.TactileTypeEnum]
        TRIAXIAL: _ClassVar[TactileSample.TactileTypeEnum]
    UNDEFINED: TactileSample.TactileTypeEnum
    PRESSURE: TactileSample.TactileTypeEnum
    VIBRATION: TactileSample.TactileTypeEnum
    TEXTURE: TactileSample.TactileTypeEnum
    FORCE_FEEDBACK: TactileSample.TactileTypeEnum
    TRIAXIAL: TactileSample.TactileTypeEnum
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    LOCATIONTAG_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    DATASHAPE_FIELD_NUMBER: _ClassVar[int]
    TACTILETYPE_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_FIELD_NUMBER: _ClassVar[int]
    CLASSIFIEDTEXTURE_FIELD_NUMBER: _ClassVar[int]
    FLOATDATA_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    NEWDATAFLAG_FIELD_NUMBER: _ClassVar[int]
    Source: str
    LocationTag: _bow_data_common_pb2.RelativeToEnum
    Data: bytes
    DataShape: _containers.RepeatedScalarFieldContainer[int]
    TactileType: TactileSample.TactileTypeEnum
    Compression: TactileSample.CompressionFormatEnum
    ClassifiedTexture: str
    FloatData: _containers.RepeatedScalarFieldContainer[float]
    Transform: _bow_data_common_pb2.Transform
    NewDataFlag: bool
    def __init__(self, Source: _Optional[str] = ..., LocationTag: _Optional[_Union[_bow_data_common_pb2.RelativeToEnum, str]] = ..., Data: _Optional[bytes] = ..., DataShape: _Optional[_Iterable[int]] = ..., TactileType: _Optional[_Union[TactileSample.TactileTypeEnum, str]] = ..., Compression: _Optional[_Union[TactileSample.CompressionFormatEnum, str]] = ..., ClassifiedTexture: _Optional[str] = ..., FloatData: _Optional[_Iterable[float]] = ..., Transform: _Optional[_Union[_bow_data_common_pb2.Transform, _Mapping]] = ..., NewDataFlag: bool = ...) -> None: ...
