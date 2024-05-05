#!/usr/bin/python3

'''
This script converts markdown documents into HTML documents.

Each function has its own doctests (just like in lab),
and you should begin this assignment by solving the doctests.
This will let you focus on completing just one small piece of the assignment at a time and not get lost in the "big picture".
Then, once all of these small pieces are complete,
the entire assignment will work "magically".

Dividing up a large project into smaller "doctestable" components is more of an art than a science.
As you get more experience programming,
you'll slowly learn how to divide up your code this way for yourself.
This is one of the main skills that separates senior programmers from junior programmers.

There's a handful of coding techniques in here that we haven't covered in class and you're not expected to understand.
This is intentional.
An important skill when learning a programming language is being able to work in an environment that you don't 100% understand.
(Again, this is similar to when learning a human language...
when we learn a new human languages,
we won't 100% understand everything in the new language,
but we still have to be able to work with the parts that we do understand.)
'''

################################################################################
#
# The functions in this section operate on only a single line of text at a time.
#
################################################################################


def compile_headers(line):
    '''
    Convert markdown headers into <h1>,<h2>,etc tags.

    HINT:
    This is the simplest function to implement in this assignment.
    Use a slices to extract the first part of the line,
    then use if statements to check if they match the appropriate header markdown commands.

    >>> compile_headers('# This is the main header')
    '<h1> This is the main header</h1>'
    >>> compile_headers('## This is a sub-header')
    '<h2> This is a sub-header</h2>'
    >>> compile_headers('### This is a sub-header')
    '<h3> This is a sub-header</h3>'
    >>> compile_headers('#### This is a sub-header')
    '<h4> This is a sub-header</h4>'
    >>> compile_headers('##### This is a sub-header')
    '<h5> This is a sub-header</h5>'
    >>> compile_headers('###### This is a sub-header')
    '<h6> This is a sub-header</h6>'
    >>> compile_headers('      # this is not a header')
    '      # this is not a header'
    '''
    if line[:6]=='######':
        line='<h6>'+line[6:]+'</h6>'
    elif line[:5]=='#####':
        line='<h5>'+line[5:]+'</h5>'
    elif line[:4]=='####':
        line='<h4>'+line[4:]+'</h4>'
    elif line[:3]=='###':
        line='<h3>'+line[3:]+'</h3>'
    elif line[:2]=='##':
        line='<h2>'+line[2:]+'</h2>'
    elif line[:1]=='#':
        line='<h1>'+line[1:]+'</h1>'
    return line



