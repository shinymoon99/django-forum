from django.contrib import admin
from .models import (
    Answer,
    Buy,
    Question_Collector,
    Resource,
    Question,
    Profile,
    Comment,
    Resource_Collector,
    Schedule,
)

admin.site.register(Resource)
admin.site.register(Question)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Buy)
admin.site.register(Answer)
admin.site.register(Schedule)
admin.site.register(Question_Collector)
admin.site.register(Resource_Collector)
