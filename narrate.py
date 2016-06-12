#!/usr/bin/env python3
# narrate.py, a tool to create a narrative out of nothing by asking questions
# Copyright 2016 Ben Wiederhake
# MIT licensed, so do whatever you want with it :)

import hashlib
from os import getenv
from blessings import Terminal


# ===== Configuration.  Feel free to modify these =====

narrator = 'God'

username = getenv('USER')  # Not really portable, but whatever.
if username is None:
    username = "User"

# Try to keep these balanced, with 'yes' being slightly favored.
# Sorting by weight is NOT necessary, but somewhat good for performance.
responses = [("Yes.", 1.1),
             ("No.", 0.9),
             ("Definitely.", 0.09),
             ("Absolutely not.", 0.09),
             ("I'm afraid it is.", 0.04),
             ("I'm afraid it isn't.", 0.04),
             ("I don't wanna say", 0.01),
             ("That's a good question.", 0.005),
             ("You'd love to know that, wouldn't you?", 0.002),
             ]

responses_total_weight = sum([w for (_, w) in responses])

hash_method = hashlib.sha1

hash_multiplier = responses_total_weight * 1.0 / \
                  int('f' * hash_method().digest_size * 2, 16)


# ===== Building blocks of "responding" =====

def to_hashable(question):
    return narrator.encode() + b'\0' + question.encode()


def to_number(hashable):
    return int(hash_method(hashable).hexdigest(), 16) * hash_multiplier


def lookup_response(mass):
    initial_mass = mass
    mass = mass - 1e-9  # Compensate for rounding errors
    for (response, weight) in responses:
        if mass <= weight:
            return response
        mass = mass - weight
    assert False, ('initial mass was {}, which is {} too much. '
                   'Bug in hash_multiplier?').format(initial_mass, mass)


def compute_response(question):
    return lookup_response(to_number(to_hashable(question)))


# ===== Building blocks of interaction =====

def greet():
    print('''{t.bold}Moderator{t.normal}:
You are now talking to {}.
Please note that they are quite busy, so only yes/no questions are allowed in
order to save bandwidth.
Apart from that, feel free to ask anything.
'''.format(narrator, t=Terminal()))


def not_a_question():
    print('''{t.bold}Moderator{t.normal}:
That doesn't look like a yes/no question.
The answer might not make much sense.
'''.format(t=Terminal()))


def check_question(question):
    good_prefix = ['am ', 'are ', 'is ', 'will ', 'can ', 'may ', 'could ',
                   'should ', 'shall ', 'ought ', 'would ', 'was ', 'do ',
                   'does ']
    bad_start = not any([question.lower().startswith(p) for p in good_prefix])
    bad_end = not question.endswith('?')
    if bad_start or bad_end:
        not_a_question()


def respond(question):
    print('{t.bold}{}{t.normal}:\n{}\n'.format(narrator,
                                               compute_response(question),
                                               t=Terminal()))


def read_question():
    # TODO: Ideally, only trigger on '?\n\n'
    # TODO: Use login-name or similar instead of 'User'
    question = input('{t.bold}{}{t.normal}:\n'.format(username, t=Terminal()))
    print()
    return question


# ===== All together =====

def interview():
    greet()
    try:
        while True:
            q = read_question()
            check_question(q)
            respond(q)
    except EOFError:
        pass


if __name__ == '__main__':
    from sys import argv
    if len(argv) > 2:
        print('Usage: ./narrate.py [narrator]'
              'Example: ./narrate.py "Chuck Norris"')
        exit
    if len(argv) == 2:
        narrator = argv[1]
    interview()
