"""

Configuration for the admin page

"""

from django.contrib import admin
from oppgavegen.models import Template, ExtendedUser, Level, Chapter, Set, Tag, UserLevelProgress
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class templateAdmin(admin.ModelAdmin):
    list_display = ('id','name','creation_date', 'question_text', 'answer','creator','editor', 'times_solved', 'times_failed')


class ExtendedInline(admin.StackedInline):
    model = ExtendedUser
    can_delete = False
    verbose_name_plural = 'extendeduser'


class UserAdmin(UserAdmin):
    inlines = (ExtendedInline, )


class LevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order')


class SetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_requirement')
    exclude = ('copy','is_requirement',) # These are excluded to prevent them from being set manually.
    # Remove the exclude line if you need to set these manually for testing, however these should be excluded in deployment


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class UserLevelProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'level')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Template, templateAdmin)
admin.site.register(Level,  LevelAdmin)
admin.site.register(Chapter,  ChapterAdmin)
admin.site.register(Set,  SetAdmin)
admin.site.register(Tag,  TagAdmin)
admin.site.register(UserLevelProgress, UserLevelProgressAdmin)
