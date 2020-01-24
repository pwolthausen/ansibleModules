import requests
import json
import datetime
from ansible.module_utils.basic import AnsibleModule

API_URL = 'https://api.datadoghq.com/api/v1/synthetics/tests'

class Ddsynthetics:

    def __init__(self):
        self.app_url = API_URL

        fields = {
            "name":{"required":False,"type":"str"},
            "check":{"required":True,"type":"dict", "options":{
              "url":{"required":True,"type":"str"},
              "content_match": {"required":False,"type":"str"},
              "header": {"required":False,"type":"str"},
              "headerType": {"required":False,"type":"str"}
            }},
            "dd_api_key":{"required":True,"type":"str"},
            "dd_app_key":{"required":True,"type":"str"},
            "prefix":{"required":True,"type":"str"}
        }

        self.module = AnsibleModule(argument_spec=fields)
        self.checkDetails = self.module.params.get("check")
        self.api_key = self.module.params.get("dd_api_key")
        self.app_key = self.module.params.get("dd_app_key")
        self.client = self.module.params.get("prefix")
        self.target_url = self.checkDetails['url']
        try:
            self.testName = self.module.params.get("name")
        except:
            self.testName = '[' + self.client + '] Test on ' + self.target_url[:24]

        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'DD-API-KEY': self.api_key,
            'DD-APPLICATION-KEY': self.app_key
        })

        self.json_output = {
            'check name': self.testName,
            'check removed': False,
            'check created': False,
            'changed': False
        }

    def get_synthetics(self):
        list = self.session.get(self.app_url)
        return list.json()

    def delete_synthetics(self,pid):
        delete_list = {'public_ids': [pid]}
        delete_body = json.dumps(delete_list)
        deleteRequest = self.session.post(self.app_url + '/delete', data = delete_body)
        if deleteRequest.status_code == 200:
            self.json_output['check removed'] = True

    def check_synthetics(self):
        current_checks = self.get_synthetics()
        for synthetic_test in current_checks['tests']:
            if self.testName in synthetic_test['name']:
                self.delete_synthetics(synthetic_test['public_id'])

        self.create_synthetic()

    def ddAssertions(self):
        assertionsList = [{'operator': 'is', 'type': 'statusCode', 'target': 200},{'operator': 'lessThan', 'target': 10000, 'type': 'responseTime'}]
        if 'content_match' in self.checkDetails:
            content = {'type': 'body', 'operator': 'contains', 'target': self.checkDetails['content_match']}
            assertionsList.append(content)

        if 'header' in self.checkDetails:
            headerAssert = {'type': 'header', 'operator': 'contains', 'property': self.checkDetails['headerType'], 'target': self.checkDetails['header']}
            assertionsList.append(headerAssert)

        return(assertionsList)

##Currently under utlisized, will elaborate if notiications are deemed optional
    def ddMessage():
        ddmessage = self.target_url + ' is down @Pagerduty'

        return(ddmessage)

    def create_synthetic(self):

        assertions = self.ddAssertions()
        synthRequest = {'method': 'GET', 'url': 'https://' + self.target_url}
        synthOptions = {'tick_every': 300,'min_location_failed': 3, 'min_failure_duration': 180, 'follow_redirects': True,'retry':{'count': 2, 'interval': 60000}}
        locations = ['aws:sa-east-1','aws:us-east-2','aws:us-west-1','aws:us-west-2','aws:ca-central-1']
        message = self.ddMessage()
        ddtags = []

        data = {'config':{'assertions': assertions,'request': synthRequest}, 'options': synthOptions, 'locations': locations, 'name': self.testName, 'message': message, 'type': 'api', 'tags': ddtags}
        body = json.dumps(data)

        post = self.session.post(self.app_url, data = body)
        if post.status_code == 200:
            self.json_output['check created'] = True
            self.json_output['changed'] = True

        self.module.exit_json(**self.json_output)

def main():
    synthCheck = Ddsynthetics()
    synthCheck.check_synthetics()


if __name__ == '__main__':
    main()
