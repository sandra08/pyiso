import requests
import copy
from datetime import timedelta
from dateutil.parser import parse as dateutil_parse
import pytz

class ISONEClient:
    def __init__(self):
        self.ba_name = 'ISNE'
        
        self.base_url = 'http://isoexpress.iso-ne.com/ws/wsclient'
        self.base_payload = {'_ns0_requestType':'url'}
        
        self.fuels = {
            'Coal': 'coal',
            'Hydro': 'hydro',
            'Natural Gas': 'natgas',
            'Nuclear': 'nuclear',
            'Oil': 'oil',
            'Solar': 'solar',
            'Wind': 'wind',
            'Wood': 'renewable',
            'Refuse': 'renewable',
            'Landfill Gas': 'renewable',
        }
        

    def get_generation(self, latest=False, start_at=False, end_at=False, **kwargs):
        # process args
        request_urls = []
        if latest:
            request_urls.append('current')

        elif start_at and end_at:
            this_date = start_at.date()
            while this_date <= end_at.date():
                request_urls.append(this_date.strftime('day/%Y%m%H'))
                this_date += timedelta(days=1)
        else:
            raise ValueError('Either latest must be True, or start_at and end_at must both be provided.')
            
        # set up storage
        raw_data = []
        parsed_data = []

        # collect raw data
        for request_url in request_urls:
            # set up request
            payload = copy.deepcopy(self.base_payload)
            payload.update({'_ns0_requestUrl':'/genfuelmix/%s' % request_url})
            print payload
            
            # carry out request
            response = requests.post(self.base_url, data=payload).json()
            print response[0]['data']
            raw_data += response[0]['data']['GenFuelMixes']['GenFuelMix']

        # parse data
        for raw_dp in raw_data:
            # set up storage
            parsed_dp = {}
            
            # add values
            parsed_dp['timestamp'] = dateutil_parse(raw_dp['BeginDate']).astimezone(pytz.utc)
            parsed_dp['gen_MW'] = raw_dp['GenMw']
            parsed_dp['fuel_name'] = self.fuels[raw_dp['FuelCategory']]
            parsed_dp['ba_name'] = 'ISNE'
            
            # add to full storage
            parsed_data.append(parsed_dp)
            
        return parsed_data