def compile_italic_star(line):
    '''
    Convert "*italic*" into "<i>italic</i>".

    HINT:
    Italics require carefully tracking the beginning and ending positions of the text to be replaced.
    This is similar to the `delete_HTML` function that we implemented in class.
    It's a tiny bit more complicated since we are not just deleting substrings from the text,
    but also adding replacement substrings.

    >>> compile_italic_star('*This is italic!* This is not italic.')
    '<i>This is italic!</i> This is not italic.'
    >>> compile_italic_star('*This is italic!*')
    '<i>This is italic!</i>'
    >>> compile_italic_star('This is *italic*!')
    'This is <i>italic</i>!'
    >>> compile_italic_star('This is not *italic!')
    'This is not *italic!'
    >>> compile_italic_star('*')
    '*'
    >>> compile_italic_star('This is \*not italic\*.')
    'This is *not italic*.'
    >>> compile_italic_star('This is \*not italic either*.')
    'This is *not italic either*.'
    >>> compile_italic_star('This one is also *not italic\*.')
    'This one is also *not italic*.'
    >>> compile_italic_star('\*This sentence is not italic\*')
    '*This sentence is not italic*'
    '''
    """accumulator=''
    italics=False
    count=line.count('*')
    for c in line:
        if c=='*':
            count-=1
            if italics==False and count>=1:
                accumulator+='<i>'
            if italics==False and count<1:
                accumulator+=c
            if italics==True:
                accumulator+='</i>'
            italics=not italics
        else:
            accumulator+=c
    line=accumulator
    return line"""
    """italics=False
    count=line.count('*')
    odd=count%2
    for i in range(count):
        location=line.index('*')
        if italics==False and count!=1:
            line=line[:location]+'<i>'+line[location+1:]
        elif italics==True and (odd==False or count!=1):
            line=line[:location]+'</i>'+line[location+1:]
        count-=1
        italics=not italics
    return line"""

    accumulator=''
    italics=False
    count_a=line.count('*')
    count_b=line.count('\*')
    count=count_a-count_b
    odd=count%2
    location_a=0
    for i in range(count_a):
        location_b=line.index('*',location_a) #check location of this
        if location_b==0 and count>1:
            accumulator+='<i>'
            italics=not italics
            count-=1
        elif italics==False and line[location_b-1]!='\\' and count>1:
            accumulator+=line[location_a:location_b]+'<i>'
            italics=not italics
            count-=1
        elif italics==True and line[location_b-1]!='\\' and (odd==False or count>1):
            accumulator+=line[location_a:location_b]+'</i>'
            italics=not italics
            count-=1
        elif count==1 and odd==True and line[location_b-1]!='\\':
            accumulator+=line[location_a:location_b+1]
        elif line[location_b-2:location_b-2]!='\\':
            accumulator+=line[location_a:location_b-1]+line[location_b]
        location_a=location_b+1 #relative to this
    accumulator+=line[location_a:] #determine whether this should be a or b
    line=accumulator
    return line


def compile_italic_underscore(line):
    '''
    Convert "_italic_" into "<i>italic</i>".

    HINT:
    This function is almost exactly the same as `compile_italic_star`.

    >>> compile_italic_underscore('_This is italic!_ This is not italic.')
    '<i>This is italic!</i> This is not italic.'
    >>> compile_italic_underscore('_This is italic!_')
    '<i>This is italic!</i>'
    >>> compile_italic_underscore('This is _italic_!')
    'This is <i>italic</i>!'
    >>> compile_italic_underscore('This is not _italic!')
    'This is not _italic!'
    >>> compile_italic_underscore('_')
    '_'
    '''
    accumulator=''
    italics=False
    count=line.count('_')
    for c in line:
        if c=='_':
            count-=1
            if italics==False and count>=1:
                accumulator+='<i>'
            if italics==False and count<1:
                accumulator+=c
            if italics==True:
                accumulator+='</i>'
            italics=not italics
        else:
            accumulator+=c
    line=accumulator
    return line


def compile_strikethrough(line):
    '''
    Convert "~~strikethrough~~" to "<ins>strikethrough</ins>".

    HINT:
    The strikethrough annotations are very similar to implement as the italic function.
    The difference is that there are two delimiting characters instead of one.
    This will require carefully thinking about the range of your for loop and all of your list indexing.

    >>> compile_strikethrough('~~This is strikethrough!~~ This is not strikethrough.')
    '<ins>This is strikethrough!</ins> This is not strikethrough.'
    >>> compile_strikethrough('~~This is strikethrough!~~')
    '<ins>This is strikethrough!</ins>'
    >>> compile_strikethrough('This is ~~strikethrough~~!')
    'This is <ins>strikethrough</ins>!'
    >>> compile_strikethrough('This is not ~~strikethrough!')
    'This is not ~~strikethrough!'
    >>> compile_strikethrough('~~')
    '~~'
    '''
    strikethrough=False
    count=line.count('~~')
    odd=count%2
    for i in range(count):
        location=line.index('~~')
        if strikethrough==False and count!=1:
            line=line[:location]+'<ins>'+line[location+2:]
        elif strikethrough==True and (odd==False or count!=1):
            line=line[:location]+'</ins>'+line[location+2:]
        count-=1
        strikethrough=not strikethrough
    return line


