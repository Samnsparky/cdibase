"""Logic for managing user-generated database queries.

@author: Sam Pottinger
@license: GNU GPL v2
"""

from ..struct import models

import constants
import db_util
import oper_interp


FIELD_MAP = {
    'child_id': oper_interp.RawInterpretField('child_id'),
    'study_id': oper_interp.RawInterpretField('study_id'),
    'study': oper_interp.RawInterpretField('study'),
    'gender': oper_interp.GenderField('gender'),
    'birthday': oper_interp.DateInterpretField('birthday'),
    'session_date': oper_interp.DateInterpretField('session_date'),
    'session_num': oper_interp.NumericalField('session_num'),
    'words_spoken': oper_interp.NumericalField('words_spoken'),
    'items_excluded': oper_interp.NumericalField('items_excluded'),
    'age': oper_interp.NumericalField('age'),
    'total_num_sessions': oper_interp.NumericalField('total_num_sessions'),
    'percentile': oper_interp.NumericalField('percentile'),
    'extra_categories': oper_interp.NumericalField('extra_categories'),
    'MCDI_type': oper_interp.RawInterpretField('mcdi_type'),
    'specific_language': oper_interp.RawInterpretField('languages'),
    'num_languages': oper_interp.NumericalField('num_languages'),
    'hard_of_hearing': oper_interp.BooleanField('hard_of_hearing'),
    'deleted': oper_interp.BooleanField('deleted')
}

OPERATOR_MAP = {
    'eq': '==',
    'lt': '<',
    'gt': '>',
    'neq': '!=',
    'lteq': '<=',
    'gteq': '>='
}


class QueryInfo:
    """Information necessary to execute a user generated SQL select."""

    def __init__(self, filter_fields, query_str):
        """Create a structure containing info needed to run SQL select.

        @param filter_fields: The filters that are included in this select
            query.
        @type filter_fields: Iterable over oper.interp.FieldInfo
        @param query_str: SQL select statement with placeholders for operand
            values.
        @type query_str: str
        """
        self.filter_fields = filter_fields
        self.query_str = query_str


def build_query_component(field, operator, operand):
    if isinstance(operand, basestring):
        operands = operand.split(',')
    else:
        operands = [operand]
    query_subcomponents = []
    for operand in operands:
        template_vals = (field.get_field_name(), operator)
        query_subcomponents.append('%s %s ?' % template_vals)

    if len(operands) > 0:
        return '(' + ' OR '.join(query_subcomponents) + ')'
    else:
        return query_subcomponents[0]


def build_query(filters, table, statement_template):
    filter_fields = map(lambda x: x.field, filters)
    # TODO: might want to catch this as a security exception
    filter_fields = filter(lambda x: x in FIELD_MAP, filter_fields)
    filter_fields = map(lambda x: FIELD_MAP[x], filter_fields)

    operators = map(lambda x: x.operator, filters)
    operators = map(lambda x: x.encode('utf8'), operators)
    operators = filter(lambda x: x in OPERATOR_MAP, operators)
    operators = map(lambda x: OPERATOR_MAP[x], operators)

    operands = map(lambda x: x.operand, filters)

    fields_and_extraneous = zip(filter_fields, operators, operands)

    filter_fields_str = map(
        lambda (field, operator, operands): build_query_component(
            field,
            operator,
            operands
        ),
        fields_and_extraneous
    )
    clause = ' AND '.join(filter_fields_str)

    stmt = statement_template % (table, clause)

    return QueryInfo(filter_fields, stmt)


def build_search_query(filters, table):
    """Build a string SQL query from the given filters.

    @param filters: The filters to build the query out of.
    @type filters: Iterable over models.Filter
    @param table: The name of the table to query.
    @type table: str
    @return: SQL select query for the given table with the given filters.
    @rtype: str
    """
    return build_query(filters, table, 'SELECT * FROM %s WHERE %s')


def build_delete_query(filters, table, restore):
    if restore:
        return build_query(filters, table, 'UPDATE %s SET deleted=0 WHERE %s')
    else:
        return build_query(filters, table, 'UPDATE %s SET deleted=1 WHERE %s')


def run_search_query(filters, table, exclude_deleted=True):
    """Builds and runs a SQL select query on the given table with given filters.

    @param filters: The filters to build the query out of.
    @type: Iterable over models.Filter
    @param table: The name of the table to query.
    @type table: str
    @return: Results of SQL select query for the given table with the given
        filters.
    @rtype: Iterable over models.SnapshotMetadata
    """
    db_connection = db_util.get_db_connection()
    db_cursor = db_connection.cursor()

    if exclude_deleted:
        filters.append(models.Filter('deleted', 'eq', 0))

    query_info = build_search_query(filters, table)
    raw_operands = map(lambda x: x.operand, filters)
    filter_fields_and_operands = zip(query_info.filter_fields, raw_operands)
    operands = map(
        lambda (field, operand): field.interpret_value(operand),
        filter_fields_and_operands
    )

    operands_flat = []
    for operand in operands:
        operands_flat.extend(operand)

    db_cursor.execute(query_info.query_str, operands_flat)

    ret_val = map(lambda x: models.SnapshotMetadata(*x), db_cursor.fetchall())
    db_connection.close()
    return ret_val


def run_delete_query(filters, table, restore):
    """Builds and runs a SQL select query on the given table with given filters.

    @param filters: The filters to build the query out of.
    @type: Iterable over models.Filter
    @param table: The name of the table to query.
    @type table: str
    @return: Results of SQL select query for the given table with the given
        filters.
    @rtype: Iterable over models.SnapshotMetadata
    """
    db_connection = db_util.get_db_connection()
    db_cursor = db_connection.cursor()

    query_info = build_delete_query(filters, table, restore)
    raw_operands = map(lambda x: x.operand, filters)
    filter_fields_and_operands = zip(query_info.filter_fields, raw_operands)
    operands = map(
        lambda (field, operand): field.interpret_value(operand),
        filter_fields_and_operands
    )
    
    operands_flat = []
    for operand in operands:
        operands_flat.extend(operand)

    db_cursor.execute(query_info.query_str, operands_flat)
    db_connection.commit()
    db_connection.close()
