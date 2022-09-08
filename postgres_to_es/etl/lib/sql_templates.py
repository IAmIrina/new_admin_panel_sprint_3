"""SQL query templates."""

get_modified_records = """
    SELECT id, modified FROM {table}
    WHERE modified > %(modified)s
    ORDER BY modified
    LIMIT %(page_size)s
"""

get_movie_info_by_id = """
    SELECT
        film_work.id as id,
        film_work.rating as imdb_rating,
        film_work.title as title,
        film_work.description as description,
        film_work.modified,
        COALESCE (
            json_agg(
                DISTINCT jsonb_build_object(
                    'role', pfw.role,
                    'id', person.id,
                    'name', person.full_name
                )
            ) FILTER (WHERE person.id is not null),
            '[]'
        ) as persons,
        array_agg(DISTINCT genre.name) as genre
    FROM content.film_work
        LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = film_work.id
        LEFT JOIN content.person ON person.id = pfw.person_id
        LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = film_work.id
        LEFT JOIN content.genre  ON genre.id = gfw.genre_id
    WHERE {where_clause_table}.id in %(pkeys)s
    AND film_work.id::text > %(last_id)s
    GROUP BY film_work.id
    ORDER BY film_work.id
    LIMIT %(page_size)s;
"""
