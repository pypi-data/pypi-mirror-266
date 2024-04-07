# Deckのインポート
from ..deck import Deck

class HighLow:
	#
	def __init__(self):
		self.deck = Deck()

	def draw_card(self):
		return self.deck.draw()

	# card1とcard2を比較してハイかローかタイの判定を出力する
	def compare_cards(self, card1, card2):
		# 柄はいらないため、数字のみを取得する
		rank1 = card1.split("_")[1]
		rank2 = card2.split("_")[1]
		# 絵札は数字にしておく。Aは今回一番大きい数とする
		if rank1 == 'A':
			value1 = 14
		elif rank1 == 'K':
			value1 = 13
		elif rank1 == 'Q':
			value1 = 12
		elif rank1 == 'J':
			value1 = 11
		else:
			value1 = int(rank1)

		if rank2 == 'A':
			value2 = 14
		elif rank2 == 'K':
			value2 = 13
		elif rank2 == 'Q':
			value2 = 12
		elif rank2 == 'J':
			value2 = 11
		else:
			value2 = int(rank2)
		# 数値を比較して、ハイかローかタイを出力する
		if value1 > value2:
			return "high"
		elif value1 < value2:
			return "low"
		else:
			return "tie"

	# ハイかローかタイを答えてもらうためのプレイヤーの入力を待つようにする
	def player_guess(self):
		guess = input("次のカードはこのカードよりもどう予想しますか？(high/low/tie): ").lower()
		while guess not in ["high", "low", "tie"]:
			print("入力が誤りです。'high'か'low'か'tie'で入力してください。")
			guess = input("次のカードはこのカードよりもどう予想しますか？(high/low/tie): ").lower()
		return guess