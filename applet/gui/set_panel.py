import wx

from applet.gui.common_config import common_font, setting_info


class SetPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(500, 300), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        sbSizer6 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Setting"), wx.VERTICAL)

        gbSizer3 = wx.GridBagSizer(0, 0)
        gbSizer3.SetFlexibleDirection(wx.BOTH)
        gbSizer3.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        m_staticText14 = wx.StaticText(self, wx.ID_ANY, u"Global", wx.DefaultPosition, wx.DefaultSize, 0)
        m_staticText14.SetFont(common_font)

        m_staticText14.Wrap(-1)

        gbSizer3.Add(m_staticText14, wx.GBPosition(1, 4), wx.GBSpan(1, 1), wx.ALL, 5)

        self.m_staticText15 = wx.StaticText(self, wx.ID_ANY, u"Default font", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText15.SetFont(common_font)

        self.m_staticText15.Wrap(-1)

        gbSizer3.Add(self.m_staticText15, wx.GBPosition(2, 4), wx.GBSpan(1, 1), wx.ALL, 5)

        # wx_notify_token = ''
        if setting_info:
            default_font_info = setting_info[0]
            # wx_notify_token = setting_info[1]

            default_font_val = wx.Font()
            default_font_val.SetFamily(default_font_info['Family'])
            default_font_val.SetFaceName(default_font_info['FaceName'])
            default_font_val.SetWeight(default_font_info['Weight'])
            default_font_val.SetPointSize(default_font_info['PointSize'])
        else:
            default_font_val = wx.NullFont

        self.default_font_ctrl = wx.FontPickerCtrl(self, wx.ID_ANY, default_font_val, wx.DefaultPosition,
                                                   wx.DefaultSize,
                                                   wx.FNTP_DEFAULT_STYLE)
        self.default_font_ctrl.SetMaxPointSize(40)
        gbSizer3.Add(self.default_font_ctrl, wx.GBPosition(2, 7), wx.GBSpan(1, 1), wx.ALL, 5)

        # notify_text = wx.StaticText(self, wx.ID_ANY, u"Notify", wx.DefaultPosition, wx.DefaultSize, 0)
        # notify_text.SetFont(common_font)
        # notify_text.Wrap(-1)
        # gbSizer3.Add(notify_text, wx.GBPosition(6, 4), wx.GBSpan(1, 1), wx.ALL, 5)
        #
        # wx_notify_label = wx.StaticText(self, wx.ID_ANY, u"WX notify token", wx.DefaultPosition, wx.DefaultSize, 0)
        # wx_notify_label.SetFont(common_font)
        # wx_notify_label.Wrap(-1)
        # gbSizer3.Add(wx_notify_label, wx.GBPosition(8, 4), wx.GBSpan(1, 1), wx.ALL, 5)
        #
        # self.wx_notify_token_text = wx.TextCtrl(self, wx.ID_ANY, wx_notify_token,
        #                                         wx.DefaultPosition, wx.Size(500, 100), wx.TE_MULTILINE | wx.TE_RICH2)
        # self.wx_notify_token_text.SetFont(common_font)
        # gbSizer3.Add(self.wx_notify_token_text, wx.GBPosition(8, 7), wx.GBSpan(3, 8), wx.ALL | wx.EXPAND, 5)

        self.save_btn = wx.Button(self, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0)
        self.save_btn.SetFont(common_font)

        gbSizer3.Add(self.save_btn, wx.GBPosition(15, 7), wx.GBSpan(1, 1), wx.ALL, 5)

        # gbSizer3.AddGrowableCol(14)

        sbSizer6.Add(gbSizer3, 1, wx.EXPAND, 5)

        self.SetSizer(sbSizer6)
        self.Layout()

    def __del__(self):
        pass
