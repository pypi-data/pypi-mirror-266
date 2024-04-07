import pytest
from hideocardgames.blackjack import Blackjack

# ゲーム開始時のカードの枚数が2枚になっていることを確認する
def test_initial_deal():
	game = Blackjack()
	game.deal_initial_cards()
	assert len(game.player_hand) == 2
	assert len(game.dealer_hand) == 2

# プレイヤーのhit関数後のカードの枚数が3枚になっていることを確認する
def test_player_hit():
	game = Blackjack()
	game.deal_initial_cards()
	game.player_hit()
	assert len(game.player_hand) == 3

# 勝負する前に相手の手札が2枚以上であることを確認する
def test_dealer_play():
	game = Blackjack()
	game.deal_initial_cards()
	game.dealer_play()
	assert len(game.dealer_hand) >= 2

# 勝負判定でプレイヤーの勝利時の文言を確認する
def test_check_winner():
	game = Blackjack()
	game.deal_initial_cards()
	game.player_hand = ["♠_A", "♠_K"]
	game.dealer_hand = ["♦︎_10", "♣︎_9"]
	assert game.check_winner() == "ブラックジャック！プレイヤーの勝ちです！"
