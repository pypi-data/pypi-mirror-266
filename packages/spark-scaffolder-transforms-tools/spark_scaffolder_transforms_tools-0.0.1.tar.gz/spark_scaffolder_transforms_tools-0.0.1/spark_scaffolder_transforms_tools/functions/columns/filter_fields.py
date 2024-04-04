def with_filter_by_field(logic_op=None,
                         filters=None):
    """
    Filter by custom criteria over one or more fields.
    :param logic_op: String ('or', 'and')
    :param filters: Array
           [
              {
                "field":"test_1",
                 "op":"like",
                 "value":"%550%"
              }
          ]
    :return:
    """
    import gc
    to_type_logic_op = ["or", "and"]
    to_type_op_filters = ["eq", "neq", "lt", "lte", "gt", "gte", "like", "rlike"]

    if logic_op in (False, None, ""):
        raise Exception(f'require var: logic_op ([' or ', ' and '])')
    if logic_op not in to_type_logic_op:
        raise Exception(f'require var: logic_op ([' or ', ' and '])')

    count_keys = 0
    for key in filters:
        count_keys += 1
        op = key.get("op", None)
        if op is None:
            raise Exception(f'The operator in filter is invalid: ("Is required op")')
        if op not in to_type_op_filters:
            raise Exception(f'The operator in filter is invalid: (op_filters)')

    def filter_by_field(df):
        sql = ""
        count_f = 0
        ope_type = ""
        for _ in filters:
            count_f += 1
            op = _["op"]
            field = _["field"]
            value = _["value"]
            if op == "eq":
                ope_type = "="
            elif op == "neq":
                ope_type = "!="
            elif op == "lt":
                ope_type = "<"
            elif op == "lte":
                ope_type = "<="
            elif op == "gt":
                ope_type = ">"
            elif op == "gte":
                ope_type = ">="
            elif op == "like":
                ope_type = "like"
            elif op == "rlike":
                ope_type = "rlike"

            sql += f"{field} {ope_type} '{value}' "
            if count_keys > 1 and count_f < count_keys:
                sql += f"{logic_op} "
        return df.filter(sql)

    gc.collect()
    return filter_by_field
