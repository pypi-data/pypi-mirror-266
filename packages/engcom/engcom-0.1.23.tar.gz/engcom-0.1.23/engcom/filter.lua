-- load utilities
local system = require 'pandoc.system'
local string = require 'string'
pandoc.utils = require 'pandoc.utils'
pandoc.List = require 'pandoc.List'

-- logging

--[[
    logging.lua: pandoc-aware logging functions (can also be used standalone)
    Copyright:   (c) 2022 William Lupton
    License:     MIT - see LICENSE file for details
    Usage:       See README.md for details
]]

-- if running standalone, create a 'pandoc' global
if not pandoc then
  _G.pandoc = {utils = {}}
end

-- if there's no pandoc.utils, create a local one
if not pcall(require, 'pandoc.utils') then
  pandoc.utils = {}
end

-- if there's no pandoc.utils.type, create a local one
if not pandoc.utils.type then
  pandoc.utils.type = function(value)
      local typ = type(value)
      if not ({table=1, userdata=1})[typ] then
          -- unchanged
      elseif value.__name then
          typ = value.__name
      elseif value.tag and value.t then
          typ = value.tag
          if typ:match('^Meta.') then
              typ = typ:sub(5)
          end
          if typ == 'Map' then
              typ = 'table'
          end
      end
      return typ
  end
end

-- namespace
local logging = {}

-- helper function to return a sensible typename
logging.type = function(value)
  -- this can return 'Inlines', 'Blocks', 'Inline', 'Block' etc., or
  -- anything that built-in type() can return, namely 'nil', 'number',
  -- 'string', 'boolean', 'table', 'function', 'thread', or 'userdata'
  local typ = pandoc.utils.type(value)

  -- it seems that it can also return strings like 'pandoc Row'; replace
  -- spaces with periods
  -- XXX I'm not sure that this is done consistently, e.g. I don't think
  --     it's done for pandoc.Attr or pandoc.List?
  typ = typ:gsub(' ', '.')

  -- map Inline and Block to the tag name
  -- XXX I guess it's intentional that it doesn't already do this?
  return ({Inline=1, Block=1})[typ] and value.tag or typ
end

-- derived from https://www.lua.org/pil/19.3.html pairsByKeys()
logging.spairs = function(list, comp)
  local keys = {}
  for key, _ in pairs(list) do
      table.insert(keys, tostring(key))
  end
  table.sort(keys, comp)
  local i = 0
  local iter = function()
      i = i + 1
      return keys[i] and keys[i], list[keys[i]] or nil
  end
  return iter
end

