import logging
import time

from django.test import TestCase

from base.models import Lexicon, User, AlphagramTag
logger = logging.getLogger(__name__)


class TagSearchCase(TestCase):
    fixtures = [
        'test/lexica.yaml',
        'test/users.json',
        'test/profiles.json'
    ]

    def create_some_tags(self):
        america = Lexicon.objects.get(lexiconName='America')
        self.america = america
        csw15 = Lexicon.objects.get(lexiconName='CSW15')
        self.csw15 = csw15
        cesar = User.objects.get(username='cesar')
        self.cesar = cesar
        user4113 = User.objects.get(username='user_4113')
        # Create a few tags.
        AlphagramTag.objects.create(user=cesar, lexicon=csw15, tag='D4',
                                    alphagram='AELMOSTU')
        AlphagramTag.objects.create(user=user4113, lexicon=america, tag='D3',
                                    alphagram='DEHIOPRT')
        AlphagramTag.objects.create(user=cesar, lexicon=america, tag='D5',
                                    alphagram='AEILT')
        AlphagramTag.objects.create(user=cesar, lexicon=america, tag='D5',
                                    alphagram='CEILNOPR')
        AlphagramTag.objects.create(user=user4113, lexicon=america, tag='D4',
                                    alphagram='CEILNOPR')
        AlphagramTag.objects.create(user=cesar, lexicon=csw15, tag='D1',
                                    alphagram='EIMNOPRS')
        AlphagramTag.objects.create(user=cesar, lexicon=america, tag='D2',
                                    alphagram='CINOZ')
        AlphagramTag.objects.create(user=cesar, lexicon=america, tag='D3',
                                    alphagram='AEEGLNOT')

    def test_tag_no_match(self):
        self.create_some_tags()
        with self.assertRaises(BadInput) as e:
            word_search([
                SearchDescription.lexicon(self.america),
                SearchDescription.length(8, 8),
                SearchDescription.has_tags(['D4'], self.cesar)
            ])
        self.assertEqual(str(e.exception), 'Query returns no results.')

    def test_tag_single(self):
        self.create_some_tags()

        qs = word_search([
            SearchDescription.lexicon(self.csw15),
            SearchDescription.length(8, 8),
            SearchDescription.has_tags(['D4'], self.cesar)
        ])

        self.assertEqual(qs.size(), 1)
        self.assertEqual(['AELMOSTU'], qs.alphagram_string_list())
        # Check that it fully populated the question
        logger.debug(qs.questions_array()[0].to_python_full())
        self.assertEqual(qs.questions_array()[0].to_python_full(), {
            'question': 'AELMOSTU',
            'probability': 2477,
            'answers': [{
                'word': 'SOULMATE',
                'def': 'a person with whom one is perfectly suited [n -S]',
                'f_hooks': '',
                'b_hooks': 'S',
                'symbols': '',
                'f_inner': False,
                'b_inner': False,
            }]
        })

    def test_tag_list(self):
        self.create_some_tags()

        qs = word_search([
            SearchDescription.lexicon(self.america),
            SearchDescription.length(8, 8),
            SearchDescription.has_tags(['D2', 'D3', 'D4', 'D5'], self.cesar)
        ])

        logger.debug('Found qs: %s', qs)
        self.assertEqual(qs.size(), 2)
        self.assertEqual(['AEEGLNOT', 'CEILNOPR'], qs.alphagram_string_list())
        self.assertTrue(len(qs.questions_array()[0].answers[0].definition) > 0)

    def test_more_tags(self):
        self.create_some_tags()

        qs = word_search([
            SearchDescription.lexicon(self.america),
            SearchDescription.length(5, 5),
            SearchDescription.has_tags(['D2', 'D5'], self.cesar)
        ])

        self.assertEqual(qs.size(), 2)
        self.assertEqual(['AEILT', 'CINOZ'], qs.alphagram_string_list())
        self.assertTrue(len(qs.questions_array()[0].answers[0].definition) > 0)


class MassiveTagSearchCase(TestCase):
    fixtures = [
        'test/lexica.yaml',
        'test/users.json',
        'test/profiles.json'
    ]

    def create_some_tags(self):
        self.america = Lexicon.objects.get(lexiconName='America')
        self.cesar = User.objects.get(username='cesar')
        t = time.time()

        qs = word_search([
            SearchDescription.lexicon(self.america),
            SearchDescription.length(8, 8),
            SearchDescription.probability_range(5001, 8500),
        ])
        logger.debug('Initial word search completed in %s seconds',
                     time.time() - t)
        self.assertEqual(qs.size(), 3500)
        # Create hella tags.
        for q in qs.questions_array():
            AlphagramTag.objects.create(user=self.cesar, lexicon=self.america,
                                        tag='D4',
                                        alphagram=q.alphagram.alphagram)
        logger.debug('And time elapsed after tag creation: %s',
                     time.time() - t)

    def test_tag_search(self):
        self.create_some_tags()
        t = time.time()
        qs = word_search([
            SearchDescription.lexicon(self.america),
            SearchDescription.length(8, 8),
            SearchDescription.probability_range(5001, 7500),
            SearchDescription.has_tags(['D4'], self.cesar),
        ])
        logger.debug('Tag search completed in %s seconds', time.time() - t)
        self.assertEqual(qs.size(), 2500)

