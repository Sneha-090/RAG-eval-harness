import unittest

from src.corpora import CORPORA, get_corpus


class CorpusRegistryTests(unittest.TestCase):
    def test_fastapi_defaults_preserve_existing_collection_names(self):
        corpus = get_corpus("fastapi-v1")
        self.assertEqual(corpus.fixed_collection, "fastapi_baseline")
        self.assertEqual(corpus.semantic_collection, "fastapi_semantic")

    def test_django_uses_separate_paths_and_collections(self):
        fastapi = CORPORA["fastapi-v1"]
        django = CORPORA["django-5.2"]
        self.assertNotEqual(fastapi.raw_dir, django.raw_dir)
        self.assertNotEqual(fastapi.dataset, django.dataset)
        self.assertNotEqual(fastapi.semantic_collection, django.semantic_collection)

    def test_unknown_corpus_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown corpus"):
            get_corpus("missing")


if __name__ == "__main__":
    unittest.main()
