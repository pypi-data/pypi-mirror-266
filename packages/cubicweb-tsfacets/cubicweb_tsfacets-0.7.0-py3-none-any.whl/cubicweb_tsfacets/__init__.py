"""cubicweb-tsfacets application package

This cube implements facets using postgresql text search vectors.
"""

import re
import string

from rql import RQLHelper

from cubicweb.server.querier import QuerierHelper, manual_build_descr
from cubicweb.server.sources.rql2sql import SQLGenerator


INVALID_TSQUERY_CHARS = string.punctuation + "\0"
SANITIZE_TRANSMAP = str.maketrans(
    INVALID_TSQUERY_CHARS, len(INVALID_TSQUERY_CHARS) * " "
)


class TSFacetsSQLGenerator(SQLGenerator):
    def __init__(self, schema, dbhelper, tsft_table, tsft_where):
        super().__init__(schema, dbhelper)
        self.tsft_table = tsft_table
        self.tsft_where = tsft_where

    def _solutions_sql(self, select, solutions, distinct, needalias):
        sqls = []
        for solution in solutions:
            self._state.reset(solution)
            # visit restriction subtree
            if select.where is not None:
                self._state.add_restriction(select.where.accept(self))
            sql = [self._selection_sql(select.selection, distinct, needalias)]
            main_variable = re.search(
                r"^SELECT(\sDISTINCT)?\s(?P<main_var>\w+\.\w+)", sql[0]
            )["main_var"]
            if self._state.restrictions:
                where_part = " AND ".join(self._state.restrictions)
                sql.append(
                    f"WHERE {where_part} AND {self.tsft_where} AND TSFT.eid = {main_variable}"
                )
            else:
                sql.append(f"WHERE {self.tsft_where} AND TSFT.eid = {main_variable}")
            self._state.merge_source_cbs(self._state._needs_source_cb)
            # add required tables
            assert len(self._state.actual_tables) == 1, self._state.actual_tables
            tables = self._state.tables_sql()
            if tables:
                tables += f", {self.tsft_table} as TSFT"
                sql.insert(1, f"FROM {tables}")
            else:
                sql.insert(1, f"FROM {self.tsft_table} as TSFT")
            sqls.append("\n".join(sql))
        if distinct:
            return "\nUNION\n".join(sqls)
        else:
            return "\nUNION ALL\n".join(sqls)


def convert_rql_to_sql(cnx, rql, rql_args=None, sql_generator=None):
    rqlhelper = RQLHelper(
        cnx.vreg.schema,
        special_relations={"eid": "uid", "has_text": "fti"},
        backend="postgres",
    )
    qhelper = QuerierHelper(cnx.repo, cnx.vreg.schema)
    union = rqlhelper.parse(rql)
    rqlhelper.compute_solutions(union)
    rqlhelper.simplify(union)
    plan = qhelper.plan_factory(union, {}, cnx)
    plan.preprocess(union)
    for select in union.children:
        select.solutions.sort(key=lambda x: list(x.items()))
    if sql_generator is None:
        dbhelper = cnx.repo.system_source.dbhelper
        sql_generator = SQLGenerator(cnx.vreg.schema, dbhelper)
    sql, args, _ = sql_generator.generate(union, rql_args)
    return sql, args


def build_rset_descr(cnx, rql, args, results):
    rqlhelper = RQLHelper(
        cnx.vreg.schema,
        special_relations={"eid": "uid", "has_text": "fti"},
        backend="postgres",
    )
    rqlst = rqlhelper.parse(rql)
    rqlhelper.compute_solutions(rqlst, {"eid": cnx.entity_type}, kwargs=args)
    return manual_build_descr(cnx, rqlst, args, results)


def convert_to_tsquery(search_string: str) -> str:
    """build a ready-to-use tsquery

    remove all invalid / potential ts_ operators and add
    ':*' at the end of each word to perform a prefixed search.
    """
    sanitized = search_string.translate(SANITIZE_TRANSMAP)
    return "&".join(f"{chunk}:*" for chunk in sanitized.split())


def includeme(config):
    pass
