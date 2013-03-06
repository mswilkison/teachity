from django.contrib import admin

from .models import Bid
from .models import BidFile
from .models import Category
from .models import Project
from .models import ProjectFile
from .models import RequiredSkill


class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 1


class RequiredSkillInline(admin.StackedInline):
    model = RequiredSkill
    extra = 1


class ProjectAdmin(admin.ModelAdmin):
    inlines = (RequiredSkillInline, ProjectFileInline)
    list_display = ('title', 'student', 'published', 'completed', 'created', 'modified')
    list_filter = ('published', 'completed', 'project_type', 'budget_type')
    search_fields = ('title', 'description', 'category__title')
    date_hierarchy = 'created'


class BidFileInline(admin.TabularInline):
    model = BidFile


class BidAdmin(admin.ModelAdmin):
    inlines = (BidFileInline,)
    readonly_fields = ('budget_type',)
    list_display = ('description', 'budget_type', 'get_budget_display', 'awarded', 'declined')
    fieldsets = ((None, {'fields': ('project', 'tutor', 'description',
                                    'budget_type', 'budget', 'awarded',
                                    'declined')
                        }),
                )
    list_filter = ('awarded', 'declined', 'budget_type')
    search_fields = ('description',)
    date_hierarchy = 'created'


admin.site.register(Bid, BidAdmin)
admin.site.register(Project, ProjectAdmin)

admin.site.register(Category)
