
import signal
import random
import collections
import shutil
import os
import sys
import json

from colorama import init, Fore, Back, Style
import numpy

LINUX, WINDOWS = False, False

if 'linux' in sys.platform:
    LINUX = True
    import readline as readline_if
elif 'win' in sys.platform:
    WINDOWS = True
    import pyreadline as readline_if
else:
    print('Currently only Linux and Windows platforms are supported. This is a ' + sys.platform + 'system.')
    print('Feel free to contact me about this at https://github.com/Antonio95/')
    exit(0)

# TODOs
#
#   installation instructions: linux =      sudo apt-get install libncurses5-dev libncursesw5-dev
#   menu to reset and backup records, etc
#   shutil necessary?
#   signal handling in windows
#   add field for clarification in reverse translation
#   adapttive rate does not take into account type of exercise   
#   automate QUESTIONS[...]
#   automate id_to_class
#   in nouns, tell meaning when asking for plural; and ask for plural when translating to DE
#
#     DONE Select types of exercises
#     DONE records (tracked)
#     DONE Select types of exercises
#     use records
#     maybe the code can be improved (particularly at the beginning of drill() with ordered dictionaries
#     full installation & use guide
#     performance: select the questions Before loading
#     Done Phonetics
#     exercise: HOMOPHONES
#     format review (limit to 99 questions/drill?)
#     Revise points
#     Drill options
#         examples
#         verbose (show all translations)
#     Accept new answer
#     Show data
#     revisar acentos
#     [, ] quitar automaticamente?
#     derivative words
#     puntos en material
#     correct: word field, answer with spaces: it then appears without them
#     exercise: match?


# Onthos: choice of exercises to ask
# * The current formula for the weighted probability of an item being asked is 
#   T/(1 + C^2), where C is the number of previous correct answers and T is the total
#   number of times it has been asked before (see exc. below)
#   note that "sorta" answers count as 0.5 correct answers
# * If an item is added to the material, the loading of the application will 
#   include it in the records file. Its record will be empty and, as an 
#   exception, its weight will be 2, which is equivalent to having been asked
#   twice with 0 correct answers


################################################################################
# GLOBALS #
###########


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATERIAL_PATH = os.path.join(BASE_DIR, 'material.json')
RECORDS_PATH = os.path.join(BASE_DIR, 'records.json')

ACCEPT_NEW = False
CASUAL = False
INITIAL_WEIGHT = 2
N_MODIFIED_IDIOMS = 3
N_QUESTIONS_DIGITS = 2

SCORES = {'yes': 1, 'no': 0, 'sorta': 0.5}

ARTICLES = {
    'm': 'der',
    'f': 'die',
    'n': 'das',
    'p': 'die'
}

# In order to always display/ask about the types in the same order
QUESTIONS = collections.OrderedDict([
    ('Noun', {'ask': True}),
    ('Verb', {'ask': False}),
    ('Adjective+preposition', {'ask': True}),
])

PRESET_THEMES = {
    'original': {
        'bg': Back.BLACK,
        'fg': Fore.YELLOW,
        'right': Fore.GREEN,
        'wrong': Fore.RED,
        'accent': Fore.MAGENTA
    },
    'programmer': {
        'bg': Back.BLACK,
        'fg': Fore.GREEN,
        'right': Fore.BLUE,
        'wrong': Fore.RED,
        'accent': Fore.MAGENTA
    },
    'marine': {
        'bg': Back.WHITE,
        'fg': Fore.BLUE,
        'right': Fore.CYAN,
        'wrong': Fore.MAGENTA,
        'accent': Fore.CYAN
    },
    'clear': {
        'bg': Back.WHITE,
        'fg': Fore.BLACK,
        'right': Fore.GREEN,
        'wrong': Fore.RED,
        'accent': Fore.MAGENTA
    },
}

THEME = PRESET_THEMES['marine']

FEEDBACK = {
    1: THEME['right'] + 'Correct! One point', 
    0.5: THEME['fg'] + 'So-so: half a point', 
    0: THEME['wrong'] +'Whoops, incorrect: no points'
}

