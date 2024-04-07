import pytest
from hideocardgames.highlow import HighLow

def test_compare_cards():
	game = HighLow()

	# カードの値が高い場合
	result = game.compare_cards("♠_K", "♠_Q")
	assert result == "high", "Expected 'high', but got {result}"

	# カードの値が低い場合
	result = game.compare_cards("♠_2", "♠_3")
	assert result == "low", "Expected 'low', but got {result}"

	# カードの値が同じ場合
	result = game.compare_cards("♠_A", "♣︎_A")
	assert result == "tie", "Expected 'tie', but got {result}"