import looker_sdk
from looker_sdk.sdk.api40 import models
from looker_sdk import error

sdk = looker_sdk.init40()

try:
    # sdk.run_inline_query(
    #     "json",
    #     models.WriteQuery(
    #         model="i__looker",
    #         view="history",
    #         fields=["history.query_run_count", "query.model"],
    #         filters={
    #             "history.created_date": '90 days',
    #             "query.model": "-system__activity, -i__looker",
    #             "history.query_run_count": ">0",
    #             "user.dev_mode": "No",
    #         },
    #         limit="5000",
    #     ),
    # )

    sdk.project('Niantic')
    print('success')


except error.SDKError as e:
    print('wtf')
    print(e.message)