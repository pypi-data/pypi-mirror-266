import base64
import io
from .constants import *


class PNG:
    def __init__(self, source):
        if source.endswith(".png"):
            with open(source, 'rb') as file:
                self._source = base64.b64encode(file.read()).decode('utf-8')
        else:
            self._source = source

    @property
    def source(self): return self._source

    @property
    def file(self): return io.BytesIO(self.bites)

    @property
    def bites(self): return base64.b64decode(self._source.encode('utf-8'))

    def _resize(self, width: int = None, height: int = None):
        pass

    # 使用 PIL.Image
    def pil_image(self, width: int = None, height: int = None):
        from PIL import Image
        image = Image.open(self.file)
        if width:
            image = image.resize((width, height if height else width))
        return image

    def pil_image_save(self, file: str = None, width: int = None, height: int = None):
        self.pil_image(width, height).save(file)

    def pil_icons(self, file: str = None, sizes: list | tuple = None):
        """
        :param file:
        :param sizes: 默认尺寸：(16, 24, 32, 48, 64, 128, 256)
        :return: 保存多尺寸图标文件
        """
        sizes = sizes if sizes else (16, 24, 32, 48, 64, 128, 256)
        file = file if file else f'icon-{'-'.join(map(str, sizes))}.ico'
        image = self.pil_image()
        image.save(file, format='ICO', sizes=[(size, size) for size in sizes])

    def pil_icons_save(self, file: str = None, sizes: list | tuple = None):
        """
        :param file:
        :param sizes: 默认尺寸：(16, 24, 32, 48, 64, 128, 256)
        :return: 保存多尺寸图标文件, 无需
        """
        sizes = sizes if sizes else (16, 24, 32, 48, 64, 128, 256)
        file = file if file else f'icon-{'-'.join(map(str, sizes))}.ico'
        image = self.pil_image()
        image.save(file, format='ICO', sizes=[(size, size) for size in sizes])

    # 使用 wx.Image
    def wx_image(self, width: int = None, height: int = None):
        import wx
        image = wx.Image(self.file)
        if width:
            image = image.Scale(width, height if height else width, wx.IMAGE_QUALITY_HIGH)
        return image

    def wx_image_save(self, file: str = None, width: int = None, height: int = None):
        self.wx_image(width, height).SaveFile(file)

    # 使用 wx.Bitmap
    def wx_bitmap(self, width: int = None, height: int = None):
        import wx
        image = wx.Image(self.file, wx.BITMAP_TYPE_ANY)
        bitmap = wx.Bitmap(image)
        if width:
            image = bitmap.ConvertToImage().Scale(width, width if height is None else height, wx.IMAGE_QUALITY_HIGH)
        return wx.Bitmap(image)

    def wx_bitmap_save(self, file: str = None, width: int = None, height: int = None):
        import wx
        self.wx_bitmap(width, height).SaveFile(file, wx.BITMAP_TYPE_PNG)

    def wx_bitmap_io(self, width: int = None, height: int = None):
        import wx
        buffer = io.BytesIO()
        self.wx_bitmap(width, height).SaveFile(buffer, wx.BITMAP_TYPE_PNG)
        return buffer.getvalue()

    # 使用 wx.Icon
    def wx_icon(self, size: int = None):
        import wx
        icon = wx.Icon()
        icon.CopyFromBitmap(self.wx_image(size if size else None).ConvertToBitmap())
        return icon

    def wx_icon_save(self, file: str = None, size: int = None):
        import wx
        image = self.wx_image(size)
        image.SaveFile(file if file else f'wx-icon-{image.GetWidth()}x{image.GetHeight()}', wx.BITMAP_TYPE_PNG)

    def wx_icons(self, sizes: list = None):
        sizes = sizes if sizes else (16, 24, 32, 48, 64, 128, 256)
        image = self.pil_image()
        ico_data = io.BytesIO()
        image.save(ico_data, format='ICO', sizes=[(size, size) for size in sizes])
        # 使用 wx.Image 创建位图对象
        import wx
        wx_image = wx.Image(ico_data, type=wx.BITMAP_TYPE_ICO)
        # 创建 wx.Icon 对象
        icon = wx.Icon()
        icon.CopyFromBitmap(wx_image.ConvertToBitmap())
        return icon


class PNGIconClose(PNG):
    def __init__(self):
        super().__init__(ICO_CLOSE)


class PNGIconDemo(PNG):
    def __init__(self):
        super().__init__(ICO_DEMO)


class PNGIconDocument(PNG):
    def __init__(self):
        super().__init__(ICO_DOCUMENT)


class PNGIconHelp(PNG):
    def __init__(self):
        super().__init__(ICO_HELP)


class PNGIconHome(PNG):
    def __init__(self):
        super().__init__(ICO_HOME)


class PNGIconIcon(PNG):
    def __init__(self):
        super().__init__(ICO_ICON)


class PNGIconInfo(PNG):
    def __init__(self):
        super().__init__(ICO_INFO)


class PNGIconLangauge(PNG):
    def __init__(self):
        super().__init__(ICO_LANGUAGE)


class PNGIconMaximize(PNG):
    def __init__(self):
        super().__init__(ICO_MAXIMIZE)


class PNGIconMinimize(PNG):
    def __init__(self):
        super().__init__(ICO_MINIMIZE)


class PNGIconMore(PNG):
    def __init__(self):
        super().__init__(ICO_MORE)


class PNGIconNormalize(PNG):
    def __init__(self):
        super().__init__(ICO_NORMALIZE)


class PNGIconQuite(PNG):
    def __init__(self):
        super().__init__(ICO_QUITE)


class PNGIconSetting(PNG):
    def __init__(self):
        super().__init__(ICO_SETTING)


class PNGIconUser(PNG):
    def __init__(self):
        super().__init__(ICO_USER)


class PNGIconHebill(PNG):
    def __init__(self):
        super().__init__(ICO_HEBILL)


class PNGIconYangs(PNG):
    def __init__(self):
        super().__init__(ICO_YANGS)
