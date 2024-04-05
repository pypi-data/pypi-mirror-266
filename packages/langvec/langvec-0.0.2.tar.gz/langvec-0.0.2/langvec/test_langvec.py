import unittest

import numpy as np

from .langvec import LangVec


class TestLangVec(unittest.TestCase):
    def setUp(self):
        self.lexicon = ['apple', 'banana', 'cherry', 'date', 'elderberry']
        self.lv = LangVec(lexicon=self.lexicon, chunk_size=3)

    def test_initialize_lexicon_distribution(self):
        expected_distribution = (20.0, 40.0, 60.0, 80.0)
        self.assertEqual(self.lv._lexicon_distribution, expected_distribution)

    def test_fit_valid_data(self):
        X = [np.random.rand(100), np.random.rand(100), np.random.rand(100)]
        self.lv.fit(X)
        self.assertIsNotNone(self.lv.percentiles)
        self.assertEqual(len(self.lv.percentiles), len(self.lexicon) - 1)

    def test_fit_invalid_data_type(self):
        X = np.random.rand(100)
        with self.assertRaises(TypeError):
            self.lv.fit(X)

    def test_fit_invalid_data_shape(self):
        X = [np.random.rand(100), np.random.rand(100).reshape(10, 10)]
        with self.assertRaises(ValueError):
            self.lv.fit(X)

    def test_predict_fitted_model(self):
        X = [np.random.rand(100), np.random.rand(100), np.random.rand(100)]
        self.lv.fit(X)
        input_vector = np.random.rand(100)
        result = self.lv.predict(input_vector, padding=False)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 100 // 3)

    def test_predict_unfitted_model(self):
        input_vector = np.random.rand(100)
        with self.assertRaises(ValueError):
            self.lv.predict(input_vector)

    def test_predict_invalid_input_vector(self):
        X = [np.random.rand(100), np.random.rand(100), np.random.rand(100)]
        self.lv.fit(X)
        input_vector = np.random.rand(100).reshape(10, 10)
        with self.assertRaises(ValueError):
            self.lv.predict(input_vector)

    def test_predict_summarized(self):
        X = [np.random.rand(100), np.random.rand(100), np.random.rand(100)]
        self.lv.fit(X)
        input_vector = np.random.rand(100)
        result = self.lv.predict(input_vector, summarized=True)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 7)  # 3 + 1 + 3

    def test_save_and_load(self):
        X = [np.random.rand(100), np.random.rand(100), np.random.rand(100)]
        self.lv.fit(X)
        filepath = 'tmp/test_model.zip'
        self.lv.save(filepath)
        loaded_lv = LangVec(lexicon=self.lexicon, chunk_size=3)
        loaded_lv.load(filepath)
        np.testing.assert_array_equal(loaded_lv.percentiles, self.lv.percentiles)

    def test_update_valid_data(self):
        X = [np.random.rand(100), np.random.rand(100), np.random.rand(100)]
        self.lv.fit(X)
        new_data = [np.random.rand(50), np.random.rand(50)]
        self.lv.update(new_data)
        self.assertIsNotNone(self.lv.percentiles)
        self.assertEqual(len(self.lv.percentiles), len(self.lexicon) - 1)

    def test_update_unfitted_model(self):
        new_data = [np.random.rand(50), np.random.rand(50)]
        self.lv.update(new_data)
        self.assertIsNotNone(self.lv.percentiles)
        self.assertEqual(len(self.lv.percentiles), len(self.lexicon) - 1)

    def test_update_invalid_data_type(self):
        X = [np.random.rand(100), np.random.rand(100), np.random.rand(100)]
        self.lv.fit(X)
        new_data = np.random.rand(50)
        with self.assertRaises(TypeError):
            self.lv.update(new_data)

    def test_update_invalid_data_shape(self):
        X = [np.random.rand(100), np.random.rand(100), np.random.rand(100)]
        self.lv.fit(X)
        new_data = [np.random.rand(50), np.random.rand(50).reshape(5, 10)]
        with self.assertRaises(ValueError):
            self.lv.update(new_data)


if __name__ == '__main__':
    unittest.main()
