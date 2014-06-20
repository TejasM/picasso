# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Address.address'
        db.delete_column(u'index_address', 'address')

        # Adding field 'Address.location'
        db.add_column(u'index_address', 'location',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1000),
                      keep_default=False)

        # Adding field 'Address.postal_code'
        db.add_column(u'index_address', 'postal_code',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)


        # Changing field 'Address.city'
        db.alter_column(u'index_address', 'city', self.gf('django.db.models.fields.CharField')(max_length=1000))
        # Adding field 'Review.user'
        db.add_column(u'index_review', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User'], null=True),
                      keep_default=False)

        # Adding field 'Listing.scraped_url'
        db.add_column(u'index_listing', 'scraped_url',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10000),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Address.address'
        db.add_column(u'index_address', 'address',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Deleting field 'Address.location'
        db.delete_column(u'index_address', 'location')

        # Deleting field 'Address.postal_code'
        db.delete_column(u'index_address', 'postal_code')


        # Changing field 'Address.city'
        db.alter_column(u'index_address', 'city', self.gf('django.db.models.fields.CharField')(max_length=100))
        # Deleting field 'Review.user'
        db.delete_column(u'index_review', 'user_id')

        # Deleting field 'Listing.scraped_url'
        db.delete_column(u'index_listing', 'scraped_url')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'index.address': {
            'Meta': {'object_name': 'Address', '_ormbases': [u'index.BaseModel']},
            u'basemodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['index.BaseModel']", 'unique': 'True', 'primary_key': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "'Toronto'", 'max_length': '1000'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "'Canada'", 'max_length': '100'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'})
        },
        u'index.basemodel': {
            'Meta': {'object_name': 'BaseModel'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 6, 19, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'index.listing': {
            'Meta': {'object_name': 'Listing', '_ormbases': [u'index.BaseModel']},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['index.Address']", 'null': 'True'}),
            u'basemodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['index.BaseModel']", 'unique': 'True', 'primary_key': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10000'}),
            'listing_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'scraped_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10000'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['index.Tag']", 'symmetrical': 'False'})
        },
        u'index.review': {
            'Meta': {'object_name': 'Review', '_ormbases': [u'index.BaseModel']},
            u'basemodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['index.BaseModel']", 'unique': 'True', 'primary_key': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10000'}),
            'listing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['index.Listing']"}),
            'rating': ('django.db.models.fields.FloatField', [], {'default': '-1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'null': 'True'})
        },
        u'index.tag': {
            'Meta': {'object_name': 'Tag', '_ormbases': [u'index.BaseModel']},
            u'basemodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['index.BaseModel']", 'unique': 'True', 'primary_key': 'True'}),
            'tag_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500'})
        }
    }

    complete_apps = ['index']