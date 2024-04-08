# stucent/client.py
from .services import CourseService
import os
import pkg_resources

if not os.path.exists(os.path.expanduser('~/.stucent')):
    os.makedirs(os.path.expanduser('~/.stucent'))


class Stucent:
    def __init__(self, api_token = None, base_url = None):
        # Add version to this library
        self.version = pkg_resources.get_distribution("stucent").version
        self.api_token = api_token
        self.base_url = base_url
        if not api_token:
            self.api_token = os.environ.get("STUCENT_API_TOKEN")
        if not self.api_token:
            raise ValueError("The api token is required. Please set it as an environment variable STUCENT_API_TOKEN or pass it as an argument to the constructor")
        
        if not base_url:
            self.base_url = os.environ.get("STUCENT_BASE_URL", "https://api.uccode.io/craft4me")

        self.course = CourseService(self.api_token, self.base_url )
        try:
            self.course.ack()
        except:
            raise ValueError("The api token is invalid or service is down")

    def ack(self):
        return "ack"

class AsyncStucent:
    # Similar to Stucent, but with async methods
    pass
