from typing import Union, Any
import aiohttp
import logging
import time

__all__ = ["ShadowDragonAPI"]

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
logger = logging.getLogger(__name__)

def log_request(func):
    async def wrapper(self, *args, **kwargs):
        start_time = time.time()

        logger.info(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}...")

        result = await func(self, *args, **kwargs)

        if "data" in result.keys():

            rate_limit = result['rate_limit']

            end_time = time.time()

            elapsed_time = end_time - start_time

            logger.info(f"{rate_limit['remaining']} requests left for next {rate_limit['reset_in']} seconds.")
            logger.info(f"Method {func.__name__} took {elapsed_time:.4f} seconds to complete.")

            return result['data']
        else:
            error = result['errors'][0]
            logger.error(f"Something went wrong: {error['code']}: {error['message']}")
            return
    return wrapper


class ShadowDragonAPI:
    def __init__(self, api_key):

        self.api_key = api_key
        self.base_url = "https://api.socialnet.shadowdragon.io"
        self.headers = {"Authorization": f"Token {self.api_key}", "Accept": "application/vnd.shadowdragon.v2+json"}

    # General Queries related to ShadowDragon API
    async def list_queries(self) -> str:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            async with session.get(f"{self.base_url}/", headers=self.headers) as response:
                text = await response.text()
                return text

    async def rate_limit(self) -> str:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            async with session.get(f"{self.base_url}/rate_limit", headers=self.headers) as response:
                text = await response.text()
                return text

    async def status(self) -> str:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            async with session.get(f"{self.base_url}/status", headers=self.headers) as response:
                text = await response.text()
                return text
            
    # General Search
    @log_request
    async def search(self, alias: str, limit: int = 1000, queue: Union[bool, None] = False) -> list[dict[str, Any]]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            url = f"{self.base_url}/search?alias={alias}"

            if limit:
                url += f"?limit={limit}"
            if queue:
                url +=f"&queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    # Instagram

    @log_request
    async def instagram_search(self, alias: Union[str, None], name: Union[str, None] = None, q: Union[str, None] = None, limit: Union[int, None] = None, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:

            url = f"{self.base_url}/instagram/search"

            params = []

            if alias:
                params.append(f"alias={alias}")
            if name:
                params.append(f"name={name}")
            if q:
                params.append(f"q={q}")
            if limit:
                params.append(f"limit={limit}")
            if queue:
                params.append(f"queue={queue}")

            if len(params) > 0:
                url += "?" + "&".join(params)

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_search_users(self, alias: Union[str, None], name: Union[str, None] = None, q: Union[str, None] = None, limit: Union[int, None] = None, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:

            url = f"{self.base_url}/instagram/search/users"

            params = []

            if alias:
                params.append(f"alias={alias}")
            if name:
                params.append(f"name={name}")
            if q:
                params.append(f"q={q}")
            if limit:
                params.append(f"limit={limit}")
            if queue:
                params.append(f"queue={queue}")

            if len(params) > 0:
                url += "?" + "&".join(params)

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_search_recovery(self, email: Union[str, None], phone: Union[str, None] = None, limit: Union[int, None] = None, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:

            url = f"{self.base_url}/instagram/search/recovery"

            params = []

            if email:
                params.append(f"email={email}")
            if phone:
                params.append(f"phone={phone}")
            if limit:
                params.append(f"limit={limit}")
            if queue:
                params.append(f"queue={queue}")

            if len(params) > 0:
                url += "?" + "&".join(params)

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_search_locations(self, name: Union[str, None], q: Union[str, None] = None, latlng: Union[str, None] = None, limit: Union[int, None] = None, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:

            url = f"{self.base_url}/instagram/search/locations"

            params = []

            if name:
                params.append(f"name={name}")
            if q:
                params.append(f"q={q}")
            if latlng:
                params.append(f"latlng={latlng}")
            if limit:
                params.append(f"limit={limit}")
            if queue:
                params.append(f"queue={queue}")

            if len(params) > 0:
                url += "?" + "&".join(params)

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_search_tags(self, alias: Union[str, None], name: Union[str, None] = None, q: Union[str, None] = None, limit: Union[int, None] = None, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:

            url = f"{self.base_url}/instagram/search/tags"

            params = []

            if alias:
                params.append(f"alias={alias}")
            if name:
                params.append(f"name={name}")
            if q:
                params.append(f"q={q}")
            if limit:
                params.append(f"limit={limit}")
            if queue:
                params.append(f"queue={queue}")

            if len(params) > 0:
                url += "?" + "&".join(params)

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_user(self, user_id: str, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:

            url = f"{self.base_url}/instagram/users/{user_id}"

            if queue:
                url += f"?queue={queue}"            

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_user_story(self, user_id: str, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:

            url = f"{self.base_url}/instagram/users/{user_id}/story"
            
            if queue:
                url += f"?queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_user_followers(self, user_id: str, limit: Union[int, None] = 1000, queue: Union[bool, None] = False) -> dict[str, Any]:
        """
            Issue: will not accurately pull followers.

            David Wells: This is based on restrictions Instagram (Meta) has put in place.
            Unfortunately, at this time for larger followings it is difficult/impossible to pull back the entirely to followers.
            One thing we recommend is to focus more on engagement, rather than just on generic follower/following relationships.
            This can include finding posts of interest and see who is liking/reacting to it, as these generally reflect more relevant relationships.
        """

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:

            url = f"{self.base_url}/instagram/users/{user_id}/followers"

            if limit:
                url += f"?limit={limit}"
            if queue:
                url += f"&queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_user_following(self, user_id: str, limit: Union[int, None] = 1000, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            url = f"{self.base_url}/instagram/users/{user_id}/following"

            if limit:
                url += f"?limit={limit}"
            if queue:
                url += f"&queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_user_posts(self, user_id: str, limit: Union[int, None] = 1000, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            url = f"{self.base_url}/instagram/users/{user_id}/posts"

            if limit:
                url += f"?limit={limit}"
            if queue:
                url += f"&queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_user_reels(self, user_id: str, limit: Union[int, None] = 1000, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            url = f"{self.base_url}/instagram/users/{user_id}/reels"

            if limit:
                url += f"?limit={limit}"
            if queue:
                url += f"&queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_user_highlights(self, user_id: str, limit: Union[int, None] = 1000, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            url = f"{self.base_url}/instagram/users/{user_id}/highlights"

            if limit:
                url += f"?limit={limit}"
            if queue:
                url += f"&queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_user_tagged_posts(self, user_id: str, limit: Union[int, None] = 1000, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            url = f"{self.base_url}/instagram/users/{user_id}/tagged_posts"

            if limit:
                url += f"?limit={limit}"
            if queue:
                url += f"&queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json


    @log_request
    async def instagram_post(self, post_id: str, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            url = f"{self.base_url}/instagram/posts/{post_id}"

            if queue:
                url += f"?queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_post_likers(self, post_id: str, limit: Union[int, None] = 1000, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            url = f"{self.base_url}/instagram/posts/{post_id}/likers"

            if limit:
                url += f"?limit={limit}"
            if queue:
                url += f"&queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                # print(json.keys())
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_post_comments(self, post_id: str, limit: Union[int, None] = 1000, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            url = f"{self.base_url}/instagram/posts/{post_id}/comments"

            if limit:
                url += f"?limit={limit}"
            if queue:
                url += f"&queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_comment_likers(self, comment_id: str, limit: Union[int, None] = 1000, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            url = f"{self.base_url}/instagram/comments/{comment_id}/likers"

            if limit:
                url += f"?limit={limit}"
            if queue:
                url += f"&queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def instagram_comment_replies(self, comment_id: str, limit: Union[int, None] = 1000, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            url = f"{self.base_url}/instagram/comments/{comment_id}/replies"

            if limit:
                url += f"?limit={limit}"
            if queue:
                url += f"&queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def facebook_user(self, user_id: str, queue: Union[bool, None] = False) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            url = f"{self.base_url}/facebook/users/{user_id}"

            if queue:
                url += f"?queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json

    @log_request
    async def facebook_user_friends(self, user_id: str, limit: Union[int, None] = 1000, queue: Union[bool, None] = False) -> list[dict[str, Any]]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            url = f"{self.base_url}/facebook/users/{user_id}/friends"

            if limit:
                url += f"?limit={limit}"
            if queue:
                url += f"&queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json
            
    @log_request
    async def facebook_posts_by_user(self, user_id: str, limit: Union[int, None] = 1000, queue: Union[bool, None] = False) -> list[dict[str, Any]]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            url = f"{self.base_url}/users/{user_id}/posts_by"

            if limit:
                url += f"?limit={limit}"
            if queue:
                url += f"&queue={queue}"

            async with session.get(url, headers=self.headers) as response:
                json = await response.json()
                json['rate_limit'] = {
                    "limit": response.headers.get("X-Ratelimit-Limit"),
                    "remaining": response.headers.get("X-Ratelimit-Remaining"),
                    "reset_in": response.headers.get("X-Ratelimit-Reset")
                }
                return json