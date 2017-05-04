# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class LastTweet(models.Model):
    latest_tweet_number = models.BigIntegerField(blank=True, null=True)
    updated = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'last_tweet'


class UserLocations(models.Model):
    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=40)
    lat = models.FloatField()
    lon = models.FloatField()

    def __str__(self):
        return self.location_name

    class Meta:
        managed = True
        db_table = 'user_locations'


class People(models.Model):
    person_id = models.AutoField(primary_key=True)
    person_name = models.CharField(max_length=40)
    location = models.ForeignKey('UserLocations', models.DO_NOTHING)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=40)

    def __str__(self):
        return self.person_name

    class Meta:
        managed = True
        db_table = 'people'


class Pokedex(models.Model):
    pokedex_id = models.AutoField(primary_key=True)
    pokemon_num = models.IntegerField()
    pokemon_name = models.CharField(max_length=40)
    updated = models.DateTimeField()

    def __str__(self):
        return self.pokemon_name

    class Meta:
        managed = True
        db_table = 'pokedex'


class PokeFilters(models.Model):
    filter_id = models.AutoField(primary_key=True)
    person = models.ForeignKey('People', models.DO_NOTHING)
    pokemon = models.ForeignKey('Pokedex', models.DO_NOTHING)
    max_dist_km = models.FloatField()
    min_iv_pct = models.IntegerField()
    active = models.IntegerField()

    def __str__(self):
        return str(self.person) + " - " + str(self.pokemon)

    class Meta:
        managed = True
        db_table = 'poke_filters'
