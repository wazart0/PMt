

def modifyRequest(request, add_fields, values, remove_fields = []):
    mutable = request.POST._mutable
    request.POST._mutable = True
    if isinstance(add_fields, list) and isinstance(values, list):
        if len(add_fields) == len(values):
            for i in range(len(add_fields)):
                request.data[add_fields[i]] = str(values[i])
        else:
            raise valuesError('modifyRequest(): some error in querry')
    else:
        request.data[add_fields] = str(values)
    for field in remove_fields:
        del request.data[field]
    request.POST._mutable = mutable
    return request

    

def buildUniversalQueryTree(tableName, parentPrimaryKey, subQuery, primaryKey = 'id'):
    return '''
        WITH RECURSIVE nodes AS (
            SELECT s1.* FROM {table} s1 WHERE s1.{parentPK} IN (
                {subQuery})
            UNION 
            SELECT s2.* FROM {table} s2, nodes s1 WHERE s2.{parentPK} = s1.{PK})
        SELECT id FROM nodes
        UNION
        {subQuery}
    '''.format(table = tableName, parentPK = parentPrimaryKey, subQuery = subQuery, PK = primaryKey)


# def checkAuthorization(authTable, privTable, privCodeName, userColumnName, userID):
#     return \
#     '''
#         select group_id from {authorization} where group_privilege_id = (
#                 select id from {privileges} where code_name = {privilege}) 
#             and {userColumn} = {userID}
#     '''
