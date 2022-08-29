import json
import boto3
import logging
import os



client = boto3.client('ec2', region_name=os.environ.get('REGION'))

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def already_exists(getCidr,tgw_rt_id):
    logger.info("funct:: already_exists started... ")
    logger.info(getCidr)
    route_search = client.search_transit_gateway_routes(
        TransitGatewayRouteTableId=tgw_rt_id,
        Filters=[
            {
                'Name': 'route-search.exact-match',
                'Values': [
                    getCidr,
                ]
            },
        ],
        MaxResults=10,
        DryRun=False
    )
    if route_search['Routes']:
        logger.info(f"funct:: already_exists: route {getCidr} found in TGW RT {tgw_rt_id}")
        return True
    else:
        logger.info(f"funct:: already_exists: route {getCidr} NOT found in TGW RT {tgw_rt_id}")
        return False


def createRoute(getCidr, tgw_rt_id, tgw_attachment_id ):

    logger.info("funct:: createRoute: started... ")
    logger.info(getCidr)
    client.create_transit_gateway_route(
            DestinationCidrBlock=getCidr,
            TransitGatewayRouteTableId=tgw_rt_id,
            TransitGatewayAttachmentId=tgw_attachment_id,
            Blackhole=False,
            DryRun=False
        )

def removeRoute(getCidr, tgw_rt_id, tgw_attachment_id):
    logger.info("funct:: removeRoute: started... ")
    logger.info(getCidr)
    client.delete_transit_gateway_route(
                TransitGatewayRouteTableId=tgw_rt_id,
                DestinationCidrBlock=getCidr,
                DryRun=False
            )

def lambda_handler(event, context):
    # TODO implement
    json_str = json.dumps(event)
    dictObj = json.loads(json_str)
    # load the json to a string
    getCidr = dictObj.get('detail').get('routes')[0].get('destinationCidrBlock')
    getEventType = dictObj.get('detail').get('changeType')
    
    tgw_rt_id=os.environ.get('TGW_ROUTE_TABLE')
    tgw_attachment_id=os.environ.get('TGW_DESTINATION_ATTACHMENT_ID')
    
    if getCidr == "10.16.0.0/12":
        logger.info(f"exclude route 10.16.0.0/12")
        
    elif getEventType == "TGW-ROUTE-UNINSTALLED":
        logger.info(f"Adding route {getCidr} via {tgw_attachment_id} to TGW RT {tgw_rt_id}")
        if not already_exists(getCidr, tgw_rt_id):
            try:
                createRoute(getCidr, tgw_rt_id, tgw_attachment_id )
            except:
                logger.info(f"exception occured while adding a tgw route:")

    elif getEventType == "TGW-ROUTE-INSTALLED":

        if already_exists(getCidr, tgw_rt_id):
            try:
                logger.info(f"Removing route {getCidr} via {tgw_attachment_id} to TGW RT {tgw_rt_id}")
                removeRoute(getCidr, tgw_rt_id, tgw_attachment_id )
            except:
                logger.info(f"exception occured while adding a tgw route")
       
    else:
        print("Something went wrong!!!")
    
    
    logger.info("funct:: lambda_handler completed... ")
    

