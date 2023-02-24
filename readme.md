# Amazon VPC IP Address Manager

**vpc-ipam-delegation.yaml:** This CloudFormation Template configures a Lambda Function that leverages parameters parsed into it via CloudFormation Parameter through the use of Environment Variables.  Specifically the Lambda Function does a number of things:
* Determines whether a Delegated Administrative Account exists for Amazon VPC IP Address Manager.  If it doesn't then it enables Delegated Administration to the AWS Account ID that is parsed in.
**vpc-ipam-pools.yaml:** This CloudFormation Template deploys Amazon VPC IP Address Manager in a single region that supports 2 AWS Regions (which can be easily modified to support additional regions).  It then shares the IPAM Pools for those specific regions to the entire AWS Organization.  This provides you with a flexible way of maintaining and IP Database of Assignments unique to both AWS Regions and to SDLC environments within each of those regions, helping to mitigate the risk of overlapping IP Address spaces being utilised.

## Pre-Requisites and Installation

### Pre-Requisites

There is an overarching assumption that you already have [Customisation for Control Tower](https://aws.amazon.com/solutions/implementations/customizations-for-aws-control-tower/) deployed within your Control Tower Environment.

1.  Clone the GitHub Repo to your local device.

### Installation

1.  Copy the CloudFormation Template `vpc-ipam-delegation.yaml` should be added to the `/templates` folder for use with Customisations for Control Tower.
2.  Copy the CloudFormation Template `vpc-ipam-pools.yaml` should be added to the `/templates` folder for use with Customisations for Control Tower.
3.  Copy the CloudFormation Parameters `vpc-ipam-delegation.json` should be added to `/parameters` folder for use with Customisations for Control Tower.
4.  Copy the CloudFormation Parameters `vpc-ipam-pools.json` should be added to `/parameters` folder for use with Customisations for Control Tower.
5.  Update the CloudFormation Parameters `vpc-ipam-delegation.json` with the required details:
    * **pLambdaLogGroupRetention:** This is used to configure the CloudWatch Log Group retention that the AWS Lambda Function will write to.  This must be within one of the following values: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653.
    * **pNetworkAccountId:** This is the AWS Account ID of the Account that you wish to configure as the delegated admin for Amazon VPC IP Address Manager.  It's recommended to use the Network Account.
    * **pTagEnvironment:** This is the name of the SDLC environment that you're deploying this solution into.

    The above values should be configured within the `vpc-ipam-delegation.json`:

    ```json
    [
        {
            "ParameterKey": "pLambdaLogGroupRetention",
            "ParameterValue": ""
        },
        {
            "ParameterKey": "pNetworkAccountId",
            "ParameterValue": ""
        },
        {
            "ParameterKey": "pTagEnvironment",
            "ParameterValue": ""
        }
    ]
    ```

6.  Update the CloudFormation Parameters `vpc-ipam-pools.yaml` with the required details:
    * **pOrganizationId:** This is used for the purpose of sharing the VPC IPAM Pools to the entire AWS Organization. This can be obtained from with AWS Organisations.
    * **pManagementAccountId:** This is the AWS Account ID of the Management Account that AWS Organizations is deployed within so as to restrict the scope when utilising AWS Resource Access Manager.
    * **pOperatingRegionList:** This is a comma seperated list of the AWS Regions that you wish to deploy this Amazon VPC IPAM  within.  This solution is currently written to support 2 regions but can be easily be expanded.
    * **pMainPoolCidrIpv4List:** This is a comma seperated list of the IP CIDR ranges that you wish to use within the different regions.  This solution is currently written to support 2 regions but can be easily be expanded, therefore this input is expecting 2 seperate IP CIDR Ranges.
    * **pProdPoolCidrIpv4List:** This is a comma seperated list of the IP CIDR ranges that you wish to use within the different regions specifically for an SDLC environment. In this template we are supporting 3 different SDLC environments Production, UAT and Development and 2 AWS Regions therefore this would be expecting 2 IP CIDR Ranges to be used for Production but in 2 different AWS Regions.
    * **pUatPoolCidrIpv4List:** This is a comma seperated list of the IP CIDR ranges that you wish to use within the different regions specifically for an SDLC environment. In this template we are supporting 3 different SDLC environments Production, UAT and Development and 2 AWS Regions therefore this would be expecting 2 IP CIDR Ranges to be used for UAT but in 2 different AWS Regions.
    * **pDevPoolCidrIpv4List:** This is a comma seperated list of the IP CIDR ranges that you wish to use within the different regions specifically for an SDLC environment. In this template we are supporting 3 different SDLC environments Production, UAT and Development and 2 AWS Regions therefore this would be expecting 2 IP CIDR Ranges to be used for Development but in 2 different AWS Regions.
    * **pTagEnvironment:** This is the name of the SDLC environment that you're deploying this solution into.

    The above values should be configured within the `vpc-ipam-pools.yaml`:

    ```json
    [
        {
            "ParameterKey": "pOrganizationId",
            "ParameterValue": ""
        },
        {
            "ParameterKey": "pManagementAccountId",
            "ParameterValue": ""
        },
        {
            "ParameterKey": "pOperatingRegionList",
            "ParameterValue": ""
        },
        {
            "ParameterKey": "pMainPoolCidrIpv4List",
            "ParameterValue": ""
        },
        {
            "ParameterKey": "pProdPoolCidrIpv4List",
            "ParameterValue": ""
        },
        {
            "ParameterKey": "pUatPoolCidrIpv4List",
            "ParameterValue": ""
        },
        {
            "ParameterKey": "pDevPoolCidrIpv4List",
            "ParameterValue": ""
        },
        {
            "ParameterKey": "pTagEnvironment",
            "ParameterValue": ""
        }
    ]
    ```

7.  Update the `manifest.yaml` and configure the `deployment_targets` and `regions` accordingly based on your needs. The deployment target should be the AWS Control Tower Management Account since the Lambda Function that is invoked uses API Calls that are run are only available to the Master Account whilst the region should be configured to the Control Tower home region.

    ```yaml
    - name: Enable-VPC-IPAM-Delegated-Admin
      description: "CloudFormation Template to Enable Delegated Administration of VPC IPAM"
      resource_file: templates/vpc-ipam-delegation.yaml
      parameter_file: parameters/vpc-ipam-delegation.json
      deploy_method: stack_set
      deployment_targets:
        accounts:
          - # Either the 12-digit Account ID or the Logical Name for the Control Tower Management Account
      regions:
        - # AWS Region that is configured as the Home Region within Control Tower
    - name: Configure-VPC-IPAM-Pools
      description: "CloudFormation Template to Configure VPC IPAM Pools"
      resource_file: templates/vpc-ipam-pools.yaml
      parameter_file: parameters/vpc-ipam-pools.json
      deploy_method: stack_set
      deployment_targets:
        accounts:
          - # Either the 12-digit Account ID or the Logical Name for the Control Tower Management Account
      regions:
        - # AWS Region that is configured as the Home Region within Control Tower
    ```