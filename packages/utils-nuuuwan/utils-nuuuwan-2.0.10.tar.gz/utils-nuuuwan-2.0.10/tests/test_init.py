import unittest

from utils import (AI, TTS, WWW, Console, Git, Hash, Image, LatLng, Log,
                   Parallel, Translator, Tweet, XMLElement, _)


class TestCase(unittest.TestCase):
    def test_init(self):
        for x in [
            AI,
            TTS,
            WWW,
            Console,
            Git,
            Image,
            LatLng,
            Translator,
            Tweet,
            Log,
            Hash,
            Parallel,
            XMLElement,
            _,
        ]:
            self.assertIsNotNone(x)

    def test_init_custom(self):
        from utils import TimeFormat

        print(TimeFormat.TIME.formatNow)


if __name__ == '__main__':
    unittest.main()
