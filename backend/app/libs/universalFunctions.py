

def modifyRequest(request, add_fields, values, remove_fields = []):
    mutable = request.POST._mutable
    request.POST._mutable = True
    if isinstance(add_fields, list) and isinstance(values, list):
        if len(add_fields) == len(values):
            for i in range(len(add_fields)):
                request.data[add_fields[i]] = str(values[i])
        else:
            raise ValueError('modifyRequest(): some error in querry')
    else:
        request.data[add_fields] = str(values)
    for field in remove_fields:
        del request.data[field]
    request.POST._mutable = mutable
    return request

    

def buildUniversalQueryTree(tableName, parentPrimaryKey, subQuery, primaryKey = 'id', level = 0):
    return '''
        WITH RECURSIVE nodes AS (
            SELECT s{level1}.{PK} FROM {table} s{level1} WHERE s{level1}.{parentPK} IN (
                {subQuery})
            UNION 
            SELECT s{level2}.{PK} FROM {table} s{level2}, nodes s{level1} WHERE s{level2}.{parentPK} = s{level1}.{PK})
        SELECT {PK} FROM nodes
        UNION
        {subQuery}
    '''.format(table = tableName, parentPK = parentPrimaryKey, subQuery = subQuery, PK = primaryKey, level1 = level*2, level2 = level*2+1)



def duplicateArgs(*args):
    out = []
    for i in args:
        out.extend(i) if isinstance(i, list) else out.append(i)
    return out + out


# def checkAuthorization(authTable, privTable, privCodeName, userColumnName, userID):
#     return \
#     '''
#         select group from {authorization} where group_privilege = (
#                 select id from {privileges} where code_name = {privilege}) 
#             and {userColumn} = {userID}
#     '''
