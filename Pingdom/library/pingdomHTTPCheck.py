
import json
import pingdom

from urllib.parse import urlparse
from ansible.module_utils.basic import AnsibleModule


class pingdomHTTPCheck:

    def __init__(self):
        ##Sets the fields that are imported from ansible
        fields = {
            "check":{"required":True,"type":"dict", "options":{
              "checkName": {"required":True,"type":"str"},
              "check_url": {"required":True,"type":"str"},
              "content_match": {"required":False,"type":"str"},
              "header_type": {"required":False,"type":"str","choices":["Accept","Accept-Charset","Accept-Encoding","aacept-language","Cache-Control","Connection","Cookie","Keep-Alive","Referer"]},
              "header": {"required":False,"type":"str"},
              "check_interval": {"required":True,"type":"int","choices":[1,5,15,30],"default":1},
              "notification_delay": {"required":False,"type":"int","default":3}
              }},
            "user": {"required": True,"type":"str"},
            "password": {"required":True,"type":"str"},
            "api_key": {"required":True,"type":"str"},
            "customer": {"required":False,"type":"str"},
            "integrations": {"required":False,"type":"str","choices":["85002"]},
            "users": {"required":False,"type":"list","elements":"str"}
        }

        ##Set the variables to be used in the function
        self.module = AnsibleModule(argument_spec=fields)
        self.checkDetails = self.module.params.get("check")
        self.userName = self.module.params.get("user")
        self.password = self.module.params.get("password")
        self.api_key = self.module.params.get("api_key")
        try:
            self.customerName = self.module.params.get("customer")
        try:
            self.integration = self.module.params.get("integrations")
        try:
            self.users = self.module.params.get("users")
        self.checkName = '[' + self.customerName.upper() + '] ' + self.checkDetails['name']

        connection = pingdom.PingdomConnection(self.userName,self.password,self.api_key)

        self.json_output = {
            "check name": self.checkName,
            "check exists": False,
            "check updated": False,
            "check created": False,
            "changed": False
        }
    ##Does the check currently exist
    def checkExists(self):
        self.configured_checks = connection.get_all_checks()
        for self.configured_check in self.configured_checks:
            if self.configured_check.name == self.checkName:
                self.json_output['check exists'] = True
                return(True)

    ##Has the existing check been changed
    def checkStatusChange(self):

    ##Update existing check
    def updateCheck(self):

    ##Create new check
    def createCheck(self):


    def pingdomCheck(self):
        if self.checkExists():
            if self.checkStatusChange():
                self.updateCheck()
        else:
            self.createCheck()
