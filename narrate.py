#!/usr/bin/env python3

import hashlib


# ===== Configuration.  Feel free to modify these :) =====

narrator = 'God'

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
    print('Moderator:\nYou are now talking to {}.\nPlease note that they are '
          'quite busy, so only yes/no questions are allowed to save bandwidth.\n'
          'Apart from that, feel free to ask anything.\n'.format(narrator))


def not_a_question():
    print('Moderator:\nThat doesn\'t look like a yes/no question.\n'
          'The answer might not make much sense.\n')


def check_question(question):
    good_prefixes = ['am ', 'are ', 'is ', 'will ', 'can ', 'may ', 'could ',
                     'should ', 'shall ', 'ought ', 'would ', 'was ', 'do ',
                     'does ']
    bad_start = not any([question.lower().startswith(p) for p in good_prefixes])
    bad_end = not question.endswith('?')
    if bad_start or bad_end:
        not_a_question()


def respond(question):
    print('{}:\n{}\n'.format(narrator, compute_response(question)))


def read_question():
    # TODO: Ideally, only trigger on '?\n\n'
    # TODO: Use login-name or similar instead of 'User'
    question = input('User:\n')
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
    interview()
