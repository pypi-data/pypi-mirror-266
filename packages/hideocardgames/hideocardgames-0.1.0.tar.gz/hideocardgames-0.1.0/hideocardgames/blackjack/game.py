from ..deck import Deck

class Blackjack:
	# デッキの生成とプレイヤーとディーラーの手札を用意
	def __init__(self):
		self.deck = Deck()
		self.player_hand = []
		self.dealer_hand = []

	# 最初にプレイヤーディーラーお互いに2枚ずつカードを引く
	def deal_initial_cards(self):
		self.player_hand = [self.deck.draw(), self.deck.draw()]
		self.dealer_hand = [self.deck.draw(), self.deck.draw()]

	# プレイヤーのヒット（カードを引く）の処理
	def player_hit(self):
		self.player_hand.append(self.deck.draw())

	# ディーラーは手札の合計が17点未満ならヒットさせる
	def dealer_play(self):
		while self._hand_value(self.dealer_hand) < 17:
			self.dealer_hand.append(self.deck.draw())

	# プレイヤーの手札がパスしたか判断
	def is_player_busted(self):
		return self._hand_value(self.player_hand) > 21

	# プレイヤーの手札がブラックジャック（ちょうど21）したか判断
	def is_player_blackjack(self):
		return self._hand_value(self.player_hand) == 21

	# 勝敗判定
	def check_winner(self):
		player_value = self._hand_value(self.player_hand)
		dealer_value = self._hand_value(self.dealer_hand)
		if player_value > 21:
			return "プレイヤーがバストしました。ディーラーの勝ちです。"
		if dealer_value > 21:
			return "ディーラーがバストしました。プレイヤーの勝ちです。"
		if player_value == dealer_value:
			return "引き分けです。"
		if player_value == 21:
			return "ブラックジャック！プレイヤーの勝ちです！"
		if dealer_value == 21:
			return "ディーラーのブラックジャック！ディーラーの勝ちです！"
		if player_value > dealer_value:
			return "プレイヤーの勝ちです。"
		else:
			return "ディーラーの勝ちです。"

	# 再度勝負できるようにし、デッキの残り枚数を確認して再生成
	def reset(self):
		self.player_hand = []
		self.dealer_hand = []
		if self.deck.remaining_cards() < 15:
			self.deck = Deck()

	# 手札のポイント計算
	def _hand_value(self, hand):
		value = 0
		aces = 0

		for card in hand:
			rank = card.split("_")[1]

			if rank == "A":
				aces += 1
				value += 11
			elif rank in ["K", "Q", "J"]:
				value += 10
			else:
				value += int(rank)
		# Aを11にするか1にするかをポイントの合計値で判断
		while value > 21 and aces > 0:
			value -= 10
			aces -= 1

		return value