"""
    for i in range(len(line)):
        if line[i]=='~' and line[i+1]=='~':
            count-=1
            if strikethrough==False and count>=1:
                accumulator+='<ins>'
            if strikethrough==False and count<1:
                accumulator+=line[i]
            if strikethrough==True:
                accumulator+='</ins>'
            strikethrough=not strikethrough
        elif line[i]!='~' or line[i-1]!='~':
            accumulator+=line[i]
    line=accumulator
    return line
"""


def compile_bold_stars(line):
    '''
    Convert "**bold**" to "<b>bold</b>".

    HINT:
    This function is similar to the strikethrough function.

    >>> compile_bold_stars('**This is bold!** This is not bold.')
    '<b>This is bold!</b> This is not bold.'
    >>> compile_bold_stars('**This is bold!**')
    '<b>This is bold!</b>'
    >>> compile_bold_stars('This is **bold**!')
    'This is <b>bold</b>!'
    >>> compile_bold_stars('This is not **bold!')
    'This is not **bold!'
    >>> compile_bold_stars('**')
    '**'
    '''
    bold=False
    count=line.count('**')
    odd=count%2
    for i in range(count):
        location=line.index('**')
        if bold==False and count!=1:
            line=line[:location]+'<b>'+line[location+2:]
        elif bold==True and (odd==False or count!=1):
            line=line[:location]+'</b>'+line[location+2:]
        count-=1
        bold=not bold
    
    return line


def compile_bold_underscore(line):
    '''
    Convert "__bold__" to "<b>bold</b>".

    HINT:
    This function is similar to the strikethrough function.

    >>> compile_bold_underscore('__This is bold!__ This is not bold.')
    '<b>This is bold!</b> This is not bold.'
    >>> compile_bold_underscore('__This is bold!__')
    '<b>This is bold!</b>'
    >>> compile_bold_underscore('This is __bold__!')
    'This is <b>bold</b>!'
    >>> compile_bold_underscore('This is not __bold!')
    'This is not __bold!'
    >>> compile_bold_underscore('__')
    '__'
    '''
    bold=False
    count=line.count('__')
    odd=count%2
    for i in range(count):
        location=line.index('__')
        if bold==False and count!=1:
            line=line[:location]+'<b>'+line[location+2:]
        elif bold==True and (odd==False or count!=1):
            line=line[:location]+'</b>'+line[location+2:]
        count-=1
        bold=not bold
    return line


def compile_code_inline(line):
    '''
    Add <code> tags.

    HINT:
    This function is like the italics functions because inline code uses only a single character as a delimiter.
    It is more complex, however, because inline code blocks can contain valid HTML inside of them,
    but we do not want that HTML to get rendered as HTML.
    Therefore, we must convert the `<` and `>` signs into `&lt;` and `&gt;` respectively.

    >>> compile_code_inline('You can use backticks like this (`1+2`) to include code in the middle of text.')
    'You can use backticks like this (<code>1+2</code>) to include code in the middle of text.'
    >>> compile_code_inline('This is inline code: `1+2`')
    'This is inline code: <code>1+2</code>'
    >>> compile_code_inline('`1+2`')
    '<code>1+2</code>'
    >>> compile_code_inline('This example has html within the code: `<b>bold!</b>`')
    'This example has html within the code: <code>&lt;b&gt;bold!&lt;/b&gt;</code>'
    >>> compile_code_inline('this example has a math formula in the  code: `1 + 2 < 4`')
    'this example has a math formula in the  code: <code>1 + 2 &lt; 4</code>'
    >>> compile_code_inline('this example has a <b>math formula</b> in the  code: `1 + 2 < 4`')
    'this example has a <b>math formula</b> in the  code: <code>1 + 2 &lt; 4</code>'
    >>> compile_code_inline('```')
    '```'
    >>> compile_code_inline('```python3')
    '```python3'
    '''
    code=False
    count=line.count('`')
    odd=count%2
    for i in range(count):
        location=line.index('`')
        if code==False and count!=1 and line[location:location+3]!='```':
            line=line[:location]+'<code>'+line[location+1:]
            location_a=line.index('<code>')+6
            location_b=line.index('`')
            line=line[:location_a]+line[location_a:location_b].replace('<','&lt;').replace('>','&gt;')+line[location_b:]
        elif code==True and (odd==False or count!=1) and line[location:location+3]!='```':
            line=line[:location]+'</code>'+line[location+1:]
        count-=1
        code=not code
    return line


