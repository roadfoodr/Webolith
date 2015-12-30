"""
Helper / util functions to simulate an ORM, for accessing the word/
alphagram sqlite dbs.

"""
import sqlite3
import os
import logging
import json
import random

from django.conf import settings

logger = logging.getLogger(__name__)


class BadInput(Exception):
    pass


class Word(object):
    def __init__(self, word, alphagram=None, definition=None, front_hooks=None,
                 back_hooks=None, inner_front_hook=None, inner_back_hook=None,
                 lexiconSymbols=None):
        self.word = word
        self.alphagram = alphagram
        # Disallow None, to keep compatibility with old code.
        self.definition = definition or ''
        self.front_hooks = front_hooks or ''
        self.back_hooks = back_hooks or ''
        # XXX: This one is camelCase for compatiblity with old model
        # Fix this once we remove old model.
        self.lexiconSymbols = lexiconSymbols or ''
        self.inner_front_hook = True if inner_front_hook == 1 else False
        self.inner_back_hook = True if inner_back_hook == 1 else False


class Alphagram(object):
    def __init__(self, alphagram, probability, length, combinations):
        self.alphagram = alphagram
        self.probability = probability
        self.length = length
        self.combinations = combinations


class Questions(object):
    def __init__(self):
        self.questions = []

    def append(self, question):
        self.questions.append(question)

    def extend(self, questions):
        self.questions.extend(questions.questions)

    def size(self):
        return len(self.questions)

    def shuffle(self):
        random.shuffle(self.questions)

    def clear(self, question):
        self.questions = []

    def to_python(self):
        return [q.to_python() for q in self.questions]

    def to_json(self):
        return json.dumps(self.to_python())


class Question(object):
    def __init__(self, alphagram, answers):
        """
        alphagram - A string
        answers - A list of Word objects. see word_db_helper.py

        """
        self.alphagram = alphagram
        self.answers = answers

    def set_answers_from_word_list(self, word_list):
        self.answers = []
        for word in word_list:
            self.answers.append(Word(word=word))

    def to_python(self):
        return {'q': self.alphagram,
                'a': [w.word for w in self.answers]}