################################################################################
# CLASSES #
###########

class Question(object):

    def ask(self, mode):
        return

    def brief(self):
        return


class NounQuestion(Question):

    def __init__(self, gender, noun, plural, meanings):
        self.gender = gender
        self.noun = noun
        self.plural = plural
        self.meanings = meanings

    def ask(self, mode=-1):

        if mode == -1:
            mode = random.randint(0, 1)

        if mode == 0:
            print('[*] Translate (DE -> EN):', self.noun)
            t = 0

            ans_mean = input('    Meaning: ')

            if ans_mean in self.meanings:
                my_print('    '+ 'Right!', THEME['right'])
                t += 1
            else:
                print('    Possible meanings:', ', '.join(self.meanings))
                corr = input_loop('    Accept ' + ans_mean + '? (yes, no, sorta): ', ['yes', 'no', 'sorta'])
                t += SCORES[corr]

            ans_gen = input('    Gender (m, f, n, p): ')

            if ans_gen == self.gender:
                my_print('    ' + 'Right!', THEME['right'])
                t += 1
            else:
                my_print('    Whoops, incorrect: ' + self.gender, THEME['wrong'])

            ans_pl = input('    Plural: ')
            
            if ans_pl == self.plural:
                my_print('    Right!', THEME['right'])
                t += 1
            else:
                my_print('    Whoops, incorrect: ' + self.plural, THEME['wrong'])
                
            if t == 0 or t == 3:
                return t / 3
            else:
                return 0.5

        elif mode == 1:

            print('[*] Translate (EN -> DE):', self.meanings[0])
            t = 0

            ans_mean = input('    Translation: ')

            if ans_mean == self.noun:
                my_print('    ' +'Right!', THEME['right'])
                t += 1
            else:
                my_print('    Whoops, incorrect: ' + self.noun, THEME['wrong'])

            ans_gen = input('    Gender (m, f, n, p): ')

            if ans_gen == self.gender:
                my_print('    Right!', THEME['right'])
                t += 1
            else:
                my_print('    Whoops, incorrect: ' + self.gender, THEME['wrong'])

            ans_pl = input('    Plural: ')
            
            if ans_pl == self.plural:
                my_print('    Right!', THEME['right'])
                t += 1
            else:
                my_print('    Whoops, incorrect: ' + self.plural, THEME['wrong'])
                
            if t == 0 or t == 3:
                return t / 3
            else:
                return 0.5

    def brief(self):
        return '{} {} ({}) -> {}'.format(ARTICLES[self.gender], self.noun, self.plural, self.meanings[0])


class VerbQuestion(Question):

    def __init__(self, infinitive, first, second, third, participle, imperative, meanings):
        self.infinitive = infinitive
        self.first = first
        self.second = second
        self.third = third
        self.participle = participle
        self.meanings = meanings

    def ask(self, mode=-1):
        return ''

    def brief(self):
        return ''


class AdjectivePrepositionQuestion(Question):

    def __init__(self, adjective, preposition, case):
        self.adjective = adjective
        self.preposition = preposition
        self.case = case

    def ask(self, mode=-1):

        print('[*] Adjective with preposition:', self.adjective)
        t = 0

        ans_prep = input('    Preposition: ')

        if ans_prep == self.preposition:
            my_print('    '+ 'Right!', THEME['right'])
            t += 1
        else:
            my_print('    Whoops, incorrect: ' + self.preposition, THEME['wrong'])

        ans_case = input('    Case: ')

        if ans_case == self.case:
            my_print('    '+ 'Right!', THEME['right'])
            t += 1
        else:
            my_print('    Whoops, incorrect: ' + self.case, THEME['wrong'])
            
        if t == 0 or t == 2:
            return t / 2
        else:
            return 0.5

    def brief(self):
        return '{} {} ({}) -> {}'.format(self.adjective, self.preposition, self.case)


ID_TO_CLASS = {
    '1': NounQuestion,
    '2': VerbQuestion,
    '3': AdjectivePrepositionQuestion
}


