from vizydrop.sdk.source import SourceSchema
from vizydrop.fields import *


class ApiExampleSchema(SourceSchema):
    id = TextField(name="ID")
    name = TextField(name="Name")
    publicationStage = TextField(name="Publication Stage")
    downloadCount = TextField(name="Download Count")
    viewCount = TextField(name="View Count")
    numberOfComments = TextField(name="Comment Count")
    owner = TextField(name="Owner", response_loc="owner-displayName")