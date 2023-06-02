from sql_metadata import Parser
from lib.utils import *
import re

def executeHiveHql(self, hqlFile, outputfileName):
    applicationId = ""
    params = f"-n '' -p '' -f {hqlFile} > {outputfileName}"
    result = executeCommand("/usr/bin/hive", params)
    applicationId = re.search("application_[0-9]{13}_[0-9]{4}", result)

    return result, applicationId

def generateHiveSetV(self):
    executeHiveQuery(self, 'set -v', "setV.out") 

def executeHiveQuery(self, query, outputFileName):
    executeCommand("/usr/bin/hive", "--outputformat=csv2 -n '' -p '' -e '{query}' > ./results/output/{outputFileName}".format(query=query, outputFileName=outputFileName)) 

def executeQueryExplain(self, query):
    queryWithoutUseSet = ""
    explainQuery = ""
    useStatement = ""
    # find the query without use or set;
    query = query.replace('\n', ' ')

    statements = query.split(';')
    for s in statements:
        if s.lower().strip().startswith('use'):
            useStatement = s.strip()
            explainQuery = ";".join([explainQuery, s.strip()]) 
            continue
        elif s.lower().strip().startswith('set'):
            explainQuery = ";".join([explainQuery, s.strip()]) 
            continue
        elif s.strip() =="":
            continue
        else:
            queryWithoutUseSet = s.strip()
            explain = f"EXPLAIN {queryWithoutUseSet}"
            explainQuery = ";".join([explainQuery, explain])
            explainQuery = f"{explainQuery};"

    # replace newline with spaces;
    saveTextToFile(self, explainQuery, "./results/output/explain_query.hql")
    result, appId = executeHiveHql(self, "./results/output/explain_query.hql", "./results/output/explain_query_result.out")
    saveTextToFile(self, result, "./results/output/explain_query_beelinetrace.out")

    return useStatement, queryWithoutUseSet, result

def executeQueryTablesDefinition(self, useStatement, queryWithoutUseSet):
    tables = Parser(queryWithoutUseSet).tables
    for table in tables:
        if table == "":
            continue
        table = table.replace("`", "")
        query = f"DESCRIBE FORMATTED {table}"
        if useStatement != "":
            query = f"{useStatement};{query}"
        
        saveTextToFile(self, query, f"./results/output/{table}_definition.hql")
        result, appId = executeHiveHql(self, f"./results/output/{table}_definition.hql", f"./results/output/{table}_dfinition.out")
        saveTextToFile(self, result, f"./results/output/{table}_definition_beelinetrace.out")


def getYarnApplicationLog(self, appId):
    executeCommand("/usr/bin/yarn", f"logs -applicationId {appId} > ./results/output/yarn_{appId}.out")