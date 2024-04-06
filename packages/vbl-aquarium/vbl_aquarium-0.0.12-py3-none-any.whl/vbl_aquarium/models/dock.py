from vbl_aquarium.utils.vbl_base_model import VBLBaseModel

# File IO


# Models for sending data to dock server
class BucketModel(VBLBaseModel):
    token: str
    password: str


class UploadModel(VBLBaseModel):
    data: str
    password: str

class DownloadModel(VBLBaseModel):
    password: str

# Models for sending save/load messages
class SaveModel(VBLBaseModel):
    filename: str = ''
    bucket: str = ''
    password: str = ''


class LoadModel(VBLBaseModel):
    filename: str = ''
    bucket: str = ''
    password: str = ''
