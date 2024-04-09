from typing import List, Optional, Union
from functools import wraps
import boto3
from pydantic import BaseModel, computed_field
from strenum import StrEnum


def _singleton(cls):
    instances = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


class AWSSecretTypeEnum(StrEnum):
    _ssm = 'ssm'
    _secretsmanager = 'secretsmanager'


class AWSRegionEnum(StrEnum):
    _af_south_1 = 'af-south-1'
    _ap_east_1 = 'ap-east-1'
    _ap_northeast_1 = 'ap-northeast-1'
    _ap_northeast_2 = 'ap-northeast-2'
    _ap_northeast_3 = 'ap-northeast-3'
    _ap_south_1 = 'ap-south-1'
    _ap_south_2 = 'ap-south-2'
    _ap_southeast_1 = 'ap-southeast-1'
    _ap_southeast_2 = 'ap-southeast-2'
    _ap_southeast_3 = 'ap-southeast-3'
    _ap_southeast_4 = 'ap-southeast-4'
    _ca_central_1 = 'ca-central-1'
    _eu_central_1 = 'eu-central-1'
    _eu_central_2 = 'eu-central-2'
    _eu_north_1 = 'eu-north-1'
    _eu_south_1 = 'eu-south-1'
    _eu_south_2 = 'eu-south-2'
    _eu_west_1 = 'eu-west-1'
    _eu_west_2 = 'eu-west-2'
    _eu_west_3 = 'eu-west-3'
    _me_central_1 = 'me-central-1'
    _me_south_1 = 'me-south-1'
    _sa_east_1 = 'sa-east-1'
    _us_east_1 = 'us-east-1'
    _us_east_2 = 'us-east-2'
    _us_west_1 = 'us-west-1'
    _us_west_2 = 'us-west-2'


class AWSSecret(BaseModel):
    type: AWSSecretTypeEnum
    path: str
    region: Optional[AWSRegionEnum] = AWSRegionEnum._eu_central_1

    def _get_ssm_parameter_from_aws(self) -> Union[str, List[str]]:
        ssm_parameter = get_ssm_client(self.region).get_parameter(
            Name=self.path,
            WithDecryption=True,
        )['Parameter']
        if ssm_parameter.get('Type') == 'StringList':
            return ssm_parameter['Value'].split(',')
        else:
            return ssm_parameter['Value']

    def _get_secrets_manager_secret_from_aws(self):
        return get_secretsmanager_client(self.region).get_secret_value(
            SecretId=self.path
        )['SecretString']

    @computed_field
    @property
    def value(
        self,
    ) -> str:
        if self.type == AWSSecretTypeEnum._ssm:
            return self._get_ssm_parameter_from_aws()
        if self.type == AWSSecretTypeEnum._secretsmanager:
            return self._get_secrets_manager_secret_from_aws()


@_singleton
def get_ssm_client(region: AWSRegionEnum):
    session = boto3.Session(region_name=region)
    return session.client('ssm')


@_singleton
def get_secretsmanager_client(region: AWSRegionEnum):
    session = boto3.Session(region_name=region)
    return session.client('secretsmanager')
