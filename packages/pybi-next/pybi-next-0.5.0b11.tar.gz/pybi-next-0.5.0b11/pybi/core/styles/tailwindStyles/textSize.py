from pybi.core.styles.styles import StyleBuilder
class TextSize:
	@property
	def text_xs(self):
		return StyleBuilder({"font-size": " 0.75rem", "line-height": " 1rem"})
	@property
	def text_sm(self):
		return StyleBuilder({"font-size": " 0.875rem", "line-height": " 1.25rem"})
	@property
	def text_base(self):
		return StyleBuilder({"font-size": " 1rem", "line-height": " 1.5rem"})
	@property
	def text_lg(self):
		return StyleBuilder({"font-size": " 1.125rem", "line-height": " 1.75rem"})
	@property
	def text_xl(self):
		return StyleBuilder({"font-size": " 1.25rem", "line-height": " 1.75rem"})
	@property
	def text_2xl(self):
		return StyleBuilder({"font-size": " 1.5rem", "line-height": " 2rem"})
	@property
	def text_3xl(self):
		return StyleBuilder({"font-size": " 1.875rem", "line-height": " 2.25rem"})
	@property
	def text_4xl(self):
		return StyleBuilder({"font-size": " 2.25rem", "line-height": " 2.5rem"})
	@property
	def text_5xl(self):
		return StyleBuilder({"font-size": " 3rem", "line-height": " 1"})
	@property
	def text_6xl(self):
		return StyleBuilder({"font-size": " 3.75rem", "line-height": " 1"})
	@property
	def text_7xl(self):
		return StyleBuilder({"font-size": " 4.5rem", "line-height": " 1"})
	@property
	def text_8xl(self):
		return StyleBuilder({"font-size": " 6rem", "line-height": " 1"})
	@property
	def text_9xl(self):
		return StyleBuilder({"font-size": " 8rem", "line-height": " 1"})
