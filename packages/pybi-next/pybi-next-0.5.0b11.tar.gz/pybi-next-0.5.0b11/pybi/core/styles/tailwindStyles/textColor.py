from pybi.core.styles.styles import StyleBuilder
class TextColor:
	@property
	def text_inherit(self):
		return StyleBuilder({"color": " inherit"})
	@property
	def text_current(self):
		return StyleBuilder({"color": " currentColor"})
	@property
	def text_transparent(self):
		return StyleBuilder({"color": " transparent"})
	@property
	def text_black(self):
		return StyleBuilder({"color": " rgb(0 0 0)"})
	@property
	def text_white(self):
		return StyleBuilder({"color": " rgb(255 255 255)"})
	@property
	def text_slate_50(self):
		return StyleBuilder({"color": " rgb(248 250 252)"})
	@property
	def text_slate_100(self):
		return StyleBuilder({"color": " rgb(241 245 249)"})
	@property
	def text_slate_200(self):
		return StyleBuilder({"color": " rgb(226 232 240)"})
	@property
	def text_slate_300(self):
		return StyleBuilder({"color": " rgb(203 213 225)"})
	@property
	def text_slate_400(self):
		return StyleBuilder({"color": " rgb(148 163 184)"})
	@property
	def text_slate_500(self):
		return StyleBuilder({"color": " rgb(100 116 139)"})
	@property
	def text_slate_600(self):
		return StyleBuilder({"color": " rgb(71 85 105)"})
	@property
	def text_slate_700(self):
		return StyleBuilder({"color": " rgb(51 65 85)"})
	@property
	def text_slate_800(self):
		return StyleBuilder({"color": " rgb(30 41 59)"})
	@property
	def text_slate_900(self):
		return StyleBuilder({"color": " rgb(15 23 42)"})
	@property
	def text_gray_50(self):
		return StyleBuilder({"color": " rgb(249 250 251)"})
	@property
	def text_gray_100(self):
		return StyleBuilder({"color": " rgb(243 244 246)"})
	@property
	def text_gray_200(self):
		return StyleBuilder({"color": " rgb(229 231 235)"})
	@property
	def text_gray_300(self):
		return StyleBuilder({"color": " rgb(209 213 219)"})
	@property
	def text_gray_400(self):
		return StyleBuilder({"color": " rgb(156 163 175)"})
	@property
	def text_gray_500(self):
		return StyleBuilder({"color": " rgb(107 114 128)"})
	@property
	def text_gray_600(self):
		return StyleBuilder({"color": " rgb(75 85 99)"})
	@property
	def text_gray_700(self):
		return StyleBuilder({"color": " rgb(55 65 81)"})
	@property
	def text_gray_800(self):
		return StyleBuilder({"color": " rgb(31 41 55)"})
	@property
	def text_gray_900(self):
		return StyleBuilder({"color": " rgb(17 24 39)"})
	@property
	def text_zinc_50(self):
		return StyleBuilder({"color": " rgb(250 250 250)"})
	@property
	def text_zinc_100(self):
		return StyleBuilder({"color": " rgb(244 244 245)"})
	@property
	def text_zinc_200(self):
		return StyleBuilder({"color": " rgb(228 228 231)"})
	@property
	def text_zinc_300(self):
		return StyleBuilder({"color": " rgb(212 212 216)"})
	@property
	def text_zinc_400(self):
		return StyleBuilder({"color": " rgb(161 161 170)"})
	@property
	def text_zinc_500(self):
		return StyleBuilder({"color": " rgb(113 113 122)"})
	@property
	def text_zinc_600(self):
		return StyleBuilder({"color": " rgb(82 82 91)"})
	@property
	def text_zinc_700(self):
		return StyleBuilder({"color": " rgb(63 63 70)"})
	@property
	def text_zinc_800(self):
		return StyleBuilder({"color": " rgb(39 39 42)"})
	@property
	def text_zinc_900(self):
		return StyleBuilder({"color": " rgb(24 24 27)"})
	@property
	def text_neutral_50(self):
		return StyleBuilder({"color": " rgb(250 250 250)"})
	@property
	def text_neutral_100(self):
		return StyleBuilder({"color": " rgb(245 245 245)"})
	@property
	def text_neutral_200(self):
		return StyleBuilder({"color": " rgb(229 229 229)"})
	@property
	def text_neutral_300(self):
		return StyleBuilder({"color": " rgb(212 212 212)"})
	@property
	def text_neutral_400(self):
		return StyleBuilder({"color": " rgb(163 163 163)"})
	@property
	def text_neutral_500(self):
		return StyleBuilder({"color": " rgb(115 115 115)"})
	@property
	def text_neutral_600(self):
		return StyleBuilder({"color": " rgb(82 82 82)"})
	@property
	def text_neutral_700(self):
		return StyleBuilder({"color": " rgb(64 64 64)"})
	@property
	def text_neutral_800(self):
		return StyleBuilder({"color": " rgb(38 38 38)"})
	@property
	def text_neutral_900(self):
		return StyleBuilder({"color": " rgb(23 23 23)"})
	@property
	def text_stone_50(self):
		return StyleBuilder({"color": " rgb(250 250 249)"})
	@property
	def text_stone_100(self):
		return StyleBuilder({"color": " rgb(245 245 244)"})
	@property
	def text_stone_200(self):
		return StyleBuilder({"color": " rgb(231 229 228)"})
	@property
	def text_stone_300(self):
		return StyleBuilder({"color": " rgb(214 211 209)"})
	@property
	def text_stone_400(self):
		return StyleBuilder({"color": " rgb(168 162 158)"})
	@property
	def text_stone_500(self):
		return StyleBuilder({"color": " rgb(120 113 108)"})
	@property
	def text_stone_600(self):
		return StyleBuilder({"color": " rgb(87 83 78)"})
	@property
	def text_stone_700(self):
		return StyleBuilder({"color": " rgb(68 64 60)"})
	@property
	def text_stone_800(self):
		return StyleBuilder({"color": " rgb(41 37 36)"})
	@property
	def text_stone_900(self):
		return StyleBuilder({"color": " rgb(28 25 23)"})
	@property
	def text_red_50(self):
		return StyleBuilder({"color": " rgb(254 242 242)"})
	@property
	def text_red_100(self):
		return StyleBuilder({"color": " rgb(254 226 226)"})
	@property
	def text_red_200(self):
		return StyleBuilder({"color": " rgb(254 202 202)"})
	@property
	def text_red_300(self):
		return StyleBuilder({"color": " rgb(252 165 165)"})
	@property
	def text_red_400(self):
		return StyleBuilder({"color": " rgb(248 113 113)"})
	@property
	def text_red_500(self):
		return StyleBuilder({"color": " rgb(239 68 68)"})
	@property
	def text_red_600(self):
		return StyleBuilder({"color": " rgb(220 38 38)"})
	@property
	def text_red_700(self):
		return StyleBuilder({"color": " rgb(185 28 28)"})
	@property
	def text_red_800(self):
		return StyleBuilder({"color": " rgb(153 27 27)"})
	@property
	def text_red_900(self):
		return StyleBuilder({"color": " rgb(127 29 29)"})
	@property
	def text_orange_50(self):
		return StyleBuilder({"color": " rgb(255 247 237)"})
	@property
	def text_orange_100(self):
		return StyleBuilder({"color": " rgb(255 237 213)"})
	@property
	def text_orange_200(self):
		return StyleBuilder({"color": " rgb(254 215 170)"})
	@property
	def text_orange_300(self):
		return StyleBuilder({"color": " rgb(253 186 116)"})
	@property
	def text_orange_400(self):
		return StyleBuilder({"color": " rgb(251 146 60)"})
	@property
	def text_orange_500(self):
		return StyleBuilder({"color": " rgb(249 115 22)"})
	@property
	def text_orange_600(self):
		return StyleBuilder({"color": " rgb(234 88 12)"})
	@property
	def text_orange_700(self):
		return StyleBuilder({"color": " rgb(194 65 12)"})
	@property
	def text_orange_800(self):
		return StyleBuilder({"color": " rgb(154 52 18)"})
	@property
	def text_orange_900(self):
		return StyleBuilder({"color": " rgb(124 45 18)"})
	@property
	def text_amber_50(self):
		return StyleBuilder({"color": " rgb(255 251 235)"})
	@property
	def text_amber_100(self):
		return StyleBuilder({"color": " rgb(254 243 199)"})
	@property
	def text_amber_200(self):
		return StyleBuilder({"color": " rgb(253 230 138)"})
	@property
	def text_amber_300(self):
		return StyleBuilder({"color": " rgb(252 211 77)"})
	@property
	def text_amber_400(self):
		return StyleBuilder({"color": " rgb(251 191 36)"})
	@property
	def text_amber_500(self):
		return StyleBuilder({"color": " rgb(245 158 11)"})
	@property
	def text_amber_600(self):
		return StyleBuilder({"color": " rgb(217 119 6)"})
	@property
	def text_amber_700(self):
		return StyleBuilder({"color": " rgb(180 83 9)"})
	@property
	def text_amber_800(self):
		return StyleBuilder({"color": " rgb(146 64 14)"})
	@property
	def text_amber_900(self):
		return StyleBuilder({"color": " rgb(120 53 15)"})
	@property
	def text_yellow_50(self):
		return StyleBuilder({"color": " rgb(254 252 232)"})
	@property
	def text_yellow_100(self):
		return StyleBuilder({"color": " rgb(254 249 195)"})
	@property
	def text_yellow_200(self):
		return StyleBuilder({"color": " rgb(254 240 138)"})
	@property
	def text_yellow_300(self):
		return StyleBuilder({"color": " rgb(253 224 71)"})
	@property
	def text_yellow_400(self):
		return StyleBuilder({"color": " rgb(250 204 21)"})
	@property
	def text_yellow_500(self):
		return StyleBuilder({"color": " rgb(234 179 8)"})
	@property
	def text_yellow_600(self):
		return StyleBuilder({"color": " rgb(202 138 4)"})
	@property
	def text_yellow_700(self):
		return StyleBuilder({"color": " rgb(161 98 7)"})
	@property
	def text_yellow_800(self):
		return StyleBuilder({"color": " rgb(133 77 14)"})
	@property
	def text_yellow_900(self):
		return StyleBuilder({"color": " rgb(113 63 18)"})
	@property
	def text_lime_50(self):
		return StyleBuilder({"color": " rgb(247 254 231)"})
	@property
	def text_lime_100(self):
		return StyleBuilder({"color": " rgb(236 252 203)"})
	@property
	def text_lime_200(self):
		return StyleBuilder({"color": " rgb(217 249 157)"})
	@property
	def text_lime_300(self):
		return StyleBuilder({"color": " rgb(190 242 100)"})
	@property
	def text_lime_400(self):
		return StyleBuilder({"color": " rgb(163 230 53)"})
	@property
	def text_lime_500(self):
		return StyleBuilder({"color": " rgb(132 204 22)"})
	@property
	def text_lime_600(self):
		return StyleBuilder({"color": " rgb(101 163 13)"})
	@property
	def text_lime_700(self):
		return StyleBuilder({"color": " rgb(77 124 15)"})
	@property
	def text_lime_800(self):
		return StyleBuilder({"color": " rgb(63 98 18)"})
	@property
	def text_lime_900(self):
		return StyleBuilder({"color": " rgb(54 83 20)"})
	@property
	def text_green_50(self):
		return StyleBuilder({"color": " rgb(240 253 244)"})
	@property
	def text_green_100(self):
		return StyleBuilder({"color": " rgb(220 252 231)"})
	@property
	def text_green_200(self):
		return StyleBuilder({"color": " rgb(187 247 208)"})
	@property
	def text_green_300(self):
		return StyleBuilder({"color": " rgb(134 239 172)"})
	@property
	def text_green_400(self):
		return StyleBuilder({"color": " rgb(74 222 128)"})
	@property
	def text_green_500(self):
		return StyleBuilder({"color": " rgb(34 197 94)"})
	@property
	def text_green_600(self):
		return StyleBuilder({"color": " rgb(22 163 74)"})
	@property
	def text_green_700(self):
		return StyleBuilder({"color": " rgb(21 128 61)"})
	@property
	def text_green_800(self):
		return StyleBuilder({"color": " rgb(22 101 52)"})
	@property
	def text_green_900(self):
		return StyleBuilder({"color": " rgb(20 83 45)"})
	@property
	def text_emerald_50(self):
		return StyleBuilder({"color": " rgb(236 253 245)"})
	@property
	def text_emerald_100(self):
		return StyleBuilder({"color": " rgb(209 250 229)"})
	@property
	def text_emerald_200(self):
		return StyleBuilder({"color": " rgb(167 243 208)"})
	@property
	def text_emerald_300(self):
		return StyleBuilder({"color": " rgb(110 231 183)"})
	@property
	def text_emerald_400(self):
		return StyleBuilder({"color": " rgb(52 211 153)"})
	@property
	def text_emerald_500(self):
		return StyleBuilder({"color": " rgb(16 185 129)"})
	@property
	def text_emerald_600(self):
		return StyleBuilder({"color": " rgb(5 150 105)"})
	@property
	def text_emerald_700(self):
		return StyleBuilder({"color": " rgb(4 120 87)"})
	@property
	def text_emerald_800(self):
		return StyleBuilder({"color": " rgb(6 95 70)"})
	@property
	def text_emerald_900(self):
		return StyleBuilder({"color": " rgb(6 78 59)"})
	@property
	def text_teal_50(self):
		return StyleBuilder({"color": " rgb(240 253 250)"})
	@property
	def text_teal_100(self):
		return StyleBuilder({"color": " rgb(204 251 241)"})
	@property
	def text_teal_200(self):
		return StyleBuilder({"color": " rgb(153 246 228)"})
	@property
	def text_teal_300(self):
		return StyleBuilder({"color": " rgb(94 234 212)"})
	@property
	def text_teal_400(self):
		return StyleBuilder({"color": " rgb(45 212 191)"})
	@property
	def text_teal_500(self):
		return StyleBuilder({"color": " rgb(20 184 166)"})
	@property
	def text_teal_600(self):
		return StyleBuilder({"color": " rgb(13 148 136)"})
	@property
	def text_teal_700(self):
		return StyleBuilder({"color": " rgb(15 118 110)"})
	@property
	def text_teal_800(self):
		return StyleBuilder({"color": " rgb(17 94 89)"})
	@property
	def text_teal_900(self):
		return StyleBuilder({"color": " rgb(19 78 74)"})
	@property
	def text_cyan_50(self):
		return StyleBuilder({"color": " rgb(236 254 255)"})
	@property
	def text_cyan_100(self):
		return StyleBuilder({"color": " rgb(207 250 254)"})
	@property
	def text_cyan_200(self):
		return StyleBuilder({"color": " rgb(165 243 252)"})
	@property
	def text_cyan_300(self):
		return StyleBuilder({"color": " rgb(103 232 249)"})
	@property
	def text_cyan_400(self):
		return StyleBuilder({"color": " rgb(34 211 238)"})
	@property
	def text_cyan_500(self):
		return StyleBuilder({"color": " rgb(6 182 212)"})
	@property
	def text_cyan_600(self):
		return StyleBuilder({"color": " rgb(8 145 178)"})
	@property
	def text_cyan_700(self):
		return StyleBuilder({"color": " rgb(14 116 144)"})
	@property
	def text_cyan_800(self):
		return StyleBuilder({"color": " rgb(21 94 117)"})
	@property
	def text_cyan_900(self):
		return StyleBuilder({"color": " rgb(22 78 99)"})
	@property
	def text_sky_50(self):
		return StyleBuilder({"color": " rgb(240 249 255)"})
	@property
	def text_sky_100(self):
		return StyleBuilder({"color": " rgb(224 242 254)"})
	@property
	def text_sky_200(self):
		return StyleBuilder({"color": " rgb(186 230 253)"})
	@property
	def text_sky_300(self):
		return StyleBuilder({"color": " rgb(125 211 252)"})
	@property
	def text_sky_400(self):
		return StyleBuilder({"color": " rgb(56 189 248)"})
	@property
	def text_sky_500(self):
		return StyleBuilder({"color": " rgb(14 165 233)"})
	@property
	def text_sky_600(self):
		return StyleBuilder({"color": " rgb(2 132 199)"})
	@property
	def text_sky_700(self):
		return StyleBuilder({"color": " rgb(3 105 161)"})
	@property
	def text_sky_800(self):
		return StyleBuilder({"color": " rgb(7 89 133)"})
	@property
	def text_sky_900(self):
		return StyleBuilder({"color": " rgb(12 74 110)"})
	@property
	def text_blue_50(self):
		return StyleBuilder({"color": " rgb(239 246 255)"})
	@property
	def text_blue_100(self):
		return StyleBuilder({"color": " rgb(219 234 254)"})
	@property
	def text_blue_200(self):
		return StyleBuilder({"color": " rgb(191 219 254)"})
	@property
	def text_blue_300(self):
		return StyleBuilder({"color": " rgb(147 197 253)"})
	@property
	def text_blue_400(self):
		return StyleBuilder({"color": " rgb(96 165 250)"})
	@property
	def text_blue_500(self):
		return StyleBuilder({"color": " rgb(59 130 246)"})
	@property
	def text_blue_600(self):
		return StyleBuilder({"color": " rgb(37 99 235)"})
	@property
	def text_blue_700(self):
		return StyleBuilder({"color": " rgb(29 78 216)"})
	@property
	def text_blue_800(self):
		return StyleBuilder({"color": " rgb(30 64 175)"})
	@property
	def text_blue_900(self):
		return StyleBuilder({"color": " rgb(30 58 138)"})
	@property
	def text_indigo_50(self):
		return StyleBuilder({"color": " rgb(238 242 255)"})
	@property
	def text_indigo_100(self):
		return StyleBuilder({"color": " rgb(224 231 255)"})
	@property
	def text_indigo_200(self):
		return StyleBuilder({"color": " rgb(199 210 254)"})
	@property
	def text_indigo_300(self):
		return StyleBuilder({"color": " rgb(165 180 252)"})
	@property
	def text_indigo_400(self):
		return StyleBuilder({"color": " rgb(129 140 248)"})
	@property
	def text_indigo_500(self):
		return StyleBuilder({"color": " rgb(99 102 241)"})
	@property
	def text_indigo_600(self):
		return StyleBuilder({"color": " rgb(79 70 229)"})
	@property
	def text_indigo_700(self):
		return StyleBuilder({"color": " rgb(67 56 202)"})
	@property
	def text_indigo_800(self):
		return StyleBuilder({"color": " rgb(55 48 163)"})
	@property
	def text_indigo_900(self):
		return StyleBuilder({"color": " rgb(49 46 129)"})
	@property
	def text_violet_50(self):
		return StyleBuilder({"color": " rgb(245 243 255)"})
	@property
	def text_violet_100(self):
		return StyleBuilder({"color": " rgb(237 233 254)"})
	@property
	def text_violet_200(self):
		return StyleBuilder({"color": " rgb(221 214 254)"})
	@property
	def text_violet_300(self):
		return StyleBuilder({"color": " rgb(196 181 253)"})
	@property
	def text_violet_400(self):
		return StyleBuilder({"color": " rgb(167 139 250)"})
	@property
	def text_violet_500(self):
		return StyleBuilder({"color": " rgb(139 92 246)"})
	@property
	def text_violet_600(self):
		return StyleBuilder({"color": " rgb(124 58 237)"})
	@property
	def text_violet_700(self):
		return StyleBuilder({"color": " rgb(109 40 217)"})
	@property
	def text_violet_800(self):
		return StyleBuilder({"color": " rgb(91 33 182)"})
	@property
	def text_violet_900(self):
		return StyleBuilder({"color": " rgb(76 29 149)"})
	@property
	def text_purple_50(self):
		return StyleBuilder({"color": " rgb(250 245 255)"})
	@property
	def text_purple_100(self):
		return StyleBuilder({"color": " rgb(243 232 255)"})
	@property
	def text_purple_200(self):
		return StyleBuilder({"color": " rgb(233 213 255)"})
	@property
	def text_purple_300(self):
		return StyleBuilder({"color": " rgb(216 180 254)"})
	@property
	def text_purple_400(self):
		return StyleBuilder({"color": " rgb(192 132 252)"})
	@property
	def text_purple_500(self):
		return StyleBuilder({"color": " rgb(168 85 247)"})
	@property
	def text_purple_600(self):
		return StyleBuilder({"color": " rgb(147 51 234)"})
	@property
	def text_purple_700(self):
		return StyleBuilder({"color": " rgb(126 34 206)"})
	@property
	def text_purple_800(self):
		return StyleBuilder({"color": " rgb(107 33 168)"})
	@property
	def text_purple_900(self):
		return StyleBuilder({"color": " rgb(88 28 135)"})
	@property
	def text_fuchsia_50(self):
		return StyleBuilder({"color": " rgb(253 244 255)"})
	@property
	def text_fuchsia_100(self):
		return StyleBuilder({"color": " rgb(250 232 255)"})
	@property
	def text_fuchsia_200(self):
		return StyleBuilder({"color": " rgb(245 208 254)"})
	@property
	def text_fuchsia_300(self):
		return StyleBuilder({"color": " rgb(240 171 252)"})
	@property
	def text_fuchsia_400(self):
		return StyleBuilder({"color": " rgb(232 121 249)"})
	@property
	def text_fuchsia_500(self):
		return StyleBuilder({"color": " rgb(217 70 239)"})
	@property
	def text_fuchsia_600(self):
		return StyleBuilder({"color": " rgb(192 38 211)"})
	@property
	def text_fuchsia_700(self):
		return StyleBuilder({"color": " rgb(162 28 175)"})
	@property
	def text_fuchsia_800(self):
		return StyleBuilder({"color": " rgb(134 25 143)"})
	@property
	def text_fuchsia_900(self):
		return StyleBuilder({"color": " rgb(112 26 117)"})
	@property
	def text_pink_50(self):
		return StyleBuilder({"color": " rgb(253 242 248)"})
	@property
	def text_pink_100(self):
		return StyleBuilder({"color": " rgb(252 231 243)"})
	@property
	def text_pink_200(self):
		return StyleBuilder({"color": " rgb(251 207 232)"})
	@property
	def text_pink_300(self):
		return StyleBuilder({"color": " rgb(249 168 212)"})
	@property
	def text_pink_400(self):
		return StyleBuilder({"color": " rgb(244 114 182)"})
	@property
	def text_pink_500(self):
		return StyleBuilder({"color": " rgb(236 72 153)"})
	@property
	def text_pink_600(self):
		return StyleBuilder({"color": " rgb(219 39 119)"})
	@property
	def text_pink_700(self):
		return StyleBuilder({"color": " rgb(190 24 93)"})
	@property
	def text_pink_800(self):
		return StyleBuilder({"color": " rgb(157 23 77)"})
	@property
	def text_pink_900(self):
		return StyleBuilder({"color": " rgb(131 24 67)"})
	@property
	def text_rose_50(self):
		return StyleBuilder({"color": " rgb(255 241 242)"})
	@property
	def text_rose_100(self):
		return StyleBuilder({"color": " rgb(255 228 230)"})
	@property
	def text_rose_200(self):
		return StyleBuilder({"color": " rgb(254 205 211)"})
	@property
	def text_rose_300(self):
		return StyleBuilder({"color": " rgb(253 164 175)"})
	@property
	def text_rose_400(self):
		return StyleBuilder({"color": " rgb(251 113 133)"})
	@property
	def text_rose_500(self):
		return StyleBuilder({"color": " rgb(244 63 94)"})
	@property
	def text_rose_600(self):
		return StyleBuilder({"color": " rgb(225 29 72)"})
	@property
	def text_rose_700(self):
		return StyleBuilder({"color": " rgb(190 18 60)"})
	@property
	def text_rose_800(self):
		return StyleBuilder({"color": " rgb(159 18 57)"})
	@property
	def text_rose_900(self):
		return StyleBuilder({"color": " rgb(136 19 55)"})
