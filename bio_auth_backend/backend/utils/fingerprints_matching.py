from utils import minutiae_matching

class FingerprintsMatching:
    def __init__(self, minutiae1, minutiae2):
        self.minutiae1 = minutiae1
        self.minutiae2 = minutiae2

    def match_score(self):
        return minutiae_matching.match(self.minutiae1, self.minutiae2)
