from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from opentok import OpenTokSDK

from users.models import Student
from users.models import Tutor


class Category(models.Model):
    """Category choices for projects."""
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __unicode__(self):
        return self.title


class ProjectFile(models.Model):
    """Supporting files for projects."""
    project_file = models.FileField(upload_to='project_files')
    project = models.ForeignKey('Project', related_name='project_files')
    scanned = models.BooleanField(default=False,
                                  help_text="True if this file "
                                             "has been virus scanned.")
    unsafe = models.BooleanField(default=False,
                                 help_text="True if this file has been "
                                            "flagged as unsafe.")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.project_file.path


class RequiredSkill(models.Model):
    """Skills required by projects."""
    name = models.CharField(max_length=100)
    project = models.ForeignKey('Project', related_name='required_skills')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class Project(models.Model):
    """A project posted by a student looking for a tutor."""
    student = models.ForeignKey(Student, related_name='projects')
    title = models.CharField(max_length=100)
    category = models.ForeignKey('Category', on_delete=models.PROTECT)
    description = models.TextField()
    project_type = models.CharField("Type of Project",
                                   max_length=10,
                                   default='one time',
                                   choices=(('one time', 'One Time'),
                                            ('recurring', 'Recurring')),
                                    help_text="Is this a recurring project \
                                               or a one-off?")
    budget_type = models.CharField("Type of Budget",
                                   max_length=7,
                                   default='hourly',
                                   choices=(('fixed', 'Fixed'),
                                            ('hourly', 'Hourly')))
    budget = models.DecimalField(max_digits=10, decimal_places=2,
                                 blank=True, null=True)
    published = models.BooleanField(default=False,
                                  help_text="False means the project is only \
                                             visible to its creator.")
    is_awarded = models.BooleanField(default=False,
                                     editable=False,
                                     help_text="Has this project been awarded "
                                               "to a tutor?")
    completed = models.BooleanField(default=False,
                                    help_text="Closes the project and marks it \
                                               as completed.")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('projects_view_detail', (), {'pk': self.pk})

    def save(self, *args, **kwargs):
        """Marks project as awarded if an awarded bid exists."""
        if self.project_bids.filter(awarded=True).exists():
            self.is_awarded = True
        else:
            self.is_awarded = False
        return super(Project, self).save(*args, **kwargs)

    def get_budget_display(self):
        if self.budget > 0:
            budget = '$%s' % self.budget
            if self.budget_type == 'hourly':
                budget = ''.join([budget, '/hour'])
        else:
            budget = '(%s)' % self.get_budget_type_display()
        return budget
    get_budget_display.short_description = 'budget'

    def get_status(self):
        """Returns a string indicating the project's current status.

        Possible values are:
            - 'Draft': Project hasn't been published yet.
            - 'Open': Project has been published.
            - 'Awarded': Project has an awarded bid
            - 'Closed': Project has been marked as complete.
        """
        if not self.published:
            return "Draft"
        elif not self.completed:
            if self.is_awarded:
                return "Awarded"
            return "Open"
        return "Closed"

    def get_tutor(self):
        """Projects can currently only have one tutor. If that changes this
        method will have to be replaced.

        Returns None if this project has no tutor.
        """
        try:
            tutor = self.project_bids.filter(awarded=True)[0].tutor
        except IndexError:
            return None
        return tutor


class BidFile(models.Model):
    """Supporting files for bids."""
    bid = models.ForeignKey('Bid', related_name='bid_files')
    bid_file = models.FileField(upload_to='bid_files')
    scanned = models.BooleanField(default=False,
                                  help_text="True if this file "
                                             "has been virus scanned.")
    unsafe = models.BooleanField(default=False,
                                 help_text="True if this file has been "
                                            "flagged as unsafe.")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.bid_file.path


class Bid(models.Model):
    """Bids on projects.
    
    Budget type is inferred from the project's budget type when the bid is
    submitted, but since the project's budget type can be edited we save it
    here as well.
    """
    project = models.ForeignKey('Project', related_name='project_bids')
    tutor = models.ForeignKey(Tutor, related_name='tutor_bids')
    description = models.TextField()
    budget_type = models.CharField("Type of Budget",
                                   max_length=7,
                                   default='',
                                   choices=(('fixed', 'Fixed'),
                                            ('hourly', 'Hourly')),
                                   help_text="This is set automatically when "
                                             "this bid is first saved based "
                                             "on the project's budget type.")
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    awarded = models.BooleanField(default=False,
                                  help_text="This bid has been accepted by "
                                            "the student.")
    declined = models.BooleanField(default=False,
                                   help_text="This bid has been rejected by "
                                             "the student.")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.description

    def save(self, update_budget_type=False, *args, **kwargs):
        """Sets budget type and project's awarded status.

        Budget type is only changed if budget_type doesn't have a value or
        if the update_budget_type argument is True, otherwise once it has
        been set it shouldn't be overridden.
        """
        if update_budget_type or not self.budget_type:
            self.budget_type = self.project.budget_type
        saved = super(Bid, self).save(*args, **kwargs)
        if self.awarded and not self.project.is_awarded:
            self.project.is_awarded = True
            self.project.save()
        return saved

    def get_budget_display(self):
        if self.budget > 0:
            budget = '$%s' % self.budget
            if self.budget_type == 'hourly':
                budget = ''.join([budget, '/hour'])
        else:
            budget = '(%s)' % self.get_budget_type_display()
        return budget
    get_budget_display.short_description = 'budget'

    def can_edit(self):
        """Bids can only be edited if their project is still open."""
        project_status = self.project.get_status()
        if project_status != "Open":
            return False
        return True


class Classroom(models.Model):
    """Chatrooms for projects.
    
    The session_id field stores the session id generated by the TokBox SDK.
    """
    project = models.OneToOneField(Project, related_name="classroom")
    session_id = models.CharField(max_length=100, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "Classroom for project: %s." % self.project

    @classmethod
    def create(cls, project):
        """Handles classroom creation.

        This method should be used instead of calling Classroom(**kwargs),
        unless you want to handle session creation manually.
        """
        # Create a classroom for the supplied project instance
        classroom = cls(project=project)
        # Create and assign a TokBox session
        api_key = settings.TOKBOX_API_KEY
        api_secret = settings.TOKBOX_API_SECRET
        opentok_sdk = OpenTokSDK.OpenTokSDK(api_key, api_secret)
        session_properties = {OpenTokSDK.SessionProperties.p2p_preference: "enabled"}
        session = opentok_sdk.create_session(None, session_properties)
        classroom.session_id = session.session_id
        classroom.save()
        return classroom


class Chatlog(models.Model):
    """Stores text chat for project classrooms."""
    classroom = models.ForeignKey(Classroom, related_name="chat_entries")
    user = models.ForeignKey(User)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.message
