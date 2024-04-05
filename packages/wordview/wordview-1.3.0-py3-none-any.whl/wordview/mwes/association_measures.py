import json
import math


class PMICalculator:
    """Calculates the Pointwise Mutual Information (PMI) of an n-gram candidate."""

    def __init__(self, ngram_count_source=None, ngram_count_file_path=None):
        """Initializes a new instance of PMICalculator class.

        Args:
            ngram_count_source: A dictionary containing ngram counts.
            ngram_count_file_path: A path to a json file containing ngram counts.

        Returns:
            None
        """
        if ngram_count_source:
            self.counts = ngram_count_source
        elif ngram_count_file_path:
            self.counts = self._load_ngram_counts(ngram_count_file_path)
        else:
            raise ValueError("Either count_source or count_file_path must be provided.")

        self.total_count = sum(self.counts.values())

    def _load_ngram_counts(self, count_file_path) -> dict[str, int]:
        with open(count_file_path, "r") as file:
            counts = json.load(file)
        return counts

    def _prob(self, ngram) -> float:
        return self.counts.get(ngram, 0) / self.total_count

    def compute_association(self, ngram: str) -> float:
        """Computes the association measure (AM)  --currently only in terms of
        PMI, of an n-gram candidate.

        Args:
            ngram: A string containing the n-gram candidate.

        Returns:
            The association measure of the n-gram candidate.

        """
        words = ngram.split()

        p_denominator = 1.0
        for word in words:
            p_denominator *= self._prob(word)

        p_ngram = self._prob(ngram)

        if p_denominator == 0 or p_ngram == 0:
            return float("-inf")
        else:
            return math.log(p_ngram / p_denominator, 2)
