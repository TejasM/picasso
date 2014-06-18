# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BaseModel'
        db.create_table(u'index_basemodel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 6, 17, 0, 0))),
        ))
        db.send_create_signal(u'index', ['BaseModel'])

        # Adding model 'Tag'
        db.create_table(u'index_tag', (
            (u'basemodel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['index.BaseModel'], unique=True, primary_key=True)),
            ('tag_name', self.gf('django.db.models.fields.CharField')(default='', max_length=500)),
        ))
        db.send_create_signal(u'index', ['Tag'])

        # Adding model 'Address'
        db.create_table(u'index_address', (
            (u'basemodel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['index.BaseModel'], unique=True, primary_key=True)),
            ('city', self.gf('django.db.models.fields.CharField')(default='Toronto', max_length=100)),
            ('country', self.gf('django.db.models.fields.CharField')(default='Canada', max_length=100)),
            ('address', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
        ))
        db.send_create_signal(u'index', ['Address'])

        # Adding model 'Listing'
        db.create_table(u'index_listing', (
            (u'basemodel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['index.BaseModel'], unique=True, primary_key=True)),
            ('listing_name', self.gf('django.db.models.fields.CharField')(default='', max_length=500)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=10000)),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['index.Address'], null=True)),
        ))
        db.send_create_signal(u'index', ['Listing'])

        # Adding M2M table for field tags on 'Listing'
        m2m_table_name = db.shorten_name(u'index_listing_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('listing', models.ForeignKey(orm[u'index.listing'], null=False)),
            ('tag', models.ForeignKey(orm[u'index.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['listing_id', 'tag_id'])

        # Adding model 'Review'
        db.create_table(u'index_review', (
            (u'basemodel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['index.BaseModel'], unique=True, primary_key=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(default='', max_length=10000)),
            ('rating', self.gf('django.db.models.fields.FloatField')(default=-1)),
            ('listing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['index.Listing'])),
        ))
        db.send_create_signal(u'index', ['Review'])


    def backwards(self, orm):
        # Deleting model 'BaseModel'
        db.delete_table(u'index_basemodel')

        # Deleting model 'Tag'
        db.delete_table(u'index_tag')

        # Deleting model 'Address'
        db.delete_table(u'index_address')

        # Deleting model 'Listing'
        db.delete_table(u'index_listing')

        # Removing M2M table for field tags on 'Listing'
        db.delete_table(db.shorten_name(u'index_listing_tags'))

        # Deleting model 'Review'
        db.delete_table(u'index_review')


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