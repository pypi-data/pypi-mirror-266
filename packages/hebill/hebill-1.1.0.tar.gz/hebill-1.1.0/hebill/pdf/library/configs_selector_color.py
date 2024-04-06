from reportlab.lib import colors


class ColorSelector:
    def __init__(self, configs, dict_key):
        self._configs = configs
        self._dict_key = dict_key

    def _set(self, i): self._configs[self._dict_key] = i

    def aliceblue(self): self._set(colors.aliceblue)

    def antiquewhite(self): self._set(colors.antiquewhite)

    def aqua(self): self._set(colors.aqua)

    def aquamarine(self): self._set(colors.aquamarine)

    def azure(self): self._set(colors.azure)

    def beige(self): self._set(colors.beige)

    def bisque(self): self._set(colors.bisque)

    def black(self): self._set(colors.black)

    def blanchedalmond(self): self._set(colors.blanchedalmond)

    def blue(self): self._set(colors.blue)

    def blueviolet(self): self._set(colors.blueviolet)

    def brown(self): self._set(colors.brown)

    def burlywood(self): self._set(colors.burlywood)

    def cadetblue(self): self._set(colors.cadetblue)

    def chartreuse(self): self._set(colors.chartreuse)

    def chocolate(self): self._set(colors.chocolate)

    def coral(self): self._set(colors.coral)

    def cornflowerblue(self): self._set(colors.cornflowerblue)

    def cornsilk(self): self._set(colors.cornsilk)

    def crimson(self): self._set(colors.crimson)

    def cyan(self): self._set(colors.cyan)

    def darkblue(self): self._set(colors.darkblue)

    def darkcyan(self): self._set(colors.darkcyan)

    def darkgoldenrod(self): self._set(colors.darkgoldenrod)

    def darkgray(self): self._set(colors.darkgray)

    def darkgrey(self): self._set(colors.darkgrey)

    def darkgreen(self): self._set(colors.darkgreen)

    def darkkhaki(self): self._set(colors.darkkhaki)

    def darkmagenta(self): self._set(colors.darkmagenta)

    def darkolivegreen(self): self._set(colors.darkolivegreen)

    def darkorange(self): self._set(colors.darkorange)

    def darkorchid(self): self._set(colors.darkorchid)

    def darkred(self): self._set(colors.darkred)

    def darksalmon(self): self._set(colors.darksalmon)

    def darkseagreen(self): self._set(colors.darkseagreen)

    def darkslateblue(self): self._set(colors.darkslateblue)

    def darkslategray(self): self._set(colors.darkslategray)

    def darkslategrey(self): self._set(colors.darkslategrey)

    def darkturquoise(self): self._set(colors.darkturquoise)

    def darkviolet(self): self._set(colors.darkviolet)

    def deeppink(self): self._set(colors.deeppink)

    def deepskyblue(self): self._set(colors.deepskyblue)

    def dimgray(self): self._set(colors.dimgray)

    def dimgrey(self): self._set(colors.dimgrey)

    def dodgerblue(self): self._set(colors.dodgerblue)

    def firebrick(self): self._set(colors.firebrick)

    def floralwhite(self): self._set(colors.floralwhite)

    def forestgreen(self): self._set(colors.forestgreen)

    def fuchsia(self): self._set(colors.fuchsia)

    def gainsboro(self): self._set(colors.gainsboro)

    def ghostwhite(self): self._set(colors.ghostwhite)

    def gold(self): self._set(colors.gold)

    def goldenrod(self): self._set(colors.goldenrod)

    def gray(self): self._set(colors.gray)

    def grey(self): self._set(colors.grey)

    def green(self): self._set(colors.green)

    def greenyellow(self): self._set(colors.greenyellow)

    def honeydew(self): self._set(colors.honeydew)

    def hotpink(self): self._set(colors.hotpink)

    def indianred(self): self._set(colors.indianred)

    def indigo(self): self._set(colors.indigo)

    def ivory(self): self._set(colors.ivory)

    def khaki(self): self._set(colors.khaki)

    def lavender(self): self._set(colors.lavender)

    def lavenderblush(self): self._set(colors.lavenderblush)

    def lawngreen(self): self._set(colors.lawngreen)

    def lemonchiffon(self): self._set(colors.lemonchiffon)

    def lightblue(self): self._set(colors.lightblue)

    def lightcoral(self): self._set(colors.lightcoral)

    def lightcyan(self): self._set(colors.lightcyan)

    def lightgoldenrodyellow(self): self._set(colors.lightgoldenrodyellow)

    def lightgreen(self): self._set(colors.lightgreen)

    def lightgrey(self): self._set(colors.lightgrey)

    def lightpink(self): self._set(colors.lightpink)

    def lightsalmon(self): self._set(colors.lightsalmon)

    def lightseagreen(self): self._set(colors.lightseagreen)

    def lightskyblue(self): self._set(colors.lightskyblue)

    def lightslategray(self): self._set(colors.lightslategray)

    def lightslategrey(self): self._set(colors.lightslategrey)

    def lightsteelblue(self): self._set(colors.lightsteelblue)

    def lightyellow(self): self._set(colors.lightyellow)

    def lime(self): self._set(colors.lime)

    def limegreen(self): self._set(colors.limegreen)

    def linen(self): self._set(colors.linen)

    def magenta(self): self._set(colors.magenta)

    def maroon(self): self._set(colors.maroon)

    def mediumaquamarine(self): self._set(colors.mediumaquamarine)

    def mediumblue(self): self._set(colors.mediumblue)

    def mediumorchid(self): self._set(colors.mediumorchid)

    def mediumpurple(self): self._set(colors.mediumpurple)

    def mediumseagreen(self): self._set(colors.mediumseagreen)

    def mediumslateblue(self): self._set(colors.mediumslateblue)

    def mediumspringgreen(self): self._set(colors.mediumspringgreen)

    def mediumturquoise(self): self._set(colors.mediumturquoise)

    def mediumvioletred(self): self._set(colors.mediumvioletred)

    def midnightblue(self): self._set(colors.midnightblue)

    def mintcream(self): self._set(colors.mintcream)

    def mistyrose(self): self._set(colors.mistyrose)

    def moccasin(self): self._set(colors.moccasin)

    def navajowhite(self): self._set(colors.navajowhite)

    def navy(self): self._set(colors.navy)

    def oldlace(self): self._set(colors.oldlace)

    def olive(self): self._set(colors.olive)

    def olivedrab(self): self._set(colors.olivedrab)

    def orange(self): self._set(colors.orange)

    def orangered(self): self._set(colors.orangered)

    def orchid(self): self._set(colors.orchid)

    def palegoldenrod(self): self._set(colors.palegoldenrod)

    def palegreen(self): self._set(colors.palegreen)

    def paleturquoise(self): self._set(colors.paleturquoise)

    def palevioletred(self): self._set(colors.palevioletred)

    def papayawhip(self): self._set(colors.papayawhip)

    def peachpuff(self): self._set(colors.peachpuff)

    def peru(self): self._set(colors.peru)

    def pink(self): self._set(colors.pink)

    def plum(self): self._set(colors.plum)

    def powderblue(self): self._set(colors.powderblue)

    def purple(self): self._set(colors.purple)

    def red(self): self._set(colors.red)

    def rosybrown(self): self._set(colors.rosybrown)

    def royalblue(self): self._set(colors.royalblue)

    def saddlebrown(self): self._set(colors.saddlebrown)

    def salmon(self): self._set(colors.salmon)

    def sandybrown(self): self._set(colors.sandybrown)

    def seagreen(self): self._set(colors.seagreen)

    def seashell(self): self._set(colors.seashell)

    def sienna(self): self._set(colors.sienna)

    def silver(self): self._set(colors.silver)

    def skyblue(self): self._set(colors.skyblue)

    def slateblue(self): self._set(colors.slateblue)

    def slategray(self): self._set(colors.slategray)

    def slategrey(self): self._set(colors.slategrey)

    def snow(self): self._set(colors.snow)

    def springgreen(self): self._set(colors.springgreen)

    def steelblue(self): self._set(colors.steelblue)

    def tan(self): self._set(colors.tan)

    def teal(self): self._set(colors.teal)

    def thistle(self): self._set(colors.thistle)

    def tomato(self): self._set(colors.tomato)

    def turquoise(self): self._set(colors.turquoise)

    def violet(self): self._set(colors.violet)

    def wheat(self): self._set(colors.wheat)

    def white(self): self._set(colors.white)

    def whitesmoke(self): self._set(colors.whitesmoke)

    def yellow(self): self._set(colors.yellow)

    def yellowgreen(self): self._set(colors.yellowgreen)

    def fidblue(self): self._set(colors.fidblue)

    def fidred(self): self._set(colors.fidred)

    def fidlightblue(self): self._set(colors.fidlightblue)
    