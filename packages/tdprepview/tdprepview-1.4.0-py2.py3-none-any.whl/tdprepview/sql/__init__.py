import os
from string import Template

current_directory = os.path.dirname(os.path.abspath(__file__))
PATHS_TO_DIR  =  os.path.join(current_directory, "templates")


def get_template(template_name):
    assert template_name in ["from","replaceview","withas"]
    filepath = os.path.join(PATHS_TO_DIR,f"{template_name}.sql")
    with open(filepath, "r", encoding="utf-8") as sql_file:
        strSqlTemplate = sql_file.read()
    objSqlTemplate = Template(strSqlTemplate)
    return objSqlTemplate