def compile_links(line):
    '''
    Add <a> tags.

    HINT:
    The links and images are potentially more complicated because they have many types of delimeters: `[]()`.
    These delimiters are not symmetric, however, so we can more easily find the start and stop locations using the strings find function.

    >>> compile_links('Click on the [course webpage](https://github.com/mikeizbicki/cmc-csci040)!')
    'Click on the <a href="https://github.com/mikeizbicki/cmc-csci040">course webpage</a>!'
    >>> compile_links('[course webpage](https://github.com/mikeizbicki/cmc-csci040)')
    '<a href="https://github.com/mikeizbicki/cmc-csci040">course webpage</a>'
    >>> compile_links('this is wrong: [course webpage]    (https://github.com/mikeizbicki/cmc-csci040)')
    'this is wrong: [course webpage]    (https://github.com/mikeizbicki/cmc-csci040)'
    >>> compile_links('this is wrong: [course webpage](https://github.com/mikeizbicki/cmc-csci040')
    'this is wrong: [course webpage](https://github.com/mikeizbicki/cmc-csci040'
    '''
    accumulator=''
    try:
        bracket_1=line.index('[')
    except:
        bracket_1=0
    try:
        bracket_2=line.index(']')
    except:
        bracket_2=0
    try:
        parenthesis_1=line.index('(')
    except:
        parenthesis_1=0
    try:
        parenthesis_2=line.index(')')
    except:
        parenthesis_2=0
    if bracket_1<bracket_2<parenthesis_1<parenthesis_2 and bracket_2+1==parenthesis_1:
        accumulator+=line[:bracket_1]
        accumulator+='<a href="'
        accumulator+=line[parenthesis_1+1:parenthesis_2]
        accumulator+='">'
        accumulator+=line[bracket_1+1:bracket_2]
        accumulator+='</a>'
        accumulator+=line[parenthesis_2+1:]
        accumulator=accumulator.replace('\\','')
        line=accumulator
    return line


def compile_images(line):
    '''
    Add <img> tags.

    HINT:
    Images are formatted in markdown almost exactly the same as links,
    except that images have a leading `!`.
    So your code here should be based off of the <a> tag code.

    >>> compile_images('[Mike Izbicki](https://avatars1.githubusercontent.com/u/1052630?v=2&s=460)')
    '[Mike Izbicki](https://avatars1.githubusercontent.com/u/1052630?v=2&s=460)'
    >>> compile_images('![Mike Izbicki](https://avatars1.githubusercontent.com/u/1052630?v=2&s=460)')
    '<img src="https://avatars1.githubusercontent.com/u/1052630?v=2&s=460" alt="Mike Izbicki" />'
    >>> compile_images('This is an image of Mike Izbicki: ![Mike Izbicki](https://avatars1.githubusercontent.com/u/1052630?v=2&s=460)')
    'This is an image of Mike Izbicki: <img src="https://avatars1.githubusercontent.com/u/1052630?v=2&s=460" alt="Mike Izbicki" />'
    '''
    accumulator=''
    try:
        exclamation=line.index('!')
    except:
        exclamation=-100
    try:
        bracket_1=line.index('[')
    except:
        bracket_1=0
    try:
        bracket_2=line.index(']')
    except:
        bracket_2=0
    try:
        parenthesis_1=line.index('(')
    except:
        parenthesis_1=0
    try:
        parenthesis_2=line.index(')')
    except:
        parenthesis_2=0
    if exclamation<bracket_1<bracket_2<parenthesis_1<parenthesis_2 and bracket_2+1==parenthesis_1 and exclamation+1==bracket_1:
        accumulator+=line[:exclamation]
        accumulator+='<img src="'
        accumulator+=line[parenthesis_1+1:parenthesis_2]
        accumulator+='" alt="'
        accumulator+=line[bracket_1+1:bracket_2]
        accumulator+='" />'
        accumulator+=line[parenthesis_2+1:]
        accumulator=accumulator.replace('\\','')
        line=accumulator
    return line


