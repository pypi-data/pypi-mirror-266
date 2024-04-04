{% macro get_merge_sql(target, source, unique_key, dest_columns, predicates=none) -%}
  {{ adapter.dispatch('get_merge_sql', 'dbt')(target, source, unique_key, dest_columns, predicates) }}
{%- endmacro %}

{% macro db2_for_i__get_merge_sql(target, source, unique_key, dest_columns, predicates) -%}
    {%- set predicates = [] if predicates is none else [] + predicates -%}
    {%- set dest_cols_csv = get_quoted_csv(dest_columns | map(attribute="name")) -%}
    {%- set update_columns = config.get('merge_update_columns', default = dest_columns | map(attribute="quoted") | list) -%}
    {%- set sql_header = config.get('sql_header', none) -%}

    {% if unique_key %}
        {% if unique_key is sequence and unique_key is not mapping and unique_key is not string %}
            {% for key in unique_key %}
                {% set this_key_match %}
                    DBT_INTERNAL_SOURCE.{{ key }} = DBT_INTERNAL_DEST.{{ key }}
                {% endset %}
                {% do predicates.append(this_key_match) %}
            {% endfor %}
        {% else %}
            {% set unique_key_match %}
                DBT_INTERNAL_SOURCE.{{ unique_key }} = DBT_INTERNAL_DEST.{{ unique_key }}
            {% endset %}
            {% do predicates.append(unique_key_match) %}
        {% endif %}
    {% else %}
        {% do predicates.append('FALSE') %}
    {% endif %}

    {{ sql_header if sql_header is not none }}

    merge into {{ target }} as DBT_INTERNAL_DEST
        using {{ source }} as DBT_INTERNAL_SOURCE
        on {{ predicates | join(' and ') }}

    {% if unique_key %}
    when matched then update set
        {% for column_name in update_columns -%}
            DBT_INTERNAL_DEST.{{ column_name }} = DBT_INTERNAL_SOURCE.{{ column_name }}
            {%- if not loop.last %}, {%- endif %}
        {%- endfor %}
    {% endif %}

    when not matched then insert
        ({{ dest_cols_csv }})
    values
        (
            {%- for col in dest_columns -%}
                DBT_INTERNAL_SOURCE.{{ col.name }}
            {%- if not loop.last -%}, {% endif %}
            {%- endfor -%}
        )

{% endmacro %}


{% macro get_delete_insert_merge_sql(target, source, unique_key, dest_columns, predicates=none) -%}
  {{ adapter.dispatch('get_delete_insert_merge_sql', 'dbt')(target, source, unique_key, dest_columns, predicates) }}
{%- endmacro %}

{% macro db2_for_i__get_delete_insert_merge_sql(target, source, unique_key, dest_columns) -%}

    {%- set dest_cols_csv = get_quoted_csv(dest_columns | map(attribute="name")) -%}

    {% if unique_key %}
        {% if unique_key is sequence and unique_key is not string %}
            DELETE FROM {{target }} AS _target
            WHERE EXISTS (
                SELECT * FROM {{ source }} AS _source
                WHERE (
                    {% for key in unique_key %}
                        _source.{{ key }} = _target.{{ key }}
                        {{ "and " if not loop.last }}
                    {% endfor %}
                )
            );
        {% else %}
            delete from {{ target }}
            where (
                {{ unique_key }}) in (
                select ({{ unique_key }})
                from {{ source }}
            );

        {% endif %}
    {% endif %}

    insert into {{ target }} ({{ dest_cols_csv }})
    (
        select {{ dest_cols_csv }}
        from {{ source }}
    )

{%- endmacro %}


{% macro get_insert_overwrite_merge_sql(target, source, dest_columns, predicates, include_sql_header=false) -%}
  {{ adapter.dispatch('get_insert_overwrite_merge_sql', 'dbt')(target, source, dest_columns, predicates, include_sql_header) }}
{%- endmacro %}

{% macro db2_for_i__get_insert_overwrite_merge_sql(target, source, dest_columns, predicates, include_sql_header) -%}
    {#-- The only time include_sql_header is True: --#}
    {#-- BigQuery + insert_overwrite strategy + "static" partitions config --#}
    {#-- We should consider including the sql header at the materialization level instead --#}

    {%- set predicates = [] if predicates is none else [] + predicates -%}
    {%- set dest_cols_csv = get_quoted_csv(dest_columns | map(attribute="name")) -%}
    {%- set sql_header = config.get('sql_header', none) -%}

    {{ sql_header if sql_header is not none and include_sql_header }}

    merge into {{ target }} as DBT_INTERNAL_DEST
        using {{ source }} as DBT_INTERNAL_SOURCE
        on FALSE

    when not matched by source
        {% if predicates %} and {{ predicates | join(' and ') }} {% endif %}
        then delete

    when not matched then insert
        ({{ dest_cols_csv }})
    values
        ({{ dest_cols_csv }})

{% endmacro %}