-- helper function to dump a value with a prefix (recursive)
-- XXX should detect repetition/recursion
-- XXX would like maxlen logic to apply at all levels? but not trivial
local function dump_(prefix, value, maxlen, level, add)
  local buffer = {}
  if prefix == nil then prefix = '' end
  if level == nil then level = 0 end
  if add == nil then add = function(item) table.insert(buffer, item) end end
  local indent = maxlen and '' or ('  '):rep(level)

  -- get typename, mapping to pandoc tag names where possible
  local typename = logging.type(value)

  -- don't explicitly indicate 'obvious' typenames
  local typ = (({boolean=1, number=1, string=1, table=1, userdata=1})
               [typename] and '' or typename)

  -- light userdata is just a pointer (can't iterate over it)
  -- XXX is there a better way of checking for light userdata?
  if type(value) == 'userdata' and not pcall(pairs(value)) then
      value = tostring(value):gsub('userdata:%s*', '')

  -- modify the value heuristically
  elseif ({table=1, userdata=1})[type(value)] then
      local valueCopy, numKeys, lastKey = {}, 0, nil
      for key, val in pairs(value) do
          -- pandoc >= 2.15 includes 'tag', nil values and functions
          if key ~= 'tag' and val and type(val) ~= 'function' then
              valueCopy[key] = val
              numKeys = numKeys + 1
              lastKey = key
          end
      end
      if numKeys == 0 then
          -- this allows empty tables to be formatted on a single line
          -- XXX experimental: render Doc objects
          value = typename == 'Doc' and '|' .. value:render() .. '|' or
          typename == 'Space' and '' or '{}'
      elseif numKeys == 1 and lastKey == 'text' then
          -- this allows text-only types to be formatted on a single line
          typ = typename
          value = value[lastKey]
          typename = 'string'
      else
          value = valueCopy
          -- XXX experimental: indicate array sizes
          if #value > 0 then
              typ = typ .. '[' .. #value .. ']'
          end
      end
  end

  -- output the possibly-modified value
  local presep = #prefix > 0 and ' ' or ''
  local typsep = #typ > 0 and ' ' or ''
  local valtyp = type(value)
  if valtyp == 'nil' then
      add('nil')
  elseif ({boolean=1, number=1, string=1})[valtyp] then
      typsep = #typ > 0 and valtyp == 'string' and #value > 0 and ' ' or ''
      -- don't use the %q format specifier; doesn't work with multi-bytes
      local quo = typename == 'string' and '"' or ''
      add(string.format('%s%s%s%s%s%s%s%s', indent, prefix, presep, typ,
                        typsep, quo, value, quo))
  -- light userdata is just a pointer (can't iterate over it)
  -- XXX is there a better way of checking for light userdata?
  elseif valtyp == 'userdata' and not pcall(pairs(value)) then
      add(string.format('%s%s%s%s %s', indent, prefix, presep, typ,
                        tostring(value):gsub('userdata:%s*', '')))
  elseif ({table=1, userdata=1})[valtyp] then
      add(string.format('%s%s%s%s%s{', indent, prefix, presep, typ, typsep))
      -- Attr and Attr.attributes have both numeric and string keys, so
      -- ignore the numeric ones
      -- XXX this is no longer the case for pandoc >= 2.15, so could remove
      --     the special case?
      local first = true
      if prefix ~= 'attributes:' and typ ~= 'Attr' then
          for i, val in ipairs(value) do
              local pre = maxlen and not first and ', ' or ''
              dump_(string.format('%s[%s]', pre, i), val, maxlen,
                    level + 1, add)
              first = false
          end
      end
      -- report keys in alphabetical order to ensure repeatability
      for key, val in logging.spairs(value) do
          local pre = maxlen and not first and ', ' or ''
          -- this check can avoid an infinite loop, e.g. with metatables
          -- XXX should have more general and robust infinite loop avoidance
          if key:match('^__') and type(val) ~= 'string' then
              add(string.format('%s%s: %s', pre, key, tostring(val)))

          -- pandoc >= 2.15 includes 'tag'
          elseif not tonumber(key) and key ~= 'tag' then
              dump_(string.format('%s%s:', pre, key), val, maxlen,
                    level + 1, add)
          end
          first = false
      end
      add(string.format('%s}', indent))
  end
  return table.concat(buffer, maxlen and '' or '\n')
end

logging.dump = function(value, maxlen)
  if maxlen == nil then maxlen = 70 end
  local text = dump_(nil, value, maxlen)
  if #text > maxlen then
      text = dump_(nil, value, nil)
  end
  return text
end

logging.output = function(...)
  local need_newline = false
  for i, item in ipairs({...}) do
      -- XXX space logic could be cleverer, e.g. no space after newline
      local maybe_space = i > 1 and ' ' or ''
      local text = ({table=1, userdata=1})[type(item)] and
          logging.dump(item) or tostring(item)
      io.stderr:write(maybe_space, text)
      need_newline = text:sub(-1) ~= '\n'
  end
  if need_newline then
      io.stderr:write('\n')
  end
end

-- basic logging support (-1=errors, 0=warnings, 1=info, 2=debug, 3=debug2)
-- XXX should support string levels?
logging.loglevel = 0

-- set log level and return the previous level
logging.setloglevel = function(loglevel)
  local oldlevel = logging.loglevel
  logging.loglevel = loglevel
  return oldlevel
end

-- verbosity default is WARNING; --quiet -> ERROR and --verbose -> INFO
-- --trace sets TRACE or DEBUG (depending on --verbose)
if type(PANDOC_STATE) == 'nil' then
  -- use the default level
elseif PANDOC_STATE.trace then
  logging.loglevel = PANDOC_STATE.verbosity == 'INFO' and 3 or 2
elseif PANDOC_STATE.verbosity == 'INFO' then
  logging.loglevel = 1
elseif PANDOC_STATE.verbosity == 'WARNING' then
  logging.loglevel = 0
elseif PANDOC_STATE.verbosity == 'ERROR' then
  logging.loglevel = -1
end

logging.error = function(...)
  if logging.loglevel >= -1 then
      logging.output('(E)', ...)
  end
end

logging.warning = function(...)
  if logging.loglevel >= 0 then
      logging.output('(W)', ...)
  end
end

logging.info = function(...)
  if logging.loglevel >= 1 then
      logging.output('(I)', ...)
  end
end

logging.debug = function(...)
  if logging.loglevel >= 2 then
      logging.output('(D)', ...)
  end
end

logging.debug2 = function(...)
  if logging.loglevel >= 3 then
      logging.warning('debug2() is deprecated; use trace()')
      logging.output('(D2)', ...)
  end
end

logging.trace = function(...)
  if logging.loglevel >= 3 then
      logging.output('(T)', ...)
  end
end

-- for temporary unconditional debug output
logging.temp = function(...)
  logging.output('(#)', ...)
end

-- return logging


-- general purpose functions 

local function get_keys(tbl)
  local keyset={}
  local n=0
  for k,v in pairs(tbl) do
    n=n+1
    keyset[n]=k
  end
  return keyset
end

local function script_path()
   local str = debug.getinfo(2, "S").source:sub(2)
   return str:match("(.*/)")
end

local function get_parent(str)
    return str:match("(.*[/\\])")
end

local function isempty(s)
  return s == nil or s == '' or next(s) == nil
end

local function starts_with(start, str)
  return str:sub(1, #start) == start
end

local function has_value(tab, val)
  for index, value in ipairs(tab) do
      if value == val then
          return true
      end
  end
  return false
end

local function has_key(tab, key)
  for index, value in ipairs(tab) do
      if index == key then
          return true
      end
  end
  return false
end

local function delimiter_dollar(text)
  -- print(text)
  text = string.gsub(text,"\\%(","$")
  text = string.gsub(text,"\\%)","$")
  return text
end

function getTableSize(t)
  local count = 0
  for _, __ in pairs(t) do
      count = count + 1
  end
  return count
end

-- inline and interior

local inline_filter = {
  {Math = Math},
  {Code = Code},
  {RawInline = RawInline},
  {Cite = Cite},
  {Span = Span},
  {Link = Link}
}

local function inline_filter_function(el_inline)
  return pandoc.walk_inline(el_inline,inline_filter)
end

local interior_filter = {
  Math = function(el)
    return Math(el)
  end,
  RawInline = function(el)
    return RawInline(el)
  end,
  RawBlock = function(el)
    return RawBlock(el)
  end,
  Span = function(el)
    return Span(el)
  end,
  Link = function(el)
    return Link(el)
  end,
  Code = function(el)
    return coder_latex(el)
  end,
  CodeBlock = function(el)
    return coder_latex(el)
  end,
  Cite = function(el)
    local first_id = el.citations[1].id
    if starts_with('sec:',first_id) or starts_with('Sec:',first_id) or starts_with('eq:',first_id) or starts_with('Eq:',first_id) or starts_with('tbl:',first_id) or starts_with('Tbl:',first_id) or starts_with('fig:',first_id) or starts_with('Fig:',first_id) or starts_with('lst:',first_id) or starts_with('Lst:',first_id) then
      return pandoccrossrefer(el)
    else
      return Cite(el)
    end
  end,
  Image = function(el)
    return figurer(el,true)
  end,
  OrderedList = function(el)
    return interior_ordered_lister(el)
  end
}

local function keyer(el)
  if FORMAT:match 'latex' then
    local text
    if el.content then
      text = pandoc.walk_block(el.content,inline_filter)
      local text_doc = pandoc.Pandoc(text)
      text = pandoc.write(text_doc,'latex')
      text = pandoc.utils.stringify(text)
    else
      text = ''
    end
    if el.classes:includes('folder') then
      text = '\\faFolder'
    elseif el.classes:includes('windows') then
      text = '\\faWindows'
    elseif el.classes:includes('enter') then
      text = 'ENTR' -- keypad
    elseif el.classes:includes('return') then
      text = '\\return' -- keyboard
    elseif el.classes:includes('leftarrow') or  el.classes:includes('left') or el.classes:includes('backspace') then
      text = '$\\leftarrow$'
    elseif el.classes:includes('uparrow') or el.classes:includes('up') then
      text = 'UP'
    elseif el.classes:includes('downarrow') or el.classes:includes('down') then
      text = 'DWN'
    end
    return pandoc.RawInline('latex', "\\mykeys{" .. text .. "}")
  elseif FORMAT:match 'html' then
    if el.classes:includes('folder') then
      return pandoc.RawInline('html',
        '<span class="material-icons">folder</span>'
      )
    elseif el.classes:includes('windows') then
      return pandoc.RawInline('html',
        '<i class="fa-brands fa-windows"></i>'
      )
    elseif el.classes:includes('enter') or el.classes:includes('return') then
      return pandoc.RawInline('html',
        '<span class="material-icons">keyboard_return</span>'
      )
    else
      return el
    end
  else
    return el 
  end
end

local function citer(el)
  local citeraw
  local citesuffix
  if FORMAT:match 'latex' then
    citeraw = "\\autocite["
    for i, c in ipairs(el.citations) do
      citekey = c.id
      citesuffix = pandoc.utils.stringify(c.suffix)
      citesuffix = string.gsub(citesuffix,',','',1) -- strip first comma
      if not citesuffix then citesuffix = '' end
      if i==1 then
        citeraw = citeraw .. citesuffix ..']{' .. citekey
      else
        citeraw = citeraw .. "," .. citekey
      end
    end
    citeraw = citeraw .. "}"
    return pandoc.RawInline('latex', citeraw)
  else
    return el 
  end
end

local function hashrefer(el)
  local content = el.content
  local text = pandoc.utils.stringify(content)
  local cap = false
  if el.classes:includes('Hashref') then
    cap = true
  end
  if FORMAT:match 'latex' then
    if cap then
      return pandoc.RawInline('latex', "\\Cref{" .. text .. "}")
    else
      return pandoc.RawInline('latex', "\\cref{" .. text .. "}")
    end
  else
    return pandoc.Link(text,"/" .. text)
  end
end

local function linerefer(el)
  local content = el.content
  local text = pandoc.utils.stringify(content)
  if FORMAT:match 'latex' then
    return pandoc.RawInline('latex', "\\lref{" .. text .. "}")
  else
    return pandoc.Link(text,"/" .. text)
  end
end

local function labeler(el)
  local content = el.content
  local text = pandoc.utils.stringify(content)
  local component = el.classes:includes('component')
  if FORMAT:match 'latex' then
    if component then
      return pandoc.RawInline('latex', "\\label[componentitem]{" .. text .. "}")
    else
      return pandoc.RawInline('latex', "\\label{" .. text .. "}")
    end
  else
    -- return pandoc.Link(text,"/" .. text)
    return el
  end
end

local function plainciter(el)
  local content = el.content
  if not content then content = '' end
  local text = pandoc.utils.stringify(content)
  if not text then text = '' end
  local pre = el.attr.attributes['pre']
  local post = el.attr.attributes['post']
  local postpost = el.attr.attributes['postpost'] -- after the parentheses
  if not pre then pre = '' end
  if not post then post = '' end
  if postpost then
    postpost = ", "..postpost
  else 
    postpost = ''
  end
  if FORMAT:match 'latex' then
    return pandoc.RawInline(
      'latex', "{\\textcite[{"..pre.."}][{"..post.."}]{" .. text .. "}"..postpost.."}")
  else
    -- return pandoc.Cite({},{content})
    return el
  end
end

function pandoccrossrefer(el)
  if FORMAT:match 'latex' then
    local citeid
    local citeids = ''
    for index, value in ipairs(el.citations) do
      citeid = value.id 
      citeids = citeids..citeid
      if not (index == #el.citations) then
        citeids = citeids..','
      end
    end
    local cref 
    local citeids_upper = citeids:sub(1,1):upper()..citeids:sub(2)
    if citeids_upper == citeids then
      cref = "\\Cref{"
    else
      cref = "\\cref{"
    end
    local citeids_lower = citeids:sub(1,1):lower()..citeids:sub(2)
    return pandoc.RawInline('latex', cref .. citeids_lower .. "}")
  else
    return el
  end
end

local function infoboxer(el)
  -- local text
  local el_walked
  el_walked = pandoc.walk_block(el,interior_filter)
  local content_doc = pandoc.Pandoc(el_walked.content)
  local content = pandoc.write(content_doc,'latex')
  local title = el.attr.attributes['title']
  local identifier = el.identifier
  if FORMAT:match 'latex' then
    if title == nil then
      title = "{}"
    else
      title = "{" .. title .. "}"
    end
    if identifier == nil then
      identifier = ""
    else
      identifier = "[label=" .. el.identifier .. "]"
    end
    return pandoc.RawBlock('latex', "\\begin{infobox}"  .. identifier .. title .. "\n" .. content .. "\n\\end{infobox}")
  elseif FORMAT:match 'html' then
    if title == nil then
      title = ""
    end
    if identifier == nil then
      identifier = ""
    else
      identifier = el.identifier
    end
    return pandoc.Div({
        pandoc.Div({
          pandoc.Header(3,title,{class="mdl-card__title-text"})
        },{class="mdl-card__title"}),
        pandoc.Div(el.content,{class="mdl-card__supporting-text"})
    },{class="infobox mdl-card mdl-shadow--2dp through mdl-shadow--4dp"})
    -- el.classes:insert('mdc-card')
    -- return el
  else
    return el 
  end
end

local function theoremer(el)
  -- local text
  local el_walked
  el_walked = pandoc.walk_block(el,interior_filter)
  local content_doc = pandoc.Pandoc(el_walked.content)
  local content = pandoc.write(content_doc,'latex')
  local title = el.attr.attributes['title']
  local identifier = el.identifier
  if FORMAT:match 'latex' then
    if title == nil then
      title = ""
    end
    if identifier == nil then
      identifier = ""
    end
    return pandoc.RawBlock('latex', "\\begin{theorem}{"..title.."}{"..identifier.."}\n"..content.."\n\\end{theorem}\n")
  elseif FORMAT:match 'html' then
    if title == nil then
      title = ""
    end
    if identifier == nil then
      identifier = ""
    else
      identifier = el.identifier
    end
    return pandoc.Div({
        pandoc.Div({
          pandoc.Header(3,title,{class="mdl-card__title-text"})
        },{class="mdl-card__title"}),
        pandoc.Div(el.content,{class="mdl-card__supporting-text"})
    },{class="theorem mdl-card mdl-shadow--2dp through mdl-shadow--4dp"})
    -- el.classes:insert('mdc-card')
    -- return el
  else
    return el 
  end
end

local function definitioner(el)
  -- local text
  local el_walked
  el_walked = pandoc.walk_block(el,interior_filter)
  local content_doc = pandoc.Pandoc(el_walked.content)
  local content = pandoc.write(content_doc,'latex')
  local title = el.attr.attributes['title']
  local identifier = el.identifier
  if FORMAT:match 'latex' then
    if title == nil then
      title = ""
    end
    if identifier == nil then
      identifier = ""
    end
    return pandoc.RawBlock('latex', "\\begin{definition}{"..title.."}{"..identifier.."}\n"..content.."\n\\end{definition}\n")
  elseif FORMAT:match 'html' then
    if title == nil then
      title = ""
    end
    if identifier == nil then
      identifier = ""
    else
      identifier = el.identifier
    end
    return pandoc.Div({
        pandoc.Div({
          pandoc.Header(3,title,{class="mdl-card__title-text"})
        },{class="mdl-card__title"}),
        pandoc.Div(el.content,{class="mdl-card__supporting-text"})
    },{class="definition mdl-card mdl-shadow--2dp through mdl-shadow--4dp"})
    -- el.classes:insert('mdc-card')
    -- return el
  else
    return el 
  end
end

local function celler(el)
  local tags = el.attr.attributes['tags']
  if tags ~= nil then
    if tags:find('remove_input') then
      el.attr.attributes['tags'] = string.gsub(el.attr.attributes['tags'], "\"remove_input\"", "")
      -- logging.temp('el before: ', el)
      table.remove(el.content,1) -- Filter out the input part of the cell
      -- logging.temp('el after: ', el)
      -- return el
    end
  end
  -- local text
  local el_walked
  el_walked = pandoc.walk_block(el,interior_filter)
  local content_doc = pandoc.Pandoc(el_walked.content)
  -- local content = pandoc.write(content_doc,'docx')
  local title = el.attr.attributes['title']
  local identifier = el.identifier
  if FORMAT:match 'docx' then
    if title == nil then
      title = ""
    end
    if identifier == nil then
      identifier = ""
    end
    return {pandoc.Para(title), el}
  else
    return el.content
  end
end

local function myurler_html(el)
  -- return {pandoc.LineBreak(),el,pandoc.LineBreak()}
  -- don't need line breaks when we use display block instead
  el.attr.attributes['target'] = '_blank'
  return el
end

local function myurler(el)
  if FORMAT:match 'latex' then
    local url = pandoc.utils.stringify(el.target)
    local hash = el.attr.attributes['h']
    local hash_alt = el.attr.attributes['hash']
    if not hash then if not hash_alt then hash = '' else hash=hash_alt end end
    local punctuation = el.attr.attributes['punctuation']
    if not punctuation then punctuation = '' end
    local safety = el.attr.attributes['safe']
    if not safety then safety = '' end
    local noid
    if el.classes:includes('noid') or el.classes:includes('star') then
      noid = '*' -- starred version
    else
      noid = ''
    end
    if not el.classes:includes('inline') then 
      if el.classes:includes('bottom') then
      return pandoc.RawInline('latex', "\\myurlbottom"..noid.."["..punctuation.."]["..safety.."]{" .. url .. "}{" .. hash .. "}")  
      else
      return pandoc.RawInline('latex', "\\myurl"..noid.."["..punctuation.."]["..safety.."]{" .. url .. "}{" .. hash .. "}")        
      end
    else
      return pandoc.RawInline('latex', "\\myurlinline"..noid.."{" .. url .. "}{" .. hash .. "}")
    end
  elseif FORMAT:match 'html' then
    return myurler_html(el)
  else
    return el
  end
end

local function pather(el) -- handles Span and Code inputs
  local path
  if el.t=='Code' then
    path = pandoc.utils.stringify(el.text)
  else
    path = pandoc.utils.stringify(el.content)
  end
  if FORMAT:match 'latex' then
    if path==nil then
      return el
    else
      return pandoc.RawInline('latex', "\\path{" .. path .. "}")
    end
  else
    return el
  end
end

local function menuer_html(el)
  local content = el.content
  content = pandoc.utils.stringify(content)
  local items = {}
  local i = 0
  for item in string.gmatch(content, '([^,]+)') do
    i = i + 1
    items[i] = pandoc.Span(item,{class='menu-item'})
  end
  items[1].classes = {'menu-item','menu-item-first'}
  items[i].classes = {'menu-item','menu-item-last'}
  return items
end

local function menuer_latex(el)
  local content = el.content
  content = pandoc.utils.stringify(content)
  content = string.gsub(content,'mouser','\\mouser')
  content = string.gsub(content,'mousel','\\mousel')
  content = string.gsub(content,'enrc','\\enrc')
  content = string.gsub(content,'eresume','\\eresume')
  content = string.gsub(content,'estepover','\\estepover')
  content = string.gsub(content,'estepinto','\\estepinto')
  content = string.gsub(content,'estepreturn','\\estepreturn')
  content = string.gsub(content,'eterminate','\\eterminate')
  local menu = pandoc.RawInline('latex',
    '\\menu{'..content..'}'
  )
  return menu
end

function figurer(el,nofloat)
  local i
  local e
  local caption = el.caption
  if caption==nil then
    caption = ""
  else
    caption = pandoc.Para(caption)
    caption = pandoc.walk_block(caption,inline_filter)
    local caption_doc = pandoc.Pandoc(caption)
    caption = pandoc.write(caption_doc,'latex')
  end
  local src = el.src
  local width
  local options
  local fig_tex
  if FORMAT:match 'latex' then
    -- get width
    width = el.attr.attributes['figwidth']
    if width==nil then
      width = ""
    else
      width = pandoc.utils.stringify(width)
      width = "width=" .. width
    end
    -- reset \graphicslist{}
    graphics_list_reset = "\\gdef\\graphicslist{}%\n"
    -- graphics command
    graphics_command = "\\begin{tikzpicture}%\n\\node[inner sep=0pt] {\\input{"..src.."}};%\n\\end{tikzpicture}%"
    -- get figcaption options
    figcaption_keys = {"color","format","credit","permission","reprint","territory","language","edition","fair","publicity","size","permissioncomment","layoutcomment"}
    options = "["
    i = 0
    for key, value in pairs(el.attr.attributes) do
      if has_value(figcaption_keys,key) then -- for markdown
        if i==0 then
          sep = ""
        else
          sep = ","
        end
        options = options .. sep .. key .. "={" .. value .. "}"
        i = i + 1
      end
    end
    options = options .. "]"
    -- nofloat option
    local fig_begin
    local fig_end
    local nofloat_text
    if nofloat then
      -- fig_begin = "\\vspace{\\intextsep}\\noindent\\begin{minipage}{1\\linewidth}%\n\\begin{centering}%\n"
      -- fig_end = "\\end{centering}%\n\\end{minipage}%\n\\vspace{\\intextsep}%\n"
      fig_begin = "\\begin{figure}[H]%\n" ..
        "\\centering\n"
      fig_end = "\\end{figure}%\n"
      nofloat_text = "nofloat"
    else
      if el.attr.attributes['position'] then
        position = el.attr.attributes['position']
      else
        position = 'htbp'
      end
      fig_begin = "\\begin{figure}["..position.."]\n" ..
        "\\centering\n"
      fig_end = "\\end{figure}\n"
      nofloat_text = "float"
    end
    -- construct latex figure
    fig_tex = graphics_list_reset ..
      fig_begin ..
      graphics_command.."\n"..
      "\\caption{"..caption.."}\n"..
      "\\label{"..el.attr.identifier.."}\n".. 
      fig_end
    return pandoc.RawInline('latex', fig_tex)
  elseif FORMAT:match 'html' then
    -- deal with filename stuff
    local stripped = string.gsub(src,"common-rtcbook/",'')
    local path
    local file
    local ext
    path,file,ext = split_filename(stripped)
    local fname
    print("\n\nExtension: "..ext.."\nStripped: "..stripped.."\n\n")
    if (ext == nil or ext == '') then
      fname = path..file..'svg'
    else -- already has extension
      fname = stripped
    end
    el.src = '/assets/' .. fname -- because relative src is to page in html
    -- normalize svg width because it looks small on the site
    -- if ext == 'svg' then
      -- el.attr.attributes['width'] = "125%"
    -- end
    return el
  else
    return el
  end
end

local function figurediver(el)
  -- for subfigure divs
  if FORMAT:match 'latex' then
    -- print(dump(el))
  elseif FORMAT:match 'html' then
    return el 
  else
    return el 
  end
end

local function algorithmerHTML(el)
  return pandoc.RawBlock('html',"<pre class='algorithm'>\n" .. el.text .. "\n</pre>")
end

local function algorithmerLATEX(el)
  -- print('algorithmer el.text: '..el.text)
  return pandoc.RawBlock('latex',el.text)
end

local function version_params_subber(el)
  -- print('version params: '..version_params_flat[el.classes[1]])
  return pandoc.Span(
    pandoc.RawInline('latex',
      version_params_flat[el.classes[1]]
    )
  )
end

function coder_latex(el)
  local language
  if not isempty(el.classes) then
    language = el.classes[1]
  else
    language = 'text'
  end
  if el.t == 'CodeBlock' then
    local code_block = el.text
    local content = pandoc.utils.stringify(code_block)
    local samepage
    if el.classes:includes('nosamepage') then
      samepage = ''
    else
      samepage = ',samepage'
    end
    local linenos
    if el.classes:includes('linenos') then
      linenos = ',linenos'
    else
      linenos = ''
    end
    return pandoc.RawBlock('latex',
      '\\nointerlineskip\\nointerlineskip\\begin{minted}[autogobble'..samepage..linenos..']{'..language..'}\n'.. 
      content..'\n'..
      '\\end{minted}\n'
    )
  elseif el.t == 'Code' then
    local content = pandoc.utils.stringify(el.text)
    return pandoc.RawInline('latex',
      '\\mintinline{'..language..'}|'..content..'|'
    )
  else
    return el
  end
end

function interior_ordered_lister(el)
  if FORMAT:match 'latex' then
    return el -- going to make alpha in environments.sty
  elseif FORMAT:match 'html' then
    el.classes[#el.classes+1] = 'alpha-ol'
    return el 
  else
    return el 
  end
end

local function exercise_solution(el)
  local el_walked = pandoc.walk_block(el,interior_filter)
  local content_doc = pandoc.Pandoc(el_walked.content)
  local content = pandoc.write(content_doc,'latex')
  content = delimiter_dollar(content)
  if el.classes:includes('lab') then
    return pandoc.RawBlock('latex',
      "\\end{labexercise}\n".. 
      "\\begin{labsolution}\n".. 
      content.."\n"..
      "\\end{labsolution}"
    )
  else
    return pandoc.RawBlock('latex',
      "\\end{exercise}\n".. 
      "\\begin{solution}\n".. 
      content.."\n"..
      "\\end{solution}"
    )
  end
end

local function exerciser(el)
  if FORMAT:match 'latex' then
    local el_walked = pandoc.walk_block(el,{
      Div = function(el)
        return exercise_solution(el)
      end
    })
    el_walked = pandoc.walk_block(el_walked,interior_filter)
    local content_doc = pandoc.Pandoc(el_walked.content)
    local content = pandoc.write(content_doc,'latex')
    content = delimiter_dollar(content)
    local title = el.attr.attributes['title']
    local hash = el.attr.attributes['h']
    local hash_alt = el.attr.attributes['hash']
    if not hash then if not hash_alt then hash = '' else hash=hash_alt end end
    if not title then title = '' end
    if el.classes:includes('lab') then
      return pandoc.RawBlock('latex',
        "\\begin{labexercise}[ID="..hash..",hash="..hash.."]\n"..
        content
      )
    else
      return pandoc.RawBlock('latex',
        "\\begin{exercise}[ID="..hash..",hash="..hash.."]\n"..
        content
      )
    end
  else
    return el 
  end
end

local function listinger(el)
  local code_block = el.content[1]
  local id = pandoc.utils.stringify(el.identifier)
  local caption = el.attr.attributes['caption']
  local language = code_block.classes[1]
  if FORMAT:match 'latex' then
    if el.attr.attributes['caption'] then
      local caption_pre = pandoc.read(caption,'markdown').blocks[1]
      local caption_walked = pandoc.walk_block(caption_pre,interior_filter)
      local caption_doc = pandoc.Pandoc(caption_walked)
      caption = pandoc.write(caption_doc,'latex')
    else
      caption = ''
    end
    local content = pandoc.utils.stringify(code_block.text)
    local mynewminted
    local language
    if code_block.classes then
      language = code_block.classes[1]
    else
      language = ''
    end
    if language == 'c' then
      if el.classes:includes('long') and el.classes:includes('texcomments') then
        mynewminted = 'clistinglongtexcomments'
      elseif el.classes:includes('linenos') then
        if el.classes:includes('long') then
          mynewminted = 'clistinglonglinenos'
        else
          mynewminted = 'clistinglinenos'
        end
      elseif el.classes:includes('long') and not el.classes:includes('texcomments') then
        mynewminted = 'clistinglong'
      elseif not el.classes:includes('long') and el.classes:includes('texcomments') then
        mynewminted = 'clistingtexcomments'
      else
        mynewminted = 'clisting'
      end
    elseif language == 'arm' then
      mynewminted = 'armlisting'
    else
      mynewminted = 'textlisting'
    end
    local list_tex
    local texcomments
    local position
    if el.classes:includes('nofloat') then
      position = 'nofloat'
    else -- float
      if el.attr.attributes['position'] then
        position = el.attr.attributes['position'] -- untested ... idea is could pass attribute position=h or similar
      else
        position = 'htbp'
      end
    end
    local ifsolution_beg = ''
    local ifsolution_end = ''
    if el.classes:includes('solutions-only') then
      ifsolution_beg = '\n\\ifdefined\\issolution\n'
      ifsolution_end = '\n\\fi\n'
    end
    if position == 'nofloat' then
      list_tex = pandoc.RawInline('latex',
        ifsolution_beg..'\\begin{listingsbox}{'..mynewminted..'}{'..caption..'}{'..id..'}\n'..
        content..'\n'..
        '\\end{listingsbox}'..ifsolution_end
      )
    else -- float
      list_tex = pandoc.RawInline('latex',
        ifsolution_beg..'\\begin{listingsboxfloat}{'..mynewminted..'}{'..caption..'}{'..id..'}{'..position..'}\n'..
        content..'\n'..
        '\\end{listingsboxfloat}'..ifsolution_end
      )
    end
    return list_tex
  elseif FORMAT:match 'html' then
    -- table.insert(code_block.attr.,{caption=caption})
    return pandoc.CodeBlock(
      code_block.text,
      {identifier=id,classes=language,caption=caption}
    )
  else
    return el
  end
end

local function bgreadinglister(el)
  if FORMAT:match 'latex' then
    local content = el.content
    content = pandoc.utils.stringify(content)
    return pandoc.RawInline('latex',
      '\\bgreadinglist{'.. 
      content.. 
      '}\n'
    )
  elseif FORMAT:match 'html' then
    return el -- TODO
  end
end

local function freadinglister(el)
  if FORMAT:match 'latex' then
    el_walked = pandoc.walk_block(el,interior_filter)
    local content_doc = pandoc.Pandoc(el_walked.content)
    local content = pandoc.write(content_doc,'latex')
    local identifier = el.identifier
    if identifier == nil then
      identifier = ""
    else
      identifier = "[label=" .. el.identifier .. "]"
    end
    return pandoc.RawInline('latex',
      '\\freadinglist'..identifier..'{'.. 
      content.. 
      '}\n'
    )
  elseif FORMAT:match 'html' then
    return el -- TODO
  end
end

local function example_solution(el)
  local el_walked 
  el_walked = pandoc.walk_block(el,interior_filter)
  local content_doc = pandoc.Pandoc(el_walked.content)
  local content = pandoc.write(content_doc,'latex')
  content = delimiter_dollar(content)
  return pandoc.RawBlock('latex',
    "\\tcblower\n".. 
    content
  )
end

local function exampler(el)
  if FORMAT:match 'latex' then
    local identifier = el.identifier
    local el_walked = pandoc.walk_block(el,{
      Div = function(el)
        return example_solution(el)
      end
    })
    el_walked = pandoc.walk_block(el_walked,interior_filter)
    local content_doc = pandoc.Pandoc(el_walked.content)
    local content = pandoc.write(content_doc,'latex')
    content = delimiter_dollar(content)
    local hash = el.attr.attributes['h']
    local v = versioned(el)
    if not v then v = '' end
    return pandoc.RawBlock('latex',
      "\\begin{myexample}["..v.."]{"..identifier.."}{"..hash.."}\n\\noindent "..
      content..
      "\n\\end{myexample}"
    )
  else
    return el 
  end
end

local function keyworder(el)
  if FORMAT:match 'latex' then
    local content = pandoc.utils.stringify(el.content)
    return pandoc.RawInline('latex', "\\keyword{" .. content .. "}")
  else
    return el
  end
end

function mathspaner(el) -- for interior math
  if FORMAT:match 'latex' then
    print(dump(el))
    if el.content[1].mathtype == 'InlineMath' then
      return pandoc.RawInline('tex', '$' .. el.text .. '$')
    else
      print(dump(el))
      local identifier = el.identifier
      local content = el.content[1].text
      if not identifier then identifier='' end
      if not content then content='' end
      return pandoc.RawInline('latex', -- this only numbers the last equation
        "\n\\begin{align*}"..
        content.."\\numberthis \\label{"..identifier.."}\n"..
        "\\end{align*}\n"
      )
    end
  else
    return el
  end
end

------------

function Code(el)
    if FORMAT:match 'html' then
      el.classes[#el.classes+1] = 'sourceCode'
      return el
    elseif FORMAT:match 'latex' then
      return coder_latex(el)
    else
      return el
    end
  -- end
end

function CodeBlock(el)
  if FORMAT:match 'html' then
    el.classes[#el.classes+1] = 'sourceCode'
    return el
  elseif FORMAT:match 'latex' then
    return coder_latex(el)
  else
    return el
  end
end

function Image(el)
  if el.classes:includes('nofloat') then
    return figurer(el,true)
  elseif el.classes:includes('figure') then
    return figurer(el,false)
  else
    return figurer(el,false)
  end
end

function Link(el)
  if el.classes:includes('myurl') then
    return myurler(el)
  else
    return el
  end
end

function RawBlock(el)
  if FORMAT:match 'latex' then
    if el.format:match 'html' then -- process html tables (and other html)
      return pandoc.read(el.text, 'html+tex_math_dollars').blocks 
    elseif el.format:match 'algorithm' then
      return algorithmerLATEX(el)
    else
      return el
    end
  elseif FORMAT:match 'html' then
    if el.format:match 'algorithm' then
      return algorithmerHTML(el)
    else
      return el
    end
  else
    return el
  end
end

function RawInline(el)
  return el
end

function Div(el)
  if el.classes:includes('cell') then
    return celler(el)
  elseif el.classes:includes('output') and el.classes:includes('display_data') then
    -- for ipynb images
    if FORMAT:match 'docx' or FORMAT:match 'pdf' or FORMAT:match 'latex' then
      return el
    else
      return {}
    end
  elseif el.classes:includes('infobox') then
    return infoboxer(el)
  elseif el.classes:includes('listing') then
    return listinger(el)
  elseif el.classes:includes('exercise') then
    return exerciser(el)
  elseif el.classes:includes('bgreadinglist') then
    return bgreadinglister(el)
  elseif el.classes:includes('freadinglist') then
    return freadinglister(el)
  elseif el.classes:includes('figure') then
    return figurediver(el)
  elseif el.classes:includes('example') then
    return exampler(el)
  elseif el.classes:includes('theorem') then
    return theoremer(el)
  elseif el.classes:includes('definition') then
    return definitioner(el)
  else
    return el
  end
end

function Span(el)
  if el.classes:includes('key') or el.classes:includes('keys') then
    return keyer(el)
  elseif el.classes:includes('menu') then
    if FORMAT:match 'html' then
      return menuer_html(el)
    elseif FORMAT:match 'latex' then
      return menuer_latex(el)
    else
      return el
    end
  elseif el.classes:includes('path') then
    return pather(el)
  elseif el.classes:includes('hashref') or el.classes:includes('Hashref') then
    return hashrefer(el)
  elseif el.classes:includes('lref') then
    return linerefer(el)
  elseif el.classes:includes('label') then
    return labeler(el)
  elseif el.classes:includes('plaincite') then
    return plainciter(el)
  elseif el.classes:includes('keyword') then
    return keyworder(el)
  elseif el.classes:includes('index') then
    return indexer(el)
  elseif el.classes:includes('ts') or el.classes:includes('ds') then
    return vspaner(el)
  elseif el.classes:includes('tsicon') or el.classes:includes('dsicon') then
    return vsiconer(el)
  elseif version_params_flat[el.classes[1]] then
    return version_params_subber(el)
  elseif starts_with('eq:',el.identifier) then -- display math inside environments like examples should have a tag wrapped arond with identifier starting with eq:
    return mathspaner(el)
  else
    return el
  end
end

function Cite(el)
  first_id = el.citations[1].id
  if starts_with('sec:',first_id) or starts_with('Sec:',first_id) or starts_with('eq:',first_id) or starts_with('Eq:',first_id) or starts_with('tbl:',first_id) or starts_with('Tbl:',first_id) or starts_with('fig:',first_id) or starts_with('Fig:',first_id) or starts_with('lst:',first_id) or starts_with('Lst:',first_id) then
    -- pandoc-crossref
    return el
  else
    return citer(el)
  end
end

function Header(el)
  if FORMAT:match 'latex' then
    -- return headerer_latex(el)
    el.level = el.level + 2
    return el
  elseif FORMAT:match 'html' then
    return headerer_html(el)
  else
    return el
  end
end

function Math(el)
  -- print('\nmath\n')
  if FORMAT:match 'latex' then
    if el.mathtype == 'InlineMath' then
      return pandoc.RawInline('tex', '$' .. el.text .. '$')
    else
      return el
    end
  else
    return el
  end
end

return {
  {Div = Div},
  {Header = Header},
  {RawBlock = RawBlock},
  {Code = Code},
  {CodeBlock = CodeBlock},
  {RawInline = RawInline},
  {Cite = Cite},
  {Span = Span},
  {Link = Link},
  {Math = Math},
  {Image = Image}
  -- {Div = Div, Header = Header,
  -- RawBlock = RawBlock,
  -- Code = Code,
  -- RawInline = RawInline,
  -- Cite = Cite,
  -- Span = Span,
  -- Link = Link,
  -- Image = Image}
}