import json


class Streamlit:
    json = json

    def title(self, arg):
        print(arg)

    def text(self, arg):
        print(arg)


st = Streamlit()

RUN_CONTEXT = 'interactive'
from peliqan import Peliqan

pq = Peliqan(
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InN1cHBvcnQraGV5bG9nK2xrd3dhbHRlckBwZWxpcWFuLmlvIiwiaWF0IjoxNzEwOTM1NTYxLCJleHAiOjI1NzQ4NDkxNjEsImp0aSI6ImEwNTI2ODQ0LWZkYmItNDEzZC04MWJhLWE4MTE0NmZkMjM3MiIsInVzZXJfaWQiOjQ4MSwidXNlcl9wcm9maWxlX2lkIjpbNDc5XSwib3JpZ19pYXQiOjE3MTA5MzU1NjEsInRva2VuX25hbWUiOiJpbnRlcmZhY2VfNDUyIiwiaW50ZXJmYWNlX2lkIjo0NTJ9.1sY9lMdR1j5nj5aA91c-THb5pU4llOGhdv_mCc57HMI',
    'https://app.eu.peliqan.io'
)
pq.INTERFACE_ID = 452

import re
import base64
import io
import pandas as pd

dw = pq.dbconnect('dw_448')
heylog_dev = pq.connect('Heylog dev workspace 2')
heylog_staging = pq.connect('Heylog staging workspace 7')  # Workspace 7 staging is LKWW staging
heylog_production = pq.connect('Heylog production workspace 275')  # Workspace 275 prod is LKWW 24/7 production


def format_lkww_date(lkww_date, lkww_time):
    lkww_date = str(lkww_date)
    lkww_time = str(lkww_time)
    if lkww_time == '0' or int(lkww_time) < 0:  # we had an LIEF_Z_BUC = -41
        lkww_time = '0000'
    iso_date = lkww_date[0:4] + '-' + lkww_date[4:6] + '-' + lkww_date[6:8]
    if len(lkww_time) == 3:
        lkww_time = '0' + lkww_time
    iso_time = lkww_time[0:2] + ':' + lkww_time[2:4] + ':00.000Z'
    return iso_date + 'T' + iso_time


def upsert_order_heylog(lkww_order, heylog_order, env):
    if not lkww_order['source'] == 'JLR_GB_SK.csv':
        # st.text("Skipping order, not from source file JLR_GB_SK.csv")
        return
    if lkww_order['heylog_' + env + '_order_id']:
        # st.text('Updating order in Heylog dev: ' + lkww_order['AG_REFER_POSITION'])
        # heylog_order["id"] = lkww_order['heylog_dev_order_id']
        # result = heylog_dev.update('order_with_labels', heylog_order)

        # To do: Think about updating orders incrementally, avoid updating all orders on each run
        #        Add timestamp changed in lkww_orders table, db.upsert should not increase value if no changes
        #        Or change field status to empty if there is a change
        pass
    else:
        st.text('Adding order to Heylog ' + env + ': ' + lkww_order['AG_REFER_POSITION'])

        if env == 'dev':
            result = heylog_dev.add('order_with_labels', heylog_order)
            if result['status'] == 'error':
                st.json(result)
            else:
                update_status = {
                    'status': result['status'],
                    'heylog_dev_order_id': result['detail'].get('id')
                }
        elif env == 'staging':
            result = heylog_staging.add('order_with_labels', heylog_order)
            if result['status'] == 'error':
                st.json(result)
            else:
                update_status = {
                    'status': result['status'],
                    'heylog_staging_order_id': result['detail'].get('id')
                }
        elif env == 'production':
            result = heylog_production.add('order_with_labels', heylog_order)
            if result['status'] == 'error':
                st.json(result)
            else:
                update_status = {
                    'status': result['status'],
                    'heylog_production_order_id': result['detail'].get('id')
                }
        else:
            st.text("Unknown env in upsert_order_heylog")
            exit()

        if result['status'] == 'success':
            dw.update('dw_448', 'lkww', 'lkww_orders', lkww_order['AG_REFER_POSITION'], update_status)


