REPLACE VIEW ${output_schema_name}.${output_view_name} AS
LOCKING ROW FOR ACCESS
${select_query}
