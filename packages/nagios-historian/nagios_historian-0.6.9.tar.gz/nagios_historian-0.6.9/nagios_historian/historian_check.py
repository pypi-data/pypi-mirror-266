#
# documentation:
import requests
import json
import arrow
import urllib3

# Return codes expected by Nagios
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

#Disable warnings https
urllib3.disable_warnings()

class HistorianChecks:
    def __init__(self, url, access_token, tags):

        #initial
        self.url = url
        self.access_token = access_token
        self.tags = tags

    def get_tags_data(self):


        # Request JSON machines
        #headers = {'accept': 'application/json'}
        header_token = {"Authorization": "Bearer {}".format(self.access_token)}

        #Add tags to the URL
        url = '{}'.format(self.url) + '{}'.format(self.tags)
        print (url)

        # requests doc http://docs.python-requests.org/en/v0.10.7/user/quickstart/#custom-headers
        r = requests.get(url=url, headers=header_token, verify=False)

        return r.json(), r.status_code

    def check_tags_data(self):

        #Vars
        retrcode = OK
                #retrcodetag = OK

        #Create tuple with json and status code
        historian_tuple = self.get_tags_data()

        #Get data tags from tuple
        historian_data = historian_tuple[0]


        perfdata_list = ["STATUS_SAC_CYCLES_SEC", "STATUS_WS_ACTIVE_SESSIONS","STATUS_SAC_OVERRUNS","STATUS_WS_CLIENT_CONNECTIONS"]

        #tags_max_value = {'{}'.format(self.STATUS_SAC_OVERRUNS): 10}

        #tags_warn_value = {'{}'.format(self.STATUS_SAC_OVERRUNS): 5}

        msgdata = ''
        msgerror = ''
        retrperfdata = ''
        retrmsg = ''


        #Validate Data
        for i, val in enumerate(historian_data['Data']):
            retrcodetag = OK
            ErrorCode = val.get('ErrorCode', 1)
            TagName = val.get('TagName', '')
            Samples = val.get('Samples', [])
            SamplesN = 0

            msgdata += 'Tag: {}, ErrorCode: {} \n'.format(val.get('TagName'), ErrorCode)

            #Validate ErrorCode (0 = Ok)
            if ErrorCode != 0:
                retrcode = CRITICAL
                retrcodetag = CRITICAL

            #Validate Samples
            for x, vsample in enumerate(Samples):

                #Def Vars
                SamplesN += 1
                Quality = vsample.get('Quality', 0)
                TimeStamp = vsample.get('TimeStamp', '')
                Value = vsample.get('Value')
                actual_time = arrow.get()

                msgdata += 'SampleN: {}, Quality: {}, TimeStamp: {}, Value: {} \n'.format(SamplesN, Quality, TimeStamp, Value)

                if TagName in perfdata_list:
                    retrperfdata += '{}={};{};{};; '.format(TagName, Value, tags_warn_value.get(TagName, ''), tags_max_value.get(TagName, ''))

                #Validate Quality (0 – Bad,  1 – Uncertain, 2 – NA , 3 – Good)
                if Quality != 3:
                    retrcode = CRITICAL
                    retrcodetag = CRITICAL

                #Validate Value (0 = Ok)
                if not TagName in ["STATUS_SAC_STATUS" , "STATUS_WS_SERVICE", "STATUS_SAC_CYCLES_SEC" , "STATUS_SAC_OVERRUNS", "STATUS_WS_ACTIVE_SESSIONS" ,"STATUS_WS_CLIENT_CONNECTIONS" , "STATUS_WS_HOST_CONNECTIONS" , "STATUS_WS_MAXIMUM_SESSIONS", "STATUS_LAST_UPDATE"]:
                    if Value != '0':
                        retrcode = CRITICAL
                        retrcodetag = CRITICAL

                #STATUS_SAC_STATUS / STATUS_WS_SERVICE - ( 0=STOP | 1=RUN )
                if TagName in ["STATUS_SAC_STATUS" , "STATUS_WS_SERVICE"] and Value != '1':
                    retrcode = CRITICAL
                    retrcodetag = CRITICAL

                #STATUS_LAST_UPDATE (LAST UPDATE > ACTUAL TIME -1 MINUTE)
                if TagName in ["STATUS_LAST_UPDATE"] and Value !='0.0000':
                    last_update_time = arrow.get(Value , 'DD/MM/YYYY HH:mm:ss')
                    actual = actual_time.shift(hours=-3, minutes=-5)
                    if not last_update_time > actual:
                        retrcode = CRITICAL
                        retrcodetag = CRITICAL

                #STATUS_SAC_OVERRUNS (Value < 10)
                if TagName in ["STATUS_SAC_OVERRUNS"]:
                    if Value > '10':
                        retrcode = CRITICAL
                        retrcodetag = CRITICAL

                #STATUS_SAC_CYCLES_SEC (Values = 20)
                if TagName in ["STATUS_SAC_CYCLES_SEC"]:
                    if Value != '20':
                        retrcode = CRITICAL
                        retrcodetag = CRITICAL


            if retrcodetag != 0:
                msgerror += 'ERROR: Tagname: {} \n'.format(TagName)

        msgerror += msgdata

        return retrcode, msgerror

