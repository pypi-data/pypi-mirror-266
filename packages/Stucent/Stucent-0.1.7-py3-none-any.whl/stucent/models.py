from typing import Optional, Literal, Union, List, Tuple, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import Union


# ========================================== RESPONSE MODELS =============================================
# Cretae a model has one ue attribute "usage" which is a dictionary and data which is union of CoursMeta, CourseTree and Context

class CourseMeta(BaseModel):
    titles: List[str] = Field(default_factory=list)
    description: str = ""
    learning_objectives: List[str] = Field(default_factory=list)
    target_audience: str = ""
    prerequisites: Union[str, List[str]] = ""
    topics: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)

class Context(BaseModel):
    context_name: Optional[str] = None
    storage_id: Optional[str] = None
    context_type: Optional[Literal['text', 'context']] = 'context'
    summary: Optional[str] = None
    query: Optional[str] = None
    retrieve_mode: Optional[Literal['summary', 'full', 'query']] = 'summary'
    mime_type: Optional[str] = None  # MIME type of the content
    content: Union[str, bytes] = ""  # Content of the context



## Activity models
class IntroVideo(BaseModel):
    title: str
    url: str
    activity_type: str = "introVideo"

class Lecture(BaseModel):
    title: str
    content: str
    activity_type: str = "lecture"

class Quiz(BaseModel):
    question: str
    options: List[str]
    correctAnswer: str
    activity_type: str = "quiz"

class Practice(BaseModel):
    task: str
    activity_type: str = "practice"

class Reading(BaseModel):
    title: str
    content: str
    activity_type: str = "reading"

class FillInTheBlank(BaseModel):
    statement: str
    options: List[str]
    correctAnswer: str
    activity_type: str = "fillInTheBlank"

class Essay(BaseModel):
    topic: str
    guidelines: str
    activity_type: str = "essay"

class Discussion(BaseModel):
    topic: str
    guidelines: str
    activity_type: str = "discussion"

# Union of all activity types
# ActivityType = Union[IntroVideo, Lecture, Quiz, Practice, Reading, FillInTheBlank, Essay, Discussion]
ActivityType = Dict[str, Any]

class Activity(BaseModel):
    activities: List[ActivityType]
    
class Activities(BaseModel):
    activities: Union[List[ActivityType], ActivityType]

class ContentNode(BaseModel):
    title: str
    node_type: str
    nodes: Optional[List['ContentNode']] = None
    activities: Optional[List[ActivityType]] = None
    class Config:
        extra = "allow"  # Allow extra fields

ContentNode.model_rebuild()

class CourseTree(BaseModel):
    courseTitle: str
    nodes: List[ContentNode]

    class Config:
        extra = "allow"  # Allow extra fields

class TaskStatusResponse(BaseModel):
    status: Literal['SUCCESS', 'PENDING', 'FAILURE', 'NOT_FOUND']
    id: Optional[str] = None
    lesson_activities: Optional[List[ActivityType]] = None
    course_content: Optional[CourseTree] = None
    data: Optional[Union[List[ActivityType], CourseTree, 'Context']] = None
    error: Optional[str] = None
    usage: Optional[dict] = None
    output_name: Optional[str] = None


    class Config:
        extra = "ignore"

# ========================================== REQUEST MODELS =============================================

# Model for agenerate_course_meta
class CourseMetaRequest(BaseModel):
    description: str
    prompt_name: Optional[str] = "course.meta"
    schema_name: Optional[str] = "course.meta"
    context: Optional[Union[Context, str]] = None
    request: Optional[str] = None
    revise: Optional[bool] = False
    revise: Optional[bool] = False

# Model for agenerate_course_outline
class CourseOutlineRequest(BaseModel):
    course_title: str
    course_meta: CourseMeta
    prompt_name: Optional[str] = "course.outline"
    schema_name: Optional[str] = "course.outline"
    nodes_count: List[Tuple[str, int]] = [("module", 2), ("unit", 2), ("lesson", 2)]
    context: Optional[Union[Context, str]] = None
    request: Optional[str] = None
    revise: Optional[bool] = False

class ActivityRequest(BaseModel):
    activity_type: str
    activity_count: int = 1
    previous_activities: Optional[list] = None
    activities_examples: Optional[str] = "lesson.activities"
    prompt_name: Optional[str] = "activity.solo"
    schema_name: Optional[str] = "activities"
    context: Optional[Union[Context, str]] = None
    request: Optional[dict] = None
    revise: Optional[bool] = False
    
    # If the given cintext is string convert it to Context object
    @validator('context', pre=True, always=True)
    def convert_str_to_context(cls, v):
        if isinstance(v, str):
            return Context(content=v)
        return v
        
# Model for agenerate_lesson_activities
class LessonActivitiesRequest(BaseModel):
    lesson_index: int
    course_title: str
    course_meta: CourseMeta
    selected_lesson: Union[Dict, ContentNode] 
    parent_node: Union[Dict, ContentNode]
    parent_node_type: str
    lesson_layout: List[str]
    prompt_name: Optional[str] = "lesson.activities"
    schema_name: Optional[str] = "activities"
    activities_examples: Optional[str] = "lesson.activities"
    context: Optional[Union[Context, str]] = None
    request: Optional[str] = None

# Model for agenerate_complete_course_content
class CourseActivitiesRequest(BaseModel):
    course_title: str
    course_meta: CourseMeta
    course_outline: CourseTree
    lesson_layout: List[str]
    prompt_name: Optional[str] = "lesson.activities"
    schema_name: Optional[str] = "activities"
    activities_examples: Optional[str] = "lesson.activities"
    context: Optional[Union[Context, str]] = None
    request: Optional[str] = None
    max_threads: Optional[int] = 5


class ContentType(str, Enum):
    JSON = "json"
    MD = "md"
    JINJA2 = "jinja2"

class RegisterRequest(BaseModel):
    name: str
    content_type: ContentType = ContentType.JSON
    content: str

class LevelProperty(BaseModel):
    type: str
    caption: str
    properties: Dict[str, str]
    # nodes: List['NodeProperty'] = []
    nextLevel: Optional['LevelProperty'] = None


LevelProperty.model_rebuild()


class SchemaRequest(BaseModel):
    # nodes: List[NodeProperty]
    root: LevelProperty


class BaseResponse(BaseModel):
    usage: Optional[dict] = None
    data: Optional[Union[CourseMeta, CourseTree, Context, Activities]] = None


class ContextRequest(BaseModel):
    context_name: str
    file_path: Optional[str] = None
    storage_id: Optional[str] = "default"
    storage_description: Optional[str] = None
    max_token: int = 3000
    merge: bool = True
    