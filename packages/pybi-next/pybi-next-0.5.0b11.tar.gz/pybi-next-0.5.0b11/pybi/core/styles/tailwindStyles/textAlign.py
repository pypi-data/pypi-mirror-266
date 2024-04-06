from pybi.core.styles.styles import StyleBuilder
class TextAlign:
	@property
	def text_left(self):
		return StyleBuilder({"text-align": " left"})
	@property
	def text_center(self):
		return StyleBuilder({"text-align": " center"})
	@property
	def text_right(self):
		return StyleBuilder({"text-align": " right"})
	@property
	def text_justify(self):
		return StyleBuilder({"text-align": " justify"})
	@property
	def text_start(self):
		return StyleBuilder({"text-align": " start"})
	@property
	def text_end(self):
		return StyleBuilder({"text-align": " end"})
