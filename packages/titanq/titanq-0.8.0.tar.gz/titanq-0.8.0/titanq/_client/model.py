from datetime import datetime
from pydantic import BaseModel, Field, field_serializer, SecretStr
from typing import List, Optional, Union


#########################
##    solve models     ##
#########################
class AwsStorage(BaseModel):
    """
    S3 backend storage
    """
    bucket_name: str
    access_key_id: SecretStr
    secret_access_key: SecretStr

    @field_serializer('access_key_id', 'secret_access_key', when_used='json')
    def dump_secret(self, v):
        return v.get_secret_value()

class Manifest(BaseModel):
    """
    The manifest object of the solver request
    """
    has_set_partitioning_constraint: bool
    has_cardinality_constraint: bool
    has_equality_constraint: bool
    has_inequality_constraint: bool

class S3Input(BaseModel):
    """
    Input object of the solve request with s3
    """
    s3: AwsStorage
    bias_file_name: str
    weights_file_name: str
    constraint_bounds_file_name: Optional[str]
    constraint_weights_file_name: Optional[str]
    variable_bounds_file_name: Optional[str]
    manifest: Optional[Manifest]


class UrlInput(BaseModel):
    """
    Input object of the solve request with url
    """
    # always true, the user does not have to set this value
    file_name_is_url: bool = Field(default=True, frozen=True)
    bias_file_name: str
    weights_file_name: str
    constraint_bounds_file_name: Optional[str]
    constraint_weights_file_name: Optional[str]
    variable_bounds_file_name: Optional[str]
    manifest: Optional[Manifest]


class S3Output(BaseModel):
    """
    Output object of the solve request with s3
    """
    result_archive_file_name: str
    s3: AwsStorage

class UrlOutput(BaseModel):
    """
    Output object of the solve request with url
    """
    # always true, the user does not have to set this value
    file_name_is_url: bool = Field(default=True, frozen=True)
    result_archive_file_name: str


class Parameters(BaseModel):
    """
    Tuning parameters used by the solver
    """
    beta: List[float]
    coupling_mult: float
    timeout_in_secs: float
    num_chains: int
    num_engines: int
    variable_types: str
    normalized: bool


class SolveRequest(BaseModel):
    """
    The actual solve request object send to the backend
    """
    input: Union[S3Input, UrlInput]
    output: Union[S3Output, UrlOutput]
    parameters: Parameters


class SolveResponse(BaseModel):
    """
    The response object returned by the backend on solve request
    """
    computation_id: str
    status: str
    message: str


#########################
##   credits models    ##
#########################
class CreditsResponse(BaseModel):
    """
    The response object returned by the backend on credits request
    """
    remaining_credits: int
    expiration_date: datetime



#########################
## temp_storage models ##
#########################
class FileUrls(BaseModel):
    """
    Object always containing a pair of a download and an upload url
    """
    download: str
    upload: str


class TempStorageInput(BaseModel):
    """
    Object containing input files for temporary storage object
    """
    weights_file: FileUrls = Field(alias="weights.npy")
    bias_file: FileUrls = Field(alias="bias.npy")
    constraint_weights_file: FileUrls = Field(alias="constraint_weights.npy")
    constraint_bounds_file: FileUrls = Field(alias="constraint_bounds.npy")
    variable_bounds_file: FileUrls = Field(alias="variable_bounds.npy")


class TempStorageOutput(BaseModel):
    """"
    Object containing output files for temporary storage object
    """
    result_archive_file: FileUrls = Field(alias="result.zip")


class TempStorageResponse(BaseModel):
    """
    The response object returned by the backend on temporary storage response
    """
    input: TempStorageInput
    output: TempStorageOutput