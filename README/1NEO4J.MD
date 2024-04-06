## CREATING CONSTRAINTS AND INDEX

### Constraints:

Constraints ensure the uniqueness or existence of certain properties in nodes or relationships.
There are two types of constraints: uniqueness constraints and existence constraints.

- Uniqueness constraints ensure that a specific property value is unique across all nodes or relationships of a given label.
  Example: CREATE CONSTRAINT ON (u:User) ASSERT u.email IS UNIQUE

- Existence constraints ensure that a specific property must exist in all nodes or relationships of a given label.
  Example: CREATE CONSTRAINT ON ()-[k:KNOWS]-() ASSERT exists(k.type)

### Indexes:

Indexes improve the query performance by allowing faster lookups based on property values.
There are different types of indexes available in Neo4j: node indexes, relationship indexes, and full-text indexes.
Indexes can be created using the CREATE INDEX statement.
Example: CREATE INDEX FOR (u:User) ON (u.email)
Example: CALL db.index.fulltext.createNodeIndex("userBioIndex", ["User"], ["bio"])

Usage:

Determine the label or relationship type and the property you want to apply the constraint or index to.
Use the appropriate statement (CREATE CONSTRAINT or CREATE INDEX) to create the constraint or index.
Execute the statement using a Neo4j database client or Neo4j Browser.
Ensure that the constraint or index creation was successful and that there are no errors.
Apply the constraint or index to the existing data if required.
Use the constraint or index in your queries to improve performance or enforce data integrity.

DELETE DUPLICATE
The qery below returned 2 items for "django"
'''
Match (s:Stack) WHERE s.name = 'django' Return s

s
{
"identity": 4,
"labels": [
"Stack"
],
"properties": {
"name": "django"
},
"elementId": "4"
}
{
"identity": 452,
"labels": [
"Stack"
],
"properties": {
"created": "2023-07-05",
"name": "django",
"description": "to be added"
},
"elementId": "452"
}
'''

the code below removes on of the items based on its ID:
'''
MATCH (s:Stack)
WHERE ID(s) = 452
OPTIONAL MATCH (s)-[r]-()
DELETE s, r
'''

## DELETE DUPLICATE RELATIONSHIPS

THE QUERY BELOW
MATCH (u)-[:WORKS_FOR]->(c)
RETURN u, c
RETURNS

| u:User                                          | c:Company                                      |
| ----------------------------------------------- | ---------------------------------------------- |
| {                                               | {                                              |
| "identity": 446,                                | "identity": 459,                               |
| "labels": [                                     | "labels": [                                    |
| "User"                                          | Company"                                       |
| ],                                              | ],                                             |
| "properties": {                                 | "properties":{                                 |
| "created": "2023-07-05",                        | "created": "2023-07-05",                       |
| "name": "victor almeida",                       | "name": "1000heads",                           |
| "bio": "to be completed",                       | "description": "to be added",                  |
| "updated": "2023-07-17",                        | "logo": "path/to/company/logo"                 |
| "email": "victor.almeida@1000heads.com",        | "elementId": "459"                             |
| "picture": "path/to/picture"                    | }                                              |
| },                                              |                                                |
| "elementId": "446"                              |                                                |
| ----------------------------------------------- | ---------------------------------------------- |
| {                                               | {                                              |
| "identity": 446,                                | "identity": 459,                               |
| "labels": [                                     | "labels": [                                    |
| "User"                                          | Company"                                       |
| ],                                              | ],                                             |
| "properties": {                                 | "properties":{                                 |
| "created": "2023-07-05",                        | "created": "2023-07-05",                       |
| "name": "victor almeida",                       | "name": "1000heads",                           |
| "bio": "to be completed",                       | "description": "to be added",                  |
| "updated": "2023-07-17",                        | "logo": "path/to/company/logo"                 |
| "email": "victor.almeida@1000heads.com",        | "elementId": "459"                             |
| "picture": "path/to/picture"                    | }                                              |
| },                                              |                                                |
| "elementId": "446"                              |                                                |
| }                                               |                                                |

CODE TO DELETE ONE OF THE RELATIONSHIPS

MATCH (u1:User)-[r:WORKS_FOR]->(c:Company)
WITH u1, c, r
ORDER BY r.created
WITH u1, c, collect(r) AS relationships
FOREACH (i IN range(1, size(relationships) - 1) |
DELETE relationships[i]
)

USING COLLECT and DISTINCT Key words

MATCH (u:User {email: "victor.almeida@1000heads.com"})

OPTIONAL MATCH (u)-[:WORKS_FOR]->(c:Company)
OPTIONAL MATCH (u)-[:WORKED_ON]->(s:Software)
OPTIONAL MATCH (u)-[:KNOWS]->(st:Stack)
OPTIONAL MATCH (u)-[:CREATED]->(e:Event)

RETURN u.email, COLLECT(DISTINCT c.name) AS companies, COLLECT(DISTINCT s.name) AS softwares, COLLECT(DISTINCT st.name) AS stacks, COLLECT(DISTINCT st.type) AS stacks_type, COLLECT(DISTINCT e.title) AS events