def transform_lkww_order_to_heylog_order(lkww_order):
    heylog_order = None
    if (lkww_order["AG_REFER"]
            and lkww_order["AG_REFER"] != ""
            and lkww_order["AG_REFER"] != 0
            and lkww_order["AG_REFER"] != "Customer REF (JLR)"):

        licensePlateTruck = lkww_order["KENNZ2"]
        licensePlateTrailer = lkww_order["KENNZ1"]
        firstName = lkww_order["WOB_VORNAM"]
        lastName = lkww_order["WOB_NAME"]
        email = lkww_order["WOB_MAIL"]
        port_from = lkww_order["FAEH_VON_K"]
        port_to = lkww_order["FAEH_NAC_K"]

        # empty cell in Excel becomes NaN, we replace NaN in the DF with 0 (see Excel import code)
        # probably not relevant for CSV files
        if str(licensePlateTruck) == '0':
            licensePlateTruck = ''
        if str(licensePlateTrailer) == '0':
            licensePlateTrailer = ''
        if str(firstName) == '0':
            firstName = ''
        if str(lastName) == '0':
            lastName = ''
        if str(email) == '0':
            email = 'unknown'
        if str(port_from) == '0':
            port_from = ''
        if str(port_to) == '0':
            port_to = ''

        if port_from and port_to:
            port_label = port_from + ' - ' + port_to
        else:
            port_label = ''
        fullName = (firstName + ' ' + lastName).strip()

        heylog_order = {
            "refNumber": lkww_order["AG_REFER"],
            "customer": "JLR",
            "licensePlateTruck": licensePlateTruck,
            "licensePlateTrailer": licensePlateTrailer,
            "start": {
                "name": lkww_order["BELAD_NAME"],
                "street": lkww_order["BELAD_STRA"],
                "zipCode": lkww_order["BELAD_PLZ"],
                "city": lkww_order["BELAD_ORT"]
            },
            "destination": {
                "name": lkww_order["ENTLAD_NAM"],
                "street": lkww_order["ENTLAD_STR"],
                "zipCode": lkww_order["ENTLAD_PLZ"],
                "city": lkww_order["ENTLAD_ORT"]
            },
            "etaFrom": format_lkww_date(lkww_order["LAD_D_BUC"], lkww_order["LAD_Z_BUC"]),
            "etaTo": format_lkww_date(lkww_order["LIEF_D_BUC"], lkww_order["LIEF_Z_BUC"]),
            "labels": [
                {"value": email, "type": "OWNER"},
                {"value": lkww_order["POSITION"], "type": "ORDER_EXTERNAL_REFERENCE"},
            ]
        }
        if port_label:
            heylog_order["labels"].append({"value": port_label})  # generic label, no type

    return heylog_order


def import_orders_from_attachment_into_peliqan_table(email):
    status = "unknown"

    if not "Attachments" in email:
        st.text("Email does not have attachments")
        status = "no attachments"
        return status

    for attachment in email["Attachments"]:
        if not "Content" in attachment and "ContentType" in attachment:
            st.text("Invalid attachment")
            status = "invalid attachment"
            continue
        if attachment["ContentType"] not in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                             "application/octet-stream"]:
            st.text("Skipping attachment, not an Excel or CSV file")
            status = "skipped attachment not Excel or CSV"
            continue

        decoded_bytes = base64.b64decode(attachment["Content"])
        file_bytes = io.BytesIO(decoded_bytes)
        try:
            if ".csv" in attachment["Name"]:
                lkww_orders_df = pd.read_csv(file_bytes, sep='\t', encoding="ISO-8859-1")
                is_csv = True
            else:
                lkww_orders_df = pd.read_excel(file_bytes)
                is_csv = False
        except:
            st.text("Cannot read Excel or CSV file")
            status = "cannot read Excel or CSV file"
            continue

        st.text("Number of rows from file: " + str(len(lkww_orders_df.index)))
        lkww_orders_df = lkww_orders_df.drop(columns=[
            'EXPORT_MRN',
            'T1_MRN',
            'FAEHR_TEXT',
            'FAE_AEND_D',
            'FAE_AEND_Z',
            'FAEHR_PNR',
            'WAB',
            'BAHN_AB_DT',
            'BAHN_AB_ZT',
            'FAEHR_AB_D',
            'ET_ZUGMA',
            'ET_PNR'])
        lkww_orders_df.fillna(0, inplace=True)
        lkww_orders = lkww_orders_df.to_dict('records')

        status = "no orders"
        for lkww_order in lkww_orders:
            lkww_order['AG_REFER_POSITION'] = str(lkww_order['AG_REFER']) + '_' + str(lkww_order['POSITION'])
            if  lkww_order['AG_REFER_POSITION'] == "NT042A-D3-M1/JLR.01568269_SND44945461":
                print(lkww_order, is_csv)
    return status


