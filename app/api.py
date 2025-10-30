import json
import os

import requests

url = "https://api.cbd.int/api/v2013/index/select"

query = {
    "df": "text_EN_txt",
    "fq": ["_state_s:public", "realm_ss:ort"],
    "q": "(schema_s : (nationalTarget7))",
    "sort": "updatedDate_dt desc",
    "fl": "id, recDate:updatedDate_dt, recCreationDate:createdDate_dt, identifier_s, uniqueIdentifier_s, url_ss, government_s, schema_s,schema_EN_s, government_EN_s, schemaSort_i, sort1_i, sort2_i, sort3_i, sort4_i, _revision_i,recCountryName:government_EN_t, recTitle:title_EN_t, recSummary:summary_t, recType:type_EN_t, recMeta1:meta1_EN_txt, recMeta2:meta2_EN_txt, recMeta3:meta3_EN_txt,recMeta4:meta4_EN_txt,recMeta5:meta5_EN_txt,globalTargetAlignment_ss,globalGoalOrTarget_s,globalGoalAlignment_ss",
    "wt": "json",
    "start": 0,
    "rows": 4000,
}

response = requests.post(url, json=query)


os.makedirs(".data_cache", exist_ok=True)
with open(".data_cache/select.json", "w", encoding="utf-8") as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=2)
