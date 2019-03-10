const program = require('commander')
const fetch = require('axios')

const GET_SCHEMA_QUERY = `
{
  __schema {
    types {
      name
      fields {
        name
        args {
          name
          description
          defaultValue
        }
        type {
          kind
          ofType {
            ofType {
              kind
              name
              description
            }
            kind
            name
            description
          }
          name
          description
        }
        
      }
    }
  }
}
`

program
  .version('1.0.0')
  .option('-u, --url [url]', 'GraphQL API URL')
  .option('-q, --query [query]', 'GraphQL query')
  .option('-s, --schema', 'Return the remote GraphQL Schema')
  .parse(process.argv)

async function query(url, query) {
  let result
  try {
    result = await fetch({
      url,
      method: 'post',
      data: { query }
    })
    console.log(JSON.stringify(result.data.data, null, 2))
  } catch (e) {
    console.error(JSON.stringify(e.response.data, null, 2))
  }
}

function normalizeSchema(types) {
  return types.reduce((schema, type) => {
    schema[type.name] = (type.fields || []).reduce((p, c) => {
      let value
      const { name, ofType } = c.type
      if (name) {
        value = name
      } else if (ofType && ofType.name) {
        value = ofType.name
      } else if (ofType && ofType.ofType && ofType.ofType.name) {
        value = ofType.ofType.name
      } else {
        value = null
      }
      return Object.assign(p, {
        [c.name]: value
      })
    }, {})
    return schema
  }, {})
}

async function getRemoteSchema(url) {
  let result
  try {
    result = await fetch({
      url,
      method: 'post',
      data: { query: GET_SCHEMA_QUERY }
    })
    console.log(
      JSON.stringify(normalizeSchema(result.data.data.__schema.types))
    )
  } catch (e) {
    console.log(e.response ? e.response.data : e)
  }
}

function main() {
  if (!program.url) {
    throw new Error('Remote URL is mandatory to perform a GraphQL query')
  }

  if (program.schema) {
    return getRemoteSchema(program.url)
  }

  if (!program.query) {
    throw new Error('URL and query are mandatory')
  }

  return query(program.url, program.query)
}

main()