################################################################################
#
# This next section contains only one function that calls the functions in the previous section.
# This is the "brains" of our application right here.
#
################################################################################

def compile_lines(text):
    r'''
    Apply all markdown transformations to the input text.

    NOTE:
    This function calls all of the functions you created above to convert the full markdown file into HTML.
    This function also handles multiline markdown like <p> tags and <pre> tags;
    because these are multiline commands, they cannot work with the line-by-line style of commands above.

    NOTE:
    The doctests are divided into two sets.
    The first set of doctests below show how this function adds <p> tags and calls the functions above.
    Once you implement the functions above correctly,
    then this first set of doctests will pass.

    NOTE:
    For your assignment, the most important thing to take away from these test cases is how multiline tests can be formatted.

    >>> compile_lines('This is a **bold** _italic_ `code` test.\nAnd *another line*!\n')
    '<p>\nThis is a <b>bold</b> <i>italic</i> <code>code</code> test.\nAnd <i>another line</i>!\n</p>'

    >>> compile_lines("""
    ... This is a **bold** _italic_ `code` test.
    ... And *another line*!
    ... """)
    '\n<p>\nThis is a <b>bold</b> <i>italic</i> <code>code</code> test.\nAnd <i>another line</i>!\n</p>'

    >>> print(compile_lines("""
    ... This is a **bold** _italic_ `code` test.
    ... And *another line*!
    ... """))
    <BLANKLINE>
    <p>
    This is a <b>bold</b> <i>italic</i> <code>code</code> test.
    And <i>another line</i>!
    </p>

    >>> print(compile_lines("""
    ... *paragraph1*
    ...
    ... **paragraph2**
    ...
    ... `paragraph3`
    ... """))
    <BLANKLINE>
    <p>
    <i>paragraph1</i>
    </p>
    <p>
    <b>paragraph2</b>
    </p>
    <p>
    <code>paragraph3</code>
    </p>

    NOTE:
    This second set of test cases tests multiline code blocks.

    HINT:
    In order to get some of these test cases to pass,
    you will have to both add new code and remove some of the existing code that I provide you.

    >>> print(compile_lines("""
    ... ```
    ... x = 1*2 + 3*4
    ... ```
    ... """))
    <BLANKLINE>
    <pre>
    x = 1*2 + 3*4
    </pre>
    <BLANKLINE>

    >>> print(compile_lines("""
    ... Consider the following code block:
    ... ```
    ... x = 1*2 + 3*4
    ... ```
    ... """))
    <BLANKLINE>
    <p>
    Consider the following code block:
    <pre>
    x = 1*2 + 3*4
    </pre>
    </p>

    >>> print(compile_lines("""
    ... Consider the following code block:
    ... ```
    ... x = 1*2 + 3*4
    ... print('x=', x)
    ... ```
    ... And here's another code block:
    ... ```
    ... print(this_is_a_variable)
    ... ```
    ... """))
    <BLANKLINE>
    <p>
    Consider the following code block:
    <pre>
    x = 1*2 + 3*4
    print('x=', x)
    </pre>
    And here's another code block:
    <pre>
    print(this_is_a_variable)
    </pre>
    </p>

    >>> print(compile_lines("""
    ... ```
    ... for i in range(10):
    ...     print('i=',i)
    ... ```
    ... """))
    <BLANKLINE>
    <pre>
    for i in range(10):
        print('i=',i)
    </pre>
    <BLANKLINE>

    >>> print(compile_lines("""
    ... 1. this
    ... 2. is
    ... 3. a
    ... 4. list
    ... """))
    <BLANKLINE>
    <ol><li>this</li>
    <li>is</li>
    <li>a</li>
    <li>list</li>
    </ol>

    >>> print(compile_lines("""
    ... * this
    ... * is
    ... * list
    ... """))
    <BLANKLINE>
    <ul><li>this</li>
    <li>is</li>
    <li>list</li>
    </ul>

    >>> print(compile_lines("""
    ... - *this*
    ... - is
    ... - a
    ... - list
    ... - indeed
    ... """))
    <BLANKLINE>
    <ul><li><i>this</i></li>
    <li>is</li>
    <li>a</li>
    <li>list</li>
    <li>indeed</li>
    </ul>

    >>> print(compile_lines("""
    ... 1. this
    ... 1. is
    ... 1. a
    ... 1. list
    ... 1. indeed
    ... """))
    <BLANKLINE>
    <ol><li>this</li>
    <li>is</li>
    <li>a</li>
    <li>list</li>
    <li>indeed</li>
    </ol>

    >>> print(compile_lines("""
    ... 1. this
    ...   1. is
    ...   1. a
    ... 1. list
    ... """))
    <BLANKLINE>
    <ol><li>this</li>
    <ol><li>is</li>
    <li>a</li>
    </ol><li>list</li>
    </ol>

    >>> print(compile_lines("""
    ... * this
    ...   * is
    ...   * a list
    ... """))
    <BLANKLINE>
    <ul><li>this</li>
    <ul><li>is</li>
    <li>a list</li>
    </ul></ul>

    >>> print(compile_lines("""
    ... 1. look
    ...   6. at
    ...    1. how
    ...       2. big
    ...        4. I
    ...       1. can
    ...    7. make
    ...       7. make
    ...        1. this
    ...   1. this
    ... 1. list
    ... """))
    <BLANKLINE>
    <ol><li>look</li>
    <ol><li>at</li>
    <ol><li>how</li>
    <ol><li>big</li>
    <ol><li>I</li>
    </ol><li>can</li>
    </ol><li>make</li>
    <ol><li>make</li>
    <ol><li>this</li>
    </ol><li>this</li>
    </ol><li>list</li>
    </ol></ol></ol>
    '''
    
    def do_everything(line):
        line = compile_headers(line)
        line = compile_strikethrough(line)
        line = compile_bold_stars(line)
        line = compile_bold_underscore(line)
        line = compile_italic_star(line)
        line = compile_italic_underscore(line)
        line = compile_code_inline(line)
        line = compile_images(line)
        line = compile_links(line)
        return line
    
    lines = text.split('\n')
    new_lines = []
    in_paragraph = False
    in_code=False
    in_ordered_list=False
    in_unordered_list=False
    for line in lines:
        if in_code==False and in_ordered_list==False and in_unordered_list==False:
            line = line.strip()
        if line=='```':
            if in_code==False:
                line='<pre>'
            else:
                line='</pre>'
            in_code=not in_code
        elif line=='' and not in_code:
            if in_paragraph:
                line='</p>'
                in_paragraph = False
            if in_ordered_list:
                line=number_of_ordered_tiers*'</ol>'
                in_ordered_list=False
            if in_unordered_list:
                line=number_of_unordered_tiers*'</ul>'
                in_unordered_list=False
        elif line.strip()[1:3]=='. ' and in_ordered_list==False and line.strip()[0].isnumeric()==True and not in_code:
            in_ordered_list=True
            line='<ol><li>'+line.strip()[3:]+'</li>'
            ordered_tier=len(line)-len(line.lstrip())
            number_of_ordered_tiers=1
            line = do_everything(line)
        elif (line[0:2]=='* ' or line[0:2]=='- ') and in_unordered_list==False and not in_code:
            in_unordered_list=True
            line='<ul><li>'+line.strip()[2:]+'</li>'
            unordered_tier=len(line)-len(line.lstrip())
            number_of_unordered_tiers=1
            line = do_everything(line)
        elif in_code==False:
            if line[0] != '#' and not in_paragraph and not in_ordered_list and not in_unordered_list:
                in_paragraph = True
                line = '<p>\n'+line
            if in_ordered_list==True:
                if line.strip()[1:3]=='. ' and line.strip()[0].isnumeric()==True and ordered_tier==len(line)-len(line.lstrip()):
                    line='<li>'+line.strip()[3:]+'</li>'
                elif line.strip()[1:3]=='. ' and line.strip()[0].isnumeric()==True and ordered_tier<len(line)-len(line.lstrip()):
                    ordered_tier=len(line)-len(line.lstrip())
                    number_of_ordered_tiers+=1
                    line='<ol><li>'+line.strip()[3:]+'</li>'
                elif line.strip()[1:3]=='. ' and line.strip()[0].isnumeric()==True and ordered_tier>len(line)-len(line.lstrip()):
                    ordered_tier=len(line)-len(line.lstrip())
                    number_of_ordered_tiers-=1
                    line='</ol><li>'+line.strip()[3:]+'</li>'
                else:
                    in_ordered_list=False
                    line=number_of_ordered_tiers*'</ol>'+line
            if in_unordered_list==True:
                if (line.strip()[0:2]=='* ' or line.strip()[0:2]=='- ') and unordered_tier==len(line)-len(line.lstrip()):
                    line='<li>'+line.strip()[2:]+'</li>'
                elif (line.strip()[0:2]=='* ' or line.strip()[0:2]=='- ') and unordered_tier<len(line)-len(line.lstrip()):
                    unordered_tier=len(line)-len(line.lstrip())
                    number_of_unordered_tiers+=1
                    line='<ul><li>'+line.strip()[2:]+'</li>'
                elif (line.strip()[0:2]=='* ' or line.strip()[0:2]=='- ') and unordered_tier>len(line)-len(line.lstrip()):
                    unordered_tier=len(line)-len(line.lstrip())
                    number_of_unordered_tiers-=1
                    line='</ul><li>'+line.strip()[2:]+'</li>'
                else:
                    in_unordered_list=False
                    line=number_of_unordered_tiers*'</ul>'+line
            line = do_everything(line)
        new_lines.append(line)
    new_text = '\n'.join(new_lines)
    return new_text
    

    """if line[0:3]=='1. ':
            in_ordered_list=True
            line='<ol><li>'+line[3:]+'</li>'
            previous=line[0]
        elif line[0:3]==str(int(previous+1))+'. ':
            line='<li>'+line[3:]+'</li>'
        elif in_ordered_list==True and line[0:3]!=str(int(previous+1))+'. ':
            in_ordered_list=False
            line='<ol>'"""

    """lines = text.split('\n')
    new_lines = []
    in_paragraph = False
    in_code=False
    for line in lines:
        if in_code==False:
            line = line.strip()
        if line=='```':
            if in_code==False:
                line='<pre>'
            else:
                line='</pre>'
            in_code=not in_code
        elif line=='':
            if in_paragraph:
                line='</p>'
                in_paragraph = False
        elif in_code==False:
            if line[0] != '#' and not in_paragraph:
                in_paragraph = True
                line = '<p>\n'+line
            line = compile_headers(line)
            line = compile_strikethrough(line)
            line = compile_bold_stars(line)
            line = compile_bold_underscore(line)
            line = compile_italic_star(line)
            line = compile_italic_underscore(line)
            line = compile_code_inline(line)
            line = compile_images(line)
            line = compile_links(line)
        new_lines.append(line)
    new_text = '\n'.join(new_lines)
    return new_text"""
