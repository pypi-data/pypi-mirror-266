PERMISSIONS_KEY = "permissions_v2"
PERMISSIONS_KEY_IGNORE_TOS = "permissions_v2_ignore_tos"

import json

auth_res = '{"admin":false,"affiliations":[[]],"email":"fcollman@mindsmatterseattle.org","groups":["default"],"id":1521,"missing_tos":[{"dataset_id":2,"dataset_name":"fafb_sandbox","tos_id":3,"tos_name":"Flywire"},{"dataset_id":7,"dataset_name":"microns_public","tos_id":2,"tos_name":"microns_public"},{"dataset_id":16,"dataset_name":"minnie65_sandbox","tos_id":2,"tos_name":"microns_public"}],"name":"Forrest Collman","parent_id":null,"permissions":{"FANC_sandbox":2,"FFN":1,"Lund":1,"flywire_public":1,"pinky100":2},"permissions_v2":{"FANC_sandbox":["edit","view"],"FFN":["view"],"Lund":["view"],"flywire_public":["view"],"pinky100":["edit","view"]},"permissions_v2_ignore_tos":{"FANC_sandbox":["edit","view"],"FFN":["view"],"Lund":["view"],"fafb_sandbox":["edit","view"],"flywire_public":["view"],"microns_public":["view"],"minnie65_sandbox":["edit","view"],"pinky100":["edit","view"]},"pi":"","service_account":false}'


auth_user = json.loads(auth_res)


def user_has_permission(a, ignore_tos=False):
    permissions_key = (
        PERMISSIONS_KEY_IGNORE_TOS
        if (ignore_tos and PERMISSIONS_KEY_IGNORE_TOS in auth_user)
        else PERMISSIONS_KEY)
    print(a, permissions_key, ignore_tos)


user_has_permission("carly", False)