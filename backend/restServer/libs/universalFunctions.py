

def modifyRequest(request, field, value):
    mutable = request.POST._mutable
    request.POST._mutable = True
    if isinstance(field, list) and isinstance(value, list):
        if len(field) == len(value):
            for i in range(len(field)):
                request.data[field[i]] = str(value[i])
        else:
            raise ValueError('modifyRequest(): some error in querry')
    else:
        request.data[field] = str(value)
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
