from pybi.core.styles.styles import StyleBuilder
class BoxShadow:
	@property
	def shadow_sm(self):
		return StyleBuilder({"box-shadow": " 0 1px 2px 0 rgb(0 0 0 / 0.05)"})
	@property
	def shadow(self):
		return StyleBuilder({"box-shadow": " 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)"})
	@property
	def shadow_md(self):
		return StyleBuilder({"box-shadow": " 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)"})
	@property
	def shadow_lg(self):
		return StyleBuilder({"box-shadow": " 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)"})
	@property
	def shadow_xl(self):
		return StyleBuilder({"box-shadow": " 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)"})
	@property
	def shadow_2xl(self):
		return StyleBuilder({"box-shadow": " 0 25px 50px -12px rgb(0 0 0 / 0.25)"})
	@property
	def shadow_inner(self):
		return StyleBuilder({"box-shadow": " inset 0 2px 4px 0 rgb(0 0 0 / 0.05)"})
	@property
	def shadow_none(self):
		return StyleBuilder({"box-shadow": " 0 0 #0000"})