def process_incoming_webhooks():
    print("Processing incoming webhooks")
    incoming_webhooks = dw.fetch('dw_448', query="SELECT * FROM webhook.incoming_webhooks")
    for incoming_webhook in incoming_webhooks:
        email = incoming_webhook["payload"]
        print("\n\n")
        #
        # extract email when To has this format: "lkww@heylog.com" <lkww@heylog.com>
        if '<' in email["To"] and '>' in email["To"]:
            email["To"] = email["To"][email["To"].find('<') + 1:email["To"].find('>')]

        # Postmark server that receives emails with Excel/CSV attachments (lkww@heylog.com forwards to Postmark)
        if ('lkww@heylog.com' in email["To"].lower() or
                '4f369339798a3c6288eb0a00e84c89e7@inbound.postmarkapp.com' in email["To"].lower()):
            st.text("Processing email: " + email["Subject"] + " To: " + email["To"].lower())
            status = import_orders_from_attachment_into_peliqan_table(email)
            # dw.update('dw_448', 'webhook', 'incoming_webhooks', incoming_webhook["id"], {"status": status})


# def imported_orders_to_heylog():
#     lkww_orders = dw.fetch('dw_448', 'lkww', 'lkww_orders')
#     for lkww_order in lkww_orders:
#         heylog_order = transform_lkww_order_to_heylog_order(lkww_order)
#         if heylog_order:
#             # upsert_order_heylog(lkww_order, heylog_order, 'dev')
#             # upsert_order_heylog(lkww_order, heylog_order, 'staging')
#             upsert_order_heylog(lkww_order, heylog_order, 'production')


process_incoming_webhooks()
st.text('DONE processing incoming webhooks (emails with LKWW orders attachment, from Postmark).')
# imported_orders_to_heylog()
st.text('DONE sending imported LKWW orders to Heylog.')

# ORGINAL CODE

