import requests
import json
from .models import *
import time
import os
stucent_dir = os.path.expanduser('~/.stucent')

class SDKError(Exception):
    """Base class for all SDK errors."""

    def __init__(self, message, status_code=None, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

    def __str__(self):
        return f"{self.message} (Status code: {self.status_code}) Details: {self.details}"

class AuthenticationError(SDKError):
    """Exception raised for errors in authentication."""
    pass

class APIRequestError(SDKError):
    """Exception raised for errors during API requests."""
    pass

class CourseService:
    """
    Provides services for creating and managing course content.

    Attributes:
        api_token (str): Authentication token for API access.
        base_url (str): Base URL of the API.
        headers (dict): Headers for API requests including authorization token.
    """

    def __init__(self, api_token, base_url):
        """
        Initializes the CourseService with necessary authentication details.

        Args:
            api_token (str): Token used for authenticating API requests.
            base_url (str, optional): Base URL of the API.
        """
        self.api_token = api_token
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        self.last_usage = {
            "meta": {"prompt_tokens": 0, 'completion_tokens': 0, 'total_tokens': 0},
            "outline": {"prompt_tokens": 0, 'completion_tokens': 0, 'total_tokens': 0},
            "lesson_activities": {"prompt_tokens": 0, 'completion_tokens': 0, 'total_tokens': 0},
            "course_activities": {"prompt_tokens": 0, 'completion_tokens': 0, 'total_tokens': 0},
            "context": {"prompt_tokens": 0, 'completion_tokens': 0, 'total_tokens': 0},
            "last": {"prompt_tokens": 0, 'completion_tokens': 0, 'total_tokens': 0}
        }

    def _post(self, endpoint, data, files=None):
        """
        Private method to make POST requests to the API.

        Args:
            endpoint (str): The API endpoint to post to.
            data (dict): The data to send in the request.
            files (dict, optional): The files to send in the request.

        Returns:
            dict: The JSON response from the API.

        Raises:
            HTTPError: If the response status code is not 200.
        """
        try:
            # Base headers for authorization
            headers = {"Authorization": f"Bearer {self.api_token}"}

            if files:
                # For multipart/form-data requests with files, do not set Content-Type
                response = requests.post(
                    url=f"{self.base_url}{endpoint}", headers=headers, data=data, files=files
                )
            else:
                # For application/json requests without files, set Content-Type to application/json
                headers["Content-Type"] = "application/json"
                response = requests.post(
                    url=f"{self.base_url}{endpoint}", headers=headers, json=data
                )

            # response.raise_for_status()
            if not response.ok:
                error_details = response.json().get('detail', 'No details provided.')
                raise APIRequestError(f"API request failed with status {response.status_code}: {response.reason}",
                            status_code=response.status_code, details=error_details)

            return response.json()

        except Exception as e:
            error_message = self._get_error_message(e)
            raise Exception(f"Failed to create meta: {error_message}")

    # Create a ack method to make GET requests to the API to make sure the server is up and token is valid
    def ack(self):
        """
        Acknowledges the API server and token.

        Returns:
            dict: The JSON response from the API.
        """
        try:
            response = self._get("/ack")
            return response
        except Exception as e:
            error_message = self._get_error_message(e)
            raise Exception(f"Failed to acknowledge server: {error_message}")

    # Create a _get method to make GET requests to the API
    def _get(self, endpoint):
        """
        Private method to make GET requests to the API.

        Args:
            endpoint (str): The API endpoint to get from.

        Returns:
            dict: The JSON response from the API.

        Raises:
            HTTPError: If the response status code is not 200.
        """
        try:
            response = requests.get(
                url=f"{self.base_url}{endpoint}", headers=self.headers)

            # response.raise_for_status()
            if not response.ok:
                # Create a custom exception that includes the response object
                raise requests.HTTPError(
                    f'{response.status_code} Error: {response.reason}', response=response)

            return response.json()
        except Exception as e:
            error_message = self._get_error_message(e)
            raise Exception(f"Failed to get data: {error_message}")

    def _get_error_message(self, e):
        try:
            if hasattr(e, 'response'):
                response = e.response
                error_message = response.json().get('detail', response.text)
            else:
                error_message = e
        except:
            error_message = response.text
        return error_message

    def save_data(self, data, data_type, output_name):
        """
        Saves the JSON data to a file in the stucent directory.

        Args:
            data (dict): The JSON data to save.
            data_type (str): The type of the data (meta, outline, course, activities).
            output_name (str): The name of the output file.
        """
        try:
            # Define the file path
            file_path = f"{stucent_dir}/{data_type}_{output_name}.json"

            # Save the data to the file
            with open(file_path, 'w') as file:
                json.dump(data, file)
        except Exception as e:
            print(f"Failed to save data: {str(e)}")

    def load_data(self, data_type, output_name):
        """
        Loads JSON data from a file in the stucent directory.

        Args:
            data_type (str): The type of the data (meta, outline, course, activities).
            output_name (str): The name of the output file.

        Returns:
            dict: The loaded JSON data.
        """
        try:
            # Define the file path
            file_path = f"{stucent_dir}/{data_type}_{output_name}.json"

            # Load the data from the file
            with open(file_path, 'r') as file:
                data = json.load(file)

            return data
        except Exception as e:
            print(f"Failed to load data: {str(e)}")
            return None

    def getTaskStatus(self, task_id: str, output_name: str = None, load_exists=False) -> TaskStatusResponse:
        """
        Private method to poll the status of an asynchronous task.

        Args:
            task_id (str): The ID of the task to check.

        Returns:
            TaskStatusResponse: The status of the task.
        """
        if os.path.exists(f"{stucent_dir}/task_{task_id}.json"):
            with open(f"{stucent_dir}/task_{output_name}.json", "r") as r:
                return TaskStatusResponse.model_validate_json(r.read())
        repeat = 0
        while True or repeat < 30:
            try:
                # response = requests.get(url=f"{self.base_url}/task-status/{task_id}", headers=self.headers)
                response = self._get(f"/task-status/{task_id}")

                task_status = TaskStatusResponse(**response)
                if task_status.status == 'NOT_FOUND':
                    return None
                if task_status.status == 'FAILURE':
                    raise Exception(task_status.error)
                if task_status.status == 'SUCCESS':
                    if task_status.id in self.last_usage:
                        usage = task_status.usage
                        self.last_usage[task_status.id] = usage

                    if output_name:
                        with open(f"{stucent_dir}/task_{output_name}.json", "w") as w:
                            w.write(task_status.model_dump_json(
                                indent=2, exclude_none=True))
                    return task_status
                time.sleep(1)
                repeat += 1
            except Exception as e:
                error_message = self._get_error_message(e)
                raise Exception(f"Failed to get task status: {error_message}")

    def createMeta(self, request: CourseMetaRequest, output_name: str = None, load_exists=False) -> CourseMeta:
        """
        Creates course metadata.

        Args:
            request (CourseMetaRequest): The request data for creating course metadata.
            output_name (str, optional): The name of the output file.

        Returns:
            CourseMeta: The created course metadata.
        """
        try:
            if os.path.exists(f"{stucent_dir}/meta_{output_name}.json"):
                with open(f"{stucent_dir}/meta_{output_name}.json", "r") as r:
                    return CourseMeta.model_validate_json(r.read())
            response = self._post("/generate/course-meta",
                                  request.model_dump())
            usage = response.get('usage', {})
            self.last_usage['meta'] = usage
            meta = CourseMeta(**response['data'])
            if output_name:
                with open(f"{stucent_dir}/meta_{output_name}.json", "w") as w:
                    w.write(meta.model_dump_json(indent=2, exclude_none=True))
            return meta
        except Exception as e:
            error_message = self._get_error_message(e)
            raise Exception(f"Failed to create meta: {error_message}")

    def generateOutline(self, request: CourseOutlineRequest,  output_name: str = None, load_exists=False) -> CourseTree:
        """
        Creates a course outline.

        Args:
            request (CourseOutlineRequest): The request data for creating a course outline.

        Returns:
            CourseTree: The created course outline.
        """
        try:
            if os.path.exists(f"{stucent_dir}/outline_{output_name}.json"):
                with open(f"{stucent_dir}/outline_{output_name}.json", "r") as r:
                    return CourseTree.model_validate_json(r.read())
            response = self._post(
                "/generate/course-outline", request.model_dump())
            usage = response.get('usage', {})
            self.last_usage['outline'] = usage
            outline = CourseTree(**response['data'])
            if output_name:
                with open(f"{stucent_dir}/outline_{output_name}.json", "w") as w:
                    w.write(outline.model_dump_json(
                        indent=2, exclude_none=True))
            return outline
        except Exception as e:
            error_message = self._get_error_message(e)
            raise Exception(f"Failed to create outline: {error_message}")

    def generateActivity3(self, request, o):
        print ("ddd")

    def generateActivity1(self, request: ActivityRequest,  output_name: str = None, load_exists=False) -> Activities:
        """
        Creates course activities individually.
        """
        try:
            if os.path.exists(f"{stucent_dir}/activity_{output_name}.json"):
                with open(f"{stucent_dir}/activity_{output_name}.json", "r") as r:
                    return Activities.model_validate_json(r.read())
            response = self._post("/generate/activity", request.model_dump())
            usage = response.get('usage', {})
            self.last_usage['activity'] = usage
            activitis = Activities(**response['data'])
            if output_name:
                with open(f"{stucent_dir}/activity_{output_name}.json", "w") as w:
                    w.write(activitis.model_dump_json(
                        indent=2, exclude_none=True))
            return activitis
        except Exception as e:
            error_message = self._get_error_message(e)
            raise Exception(f"Failed to create activity: {error_message}")

    def generateLessonActivities(self, request: LessonActivitiesRequest) -> TaskStatusResponse:
        """
        Initiates the generation of lesson activities and returns the task status.

        Args:
            request (LessonActivitiesRequest): The request data for lesson activities generation.

        Returns:
            TaskStatusResponse: The status of the lesson activities generation task.
        """
        try:
            response = self._post(
                "/generate/lesson-activities", request.dict())
            usage = response.get('usage', {})
            self.last_usage[response.get('id', 'last')] = usage
            return TaskStatusResponse(**response)
        except Exception as e:
            error_message = self._get_error_message(e)
            raise Exception(
                f"Failed to generate lesson activities: {error_message}")

    def generateCourseActivities(self, request: CourseActivitiesRequest,  output_name: str = None, load_exists=False) -> TaskStatusResponse:
        """
        Initiates the generation of course activities and returns the task status.

        Args:
            request (CourseActivitiesRequest): The request data for course activities generation.

        Returns:
            TaskStatusResponse: The status of the course activities generation task.
        """
        try:
            if os.path.exists(f"{stucent_dir}/task_{output_name}.json"):
                with open(f"{stucent_dir}/task_{output_name}.json", "r") as r:
                    return TaskStatusResponse.model_validate_json(r.read())

            response = self._post(
                "/generate/course-activities", request.dict())
            usage = response.get('usage', {})
            self.last_usage[response.get('id', 'last')] = usage
            task = TaskStatusResponse(**response)
            return task
        except Exception as e:
            error_message = self._get_error_message(e)
            raise Exception(
                f"Failed to generate course activities: {error_message}")

    def generateDebugCourseActivities(self, request: CourseActivitiesRequest) -> TaskStatusResponse:
        """
        Initiates the generation of course activities and returns the task status.

        Args:
            request (CourseActivitiesRequest): The request data for course activities generation.

        Returns:
            TaskStatusResponse: The status of the course activities generation task.
        """
        try:
            response = self._post("/debug/course-activities", request.dict())
            return TaskStatusResponse(**response)
        except Exception as e:
            error_message = self._get_error_message(e)
            raise Exception(
                f"Failed to generate course activities: {error_message}")

    def generateDebugLessonActivities(self, request: LessonActivitiesRequest) -> TaskStatusResponse:
        """
        Initiates the generation of lesson activities and returns the task status.

        Args:
            request (LessonActivitiesRequest): The request data for lesson activities generation.

        Returns:
            TaskStatusResponse: The status of the lesson activities generation task.
        """
        try:
            response = self._post("/debug/lesson-activities", request.dict())
            return TaskStatusResponse(**response)
        except Exception as e:
            error_message = self._get_error_message(e)
            raise Exception(
                f"Failed to generate lesson activities: {error_message}")

    def createTemplate(self, target: str, request: RegisterRequest) -> str:
        """
        Creates a new template.

        Args:
            target (str): The target category for the template.
            request (RegisterRequest): The request data for template creation.

        Returns:
            str: The unique name of the created template.
        """
        try:
            response = self._post(f"/templates/{target}", request.model_dump())
            return response.get("id", None)
        except Exception as e:
            error_message = self._get_error_message(e)
            raise Exception(f"Failed to create template: {error_message}")

    def getTemplateContent(self, target: str, template_name: str) -> str:
        """
        Retrieves the content of a specified template.

        Args:
            target (str): The target category of the template.
            template_name(str): The name of the template.

        Returns:
            str: The content of the template.
        """
        try:
            response = self._get(f"/templates/{target}/{template_name}")
            return response
        except Exception as e:
            error_message = self._get_error_message(e)
            raise Exception(f"Failed to get template content: {error_message}")
        # response = requests.get(
        #     url=f"{self.base_url}/templates/{target}/{template_name}", headers=self.headers
        # )
        # response.raise_for_status()
        # return response.text

    def generateOutlineSchema(self, request: SchemaRequest) -> dict:
        """
        Creates a course outline schema.

        Args:
            request (SchemaRequest): The request data for creating an outline schema.

        Returns:
            dict: The created outline schema.
        """
        try:
            response = self._post("/generate/outline-schema", request.dict())
            return response
        except Exception as e:
            error_message = self._get_error_message(e)
            raise Exception(
                f"Failed to create outline schema: {error_message}")

    def generateContext(
            self,
            contextRequest: ContextRequest,
            output_name: str = None, load_exists=False) -> TaskStatusResponse:
        """
        Generates context from an uploaded resource file.

        Args:
            file_path (str): The path to the file to upload.
            storage_id (str): The ID for the storage.
            storage_description (str): The description for the storage.

        Returns:
            TaskStatusResponse: The status of the context generation task.
        """
        if not os.path.exists(contextRequest.file_path):
            raise Exception(f"File does not exist: {contextRequest.file_path}")

        if output_name:
            if os.path.exists(f"{stucent_dir}/task_{output_name}.json"):
                with open(f"{stucent_dir}/task_{output_name}.json", "r") as r:
                    return TaskStatusResponse.model_validate_json(r.read())

        try:
            url = f"/generate/context-from-resource"
            # Open the file in binary read mode
            with open(contextRequest.file_path, 'rb') as file:
                files = {'file': (os.path.basename(
                    contextRequest.file_path), file, 'text/plain')}
                data = contextRequest.model_dump()

                response = self._post(url, data, files)
                return TaskStatusResponse(**response)
        except Exception as e:
            error_message = self._get_error_message(e)
            raise Exception(f"Failed to generate context: {error_message}")

    @classmethod
    def generate_markdown_outline(self, data, prefix='', indent=0):
        markdown = ""
        if isinstance(data, dict):
            course_title = data.get('title', '')
            node_type = data.get('node_type', '').capitalize()
            objective = data.get('objective', '')
            if course_title:
                if objective:
                    markdown += f"{indent * '  '}{prefix} {node_type} {course_title}: {objective}\n"
                else:
                    markdown += f"{indent * '  '}{prefix} {node_type} {course_title}\n"
            if 'nodes' in data and data['nodes']:
                for index, node in enumerate(data['nodes'], start=1):
                    markdown += self.generate_markdown_outline(node, prefix=f"{prefix}{index}." , indent=indent+1)
        elif isinstance(data, list):
            for item in data:
                markdown += self.generate_markdown_outline(item, prefix)
        return markdown