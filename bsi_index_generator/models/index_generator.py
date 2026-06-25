# -*- coding: utf-8 -*-
import base64
import re
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource


class BsiIndexGenerator(models.Model):
    _name = 'bsi.index.generator'
    _description = 'BSI Dynamic Index Generator'
    _rec_name = 'main_header'

    # ── Company / Contact ─────────────────────────────────────────────────────
    company_name = fields.Char(string='Company Name', default='Botspot Infoware Pvt. Ltd.')
    company_email = fields.Char(string='Company Email', default='contact@botspotinfoware.com')
    website = fields.Char(string='Website', default='https://www.botspotinfoware.com')
    copyright_year = fields.Char(string='Copyright Year', default='2026')

    # ── SEO ───────────────────────────────────────────────────────────────────
    seo_title = fields.Char(string='SEO Title')
    seo_description = fields.Char(string='SEO Description')

    # ── Hero Section ──────────────────────────────────────────────────────────
    main_header = fields.Char(string='Module Heading',
                              help='Main title shown in the hero section and used as the page title')
    main_description = fields.Text(string='Module Description',
                                   help='Short tagline shown below the heading in the hero')

    # ── Why Choose Section ────────────────────────────────────────────────────
    why_choose_title = fields.Char(string='Why Choose – Heading',
                                   help='H2 heading inside the "Why choose this module" card')
    why_choose_para1 = fields.Text(string='Why Choose – Paragraph 1')
    why_choose_para2 = fields.Text(string='Why Choose – Paragraph 2')

    # Stats (three numbered cards inside the why-choose block)
    stat_1_value = fields.Char(string='Value', default='9+')
    stat_1_label = fields.Char(string='Label', default='Filter Options')
    stat_2_value = fields.Char(string='Value', default='v16–v18')
    stat_2_label = fields.Char(string='Label', default='Compatible Versions')
    stat_3_value = fields.Char(string='Value', default='6')
    stat_3_label = fields.Char(string='Label', default='Languages')

    # ── How It Works Section ─────────────────────────────────────────────────
    how_it_works_heading = fields.Char(
        string='How It Works – Heading',
        default='Three steps to instant clarity',
    )
    module_steps = fields.One2many('bsi.module.step', 'generator_id', string='Steps')

    # ── Features Section ──────────────────────────────────────────────────────
    features_main_heading = fields.Char(
        string='Features – Main Heading',
        default='All-in-One Solution',
    )
    feature_main_description = fields.Char(
        string='Features – Sub Description',
        help='Short sentence shown below the features heading',
    )
    feature_ids = fields.One2many('bsi.module.feature', 'generator_id', string='Features')

    # ── Screenshots Section ───────────────────────────────────────────────────
    screenshot_section_description = fields.Char(
        string='Screenshots – Description',
        help='Subtitle shown under the Screenshots heading',
    )
    screenshot_ids = fields.One2many('bsi.module.screenshot', 'generator_id', string='Screenshots')

    # ── Demo Video Section ────────────────────────────────────────────────────
    demo_heading = fields.Char(string='Demo – Heading', default='Watch It in Action')
    demo_description = fields.Char(string='Demo – Description')
    demo_video_link = fields.Char(string='Demo Video URL',
                                  help='YouTube or direct embed URL for the demo video')
    demo_video_thumbnail_html = fields.Html(
        compute='_compute_demo_video_thumbnail_html',
        string='Video Thumbnail',
        sanitize=False,
    )

    @api.depends('demo_video_link')
    def _compute_demo_video_thumbnail_html(self):
        for record in self:
            url = (record.demo_video_link or '').strip()
            video_id = record._extract_youtube_id(url)
            if video_id:
                thumb = f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
                record.demo_video_thumbnail_html = (
                    f'<a href="{url}" target="_blank" rel="noopener noreferrer" style="display:block;">'
                    f'<img src="{thumb}" style="width:100%;border-radius:8px;cursor:pointer;" alt="Video Thumbnail"/>'
                    f'</a>'
                )
            else:
                record.demo_video_thumbnail_html = False

    def _extract_youtube_id(self, url):
        url = (url or '').strip()
        if not url:
            return ''
        parsed = urlparse(url)
        host = (parsed.hostname or '').lower()
        if host in ('youtu.be', 'www.youtu.be'):
            return parsed.path.strip('/')
        if host in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
            if parsed.path == '/watch':
                return parse_qs(parsed.query).get('v', [''])[0]
            if parsed.path.startswith('/embed/'):
                return parsed.path.split('/embed/')[-1].split('?')[0]
        return ''

    # ── Related Modules Section ───────────────────────────────────────────────
    related_module_ids = fields.One2many(
        'bsi.related.module', 'generator_id', string='Related Modules'
    )
    related_modules_explore_url = fields.Char(
        string='Explore All Modules URL',
        default='https://apps.odoo.com/apps/modules/browse?author=Botspot+Infoware',
    )

    # ── Multi-Language Support ────────────────────────────────────────────────
    language_ids = fields.Many2many(
        'bsi.index.language',
        'bsi_gen_language_rel',
        'generator_id',
        'language_id',
        string='Languages',
        help='Select languages to display. If empty, all default languages are shown.',
    )

    # ── Section Visibility ────────────────────────────────────────────────────
    auto_hide_empty_sections = fields.Boolean(
        string='Auto-hide Empty Sections', default=True,
        help='Automatically remove tabs/sections that have no content',
    )
    hide_why_choose_section = fields.Boolean(string='Hide Why Choose Section')
    hide_stats_section = fields.Boolean(string='Hide Stats Cards')
    hide_steps_section = fields.Boolean(string='Hide Steps Section')
    hide_features_section = fields.Boolean(string='Hide Features Tab')
    hide_screenshots_section = fields.Boolean(string='Hide Screenshots Tab')
    hide_demo_section = fields.Boolean(string='Hide Demo Tab')
    hide_related_modules_section = fields.Boolean(string='Hide Related Modules')
    hide_language_section = fields.Boolean(string='Hide Language Section')

    # ── Template & Output ─────────────────────────────────────────────────────
    index_file_id = fields.Many2one(
        'bsi.index.file',
        string='Index Template',
        ondelete='set null',
        default=lambda self: self.env['bsi.index.file'].search(
            [('use_template', '=', True)], limit=1
        ),
        help='Select a saved template. Takes priority over the uploaded template file.',
    )
    # Read-only mirror of the selected library template — shown in form for reference
    index_file_template = fields.Binary(
        related='index_file_id.template',
        string='Template File',
        readonly=True,
    )
    index_file_template_filename = fields.Char(
        related='index_file_id.template_filename',
        string='Template Filename',
        readonly=True,
    )
    template_attachment_ids = fields.Many2many(
        'ir.attachment',
        'bsi_dyn_gen_template_attachment_rel',
        'generator_id',
        'attachment_id',
        string='Custom Template File',
        help='Upload a custom index.html. Used only when no library template is selected.',
    )
    generated_file = fields.Binary(readonly=True)

    # ── Constraints ───────────────────────────────────────────────────────────

    @api.constrains('template_attachment_ids')
    def _check_single_template(self):
        for record in self:
            if len(record.template_attachment_ids) > 1:
                raise ValidationError('Only one template file is allowed at a time.')

    # ── Template Loading ──────────────────────────────────────────────────────

    def _get_template_html(self):
        self.ensure_one()
        # Priority 1: explicitly selected template from library
        if self.index_file_id and self.index_file_id.template:
            return base64.b64decode(self.index_file_id.template).decode('utf-8')
        # Priority 2: active (use_template=True) library record
        default_tpl = self.env['bsi.index.file'].search(
            [('use_template', '=', True)], limit=1
        )
        if default_tpl and default_tpl.template:
            return base64.b64decode(default_tpl.template).decode('utf-8')
        # Priority 3: manually uploaded attachment
        if self.template_attachment_ids:
            return base64.b64decode(self.template_attachment_ids[:1].datas).decode('utf-8')
        # Priority 4: built-in module template
        template_path = get_module_resource(
            'bsi_dynamic_index_generator', 'static', 'description', 'index.html'
        )
        if template_path:
            with open(template_path, 'rb') as fh:
                return fh.read().decode('utf-8')
        return ''

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _image_as_data_uri(self, binary_field, mimetype='image/png'):
        if not binary_field:
            return ''
        data = binary_field if isinstance(binary_field, str) else binary_field.decode('utf-8')
        return f'data:{mimetype};base64,{data}'

    def _set_text(self, soup, selector, value):
        el = soup.select_one(selector)
        if el is not None:
            el.string = value or ''

    def _set_attr(self, soup, selector, attr, value):
        el = soup.select_one(selector)
        if el is not None:
            el[attr] = value or ''

    def _hide_tab(self, soup, pane_id):
        pane = soup.select_one(f'#{pane_id}')
        if pane:
            pane.decompose()
        nav_link = soup.select_one(f'[data-bs-target="#{pane_id}"]')
        if nav_link:
            li = nav_link.find_parent('li')
            if li:
                li.decompose()

    def _resolve_youtube_embed(self, url):
        url = (url or '').strip()
        if not url:
            return ''
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return ''
        host = (parsed.hostname or '').lower()
        if host in ('youtu.be', 'www.youtu.be'):
            vid = parsed.path.strip('/')
            return f'https://www.youtube.com/embed/{vid}' if vid else ''
        if host in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
            if parsed.path == '/watch':
                vid = parse_qs(parsed.query).get('v', [''])[0]
                return f'https://www.youtube.com/embed/{vid}' if vid else ''
            if parsed.path.startswith('/embed/'):
                return url
        return url

    def _get_download_filename(self):
        name = self.main_header or self.company_name or 'index'
        slug = re.sub(r'[^A-Za-z0-9_.-]+', '_', name).strip('_').lower()
        return f'{slug or "index"}.html'

    def _get_language_icon_src(self, lang):
        if lang.icon:
            ext = (lang.icon_filename or '').rsplit('.', 1)[-1].lower()
            mime = 'image/jpeg' if ext in ('jpg', 'jpeg') else 'image/png'
            return self._image_as_data_uri(lang.icon, mime)
        if lang.icon_asset_name:
            try:
                icon_path = get_module_resource(
                    'bsi_dynamic_index_generator',
                    'static', 'description', 'assets', 'icons',
                    lang.icon_asset_name,
                )
                if icon_path:
                    with open(icon_path, 'rb') as f:
                        data = base64.b64encode(f.read()).decode('utf-8')
                    ext = lang.icon_asset_name.rsplit('.', 1)[-1].lower()
                    mime = 'image/jpeg' if ext in ('jpg', 'jpeg') else 'image/png'
                    return f'data:{mime};base64,{data}'
            except Exception:
                pass
        return ''

    # ── Section Injectors ─────────────────────────────────────────────────────

    def _inject_seo(self, soup):
        title_el = soup.select_one('title')
        if title_el:
            title_el.string = self.seo_title or self.main_header or self.company_name or ''
        meta = soup.select_one('meta[name="description"]')
        if not meta:
            head = soup.select_one('head')
            if head:
                meta = soup.new_tag('meta', attrs={'name': 'description'})
                head.append(meta)
        if meta:
            meta['content'] = self.seo_description or self.main_description or ''

    def _inject_hero(self, soup):
        self._set_text(soup, '#hero_heading', self.main_header)
        self._set_text(soup, '#hero_description', self.main_description)

        email_link = soup.select_one('#header_contact_email')
        if email_link:
            email_link['href'] = f'mailto:{self.company_email or ""}'
            email_link.string = self.company_email or ''

    def _inject_why_choose(self, soup):
        self._set_text(soup, '#section_title', self.why_choose_title)
        self._set_text(soup, '#sub_description', self.why_choose_para1)
        self._set_text(soup, '#sub_description_2', self.why_choose_para2)

        self._set_text(soup, '#stat_1_value', self.stat_1_value)
        self._set_text(soup, '#stat_1_label', self.stat_1_label)
        self._set_text(soup, '#stat_2_value', self.stat_2_value)
        self._set_text(soup, '#stat_2_label', self.stat_2_label)
        self._set_text(soup, '#stat_3_value', self.stat_3_value)
        self._set_text(soup, '#stat_3_label', self.stat_3_label)

    def _inject_steps(self, soup):
        self._set_text(soup, '#how_it_works_heading', self.how_it_works_heading)
        step_row = soup.select_one('#module_steps_section')
        if not step_row or not self.module_steps:
            return
        for idx, step in enumerate(self.module_steps, start=1):
            card = BeautifulSoup(f"""
            <div class="col-md-4">
                <div class="h-100" style="background-color:#fdf8ff;border:2px solid #875A7B;
                     border-radius:18px;box-shadow:0 4px 16px #d4b8cc;padding:28px 22px;">
                    <div style="font-size:36px;font-weight:900;color:#875A7B;
                         line-height:1;margin-bottom:10px;">{idx:02d}</div>
                    <h4 style="font-size:14px;font-weight:700;color:#1a1025;
                         margin-bottom:8px;white-space:normal;word-wrap:break-word;
                         overflow-wrap:break-word;">{step.step_heading or ''}</h4>
                    <p style="font-size:13px;color:#7a6b76;line-height:1.7;margin:0;
                       white-space:normal;word-wrap:break-word;
                       overflow-wrap:break-word;">{step.step_description or ''}</p>
                </div>
            </div>
            """, 'html.parser')
            step_row.append(card)

    def _inject_features(self, soup):
        self._set_text(soup, '#features_main_heading', self.features_main_heading)
        self._set_text(soup, '#feature_main_description', self.feature_main_description)
        feature_row = soup.select_one('#features_listing_section')
        if not feature_row or not self.feature_ids:
            return
        for idx, feat in enumerate(self.feature_ids, start=1):
            card = BeautifulSoup(f"""
            <div class="col-md-4">
                <div class="card h-100" style="background-color:#f5edf8;border:2px solid #875A7B;
                     border-radius:18px;box-shadow:0 4px 16px #d4b8cc;padding:24px 20px;">
                    <div style="font-size:10px;font-weight:800;letter-spacing:.15em;
                         text-transform:uppercase;color:#c9a8be;margin-bottom:8px;">
                         {idx:02d} &nbsp;/&nbsp; {feat.feature_title or ''}</div>
                    <h4 style="font-size:14px;font-weight:700;color:#1a1025;
                         margin-bottom:6px;white-space:normal;word-wrap:break-word;
                         overflow-wrap:break-word;">{feat.feature_heading or ''}</h4>
                    <p style="font-size:13px;color:#7a6b76;line-height:1.7;margin:0;
                       white-space:normal;word-wrap:break-word;
                       overflow-wrap:break-word;">{feat.feature_description or ''}</p>
                </div>
            </div>
            """, 'html.parser')
            feature_row.append(card)

    def _inject_screenshots(self, soup):
        self._set_text(soup, '#screenshot_description', self.screenshot_section_description)
        ss_container = soup.select_one('#screenshot_section')
        if not ss_container or not self.screenshot_ids:
            return
        for idx, ss in enumerate(self.screenshot_ids, start=1):
            img_src = self._image_as_data_uri(ss.ss_image)
            img_tag = (
                f'<img src="{img_src}" alt="Screenshot {idx}" '
                'class="img-fluid d-block w-100">'
                if img_src else
                f'<div style="height:200px;background:#f0e8f0;display:flex;'
                'align-items:center;justify-content:center;color:#9b8fa3;'
                f'font-size:13px;">No image for step {idx}</div>'
            )
            card = BeautifulSoup(f"""
            <div class="card overflow-hidden mb-4"
                 style="border:2px solid #875A7B;border-radius:18px;">
                <div class="card-header bg-white d-flex align-items-center gap-3 py-3 px-4"
                     style="border-bottom:1.5px solid #e4d0dc;">
                    <span style="min-width:32px;height:32px;font-size:11px;
                         background-color:#875A7B;color:#ffffff;border-radius:6px;
                         display:inline-flex;align-items:center;justify-content:center;
                         font-weight:bold;">{idx:02d}</span>
                    <h3 style="margin:0;font-weight:bold;font-size:14px;
                         color:#1a1025;">{ss.ss_heading or ''}</h3>
                </div>
                {img_tag}
                <div class="card-body px-4 py-3"
                     style="border-top:1.5px solid #e4d0dc;">
                    <p class="mb-0" style="font-size:13px;color:#7a6b76;line-height:1.7;">
                        <strong style="color:#3d2e3a;">{ss.ss_description or ''}</strong>
                    </p>
                </div>
            </div>
            """, 'html.parser')
            ss_container.append(card)

    def _inject_demo(self, soup):
        self._set_text(soup, '#demo_heading', self.demo_heading)
        self._set_text(soup, '#demo_description', self.demo_description)

        link = soup.select_one('#demo_video_link')
        if not link:
            return
        url = (self.demo_video_link or '').strip()
        link['href'] = url or '#'

        # Set thumbnail image src to the YouTube thumbnail
        thumb_img = soup.select_one('#demo_video_thumbnail')
        if thumb_img:
            video_id = self._extract_youtube_id(url)
            if video_id:
                thumb_img['src'] = f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
            else:
                thumb_img['src'] = url  # fallback: use the URL itself (e.g. direct image link)

    def _inject_related_modules(self, soup):
        desktop_inner = soup.select_one('#related_modules_desktop .carousel-inner')
        mobile_inner = soup.select_one('#related_modules_mobile .carousel-inner')
        explore_link = soup.select_one('#related_modules_explore_link')

        if explore_link and self.related_modules_explore_url:
            explore_link['href'] = self.related_modules_explore_url

        if not self.related_module_ids:
            return

        modules = self.related_module_ids

        # Desktop: 4 cards per slide
        if desktop_inner:
            desktop_inner.clear()
            chunks = [modules[i:i + 4] for i in range(0, len(modules), 4)]
            for slide_idx, chunk in enumerate(chunks):
                active = 'active' if slide_idx == 0 else ''
                cards_html = ''
                for mod in chunk:
                    img_src = self._image_as_data_uri(mod.image)
                    cards_html += f"""
                    <div class="col-3">
                        <a href="{mod.store_url or '#'}" target="_blank" rel="noopener"
                           class="d-flex flex-column text-decoration-none bg-white rounded-3 overflow-hidden shadow"
                           style="color:inherit;">
                            <div style="height:160px;overflow:hidden;background-color:#f5f0f8;
                                 border-radius:12px 12px 0 0;">
                                <img src="{img_src}" alt="{mod.name or ''}"
                                     style="width:100%;height:100%;object-fit:cover;
                                     display:block;border-radius:12px 12px 0 0;">
                            </div>
                            <div class="p-3 d-flex flex-column" style="flex:1;">
                                <div class="fw-bold mb-1"
                                     style="font-size:12px;color:#1a1025;line-height:1.4;">
                                     {mod.name or ''}</div>
                                <div style="font-size:11px;color:#9b8fa3;line-height:1.5;
                                     margin-bottom:10px;">{mod.short_description or ''}</div>
                                <div class="d-flex align-items-center
                                     justify-content-between mt-auto">
                                    <span style="font-size:13px;font-weight:800;
                                         color:#1a1025;"> ${mod.price or ''}</span>
                                    <div class="d-flex align-items-center justify-content-center"
                                         style="width:28px;height:28px;border-radius:50%;
                                         background-color:#875A7B;font-size:16px;font-weight:700;
                                         color:#fff;line-height:1;">&#8250;</div>
                                </div>
                            </div>
                        </a>
                    </div>"""
                slide = BeautifulSoup(
                    f'<div class="carousel-item {active}"><div class="row g-3">'
                    f'{cards_html}</div></div>',
                    'html.parser',
                )
                desktop_inner.append(slide)

        # Mobile: 1 card per slide
        if mobile_inner:
            mobile_inner.clear()
            for mob_idx, mod in enumerate(modules):
                active = 'active' if mob_idx == 0 else ''
                img_src = self._image_as_data_uri(mod.image)
                slide = BeautifulSoup(f"""
                <div class="carousel-item {active}">
                    <a href="{mod.store_url or '#'}" target="_blank" rel="noopener"
                       class="d-flex flex-column text-decoration-none"
                       style="background-color:#ffffff;border:1.5px solid #e0ceda;
                       border-radius:14px;overflow:hidden;color:inherit;">
                        <div style="height:160px;overflow:hidden;background-color:#f5f0f8;
                             border-radius:12px 12px 0 0;">
                            <img src="{img_src}" alt="{mod.name or ''}"
                                 style="width:100%;height:100%;object-fit:cover;
                                 display:block;border-radius:12px 12px 0 0;">
                        </div>
                        <div class="p-3 d-flex flex-column">
                            <div class="fw-bold mb-1"
                                 style="font-size:13px;color:#1a1025;line-height:1.4;">
                                 {mod.name or ''}</div>
                            <div style="font-size:12px;color:#9b8fa3;line-height:1.5;
                                 margin-bottom:10px;">{mod.short_description or ''}</div>
                            <div class="d-flex align-items-center
                                 justify-content-between mt-auto">
                                <span style="font-size:14px;font-weight:800;
                                     color:#1a1025;"> ${mod.price or ''}</span>
                                <div class="d-flex align-items-center justify-content-center"
                                     style="width:30px;height:30px;border-radius:50%;
                                     background-color:#875A7B;font-size:17px;font-weight:700;
                                     color:#fff;line-height:1;">&#8250;</div>
                            </div>
                        </div>
                    </a>
                </div>""", 'html.parser')
                mobile_inner.append(slide)

    def _inject_languages(self, soup):
        container = soup.select_one('#language_pills_container')
        if container is None:
            return

        langs = self.language_ids or self.env['bsi.index.language'].search([])
        if not langs:
            return

        container.clear()
        for lang in langs:
            icon_src = self._get_language_icon_src(lang)
            icon_html = ''
            if icon_src:
                icon_html = (
                    f'<div style="width:20px;height:20px;border-radius:50%;overflow:hidden;flex-shrink:0;">'
                    f'<img src="{icon_src}" alt="{lang.name or ""}" '
                    f'style="width:100%;height:100%;object-fit:cover;"></div>'
                )
            pill = BeautifulSoup(
                f'<div class="d-flex align-items-center gap-2" '
                f'style="background-color:#ffffff;border:1.5px solid #e0ceda;border-radius:999px;'
                f'padding:7px 16px;font-size:13px;font-weight:600;color:#3d2e3a;">'
                f'{icon_html}<span>{lang.name or ""}</span></div>',
                'html.parser',
            )
            container.append(pill)

    def _inject_footer(self, soup):
        self._set_text(soup, '#footer_company_name', self.company_name)
        copyright_el = soup.select_one('#footer_copyright')
        if copyright_el:
            copyright_el.string = (
                f'© {self.copyright_year or "2026"} '
                f'{self.company_name or ""}. All rights reserved.'
            )

        email_link = soup.select_one('#support_email_link')
        if email_link:
            email_link['href'] = f'mailto:{self.company_email or ""}'
            email_link.string = self.company_email or ''

        website_link = soup.select_one('#support_website_link')
        if website_link:
            website_link['href'] = self.website or '#'
            label = (self.website or '').replace('https://', '').replace('http://', '').strip('/')
            website_link.string = label

    def _apply_section_visibility(self, soup):
        # Why Choose (entire card, including stats)
        if self.hide_why_choose_section:
            section = soup.select_one('#why_choose_section')
            if section:
                section.decompose()
        elif self.hide_stats_section:
            # Hide only the stats row, keep the text content
            section = soup.select_one('#stats_section')
            if section:
                section.decompose()

        # Steps / How It Works — always hidden when empty
        if self.hide_steps_section or not self.module_steps:
            section = soup.select_one('#how_it_works_section')
            if section:
                section.decompose()

        # Languages
        if self.hide_language_section:
            section = soup.select_one('#multilanguage_section')
            if section:
                section.decompose()

        # Demo
        if self.hide_demo_section or (
            self.auto_hide_empty_sections and not self.demo_video_link
        ):
            self._hide_tab(soup, 'bsi-videos')

        # Features
        if self.hide_features_section or (
            self.auto_hide_empty_sections and not self.feature_ids
        ):
            self._hide_tab(soup, 'bsi-features')

        # Screenshots
        if self.hide_screenshots_section or (
            self.auto_hide_empty_sections and not self.screenshot_ids
        ):
            self._hide_tab(soup, 'bsi-screenshots')

        # Related Modules
        if self.hide_related_modules_section or (
            self.auto_hide_empty_sections and not self.related_module_ids
        ):
            outer = soup.select_one('#related_modules_outer')
            if outer:
                outer.decompose()

    # ── Main Generation ───────────────────────────────────────────────────────

    def _prepare_generated_html(self):
        self.ensure_one()
        html = self._get_template_html()
        if not html:
            return ''
        soup = BeautifulSoup(html, 'html.parser')

        self._inject_seo(soup)
        self._inject_hero(soup)
        self._inject_why_choose(soup)
        self._inject_steps(soup)
        self._inject_features(soup)
        self._inject_screenshots(soup)
        self._inject_demo(soup)
        self._inject_related_modules(soup)
        self._inject_languages(soup)
        self._inject_footer(soup)
        self._apply_section_visibility(soup)

        return str(soup)

    # ── Public Actions ────────────────────────────────────────────────────────

    def action_generate_html(self):
        self.ensure_one()
        html = self._prepare_generated_html()
        if not html:
            raise UserError('No HTML template was found. Please check the module installation.')
        self.write({'generated_file': base64.b64encode(html.encode('utf-8'))})
        return {
            'type': 'ir.actions.act_url',
            'url': f'/bsi_dynamic_index_generator/preview/{self.id}',
            'target': 'new',
        }

    def action_download_html(self):
        self.ensure_one()
        html = self._prepare_generated_html()
        if not html:
            raise UserError('No HTML template was found for download.')
        self.write({'generated_file': base64.b64encode(html.encode('utf-8'))})
        attachment = self.env['ir.attachment'].create({
            'name': self._get_download_filename(),
            'type': 'binary',
            'datas': self.generated_file,
            'mimetype': 'text/html',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def _reload_form(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'views': [(False, 'form')],
            'view_mode': 'form',
            'target': 'current',
        }
