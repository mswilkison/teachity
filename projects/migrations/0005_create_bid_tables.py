# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BidFile'
        db.create_table('projects_bidfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bid', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bid_files', to=orm['projects.Bid'])),
            ('bid_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('scanned', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('unsafe', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('projects', ['BidFile'])

        # Adding model 'Bid'
        db.create_table('projects_bid', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='project_bids', to=orm['projects.Project'])),
            ('tutor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tutor_bids', to=orm['users.Tutor'])),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('budget_type', self.gf('django.db.models.fields.CharField')(default='', max_length=7)),
            ('budget', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('awarded', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('declined', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('projects', ['Bid'])


    def backwards(self, orm):
        # Deleting model 'BidFile'
        db.delete_table('projects_bidfile')

        # Deleting model 'Bid'
        db.delete_table('projects_bid')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'projects.bid': {
            'Meta': {'object_name': 'Bid'},
            'awarded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'budget': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'budget_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '7'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'declined': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'project_bids'", 'to': "orm['projects.Project']"}),
            'tutor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tutor_bids'", 'to': "orm['users.Tutor']"})
        },
        'projects.bidfile': {
            'Meta': {'object_name': 'BidFile'},
            'bid': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bid_files'", 'to': "orm['projects.Bid']"}),
            'bid_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'scanned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unsafe': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'projects.category': {
            'Meta': {'object_name': 'Category'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'projects.project': {
            'Meta': {'object_name': 'Project'},
            'budget': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'budget_type': ('django.db.models.fields.CharField', [], {'default': "'hourly'", 'max_length': '7'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Category']", 'on_delete': 'models.PROTECT'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'project_type': ('django.db.models.fields.CharField', [], {'default': "'one time'", 'max_length': '10'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'projects'", 'to': "orm['users.Student']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'projects.projectfile': {
            'Meta': {'object_name': 'ProjectFile'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'project_files'", 'to': "orm['projects.Project']"}),
            'project_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'scanned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unsafe': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'projects.requiredskill': {
            'Meta': {'object_name': 'RequiredSkill'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'required_skills'", 'to': "orm['projects.Project']"})
        },
        'users.country': {
            'Meta': {'object_name': 'Country'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'users.student': {
            'Meta': {'object_name': 'Student', '_ormbases': ['users.UserProfile']},
            'userprofile_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['users.UserProfile']", 'unique': 'True', 'primary_key': 'True'})
        },
        'users.timezone': {
            'Meta': {'object_name': 'Timezone'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'users.tutor': {
            'Meta': {'object_name': 'Tutor', '_ormbases': ['users.UserProfile']},
            'institution': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'other_qualifications': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'skills': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'userprofile_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['users.UserProfile']", 'unique': 'True', 'primary_key': 'True'})
        },
        'users.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'bio': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Country']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'picture': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'timezone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Timezone']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['projects']
