import os.path
import uuid
from io import BytesIO

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from .constants import STYLES, MM_PX, IN_PX, DOCUMENT_CONFIGS, PAGE_CONFIGS
from .page.core import Page
from .configs.document_configs import DocumentConfigs
from .configs.page_configs import PageConfigs
from .configs.styles import Styles


class Document:
    def __init__(self, size: tuple | list = None, unit: str = None):
        """
        :param size: list | tuple, like A4: (210, 297) in mm
        :param unit: 'mm', 'in', 'px'
        """
        self.size = size
        self._xs = []
        self._pages = {}
        self._fonts = {}
        self._configs = DocumentConfigs(self, None, DOCUMENT_CONFIGS)
        self._page_configs = PageConfigs(self, None, PAGE_CONFIGS)
        self._styles = Styles(self, None, STYLES)
        # 单位和页面尺寸处理
        self._unit = unit.lower() if unit is not None and unit.lower() in ['mm', 'in', 'px'] else 'mm'
        match self.unit:
            case 'in':
                self._unit_ratio = IN_PX
            case 'mm':
                self._unit_ratio = MM_PX
            case _:
                self._unit_ratio = 1
        # 设置默认值：
        self.add_font(self.styles.font_name)
        if self.unit != 'mm':
            for n, v in self.configs.items():
                if isinstance(v, int) or isinstance(v, float):
                    self.configs[n] = v / 25.4 * 72 / self.unit_ratio
            for n, v in self.page_configs.items():
                if isinstance(v, int) or isinstance(v, float):
                    self.page_configs[n] = v / 25.4 * 72 / self.unit_ratio
            for n, v in self.styles.items():
                if isinstance(v, int) or isinstance(v, float):
                    self.styles[n] = v / 25.4 * 72 / self.unit_ratio

    @property
    def xs(self):
        return self._xs

    def xp(self, m, a=None):
        self._xs.append([m, a])

    @property
    def pages(self):
        return self._pages

    @property
    def fonts(self):
        return self._fonts

    @property
    def page(self) -> Page:
        if len(self._pages) == 0:
            self.add_page()
        return self._pages[len(self._pages)]

    @property
    def unit(self):
        return self._unit

    def page_header(self, page: Page):
        pass

    def page_footer(self, page: Page):
        pass

    @property
    def unit_ratio(self):
        return self._unit_ratio

    @property
    def k(self):
        return self._unit_ratio

    @property
    def configs(self) -> DocumentConfigs:
        return self._configs

    @property
    def page_configs(self) -> PageConfigs:
        return self._page_configs

    @property
    def styles(self) -> Styles:
        return self._styles

    def add_page(self, size=None) -> Page:
        number = len(self._pages) + 1
        self._pages[number] = Page(self, number, size)
        self.page_header(self.page)
        self.page_footer(self.page)
        return self._pages[number]

    def add_font(self, name):
        if name in self._fonts:
            return True
        file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', name + '.ttf')
        if not os.path.exists(file):
            return False
        self._fonts[name] = file

    def _generate(self, pdf: canvas.Canvas):
        # 设置页面标题
        self.xp('setTitle', {'title': self.configs.title})
        self.xp('setAuthor', {'author': self.configs.author})
        self.xp('setSubject', {'subject': self.configs.subject})
        self.xp('setKeywords', {'keywords': self.configs.keywords})
        # 没有页面则创建页面
        if len(self._pages) < 1:
            self.add_page()
        # 加密PDF
        if self.configs.encrypted:
            from reportlab.lib.pdfencrypt import StandardEncryption
            user_password = self.configs.encrypt_user_password \
                if self.configs.encrypt_owner_password is not None else ''
            owner_password = self.configs.encrypt_owner_password \
                if self.configs.encrypt_owner_password is not None else str(uuid.uuid4())
            a1 = StandardEncryption(**{
                'userPassword': user_password,
                'ownerPassword': owner_password,
                'canPrint': 0,
                'canModify': 0,
                'canCopy': 0,
                'canAnnotate': 0,
                'strength': None,
            })
            self.xp('setEncrypt', {'encrypt': a1})
        # 加载字体文件
        for n, f in self.fonts.items():
            pdfmetrics.registerFont(TTFont(n, f))

        # 流水操作
        def generate(xs):
            for x in xs:
                (m1, m2, a) = (*x[0], x[1]) if isinstance(x[0], list) else (x[0], None, x[1])
                match m1:
                    case 'setTitle':
                        pdf.setTitle(**a)
                    case 'setAuthor':
                        pdf.setAuthor(**a)
                    case 'setSubject':
                        pdf.setSubject(**a)
                    case 'setKeywords':
                        pdf.setKeywords(**a)
                    case 'showPage':
                        pdf.showPage()
                    case 'setPageSize':
                        pdf.setPageSize(**a)
                    case 'setLineWidth':
                        pdf.setLineWidth(**a)
                    case 'setStrokeColor':
                        pdf.setStrokeColor(**a)
                    case 'setFont':
                        pdf.setFont(**a)
                    case 'drawString':
                        pdf.drawString(**a)
                    case 'rect':
                        pdf.rect(**a)
                    case 'setFillColor':
                        pdf.setFillColor(**a)
                    case 'line':
                        pdf.line(**a)
                    case 'circle':
                        pdf.circle(**a)
                    case 'setEncrypt':
                        pdf.setEncrypt(**a)
                    case 'beginPath':
                        e = pdf.beginPath()
                        for i in a[0]:
                            match i[0]:
                                case 'move_to':
                                    e.moveTo(**i[1])
                                case 'line_to':
                                    e.lineTo(**i[1])
                                case 'close':
                                    e.close()
                        pdf.drawPath(e, **a[1])
                    case _:
                        print(f'函数"{m1}"没有设定')
                        continue

        generate(self.xs)
        for n, p in self._pages.items():
            generate(p.xs)

    def output(self):
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, self.size)
        self._generate(pdf)
        pdf.save()
        return buffer.getvalue()

    def save(self, file):
        pdf = canvas.Canvas(file, self.size)
        self._generate(pdf)
        pdf.save()
        print(f'文件：{os.path.abspath(file)}（文件大小：{os.path.getsize(file) / 1024} Kbs） 已经保存')


class DocumentA0(Document):
    def __init__(self):
        super().__init__((841, 1189), 'mm')


class DocumentA1(Document):
    def __init__(self):
        super().__init__((594, 841), 'mm')


class DocumentA2(Document):
    def __init__(self):
        super().__init__((420, 594), 'mm')


class DocumentA3(Document):
    def __init__(self):
        super().__init__((297, 420), 'mm')


class DocumentA4(Document):
    def __init__(self):
        super().__init__((210, 297), 'mm')


class DocumentA5(Document):
    def __init__(self):
        super().__init__((148, 210), 'mm')
