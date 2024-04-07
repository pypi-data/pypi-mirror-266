# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lineagex']

package_data = \
{'': ['*'],
 'lineagex': ['examples/dependency_example/*',
              'examples/github_example/*',
              'examples/mimic-iii/*',
              'examples/mimic-iii/comorbidity/*',
              'examples/mimic-iii/demographics/*',
              'examples/mimic-iii/diagnosis/*',
              'examples/mimic-iii/durations/*',
              'examples/mimic-iii/firstday/*',
              'examples/mimic-iii/fluid_balance/*',
              'examples/mimic-iii/measurement/*',
              'examples/mimic-iii/medication/*',
              'examples/mimic-iii/organfailure/*',
              'examples/mimic-iii/sepsis/*',
              'examples/mimic-iii/severityscores/*',
              'examples/mimic-iii/treatment/*',
              'examples/mimic-iv/*',
              'examples/mimic-iv/comorbidity/*',
              'examples/mimic-iv/demographics/*',
              'examples/mimic-iv/firstday/*',
              'examples/mimic-iv/measurement/*',
              'examples/mimic-iv/medication/*',
              'examples/mimic-iv/organfailure/*',
              'examples/mimic-iv/score/*',
              'examples/mimic-iv/sepsis/*',
              'examples/mimic-iv/treatment/*']}

install_requires = \
['psycopg2-binary>=2.9.6,<3.0.0', 'sqlglot>=12.3.0,<13.0.0']

setup_kwargs = {
    'name': 'lineagex',
    'version': '0.0.20',
    'description': 'A column lineage tool',
    'long_description': '# Introduction\n\nA Column Level Lineage Graph for SQL.\n\nHave you ever wondered what is the column level relationship among your SQL scripts and base tables? \nDon\'t worry, this tool is intended to help you by creating an interactive graph on a webpage to explore the \ncolumn level lineage among them(Currently only supports Postgres, other connection types or dialects are under development).\n\n## How to run\nHere is a [live demo](https://zshandy.github.io/lineagex-demo/) with the [mimic-iv concepts_postgres](https://github.com/MIT-LCP/mimic-code/tree/main/mimic-iv/concepts_postgres) files([navigation instructions](https://sfu-db.github.io/lineagex/output.html#how-to-navigate-the-webpage)) and that is created with one line of code:\n\n```python\nfrom lineagex.lineagex import lineagex\n  \nlineagex(sql=path/to/sql, target_schema="schema1", conn_string="postgresql://username:password@server:port/database", search_path_schema="schema1, public")\n```\nCheck out more detailed usage and examples [here](https://sfu-db.github.io/lineagex/api.html). \n\n## What does it output\nThe input can be a path to a SQL file, a path to a folder containing SQL files, a list of SQLs or a list of view names and/or schemas. Optionally, you can provide less information with only the SQLs, but providing the schema information and database connection is highly recommended for the best result.\nThe output would be a output.json and a index.html file in the folder. Start a local http server and you would be able to see the interactive graph.\n<img src="https://raw.githubusercontent.com/sfu-db/lineagex/main/docs/example.gif"/>\nCheck out more detailed navigation instructions [here](https://sfu-db.github.io/lineagex/output.html#how-to-navigate-the-webpage).\n\n## Why use LineageX\nA general introduction of the project can be found in this [blog post](https://medium.com/@shz1/lineagex-the-python-library-for-your-lineage-needs-5e51b77a0032).\n- Automatic dependency creation: When there are dependency among the SQL files, and those tables are not yet in the database, LineageX will automatically tries to find the dependency table and creates it.\n- Clean and simple but very interactive user interface: The user interface is very simple to use with minimal clutters on the page while showing all of the necessary information.\n- Variety of SQL statements: LineageX supports a variety of SQL statements, aside from the typical `SELECT` statement, it also supports `CREATE TABLE/VIEW [IF NOT EXISTS]` statement as well as the `INSERT` and `DELETE` statement.\n- [dbt](https://docs.getdbt.com/) support: LineageX also implemented in the [dbt-LineageX](https://github.com/sfu-db/dbt-lineagex), it is added into a dbt project and by using the dbt library [fal](https://github.com/fal-ai/fal), it is able to reuse the Python core and create the similar output from the dbt project.\n\n## Supported JSON format:\nYou can upload JSON files into the HTML produced and draw its lineage graph. Here is the supported format:\n```javascript\n{\n    table_name: {\n        tables:[],\n        columns:{\n            column1: [[], []], // The first element is the list of columns that contribute directly to column1, \n                               // The second element is the list of columns that are referenced, such as columns from WHERE/GROUP BY\n            column2: [[], []]\n        },\n        table_name: "",\n        sql: "",\n    }, \n}\n```\nAs an example:\n```javascript\n{\n  table1: {\n    tables: [schema1.other_table], \n    columns: {\n      column1: [[schema1.other_table.columns1], [schema1.other_table.columns3]], \n      column2: [[schema1.other_table.columns2], [schema1.other_table.columns3]]\n    }, \n    table_name: schema1.table1,\n    sql: SELECT column1, column2 FROM schema1.other_table WHERE column3 IS NOT NULL;\n  }, \n}\n```\n\n# Supported Database Connection Types\nWhen entering the `conn_string` parameter, only supported databases\' connection types can be parsed successfully, or the lineage graph would be created as if no `conn_string` parameter is given.\n\n## Database Connection Types\n- [x] Postgres\n- [x] dbt-Postgres\n- [ ] Mysql\n- [ ] Sqlite\n- [ ] SQL Server\n- [ ] Oracle\n- [ ] ...\n\n\n# Documentation\nDoc: https://sfu-db.github.io/lineagex/intro.html or just [here](https://sfu-db.github.io/lineagex/intro.html)',
    'author': 'zshandy',
    'author_email': 'zshandy@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
