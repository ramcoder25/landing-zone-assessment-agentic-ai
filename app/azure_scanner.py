import asyncio
import logging
from azure.identity.aio import DefaultAzureCredential
from azure.mgmt.resource.subscriptions.aio import SubscriptionClient
from azure.mgmt.network.aio import NetworkManagementClient
from azure.mgmt.compute.aio import ComputeManagementClient
from azure.mgmt.storage.aio import StorageManagementClient
from azure.core.exceptions import HttpResponseError

async def get_subscriptions(credential: DefaultAzureCredential):
    subs_data = []
    try:
        subscription_client = SubscriptionClient(credential)
        async for sub in subscription_client.subscriptions.list():
            subs_data.append({'id': sub.id, 'subscription_id': sub.subscription_id, 'display_name': sub.display_name})
    except Exception as e:
        logging.error(f'Could not list subscriptions: {e}')
    return subs_data

async def scan_subscription_resources(sub, credential):
    sub_id = sub['subscription_id']
    logging.info(f"Scanning subscription: {sub['display_name']} ({sub_id})")
    resources = []
    try:
        network_client = NetworkManagementClient(credential, sub_id)
        compute_client = ComputeManagementClient(credential, sub_id)
        storage_client = StorageManagementClient(credential, sub_id)
        tasks = [network_client.virtual_networks.list_all(), network_client.network_security_groups.list_all(), network_client.route_tables.list_all(), compute_client.virtual_machines.list_all(), storage_client.storage_accounts.list()]
        results = await asyncio.gather(*[asyncio.create_task(t) for t in tasks], return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                logging.warning(f'An API call failed in {sub_id}: {result}')
                continue
            async for item in result:
                resources.append(item.as_dict())
    except Exception as e:
        logging.error(f'Failed to process subscription {sub_id}: {e}')
    finally:
        if 'network_client' in locals():
            await network_client.close()
        if 'compute_client' in locals():
            await compute_client.close()
        if 'storage_client' in locals():
            await storage_client.close()
    return resources

async def scan_full_environment(credential: DefaultAzureCredential):
    all_resources = []
    subscriptions = await get_subscriptions(credential)
    if not subscriptions:
        raise Exception("No subscriptions found. Check the ACI's Managed Identity permissions.")
    scan_tasks = [scan_subscription_resources(sub, credential) for sub in subscriptions]
    results = await asyncio.gather(*scan_tasks)
    for res_list in results:
        all_resources.extend(res_list)
    return (all_resources, subscriptions)

async def scan_targeted_resource(credential: DefaultAzureCredential, resource_id: str):
    logging.info(f'Targeted scan for: {resource_id}')
    return {'message': 'Targeted scan not fully implemented yet.'}