################################################################################
# METHODS #
###########

def signal_handler_casual_mode(signal, frame):
    
    global CASUAL

    CASUAL = not CASUAL    
    print('\u001b[s', '\u001b[;f', THEME['accent'], 'Casual mode: ', 'ON ' if CASUAL else 'OFF', THEME['fg'], '\u001b[u', sep='', end='', flush=True)

def praise(grade):
    if grade < 0 or grade > 100:
        return 'Whoops! Invalid grade: ' + str(grade)
    
    if grade < 40: 
        return 'Madre mia, la que ha liado pollito...'
    elif grade < 60:
        return 'Así va a asentarse en alemania tu prima'
    elif grade < 80:
        return 'Need to work on these a bit more!'
    elif grade < 90:
        return 'Good job! Practice makes perfect tho'
    elif grade < 100:
        return 'Amazing, you pompous piece of... knowledge'
    else:
        return 'Flawless! More perfect than a potato omelette. Keep it up!'


def load():

    global QUESTIONS

    print ('Loading...')

    with open(RECORDS_PATH, 'r') as rf:
        records = json.load(rf)
    
        with open(MATERIAL_PATH, 'r') as mf:
            material = json.load(mf)

            for item in [inner for outer in material.values() for inner in outer.keys()]:
                if item not in records:
                    records[item] = [0, 0, INITIAL_WEIGHT]
                    print('Added item', item, 'to records')

    with open(RECORDS_PATH, 'w') as rf:
        json.dump(records, rf, indent='    ')

    for qt in QUESTIONS:
        QUESTIONS[qt]["exercises"] = dict([(k, (v, records[k])) for k, v in material[qt].items()])

    print ('Loaded')    


def erase(nl=True, reset=False):
    print('\u001b[2J\u001b[;f' + THEME['fg'], end='\n' if nl else '')
    if reset:
        print(Style.RESET_ALL)


def my_print(s, color=THEME['fg'], end='\n'):
    print(color + s + THEME['fg'], end)


def input_loop(prompt, expected):
    
    ans = None

    while ans not in expected:
        ans = input(prompt).lower()

    return ans


def number_input_loop(prompt, v_min, v_max):
    
    # TODO give feedback?

    ans = 0

    # Awkward flag due to the lack of do-while and potentially unbounded min/max
    enter = True

    while enter == True or ans < v_min or ans > v_max:
        ans = input(prompt)
        
        try:
            ans = int(ans)
            enter = False
        except:
            enter = True
            continue

    return ans