class WordDB(object):
    """
    A database of words/definitions/alphagrams, created by the
    dbCreator C++ program.

    """
    def __init__(self, lexicon_name):
        """
        lexicon is an instance of base.models.Lexicon

        """
        self.conn = sqlite3.connect(os.path.join(settings.WORD_DB_LOCATION,
                                    '%s.db' % lexicon_name))

    def get_word_data(self, word):
        """
        Gets data for the word passed in.

        """
        c = self.conn.cursor()
        c.execute('SELECT lexicon_symbols, definition, front_hooks, '
                  'back_hooks, inner_front_hook, inner_back_hook, '
                  'alphagram FROM words WHERE word = ?', (word,))
        row = c.fetchone()
        if row:
            return Word(word=word, definition=row[1], front_hooks=row[2],
                        back_hooks=row[3], inner_front_hook=row[4],
                        inner_back_hook=row[5], lexiconSymbols=row[0],
                        alphagram=row[6])
        return None

    def get_words_data(self, words):
        """ Gets data for the words passed in. """
        c = self.conn.cursor()
        c.execute(""" SELECT lexicon_symbols, definition, front_hooks,
                  back_hooks, inner_front_hook, inner_back_hook, alphagram,
                  word FROM words WHERE word IN (%s) ORDER BY word""" %
                  ','.join('?' * len(words)), words)
        rows = c.fetchall()
        words = []
        for row in rows:
            words.append(Word(word=row[7], definition=row[1],
                              front_hooks=row[2], back_hooks=row[3],
                              inner_front_hook=row[4], inner_back_hook=row[5],
                              lexiconSymbols=row[0], alphagram=row[6]))
        return words

    def get_words_for_alphagram(self, alphagram):
        """
        Gets a list of words for an alphagram.

        """
        c = self.conn.cursor()
        c.execute('SELECT lexicon_symbols, definition, front_hooks, '
                  'back_hooks, inner_front_hook, inner_back_hook, '
                  'word FROM words WHERE alphagram = ?', (alphagram,))
        rows = c.fetchall()
        words = []
        # Why am I writing my own ORM?
        for row in rows:
            words.append(Word(word=row[6], definition=row[1],
                              front_hooks=row[2], back_hooks=row[3],
                              inner_front_hook=row[4], inner_back_hook=row[5],
                              lexiconSymbols=row[0], alphagram=alphagram))
        return words

    def get_questions_for_probability_range(self, probability_min,
                                            probability_max, length):
        """
        Use a single query to return alphagrams and words for a
        probability range, fully populated. This makes this more
        efficient than calling `get_words_for_alphagram` above
        repeatedly.

        """
        ret = Questions()
        c = self.conn.cursor()

        c.execute("""
            SELECT lexicon_symbols, definition, front_hooks, back_hooks,
            inner_front_hook, inner_back_hook, word, words.alphagram FROM words
            INNER JOIN alphagrams ON words.alphagram = alphagrams.alphagram
            WHERE alphagrams.length = ? AND
            alphagrams.probability BETWEEN ? and ?
            ORDER BY alphagrams.probability

        """, (length, probability_min, probability_max))
        rows = c.fetchall()
        last_alphagram = None
        cur_words = []
        for row in rows:
            alpha = row[7]
            if alpha != last_alphagram and last_alphagram is not None:
                ret.append(Question(last_alphagram, cur_words))
                cur_words = []
            cur_words.append(Word(word=row[6], definition=row[1],
                             front_hooks=row[2], back_hooks=row[3],
                             inner_front_hook=row[4], inner_back_hook=row[5],
                             lexiconSymbols=row[0], alphagram=alpha))
            last_alphagram = alpha
        ret.append(Question(last_alphagram, cur_words))
        return ret

    def get_alphagram_data(self, alphagram):
        c = self.conn.cursor()
        c.execute('SELECT probability, combinations, length FROM alphagrams '
                  'WHERE alphagram = ?', (alphagram,))
        row = c.fetchone()
        if row:
            return Alphagram(alphagram=alphagram, probability=row[0],
                             combinations=row[1], length=row[2])
        return None

    def probability(self, alphagram):
        """
        Gets the probability for the alphagram. Returns None if the
        alphagram is not found (this can be the case for words with
        blanks).

        """
        c = self.conn.cursor()
        c.execute('SELECT probability FROM alphagrams WHERE alphagram=?',
                  (alphagram,))
        row = c.fetchone()
        return row[0]

    def _alphagrams(self, c):
        """ Returns a list of alphagrams fetched by cursor `c`."""
        alphagrams = []
        rows = c.fetchall()
        for row in rows:
            alphagrams.append(Alphagram(alphagram=row[0],
                                        probability=row[1],
                                        combinations=row[2],
                                        length=len(row[0])))
        return alphagrams

    def alphagrams_by_length(self, length):
        """ Get a list of alphagrams by word length. """
        c = self.conn.cursor()
        c.execute('SELECT alphagram, probability, combinations '
                  'FROM alphagrams WHERE length = ?', (length,))
        return self._alphagrams(c)

    def alphagrams_by_probability_range(self, probability_min, probability_max,
                                        length):
        """ Get a list of Alphagrams by probability range. """
        c = self.conn.cursor()
        c.execute('SELECT alphagram, probability, combinations '
                  'FROM alphagrams WHERE length = ? AND '
                  'probability BETWEEN ? AND ?',
                  (length, probability_min, probability_max))
        return self._alphagrams(c)

    def alphagrams_by_probability_list(self, p_list, length):
        """ Gets a list of alphagrams for a list of probabilities."""
        # We're doing straight %-interpolation here so let's verify
        # p_list is a list of integers. Don't want to do SQL-injection.
        for p in p_list:
            if type(p) is not int:
                raise BadInput("Every probability must be an integer. %s" %
                               p_list)
        # Generate IN string.
        in_string = str(tuple(p_list))
        c = self.conn.cursor()
        c.execute('SELECT alphagram, probability, combinations '
                  'FROM alphagrams WHERE length = ? AND '
                  'probability IN %s' % in_string, (length,))

        return self._alphagrams(c)

    def get_questions(self, alphagrams):
        """
        A helper function to return an entire structure, a list of
        alphagrams and words, given a list of alphagrams.

        param:
            - alphagrams - A list of alphagram objects, or strings.
            This function handles both cases.

        """
        ret = Questions()
        for alphagram in alphagrams:
            if hasattr(alphagram, 'alphagram'):
                alph_string = alphagram.alphagram
            else:
                alph_string = alphagram
            question = Question(alph_string,
                                self.get_words_for_alphagram(alph_string))
            ret.append(question)
        return ret
