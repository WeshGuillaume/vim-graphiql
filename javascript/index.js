const program = require('commander')
const fetch = require('axios')

program
  .version('1.0.0')
  .option('-u, --url [url]', 'GraphQL API URL')
  .option('-q, --query [query]', 'GraphQL query')
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

if (!program.url || !program.query) {
  throw new Error('URL and query are mandatory')
}

query(program.url, program.query)
