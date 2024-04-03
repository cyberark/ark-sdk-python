from enum import Enum


class ArkRegion(str, Enum):
    Ohio = 'us-east-2'
    NorthVirginia = 'us-east-1'
    NorthCalifornia = 'us-west-1'
    Oregon = 'us-west-2'
    CapeTown = 'af-south-1'
    HongKong = 'ap-east-1'
    Mumbai = 'ap-south-1'
    OsakaLocal = 'ap-northeast-3'
    Seoul = 'ap-northeast-2'
    Singapore = 'ap-southeast-1'
    Sydney = 'ap-southeast-2'
    Tokyo = 'ap-northeast-1'
    CanadaCentral = 'ca-central-1'
    Beijing = 'cn-north-1'
    Ningxia = 'cn-northwest-1'
    Frankfurt = 'eu-central-1'
    Ireland = 'eu-west-1'
    London = 'eu-west-2'
    Milan = 'eu-south-1'
    Paris = 'eu-west-3'
    Stockholm = 'eu-north-1'
    Bahrain = 'me-south-1'
    SaoPaulo = 'sa-east-1'
    USEast = 'us-gov-east-1'
    USWest = 'us-gov-west-1'
    USEastPerf = 'us-east-perf'
    USEastPod = 'us-east-pod'
    Jakarta = 'ap-southeast-3'
    Indonesia = 'ap-southeast-3'
    Melbourne = 'ap-southeast-4'
    UAE = 'me-central-1'


regions_full_names = {
    ArkRegion.Ohio: 'us-east-2 (Ohio)',
    ArkRegion.NorthVirginia: 'us-east-1 (N. Virginia)',
    ArkRegion.NorthCalifornia: 'us-west-1 (N. California)',
    ArkRegion.Oregon: 'us-west-2 (Oregon)',
    ArkRegion.CapeTown: 'af-south-1 (Cape Town)',
    ArkRegion.HongKong: 'ap-east-1 (Hong Kong)',
    ArkRegion.Mumbai: 'ap-south-1 (Mumbai)',
    ArkRegion.OsakaLocal: 'ap-northeast-3 (Osaka-Local)',
    ArkRegion.Seoul: 'ap-northeast-2 (Seoul)',
    ArkRegion.Singapore: 'ap-southeast-1 (Singapore)',
    ArkRegion.Sydney: 'ap-southeast-2 (Sydney)',
    ArkRegion.Tokyo: 'ap-northeast-1 (Tokyo)',
    ArkRegion.CanadaCentral: 'ca-central-1 (Central)',
    ArkRegion.Beijing: 'cn-north-1 (Beijing)',
    ArkRegion.Ningxia: 'cn-northwest-1 (Ningxia)',
    ArkRegion.Frankfurt: 'eu-central-1 (Frankfurt)',
    ArkRegion.Ireland: 'eu-west-1 (Ireland)',
    ArkRegion.London: 'eu-west-2 (London)',
    ArkRegion.Milan: 'eu-south-1 (Milan)',
    ArkRegion.Paris: 'eu-west-3 (Paris)',
    ArkRegion.Stockholm: 'eu-north-1 (Stockholm)',
    ArkRegion.Bahrain: 'me-south-1 (Bahrain)',
    ArkRegion.SaoPaulo: 'sa-east-1 (São Paulo)',
    ArkRegion.USEast: 'us-gov-east-1 (US-East)',
    ArkRegion.USWest: 'us-gov-west-1 (US-West)',
    ArkRegion.USEastPerf: 'us-east-perf (US-East-Perf)',
    ArkRegion.USEastPod: 'us-east-pod (US-East-Pod)',
    ArkRegion.Jakarta: 'ap-southeast-3 (Jakarta)',
    ArkRegion.Indonesia: 'ap-southeast-3 (Indonesia)',
    ArkRegion.Melbourne: 'ap-southeast-4 (Melbourne)',
    ArkRegion.UAE: 'me-central-1 (UAE)',
}

platform_region_dict = {
    'America East': 'us-east-1',
    'America West': 'us-west-1',
    'Oregon': 'us-west-2',
    'Canada': 'ca-central-1',
    'South America': 'sa-east-1',
    'UK': 'eu-west-2',
    'Ireland': 'eu-west-1',
    'Germany': 'eu-central-1',
    'France': 'eu-west-3',
    'Sweden': 'eu-north-1',
    'Italy': 'eu-south-1',
    'Middle East': 'me-south-1',
    'Africa': 'af-south-1',
    'China': 'cn-north-1',
    'Hong-Kong': 'ap-east-1',
    'Japan': 'ap-northeast-1',
    'Singapore': 'ap-southeast-1',
    'South Korea': 'ap-northeast-2',
    'India': 'ap-south-1',
    'Australia': 'ap-southeast-2',
    'GovCloud (US East)': 'us-gov-east-1',
    'GovCloud (US West)': 'us-gov-east-1',
    'US-East-Perf': 'us-east-perf',
    'us-east-perf': 'US-East-Perf',
    'US-East-Pod': 'us-east-pod',
    'us-east-pod': 'US-East-Pod',
    'ISP-PcloudPerf-US East': 'isp-pcloudperf-us east',
    'Jakarta': 'ap-southeast-3',
    'Indonesia': 'ap-southeast-3',
    'Melbourne': 'ap-southeast-4',
    'UAE': 'me-central-1',
}


def region_to_platform_region(region: str) -> str:
    return list(platform_region_dict.keys())[list(platform_region_dict.values()).index(region)]