def drill(n=10, review=False):

    global QUESTIONS

    erase()

    print('Current settings:',
        '\n    * number of questions: {}'
        '\n    * review afterwards: {}\n'.format(n, review), THEME['fg'])

    s = input('ENTER to continue, anything else to change: ')

    if '' != s:
        n = number_input_loop('    * Enter the number of questions (1 to {}): '.format(10 ** N_QUESTIONS_DIGITS - 1) + THEME['fg'], 1, 10**N_QUESTIONS_DIGITS - 1)
        review = input_loop('    * Give the option to review at the end? [yes, no]: ' + THEME['fg'], ['yes', 'no']) == 'yes'
        print('    * Select which types of questions you want [yes, no]:' + THEME['fg'])
        for typ, val in QUESTIONS.items():
            val['ask'] = input_loop(' ' * 8 + '- ' + typ + ': ' + THEME['fg'], ['yes', 'no']) == 'yes'

    erase()

    questions = {}

    for val in QUESTIONS.values():
        if val['ask']:
            questions.update(val['exercises'])

    if len(questions) < n:
        print('/!\\ Number of requested questions ({}) larger than that of available ones ({})'
                            '\n    Drill reduced to {} questions'.format(n, len(questions), len(questions)), THEME['fg'] + '\n')
        n = len(questions)

    sorted_ids = list(questions.keys())
    sorted_weights = [questions[i][1][2] for i in sorted_ids]
    total_weight = sum(sorted_weights)
    sorted_weights = list(map(lambda x: x * 1.0 / total_weight, sorted_weights))
    selected_ids = numpy.random.choice(sorted_ids, size=n, replace=False, p=sorted_weights)
    selected_q = [ID_TO_CLASS[i[0]](*questions[i][0]) for i in selected_ids]
    
    score, results = 0, []

    for q in selected_q:
        res = q.ask()
        my_print('    ->', FEEDBACK[res], end='\n\n')
        
        score += res
        results.append(res)
    
    grade = 100.0 * score / n
    
    print('Final score: {} out of {} ({}%). {}'.format(score, n, int(grade), praise(grade)))

    if review:

        ans = input_loop('Move on to review? (yes, no): ', ['yes', 'no'])
        if 'yes' == ans:
                
            erase()

            print('Score: {} out of {} ({}%)'.format(score, n, int(grade)), end='\n\n')
            print('In order to review, enter a sentence involving each of the previous questions\n'
                  'If at some point you cannot remember any more questions, enter an empty line to finish')

            for i in range(n):
                if '' == input('{:4}'.format(str(i + 1) + ':') + THEME['fg']):
                    break

            print('\nThe concepts featured in the questions were: ')
            print('\n'.join(['{:4}'.format(str(i + 1) + '.') + THEME['fg'] + q.brief() for (i, q) in enumerate(selected_q)]))

    if not CASUAL:

        print('Saving records, please do not exit now...')

        with open(RECORDS_PATH, 'r') as rf:
            records = json.load(rf)
        
            for n, i  in enumerate(selected_ids):
                previous = records[i]
                previous[0] += results[n]
                previous[1] += 1
                previous[2] = previous[1] * 1.0 / (1 + previous[0] ** 2)

        with open(RECORDS_PATH, 'w') as rf:
            json.dump(records, rf, indent='    ')

        print('Records saved')


def reset_records(filename=RECORDS_PATH):

    ans = input_loop('Are you sure you want to reset the answers record for ' + Fore.CYAN + filename + THEME['fg'] + '? (yes, no): ', ['yes', 'y', 'no', 'n'])

    if ans in ['yes', 'y']:

        with open(filename, 'r') as file:
            questions = json.load(file)

            for k in questions.keys():
                questions[k] = [0, 0, INITIAL_WEIGHT]

        with open(filename, 'w') as file:
            json.dump(questions, file, indent='    ')

        print('Record reset successful')

    else:
        print('Record reset aborted')


def backup_records(target, source=RECORDS_PATH):

    ans = input_loop('Are you sure you want to backup the records from ' + Fore.CYAN + source + THEME['fg'] + ' into ' + Fore.CYAN + target + THEME['fg'] + '? (yes, no): ', ['yes', 'y', 'no', 'n'])

    if ans in ['yes', 'y']:
        shutil.copyfile(source, target)
        print('Record backup successful')
    else:
        print('Record backup aborted')


################################################################################
# MAIN #
########

if LINUX:
    signal.signal(signal.SIGTSTP, signal_handler_casual_mode)

load()

init()
# load theme
THEME = PRESET_THEMES['marine']

print(THEME['bg'] + THEME['fg'])
erase()

my_print('Sharp Language DE v0.2, by Antonio Mejías Gil' + THEME['right'] + '\nhttps://github.com/Antonio95/')
print('\nNumber of items stored:')
for typ, val in QUESTIONS.items():
    print('    ' + typ, ': ', len(val['exercises']), sep='')
print('    * Total:', sum([len(v['exercises']) for v in QUESTIONS.values()]))

if LINUX:
    my_print('\nUse ' + THEME['accent'] + 'ctrl+z ' + THEME['fg'] + 'at any time to switch casual mode on or off')
    my_print('Use ' + THEME['wrong'] + 'ctrl+c ' + THEME['fg'] + 'at any time to quit')

input('\n(Press Enter to continue)')

drill(15, review=True)

input('\n(Press Enter to finish)')

erase(nl=False, reset=True)

# reset_records()