# import json
# import re
# import base64
# import io
# import pandas as pd
#
# dw = pq.dbconnect('dw_448')
# heylog_dev = pq.connect('Heylog dev workspace 2')
# heylog_staging = pq.connect('Heylog staging workspace 7')  # Workspace 7 staging is LKWW staging
# heylog_production = pq.connect('Heylog production workspace 275')  # Workspace 275 prod is LKWW 24/7 production
#
#
# def format_lkww_date(lkww_date, lkww_time):
#     lkww_date = str(lkww_date)
#     lkww_time = str(lkww_time)
#     if lkww_time == '0' or int(lkww_time) < 0:  # we had an LIEF_Z_BUC = -41
#         lkww_time = '0000'
#     iso_date = lkww_date[0:4] + '-' + lkww_date[4:6] + '-' + lkww_date[6:8]
#     if len(lkww_time) == 3:
#         lkww_time = '0' + lkww_time
#     iso_time = lkww_time[0:2] + ':' + lkww_time[2:4] + ':00.000Z'
#     return iso_date + 'T' + iso_time
#
#
# def upsert_order_heylog(lkww_order, heylog_order, env):
#     if not lkww_order['source'] == 'JLR_GB_SK.csv':
#         # st.text("Skipping order, not from source file JLR_GB_SK.csv")
#         return
#     if lkww_order['heylog_' + env + '_order_id']:
#         # st.text('Updating order in Heylog dev: ' + lkww_order['AG_REFER_POSITION'])
#         # heylog_order["id"] = lkww_order['heylog_dev_order_id']
#         # result = heylog_dev.update('order_with_labels', heylog_order)
#
#         # To do: Think about updating orders incrementally, avoid updating all orders on each run
#         #        Add timestamp changed in lkww_orders table, db.upsert should not increase value if no changes
#         #        Or change field status to empty if there is a change
#         pass
#     else:
#         st.text('Adding order to Heylog ' + env + ': ' + lkww_order['AG_REFER_POSITION'])
#
#         if env == 'dev':
#             result = heylog_dev.add('order_with_labels', heylog_order)
#             if result['status'] == 'error':
#                 st.json(result)
#             else:
#                 update_status = {
#                     'status': result['status'],
#                     'heylog_dev_order_id': result['detail'].get('id')
#                 }
#         elif env == 'staging':
#             result = heylog_staging.add('order_with_labels', heylog_order)
#             if result['status'] == 'error':
#                 st.json(result)
#             else:
#                 update_status = {
#                     'status': result['status'],
#                     'heylog_staging_order_id': result['detail'].get('id')
#                 }
#         elif env == 'production':
#             result = heylog_production.add('order_with_labels', heylog_order)
#             if result['status'] == 'error':
#                 st.json(result)
#             else:
#                 update_status = {
#                     'status': result['status'],
#                     'heylog_production_order_id': result['detail'].get('id')
#                 }
#         else:
#             st.text("Unknown env in upsert_order_heylog")
#             exit()
#
#         if result['status'] == 'success':
#             dw.update('dw_448', 'lkww', 'lkww_orders', lkww_order['AG_REFER_POSITION'], update_status)
#
#
# def transform_lkww_order_to_heylog_order(lkww_order):
#     heylog_order = None
#     if (lkww_order["AG_REFER"]
#             and lkww_order["AG_REFER"] != ""
#             and lkww_order["AG_REFER"] != 0
#             and lkww_order["AG_REFER"] != "Customer REF (JLR)"):
#
#         licensePlateTruck = lkww_order["KENNZ2"]
#         licensePlateTrailer = lkww_order["KENNZ1"]
#         firstName = lkww_order["WOB_VORNAM"]
#         lastName = lkww_order["WOB_NAME"]
#         email = lkww_order["WOB_MAIL"]
#         port_from = lkww_order["FAEH_VON_K"]
#         port_to = lkww_order["FAEH_NAC_K"]
#
#         # empty cell in Excel becomes NaN, we replace NaN in the DF with 0 (see Excel import code)
#         # probably not relevant for CSV files
#         if str(licensePlateTruck) == '0':
#             licensePlateTruck = ''
#         if str(licensePlateTrailer) == '0':
#             licensePlateTrailer = ''
#         if str(firstName) == '0':
#             firstName = ''
#         if str(lastName) == '0':
#             lastName = ''
#         if str(email) == '0':
#             email = 'unknown'
#         if str(port_from) == '0':
#             port_from = ''
#         if str(port_to) == '0':
#             port_to = ''
#
#         if port_from and port_to:
#             port_label = port_from + ' - ' + port_to
#         else:
#             port_label = ''
#         fullName = (firstName + ' ' + lastName).strip()
#
#         heylog_order = {
#             "refNumber": lkww_order["AG_REFER"],
#             "customer": "JLR",
#             "licensePlateTruck": licensePlateTruck,
#             "licensePlateTrailer": licensePlateTrailer,
#             "start": {
#                 "name": lkww_order["BELAD_NAME"],
#                 "street": lkww_order["BELAD_STRA"],
#                 "zipCode": lkww_order["BELAD_PLZ"],
#                 "city": lkww_order["BELAD_ORT"]
#             },
#             "destination": {
#                 "name": lkww_order["ENTLAD_NAM"],
#                 "street": lkww_order["ENTLAD_STR"],
#                 "zipCode": lkww_order["ENTLAD_PLZ"],
#                 "city": lkww_order["ENTLAD_ORT"]
#             },
#             "etaFrom": format_lkww_date(lkww_order["LAD_D_BUC"], lkww_order["LAD_Z_BUC"]),
#             "etaTo": format_lkww_date(lkww_order["LIEF_D_BUC"], lkww_order["LIEF_Z_BUC"]),
#             "labels": [
#                 {"value": email, "type": "OWNER"},
#                 {"value": lkww_order["POSITION"], "type": "ORDER_EXTERNAL_REFERENCE"},
#             ]
#         }
#         if port_label:
#             heylog_order["labels"].append({"value": port_label})  # generic label, no type
#
#     return heylog_order
#
#
# def import_orders_from_attachment_into_peliqan_table(email):
#     status = "unknown"
#
#     if not "Attachments" in email:
#         st.text("Email does not have attachments")
#         status = "no attachments"
#         return status
#
#     for attachment in email["Attachments"]:
#         if not "Content" in attachment and "ContentType" in attachment:
#             st.text("Invalid attachment")
#             status = "invalid attachment"
#             continue
#         if attachment["ContentType"] not in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#                                              "application/octet-stream"]:
#             st.text("Skipping attachment, not an Excel or CSV file")
#             status = "skipped attachment not Excel or CSV"
#             continue
#
#         decoded_bytes = base64.b64decode(attachment["Content"])
#         file_bytes = io.BytesIO(decoded_bytes)
#         try:
#             if ".csv" in attachment["Name"]:
#                 lkww_orders_df = pd.read_csv(file_bytes, sep='\t', encoding="ISO-8859-1")
#             else:
#                 lkww_orders_df = pd.read_excel(file_bytes)
#         except:
#             st.text("Cannot read Excel or CSV file")
#             status = "cannot read Excel or CSV file"
#             continue
#
#         st.text("Number of rows from file: " + str(len(lkww_orders_df.index)))
#         lkww_orders_df = lkww_orders_df.drop(columns=[
#             'EXPORT_MRN',
#             'T1_MRN',
#             'FAEHR_TEXT',
#             'FAE_AEND_D',
#             'FAE_AEND_Z',
#             'FAEHR_PNR',
#             'WAB',
#             'BAHN_AB_DT',
#             'BAHN_AB_ZT',
#             'FAEHR_AB_D',
#             'ET_ZUGMA',
#             'ET_PNR'])
#         lkww_orders_df.fillna(0, inplace=True)
#         lkww_orders = lkww_orders_df.to_dict('records')
#
#         status = "no orders"
#         for lkww_order in lkww_orders:
#             # AG_REFER is not unique in Excel/CSV files
#             lkww_order['AG_REFER_POSITION'] = str(lkww_order['AG_REFER']) + '_' + str(lkww_order['POSITION'])
#             lkww_order['source'] = attachment["Name"]
#             result = dw.upsert('dw_448', 'lkww', 'lkww_orders', lkww_order['AG_REFER_POSITION'], lkww_order)
#             st.text(lkww_order['AG_REFER_POSITION'] + ': ' + result['status'])
#             status = "processed"
#     return status
#
#
# def process_incoming_webhooks():
#     incoming_webhooks = dw.fetch('dw_448', 'webhook', 'incoming_webhooks')
#     for incoming_webhook in incoming_webhooks:
#         if not incoming_webhook["status"] and incoming_webhook["id"] >= 1163:
#             email = incoming_webhook["payload"]
#
#             # extract email when To has this format: "lkww@heylog.com" <lkww@heylog.com>
#             if '<' in email["To"] and '>' in email["To"]:
#                 email["To"] = email["To"][email["To"].find('<') + 1:email["To"].find('>')]
#
#             # Postmark server that receives emails with Excel/CSV attachments (lkww@heylog.com forwards to Postmark)
#             if ('lkww@heylog.com' in email["To"].lower() or
#                     '4f369339798a3c6288eb0a00e84c89e7@inbound.postmarkapp.com' in email["To"].lower()):
#                 st.text("Processing email: " + email["Subject"] + " To: " + email["To"].lower())
#                 status = import_orders_from_attachment_into_peliqan_table(email)
#                 dw.update('dw_448', 'webhook', 'incoming_webhooks', incoming_webhook["id"], {"status": status})
#
#
# def imported_orders_to_heylog():
#     lkww_orders = dw.fetch('dw_448', 'lkww', 'lkww_orders')
#     for lkww_order in lkww_orders:
#         heylog_order = transform_lkww_order_to_heylog_order(lkww_order)
#         if heylog_order:
#             # upsert_order_heylog(lkww_order, heylog_order, 'dev')
#             # upsert_order_heylog(lkww_order, heylog_order, 'staging')
#             upsert_order_heylog(lkww_order, heylog_order, 'production')
#
#
# process_incoming_webhooks()
# st.text('DONE processing incoming webhooks (emails with LKWW orders attachment, from Postmark).')
# imported_orders_to_heylog()
# st.text('DONE sending imported LKWW orders to Heylog.')
