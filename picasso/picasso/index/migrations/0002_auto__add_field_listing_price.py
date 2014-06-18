# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Listing.price'
        db.add_column(u'index_listing', 'price',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Listing.price'
        db.delete_column(u'index_listing', 'price')


    models = {
        u'index.address': {
            'Meta': {'object_name': 'Address', '_ormbases': [u'index.BaseModel']},
            'address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            u'basemodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['index.BaseModel']", 'unique': 'True', 'primary_key': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "'Toronto'", 'max_length': '100'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "'Canada'", 'max_length': '100'})
        },
        u'index.basemodel': {
            'Meta': {'object_name': 'BaseModel'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 6, 17, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'index.listing': {
            'Meta': {'object_name': 'Listing', '_ormbases': [u'index.BaseModel']},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['index.Address']", 'null': 'True'}),
            u'basemodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['index.BaseModel']", 'unique': 'True', 'primary_key': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10000'}),
            'listing_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['index.Tag']", 'symmetrical': 'False'})
        },
        u'index.review': {
            'Meta': {'object_name': 'Review', '_ormbases': [u'index.BaseModel']},
            u'basemodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['index.BaseModel']", 'unique': 'True', 'primary_key': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10000'}),
            'listing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['index.Listing']"}),
            'rating': ('django.db.models.fields.FloatField', [], {'default': '-1'})
        },
        u'index.tag': {
            'Meta': {'object_name': 'Tag', '_ormbases': [u'index.BaseModel']},
            u'basemodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['index.BaseModel']", 'unique': 'True', 'primary_key': 'True'}),
            'tag_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500'})
        }
    }

    complete_apps = ['index']