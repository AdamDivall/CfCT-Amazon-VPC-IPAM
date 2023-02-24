import boto3
import cfnresponse
from botocore.exceptions import ClientError

ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
    if (event['RequestType'] == 'Create' or event['RequestType'] == 'Update'):
        try:
            response = ec2_client.enable_ipam_organization_admin_account(
                DryRun = False, 
                DelegatedAdminAccountId = (event['ResourceProperties']['accountid'])
            )
            print(response)
            if response['Success'] == True:
                print(f"IPAM configured")
                cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
        except ClientError as e: 
            print(e.response['Error']['Message']) 
            cfnresponse.send(event, context, cfnresponse.FAILED, e.response)
    elif (event['RequestType'] == 'Delete'):
        try:
            response = ec2_client.disable_ipam_organization_admin_account(
                DryRun = False, 
                DelegatedAdminAccountId = (event['ResourceProperties']['accountid'])
            )
            print(response)
            if response['Success'] == True:
                print("IPAM Disabled")
                cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
        except ClientError as e: 
            print(e.response['Error']['Message']) 
            cfnresponse.send(event, context, cfnresponse.FAILED, e.response)
    else:
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {})