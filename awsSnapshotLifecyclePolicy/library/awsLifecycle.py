#! /bin

import requests
import json
import datetime
import boto3
from ansible.module_utils.basic import AnsibleModule

class AwsLifecycle:

    def __init__(self):
        ##Sets the fields that are imported from ansible
        fields = {
            "RoleArn":{"required":True,"type":"str"},
            "name":{"required":True,"type":"str"},
            "tagKey":{"required":False,"type":"str","default":"environment"},
            "tagValue":{"required":False,"type":"str","default":"prod"},
            "retention":{"required": True,"type":"int"},
            "region": {"required": True,"type":"str"},
            "aws_key": {"required": True,"type":"str"},
            "aws_secret": {"required": True,"type":"str"}
        }

        ##Set the variables to be used in the function
        self.module = AnsibleModule(argument_spec=fields)
        self.RoleArn = self.module.params.get("RoleArn")
        self.Description = self.module.params.get("name") + '-daily-backup'
        self.key = self.module.params.get("tagKey")
        self.value = self.module.params.get("tagValue")
        self.retentionPeriod = self.module.params.get("retention")
        self.region = self.module.params.get("region")
        self.aws_key = self.module.params.get("aws_key")
        self.aws_secret = self.module.params.get("aws_secret")

        ##Define the response for Ansible, this is required
        self.json_output = {
            'policy name': self.Description,
            'changed': False
        }

        ##Set credentials to use when connecting to AWS dlm API
        self.client = boto3.client('dlm',
            region_name=self.region,
            aws_access_key_id=self.aws_key,
            aws_secret_access_key=self.aws_secret)

        if self.checkSnapshotPolicy():
            self.json_output['Polciy Exists'] = True
        else:
            self.createSnapshotLifecycle()

    def checkSnapshotPolicy(self):
        policyList = self.client.get_lifecycle_policies()
        for policy in policyList['Policies']:
            if self.Description == policy['Description']:
                return(True)
        return(False)


    def createSnapshotLifecycle(self):
        try:
            response = self.client.create_lifecycle_policy(
                ExecutionRoleArn=self.RoleArn,
                Description=self.Description,
                State='ENABLED',
                Tags={
                    self.key: self.value
                },
                PolicyDetails={
                    'PolicyType': 'EBS_SNAPSHOT_MANAGEMENT',
                    'ResourceTypes': ['INSTANCE'],
                    'TargetTags': [
                        {
                            'Key': self.key,
                            'Value': self.value
                        }
                    ],
                    'Schedules': [
                        {
                            'Name': 'Default Schedule',
                            'CopyTags': True,
                            'VariableTags': [
                                {
                                    'Key': 'instance-id',
                                    'Value': '$(instance-id)'
                                },
                                {
                                    'Key': 'timestamp',
                                    'Value': '$(timestamp)'
                                }
                            ],
                            'CreateRule': {
                                'Interval': 24,
                                'IntervalUnit': 'HOURS',
                            },
                            'RetainRule': {
                                'Count': self.retentionPeriod,
                            }
                        }
                    ],
                    'Parameters': {
                        'ExcludeBootVolume': False
                    }
                }
            )

            self.json_output['Policy Created'] = True
            self.json_output['changed'] = True

        except:
            self.json_output['API call to AWS failed'] = True

        self.module.exit_json(**self.json_output)


def main():
    lifecyclePolicy = AwsLifecycle()

if __name__ == '__main__':
    main()
