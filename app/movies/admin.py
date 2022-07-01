from django.contrib import admin

from . import models


@admin.register(models.Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description', 'id')


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ('full_name', 'id')


class GenreFilmworkInline(admin.TabularInline):
    model = models.GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = models.PersonFilmwork
    autocomplete_fields = ['person']


@admin.register(models.Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'type',
        'creation_date',
        'rating',
    )

    inlines = (GenreFilmworkInline, PersonFilmworkInline)

    list_per_page = 25
    list_filter = ('type', 'genres')
    search_fields = ('title', 'description', 'id')
    list_prefetch_related = ('persons', 'genres')
