# coding: utf-8
# Copyright (c) 2008-2011 Volvox Development Team
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Author: Konstantin Lepa <konstantin.lepa@gmail.com>

'''ANSII Color formatting for output in terminal.'''

from __future__ import print_function
import os

__ALL__ = [
    'colored',
    'cprint'
    'grey',
    'red',
    'green',
    'yellow',
    'blue',
    'magenta',
    'cyan',
    'white',
]

ATTRIBUTES = {
    'bold': 1,
    'dark': 2,
    'underline': 4,
    'blink': 5,
    'reverse': 7,
    'concealed': 8,
}

HIGHLIGHTS = {
    'grey': 40,
    'red': 41,
    'green': 42,
    'yellow': 43,
    'blue': 44,
    'magenta': 45,
    'cyan': 46,
    'white': 47,
}

COLORS = {
    'grey': 30,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,
}

RESET = '\033[0m'

FMT_STR = '\033[%dm%s'

ANSI_COLORS_DISABLED = os.getenv('ANSI_COLORS_DISABLED')

def colored(text, color=None, on=None, attrs=None):
    '''
    Colorize text.

    Available text colors:
        red, green, yellow, blue, magenta, cyan, white.

    Available text highlights:
        red, green, yellow, blue, magenta, cyan, white.

    Available attributes:
        bold, dark, underline, blink, reverse, concealed.

    Example:
        colored('Hello, World!', 'red', 'grey', ['blue', 'blink'])
        colored('Hello, World!', 'green')
    '''

    if ANSI_COLORS_DISABLED is None:
        if color is not None:
            text = FMT_STR % (COLORS[color], text)

        if on is not None:
            text = FMT_STR % (HIGHLIGHTS[on], text)

        if attrs is not None:
            for attr in attrs:
                text = FMT_STR % (ATTRIBUTES[attr], text)

        text += RESET

    return text

def cprint(text, color=None, on=None, attrs=None, **kwargs):
    '''Print colorized text. Accepts the same arguments as print().'''
    print((colored(text, color, on, attrs)), **kwargs)

def grey(text, **kwargs):
    return colored(text, color='grey', **kwargs)

def red(text, **kwargs):
    return colored(text, color='red', **kwargs)

def green(text, **kwargs):
    return colored(text, color='green', **kwargs)

def yellow(text, **kwargs):
    return colored(text, color='yellow', **kwargs)

def blue(text, **kwargs):
    return colored(text, color='blue', **kwargs)

def magenta(text, **kwargs):
    return colored(text, color='magenta', **kwargs)

def cyan(text, **kwargs):
    return colored(text, color='cyan', **kwargs)

def white(text, **kwargs):
    return colored(text, color='white', **kwargs)

if __name__ == '__main__':
    print('Current terminal type: %s' % os.getenv('TERM'))
    print('Test basic colors:')
    cprint('Grey color', 'grey')
    cprint('Red color', 'red')
    cprint('Green color', 'green')
    cprint('Yellow color', 'yellow')
    cprint('Blue color', 'blue')
    cprint('Magenta color', 'magenta')
    cprint('Cyan color', 'cyan')
    cprint('White color', 'white')
    print(('-' * 78))

    print('Test highlights:')
    cprint('On grey color', on='grey')
    cprint('On red color', on='red')
    cprint('On green color', on='green')
    cprint('On yellow color', on='yellow')
    cprint('On blue color', on='blue')
    cprint('On magenta color', on='magenta')
    cprint('On cyan color', on='cyan')
    cprint('On white color', color='grey', on='white')
    print('-' * 78)

    print('Test attributes:')
    cprint('Bold grey color', 'grey', attrs=['bold'])
    cprint('Dark red color', 'red', attrs=['dark'])
    cprint('Underline green color', 'green', attrs=['underline'])
    cprint('Blink yellow color', 'yellow', attrs=['blink'])
    cprint('Reversed blue color', 'blue', attrs=['reverse'])
    cprint('Concealed Magenta color', 'magenta', attrs=['concealed'])
    cprint('Bold underline reverse cyan color', 'cyan',
            attrs=['bold', 'underline', 'reverse'])
    cprint('Dark blink concealed white color', 'white',
            attrs=['dark', 'blink', 'concealed'])
    print(('-' * 78))

    print('Test mixing:')
    cprint('Underline red on grey color', 'red', 'grey',
            ['underline'])
    cprint('Reversed green on red color', 'green', 'red', ['reverse'])

    print('Test color-specific functions:')
    print(grey('Grey color'))
    print(red('Red color'))
    print(green('Green color'))
    print(yellow('Yellow color'))
    print(blue('Blue color'))
    print(magenta('Magenta color'))
    print(cyan('Cyan color'))
    print(white('White color'))
    print(red('Red on grey color', on='grey'))
    print(green('Reversed green on red color', on='red', attrs=['reverse']))
    print(('-' * 78))
