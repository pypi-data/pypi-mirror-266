import sys
import os
sys.path.append(os.path.abspath("/Users/lmarchand.PS/PycharmProjects/pypscloud/pypscloud"))

from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta


from pypscloud import *


def test_site(ps):
    mps = ps.get_all_mp_from_account(6)
    for mp in mps:
        accountId = mp['accountId']
        siteId = mp['locationId']
        site = ps.get_site(mp['locationId'])
        if site['locationName'] == 'PQube3 e Test wall':
            print(mp)
            print(site)
            new_site = site
            del new_site['locationId']
            del new_site['measurementPoints']
            new_site['locationName'] = 'PQube3 e Test wall 09'

            ps.set_site(accountId, siteId, new_site)


def test_all_mps_accounts(ps):
    df = ps.get_all_mps_from_all_accounts_as_df()
    print(df)


def test_tz():
    s, e = ps_build_start_end_date_from_midnight(7, 'America/Los_Angeles')
    print(s)
    print(e)

    d = ps_time_utc_to_local('2024-01-26T08:00:00.000Z', 'America/Los_Angeles')
    print(d)
    d = ps_time_utc_to_local('2024-01-26T08:00:00.000Z', 'America/New_York')
    print(d)
    ss = ps_time_with_tz(s, 'America/Los_Angeles')
    print(ss)
    ee = ps_time_with_tz(e, 'America/Los_Angeles')
    print(ee)


def test_param(ps):
    p = ps.get_mp_parameters(15206)
    print(p)

    p = ps.get_maxLoadCurrentDemand(15206)
    print(p)



def test_fwu(ps):
    f = ps.firmware_set_version_to_device('3.10.6.24.02.01', [13817])
    print(f)
    accounts = ps.get_all_accounts()
    print(accounts)

    p = ps.get_mp(13817)
    print(p)

    s = ps.firmware_start([13817])
    print(s)


def test_account(ps):
    acc_edge_test_bench = 489
    test_acc = 138
    a2 = {}
    a = ps.get_account(test_acc)
    print(a)
    if a['useFirmwareAutomaticUpdates'] == False:
        if 'address' not in a:
            a2['address'] = {}
            a2['address']['country'] = ''
            a2['address']['state'] = ''
            a2['address']['city'] = ''
            a2['address']['street1'] = ''
            a2['address']['street2'] = ''
            a2['address']['zipCode'] = ''
        else:
            a2['address'] = a['address']
            del a2['address'] ['addressId']

        if a2['address']['country'] == None: a2['address']['country'] = ''
        if a2['address']['state'] == None: a2['address']['state'] = ''
        if a2['address']['city'] == None: a2['address']['city'] = ''
        if a2['address']['street1'] == None: a2['address']['street1'] = ''
        if a2['address']['street2'] == None: a2['address']['street2'] = ''
        if a2['address']['zipCode'] == None: a2['address']['zipCode'] = ''


        a2['useFirmwareAutomaticUpdates'] = True
        a2['isPartner'] = a['isPartner']
        a2['partnerAccountId'] = a['partnerAccountId']
        a2['name'] = a['name']
        a2['subscriptionExpiry'] = "2024-04-01T23:00:00.000Z"
        a2['subscriptionType'] = a['subscriptionType']

        info = ps.set_account(test_acc,a2)
        print(info)
    a2 = ps.get_account(test_acc)
    print(a2)


def test_firmware_search(ps):
    f = ps.firmware_search()
    print(f)


def test_changing_mp_name(ps):
    dominion = 252
    datacenters = 572
    #mps = ps.get_all_mp_from_account(datacenters, True)
    #print(mps)
    accountId = 8869
    siteId = 11284
    mpId = 86355902

    mp = ps.get_mp(mpId)
    print(mp)

    site_mp = {
        "site": {
            "locationName": "move to",
            # "shortname": "move to",
            "address1": "1683-1, Prieur Est",
            "address2": "",
            "city": "Montréal",
            "state": "PQ",
            "zipCode": "H2C 1M5",
            "country": "Canada",
            "siteInformation": "",
            "latitude": 45.5667066,
            "longitude": -73.6578514
        },
        "measurementPoint": {
            "mpId": mp['mpId'],
            "measurementPointTypeId": 1
        },
        "parameters": None
    }

    code = ps.set_site_mp(accountId, siteId, mpId, site_mp)
    print(code)


def test_notification_groups(ps):
    ngs = ps.get_notification_groups()
    
    ng_recs = ngs['records'] 
    for ng_rec in ng_recs:
        ng_info = ps.get_notification_group(ng_rec['notificationGroupId'])
        print(ng_info)


def test_s3_download_date_range(ps):
    env = ps.get_env()
    p = env['awsprofile']
    s3 = PSS3(p)
    start = '2023-12-01T00:00:00.000Z'
    end = '2024-04-01T12:00:00.000Z'
    beg_date = dateutil.parser.isoparse(start)
    end_date = dateutil.parser.isoparse(end)

    device_event_dir = 'iot/pqube/P3019857/event'
    #os.makedirs(device_event_dir, exist_ok=True)
    s3.download_date_range(device_event_dir, beg_date, end_date)


def main():
    ps = PSCommon('production')
    ps.login()

    print(ps)
    print(ps.get_env())

    test_s3_download_date_range(ps)

    # ps_post_cmd(13817,7)

    # ps.device_file_request_by_mp(16667, ["channels-P3020805.json"])

    # test_site(ps)
    # test_all_mps_accounts(ps)
    # cd = ps.get_mp_channel_def(15206)
    # hb = ps.get_mp_heartbeat(20247, 2)
    # print(hb)
    # test_tz()
    # test_param(ps)
    # test_fwu(ps)

    # test_account(ps)
    # test_changing_mp_name(ps)
    # test_firmware_search(ps)
    # test_notification_groups(ps)


main()