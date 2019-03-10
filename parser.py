#  <Document:
    #  definitions=[
        #  <Query: selections=[
            #  <Field: selections=[
                #  <Field: selections=[
                    #  <Field: name=id>
                    #  ], name=user>
                #  ], name=query>
            #  ]>
        #  ]>

import re
from graphql.parser import GraphQLParser

query2 = "{ query { contact { id } user { hobbies { name } } } } "


query = """{
    query {
        contact(id: $id) {
            @defer id
        }
        user(id: $id) {
             hello
             
            hobbies(category: "sports") {
                name
            }
        }
    }
}
"""

#  parser = GraphQLParser()
#  ast = parser.parse(query)

#  root = ast.definitions[0].selections[0]

#  if root.name not in ['query', 'mutation']:
    #  raise 'Document must be a query or a selection'

def get_slice_length(p, c):
    return p + len(c)

def replace_inner_braces(m):
    if m.group(1) is None:
        return m.group()
    return m.group().replace(m.group(1), "")

def get_query_path(query, position):
    lines = query.split('\n')
    current_line = lines[position[1] - 1]
    current_line_content = current_line[0:position[2] + 1]
    to_keep = lines[0:position[1] - 1]
    #  length = reduce(get_slice_length, lines[0:position[1] - 1], 0)
    new_string = ' '.join(to_keep) + ' ' + current_line_content
    is_finishing_a_word = current_line[-1].isalnum()

    paramsR = r"\([^\(]*\)|@([a-zA-Z]+[a-zA-Z0-9]*)*"
    without_params = re.sub(paramsR, '', new_string) 

    innerBraceR = r"([a-zA-Z][a-zA-Z0-9])*\s*[^{]*"
    innerBraceR = r"([a-zA-Z][a-zA-Z0-9]*)(?!.*(\s*{))"
    without_inner_braces = re.sub(innerBraceR, replace_inner_braces, without_params)

    nestedR = r"([a-zA-Z0-9]+\s*{[^{]+})|\s|[{}]"
    without_previous_nest = re.sub(nestedR, ' ', without_inner_braces)

    return without_previous_nest.split()

get_query_path(query, [0, 8, 13, 0])
