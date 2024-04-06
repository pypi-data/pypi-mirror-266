from typing import Union, Any, Optional, get_origin
import aiohttp
import logging
import time
import asyncio
import functools
from enum import Enum
import json

__all__ = ["ShadowDragonAPI"]

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
logger = logging.getLogger(__name__)

def check_keys_exist(dict_1, dict_2):
    for key in dict_2.keys():
        if key not in dict_1:
            return False
    return True

def log_request(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        start_time = time.time()

        logger.info(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}...")

        # __annotations__ = func.__annotations__

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

class SDMethod(Enum):
    SEARCH = "search"
    FACEBOOK_USER = "facebook_user"
    FACEBOOK_USER_FRIENDS = "facebook_user_friends"
    FACEBOOK_POSTS_BY_USER = "facebook_posts_by_user"
    INSTAGRAM_SEARCH = "instagram_search"
    INSTAGRAM_SEARCH_USERS = "instagram_search_users"
    INSTAGRAM_USER = "instagram_user"
    INSTAGRAM_USER_POSTS = "instagram_user_posts"
    INSTAGRAM_USER_REELS = "instagram_user_reels"
    INSTAGRAM_USER_STORY = "instagram_user_story"
    INSTAGRAM_USER_TAGGED_POSTS = "instagram_user_tagged_posts"
    INSTAGRAM_POST = "instagram_post"
    INSTAGRAM_POST_COMMENTS = "instagram_post_comments"
    INSTAGRAM_POST_LIKERS = "instagram_post_likers"
    INSTAGRAM_COMMENT_LIKERS = "instagram_comment_likers"
    INSTAGRAM_COMMENT_REPLIES = "instagram_comment_replies"
    INSTAGRAM_SEARCH_LOCATIONS = "instagram_search_locations"
    INSTAGRAM_SEARCH_RECOVERY = "instagram_search_recovery"
    INSTAGRAM_SEARCH_TAGS = "instagram_search_tags"
    INSTAGRAM_USER_FOLLOWERS = "instagram_user_followers"
    INSTAGRAM_USER_FOLLOWING = "instagram_user_following"
    INSTAGRAM_USER_HIGHLIGHTS = "instagram_user_highlights"

class CompletedRequestStatus(Enum):
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"

class QueuedRequest:
    def __init__(self, method: SDMethod, params: dict[str, Any]):
        self.method = method
        self.params = params
        self.task_id: Union[str, None] = None

    def __str__(self):
        return f"Queued Request: {"SENT" if self.is_sent() else "PENDING"}"

    def get_method_value(self) -> str:
        return self.method.value
    
    def get_params(self) -> dict[str, Any]:
        return self.params

    def set_task_id(self, task_id: str):
        self.task_id = task_id

    def get_task_id(self) -> str:
        return self.task_id
    
    def is_sent(self) -> bool:
        return self.task_id is not None
    
class CompletedRequest:
    def __init__(self, task_id: str, response: Union[dict[str, Any], list[dict[str, Any]]], status: CompletedRequestStatus):
        self.task_id = task_id
        self.response = response

        self.status = status

    def __str__(self):
        return f"Completed Request: {"SUCCESSFUL" if self.status is CompletedRequestStatus.COMPLETED else "FAILED"}"

    def __repl__(self):
        return f"Completed Request: {"SUCCESSFUL" if self.status is CompletedRequestStatus.COMPLETED else "FAILED"}"


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
                json = await response.json()
                return json["data"]["rate"]

    async def status(self) -> str:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1200)) as session:
            async with session.get(f"{self.base_url}/status", headers=self.headers) as response:
                text = await response.text()
                return text
            
    # Queuing + Waiting for 
    async def report_status_every_30_secs(remaining: int):
        remaining_wait = float(remaining)
        while True:
            await asyncio.sleep(30.0)
            remaining_wait -= 30.0
            print(f"Still sleeping for {remaining_wait} seconds...")

    async def sleep_for(remaining: int):
        await asyncio.sleep(float(remaining))
    
    async def run_queued_requests(self, reqs: list[QueuedRequest]):
        """
        Send requests and put them into the queue.
        """
        for queued_request in reqs:
            rate_limits = await self.rate_limit()

            if rate_limits["remaining"] == 0:
                logger.info(f"Rate limit reached, sleeping for {rate_limits['reset']} seconds")
                await asyncio.gather(self.report_status_every_30_secs(rate_limits['reset']), self.sleep_for(rate_limits['reset']))

            req_method = getattr(self, queued_request.get_method_value())

            required_input_params_annotations = {param: annotation for param, annotation in req_method.__annotations__.items() if param != 'return' and get_origin(annotation) is not Union}

            req_params = queued_request.get_params()

            if len(req_params.keys()) != len(required_input_params_annotations.keys()) or not check_keys_exist(req_params, required_input_params_annotations):
                raise Exception(f"The method {queued_request.get_method_value()} needs required parameters: {list(required_input_params_annotations.keys())} and you provided {list(req_params.keys())}")

            queue_response = await req_method(**req_params, queue=True)

            queued_request.set_task_id(queue_response["task_id"])

            logger.info(f"Queued request with task_id: {queued_request.get_task_id()}: {queued_request}")
            

    async def start_queue_websocket_client(self, completed_queue: asyncio.Queue, total_requests: int):
        """
        Retrieve responses from the /queue endpoint and update queued requests.
        """
        try:
            async with aiohttp.ClientSession() as session:
                logger.info("Starting websocket connection to /queue...")

                found_requests = 0
                async with session.ws_connect(f"{self.base_url}/queue", headers=self.headers) as ws:
                    while True:
                        logger.info("running websocket loop")
                        msg = await ws.receive()
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            returned_json = json.loads(msg.data)
                            returned_task_id = returned_json["task_id"]
                            returned_response_data = returned_json["response"]["data"]
                            returned_status = CompletedRequestStatus.COMPLETED if returned_json["state"] == "COMPLETED" else CompletedRequestStatus.FAILED

                            logger.info(f"{returned_task_id} {returned_status}")

                            await completed_queue.put(CompletedRequest(returned_task_id, returned_response_data, returned_status))
                            found_requests += 1

                            if found_requests == total_requests:
                                break
                        else:
                            break
                        
                    logger.info("All queued requests have been successfully processed. Closing WebSocket connection.")
        except Exception as e:
            logger.error(f"Error in websocket client: {e}")

    async def check_completed_requests(self, completed_queue: asyncio.Queue, total_requests: int) -> Union[dict[str, Any], list[dict[str, Any]]]:
        """
        Continuously check for completed requests and perform any necessary actions.

        Parameters:
            queue (asyncio.Queue): An asyncio queue containing queued requests.

        """
        completed_data = []

        found_requests = 0
        while True:
            queued_request = await completed_queue.get()

            completed_data.append(queued_request)
            found_requests += 1

            if found_requests == total_requests:
                break

        return completed_data


    async def queue_requests(self, reqs: list[QueuedRequest]) -> list[dict[str, Any]]:
        """
            WIP: This function sends the listed requests, and listens for their responses in 
        """

        completed_queue = asyncio.Queue()

        results = await asyncio.gather(self.run_queued_requests(reqs), self.start_queue_websocket_client(completed_queue, len(reqs)), self.check_completed_requests(completed_queue, len(reqs)))

        return [result for result in results if result is not None][0]

            
    # General Search
    @log_request
    async def search(self, alias: str, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> list[dict[str, Any]]:
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
    async def instagram_search(self, alias: Optional[str] = None, name: Optional[str] = None, q: Optional[str] = None, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_search_users(self, alias: Optional[str] = None, name: Optional[str] = None, q: Optional[str] = None, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_search_recovery(self, email: Optional[str] = None, phone: Optional[str] = None, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_search_locations(self, name: Optional[str] = None, q: Optional[str] = None, latlng: Optional[str] = None, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_search_tags(self, alias: Optional[str] = None, name: Optional[str] = None, q: Optional[str] = None, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_user(self, user_id: str, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_user_story(self, user_id: str, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_user_followers(self, user_id: str, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_user_following(self, user_id: str, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_user_posts(self, user_id: str, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_user_reels(self, user_id: str, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_user_highlights(self, user_id: str, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_user_tagged_posts(self, user_id: str, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_post(self, post_id: str, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_post_likers(self, post_id: str, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_post_comments(self, post_id: str, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_comment_likers(self, comment_id: str, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def instagram_comment_replies(self, comment_id: str, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def facebook_user(self, user_id: str, queue: Optional[bool] = None) -> dict[str, Any]:
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
    async def facebook_user_friends(self, user_id: str, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> list[dict[str, Any]]:
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
    async def facebook_posts_by_user(self, user_id: str, limit: Optional[int] = 1000, queue: Optional[bool] = None) -> list[dict[str, Any]]:
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
