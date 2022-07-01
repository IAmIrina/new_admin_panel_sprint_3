"""Sprint 2, Task 2 Movies API."""

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.jsonencoder import JSONEncoderDecimalSupport
from movies.models import Filmwork, PersonFilmwork


class MoviesApiMixin(object):
    """A mixin for Movies API views."""

    model = Filmwork
    http_method_names = ['get']

    genres = ArrayAgg(
        'genres__name',
        distinct=True,
    )
    actors = ArrayAgg(
        'persons__full_name',
        filter=Q(personfilmwork__role=PersonFilmwork.ACTOR),
        distinct=True,
    )
    directors = ArrayAgg(
        'persons__full_name',
        filter=Q(personfilmwork__role=PersonFilmwork.DIRECTOR),
        distinct=True,
    )
    writers = ArrayAgg(
        'persons__full_name',
        filter=Q(personfilmwork__role=PersonFilmwork.SCREENWRITER),
        distinct=True,
    )

    filmwork_qs = Filmwork.objects.prefetch_related('genres', 'persons').values(
    ).annotate(
        genres=genres,
    ).annotate(
        actors=actors,
    ).annotate(
        directors=directors,
    ).annotate(
        writers=writers,
    )

    def render_to_response(self, context, **response_kwargs):
        """Convert to JsonResponse with custom encoder."""
        return JsonResponse(context, encoder=JSONEncoderDecimalSupport)


class MoviesListApi(MoviesApiMixin, BaseListView):
    """GET Movies list API view."""

    paginate_by = 50

    def get_queryset(self):
        """Return movies list query set."""
        return self.filmwork_qs.order_by('title')

    def get_context_data(self, *, object_list=None, **kwargs):
        """Get context data using Paginator."""
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            self.get_queryset(),
            self.paginate_by,
        )
        return {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(queryset),
        }


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    """GET Movies list API view."""

    def get_queryset(self):
        """Return detailed movie query set."""
        return self.filmwork_qs.filter(id=self.kwargs['pk'])

    def get_context_data(self, *, object_list=None, **kwargs):
        """Get context data."""
        return dict(self.get_queryset().first())
