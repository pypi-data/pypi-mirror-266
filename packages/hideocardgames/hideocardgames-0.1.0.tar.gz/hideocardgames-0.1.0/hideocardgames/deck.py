import random

class Deck:
	# トランプの絵柄と英数字を事前に用意
	suits = ["♠", "❤︎", "♦︎", "♣︎"]
	values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

	# 生成時にカード全てが揃うように配列で生成
	def __init__(self):
		self.cards = [f"{suit}_{value}" for suit in self.suits for value in self.values]
		# 配列が完成した後、中身を混ぜる
		random.shuffle(self.cards)

	# カードを引く動作
	def draw(self):
		# カードがもうない場合引けないためエラーを表示
		if len(self.cards) == 0:
			raise ValueError("デッキが空です。")
		return self.cards.pop()

	# 残り枚数を確認
	def remaining_cards(self):
		# 配列の長さを取得して残り枚数を確認
		return len(self.cards)