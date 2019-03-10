import os
import json
import re
from graphql.parser import GraphQLParser
from .base import Base
from deoplete.util import getlines

def get_slice_length(p, c):
    return p + len(c)

def replace_inner_braces(m):
    if m.group(1) is None:
        return m.group()
    return m.group().replace(m.group(1), "")

def get_query_path(query, position):
    lines = query.split('\n')
    #  current_line = lines[position[1] - 1]
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

def get_graphql_tree(content):
    parser = GraphQLParser()
    ast = parser.parse(query)
    return ast.definitions[0].selections[0]

def get_type_from_path(path, types):
    #  results = []
    current_type = None
    i = 0
    while i < len(path):
        if path[i] == 'query':
            current_type = 'Query'
            i = i + 1
            continue
        if path[i] == 'mutation':
            current_type = 'Mutation'
            i = i + 1
            continue

        if path[i] not in types[current_type]:
            return None

        current_type = types[current_type][path[i]]
        #  results = [str(current_type), str(path[i]), str(current_type)]
        #  return results
        i = i + 1
    return current_type

class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = 'GraphQL'
        self.mark = '[GraphQL]'
        self.min_pattern_length = 0
        return

    def _gather_candidates(self, context):
        line = context['position'][1]
        lines = getlines(self.vim, 0, line)
        content = '\n'.join(lines)
        path = get_query_path(content, context['position'])

        if len(path) > 0 and path[0].lower() is not 'query' and path[0].lower() is not 'mutation':
            path.insert(0, 'query')

        schema = self.vim.vars.get('graphiql#interface#current_schema')
        types = {}
        if schema is not None:
            types = json.loads(schema)

        current_type = get_type_from_path(path, types)

        results = []
        for k, v in types[current_type].items():
            results.append({ 'word': k, 'kind': v })

        return results

    def gather_candidates(self, context):
        try:
            return self._gather_candidates(context)
        except:
            return []
