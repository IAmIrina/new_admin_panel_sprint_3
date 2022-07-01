import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

STRING_MAX_LENGTH = 255


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=STRING_MAX_LENGTH)
    description = models.TextField(_('description'), null=True, blank=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):

    full_name = models.CharField(_('name'), max_length=STRING_MAX_LENGTH)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):

    class TypeOfArtwork(models.TextChoices):
        MOVIE = 'movie', _('Movie')
        TV_SHOW = 'tv_show', _('TV Show')

    title = models.CharField(_('title'), max_length=STRING_MAX_LENGTH)
    description = models.TextField(_('description'), null=True, blank=True)
    creation_date = models.DateField(_('creation_date'), null=True, blank=True)
    rating = models.DecimalField(_('rating'), max_digits=5, decimal_places=1, null=True, blank=True,
                                 validators=[MinValueValidator(0),
                                             MaxValueValidator(100)])
    type = models.CharField(_('type'), choices=TypeOfArtwork.choices, max_length=STRING_MAX_LENGTH)
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('Movie')
        verbose_name_plural = _('Movies')

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE, verbose_name=_("Filmwork"))
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE, verbose_name=_("Genre"))
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')
        constraints = [
            models.UniqueConstraint(fields=['genre', 'film_work'], name='unique genres'),
        ]

    def __str__(self):
        return 'Genres'


class PersonFilmwork(UUIDMixin):
    DIRECTOR = 'director'
    SCREENWRITER = 'writer'
    ACTOR = 'actor'
    ROLES = [
        (DIRECTOR, _('Director')),
        (SCREENWRITER, _('Screen writer')),
        (ACTOR, _('Actor')),
    ]
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE, verbose_name=_("Filmwork"))
    person = models.ForeignKey('Person', on_delete=models.CASCADE, verbose_name=_("Person"))
    role = models.TextField(_('role'), choices=ROLES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')
        constraints = [
            models.UniqueConstraint(fields=['film_work', 'person', 'role'], name='unique persons'),
        ]
