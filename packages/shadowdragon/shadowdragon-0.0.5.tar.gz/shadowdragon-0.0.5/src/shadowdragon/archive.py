import requests
import json
import pandas as pd
import os
import facebook
import re
from dotenv import load_dotenv

# Testing on the Facebook API (OLD)

# def test_api(api_key: str):
#     url = "https://api.socialnet.shadowdragon.io/facebook/search/users?alias=georgie.denbrough.716&limit=25&queue=false"
#     headers = {"Authorization": f"Token {api_key}", "Accept": "application/vnd.shadowdragon.v2+json"}
#     response = requests.get(url, headers=headers)

#     print(response.json()['data']())

#     # get number of requests remaining
#     print(response.headers.get("X-Ratelimit-Remaining"))

#     # wait time
#     print(response.headers.get("X-Ratelimit-Reset"))

class User:
    def __init__(self, user_id: str | None) -> None:
        self.user_id = user_id

class FacebookUser(User):
    def __init__(self, user_id):
        super().__init__(user_id)
        self.graph = facebook.GraphAPI(access_token=os.getenv("FB_USER_TOKEN"), version = 2.7)

    @classmethod
    def from_link(cls, link: str):

        # ID Included
        id_included_pattern = r"https://www.facebook.com/profile\.php\?id=(.*)"

        match = re.search(id_included_pattern, link)

        if match:
            extracted_string = str(match.group(1))
            return cls(extracted_string)
        else:
            # ID not included
            id_not_included_pattern = r"https://www.facebook.com/(.*)"
            not_included_match = re.search(id_not_included_pattern, link)
            if not_included_match:
                not_included_extracted_string = not_included_match.group(1)

                # replace with Facebook Id
                return get_facebook_id_from_username(not_included_extracted_string)

    def get_friend_count(self) -> int:



        return 0

def get_facebook_id_from_username(username: str):
    url = f"https://api.socialnet.shadowdragon.io/facebook/search/users?alias={username}&limit=25&queue=false"
    headers = {"Authorization": f"Token {os.getenv('SHADOW_API')}", "Accept": "application/vnd.shadowdragon.v2+json"}
    response = requests.get(url, headers=headers)

    # get number of requests remaining
    print(response.headers.get("X-Ratelimit-Remaining"))

    # wait time
    print(response.headers.get("X-Ratelimit-Reset"))


    return response.json()['data'][0]['id']

def get_facebook_id_from_link(link: str):

    id_included_pattern = r"https://www.facebook.com/profile\.php\?id=(.*)"

    match = re.search(id_included_pattern, link)

    if match:
        extracted_string = match.group(1)
        return extracted_string
    else:
        id_not_included_pattern = r"https://www.facebook.com/(.*)"
        not_included_match = re.search(id_not_included_pattern, link)
        if not_included_match:
            not_included_extracted_string = not_included_match.group(1)
            return get_facebook_id_from_username(not_included_extracted_string)

def facebook_process():
    print('facebook')


if __name__ == "__main__":
    load_dotenv()

    # test_api(os.getenv("SHADOW_API"))

    # facebook_df = pd.read_csv("data/facebook.csv")
    # insta_df = pd.read_csv("data/instagram.csv")

    # # print(len(facebook_df))
    # # print(len(insta_df))

    # facebook_groups_df = facebook_df.loc[facebook_df["Type"] == "Group"]
    # facebook_accounts_df = facebook_df.loc[facebook_df["Type"] == "Account"]

    # print(facebook_accounts_df)

    # account_link = facebook_accounts_df["Link"]
    # id = account_link.rename("id").apply(get_facebook_id_from_link)
    # print(len(id))

    # facebook_accounts_df.insert(0, "id", id, True)

    # facebook_accounts_df.to_csv('finished/facebook_accounts.csv')



    # facebook_with_id = pd.read_csv("finished/facebook_accounts.csv")

    # print(facebook_with_id)


    graph = facebook.GraphAPI(access_token=os.getenv("FB_USER_TOKEN"), version = 3.1)
    print(graph.request('/search?q=kojinp&type=user'))

    # test rate limit
    url = "https://api.socialnet.shadowdragon.io/rate_limit"
    headers = {"Authorization": f"Token {os.getenv('SHADOW_API')}", "Accept": "application/vnd.shadowdragon.v2+json"}
    response = requests.get(url, headers=headers)

    # get number of requests remaining
    print(response.headers.get("X-Ratelimit-Remaining"))

    # wait time
    print(response.headers.get("X-Ratelimit-Reset"))
