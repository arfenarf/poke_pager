from django.contrib import admin

from .models import Pokedex, People, PokeFilters, UserLocations

admin.site.register(Pokedex)
admin.site.register(People)
admin.site.register(PokeFilters)
admin.site.register(UserLocations)
