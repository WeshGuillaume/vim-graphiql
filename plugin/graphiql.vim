let s:cwd = expand('<sfile>:p:h:h')
let s:js_script = s:cwd . '/javascript'
let s:last_check_url = ''
let g:graphiql#interface#current_schema = '{}'

function! graphiql#get_visual_selection() abort
  try
    let a_save = @a
    silent! normal! gv"ay
    return @a[0:-2]
  finally
    let @a = a_save
  endtry
endfunction

function! graphiql#request_command(url, query) abort
  return "node " . s:js_script . ' -u ' . shellescape(a:url) . ' -q ' . shellescape(a:query)
endfunction

function! graphiql#get_output() range
  let selection = substitute(graphiql#get_visual_selection(), '\n', ' ', 'g')
  let url = input('GraphQL Endpoint: ')
  let com = graphiql#request_command(url, selection)
  silent! execute "'<,'>!" . com
endfunction

function! graphiql#goto_window(ref)
  call win_gotoid(a:ref)
endfunction

function! graphiql#replace_window_content(ref, content)
  call graphiql#goto_window(a:ref)
  set modifiable
  silent! execute ':normal! ggdG'
  for line in a:content
    silent! call append(line('$'), line)
  endfor
  set nomodifiable
endfunction

function! graphiql#execute_query()
  call graphiql#goto_window(s:winQuery)
  let content = join(getline(1, '$'), ' ')
  let url = graphiql#get_url()
  let result = split(system(graphiql#request_command(url, content)), '\n')
  silent! call graphiql#replace_window_content(s:winResult, result)
  call graphiql#ensure_graphql_schema()
  call graphiql#goto_window(s:winQuery)
endfunction

function! graphiql#get_url()
  silent! call graphiql#goto_window(s:winURL)
  execute ':normal gg'
  return getline('.')
endfunction

function! graphiql#setup_graphiql() abort
  enew
  let s:winQuery = win_getid()
  set filetype=graphql

  let query = readfile(s:cwd . '/query-template.graphql')
  for line in query
    call append(line('$'), line)
  endfor

  execute ':normal! dd'

  top copen 1
  enew
  let s:winURL = win_getid()
  execute ':se stl=- fcs=stl:-,stlnc:-,vert:\|'
  set number
  set norelativenumber
  silent! call setline('.', 'http://api.catalysis-hub.org/graphql')

  silent! call graphiql#goto_window(s:winQuery)
  set splitright

  vnew
  let s:winResult = win_getid()
  set filetype=json
  set readonly
  set nomodifiable
  set nonu
  set norelativenumber

  call graphiql#goto_window(s:winQuery)
  nnoremap <silent> <leader>g :call graphiql#execute_query()<enter>

  call graphiql#ensure_graphql_schema()
endfunction

function! graphiql#ensure_graphql_schema()
  let url = graphiql#get_url()
  if s:last_check_url != url
    let g:graphiql#interface#current_schema = '{}'
  endif
  if g:graphiql#interface#current_schema != '{}'
    return
  endif
  let s:last_check_url = url
  let g:graphiql#interface#current_schema = system('node '. s:js_script . ' -u ' . shellescape(url) . ' -s')
endfunction

" One of my plugin probably delays the mapping, so i use
" <nowait> to prevent that
vnoremap <nowait> <silent> <leader>g :call graphiql#get_output()<enter>
nnoremap <silent> <leader>f :call graphiql#setup_graphiql()

