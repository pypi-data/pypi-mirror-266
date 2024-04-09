from .base import Detector


class CustomDetector(Detector):
    def score(self, question, answer=None, samples=None):
        # do your logic here using the building blocks from the Detector class
        # or use your own
        score = 0.0
        return score, answer, samples
