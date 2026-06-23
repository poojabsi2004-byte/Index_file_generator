from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource
import base64
import re
from urllib.parse import parse_qs, urlparse
from bs4 import BeautifulSoup

class IndexFileGenerator(models.Model):
    _name = 'index.file.generator'
    _description = 'Index File Generator'
    _rec_name = 'company_name'
    
    company_name = fields.Char(string="Company name", help="Company name to show in header")
    company_email = fields.Char(string="Company Email", default="contact@botspotinfoware.com")
    website = fields.Char(string="Website", default="https://www.botspotinfoware.com/")
    version = fields.Char(string="Odoo Version", help="Odoo's Version")
    main_header = fields.Text(string="Module Heading", help="Add Module heading to display in module")
    main_des = fields.Text(string="Module description", help="Add Module Description For module")
    topbar_text = fields.Char(string="Topbar Text")
    seo_title = fields.Char(string="SEO Title")
    seo_description = fields.Char(string="SEO Description")
    primary_cta_label = fields.Char(string="Primary CTA", default="Watch Demo")
    secondary_cta_label = fields.Char(string="Secondary CTA", default="Get Support")
    footer_tagline = fields.Char(string="Footer Tagline")
    copyright_year = fields.Char(string="Copyright Year", default="2024")
    accent_color = fields.Char(string="Accent Color", default="#9d4c90")
    gold_color = fields.Char(string="Highlight Color", default="#c49a42")
    auto_hide_empty_sections = fields.Boolean(string="Auto-hide Empty Sections", default=True)
    hide_steps_section = fields.Boolean(string="Hide Steps")
    hide_demo_section = fields.Boolean(string="Hide Demo")
    hide_features_section = fields.Boolean(string="Hide Features")
    hide_screenshots_section = fields.Boolean(string="Hide Screenshots")
    hide_related_modules_section = fields.Boolean(string="Hide Related Modules")
    hide_languages_section = fields.Boolean(string="Hide Languages")
    hide_services_section = fields.Boolean(string="Hide Services")
    hide_support_section = fields.Boolean(string="Hide Support")
    
    # Module Info.
    sub_heading = fields.Char(string="Module Sub Heading", help="Module sub heading for Module information")
    sub_des = fields.Char(string="Module Sub Description", help="Module sub Description for Module information")
    module_steps = fields.One2many('module.steps', 'generator_id')
    
    # Demo Video Section
    demo_heading = fields.Char(string="Demo Video Heading", help="Add Heading for Demo Video")
    demo_des = fields.Char(string="Demo Video Description", help="Add Decription for video")
    demo_video_link = fields.Char(string="Video Link", help="Demo Video Link")
    
    # Features Section
    feature_main_des = fields.Char(string="Main Description")
    feature_ids = fields.One2many('index.generator.feature','generator_id')
    
    # Screenshot
    screenshot_ids = fields.Many2many('index.generator.screenshot')
    
    module_logo = fields.Binary(string="Module Logo")
    template_file = fields.Binary()
    template_attachment_ids = fields.Many2many(
        'ir.attachment',
        'index_generator_template_attachment_rel',
        'generator_id',
        'attachment_id',
        string="Template File",
    )
    generated_file = fields.Binary(readonly=True)
    show_preview = fields.Boolean(default=True)
    preview_html = fields.Html(
        string="Preview",
        compute="_compute_preview_html",
        sanitize=False,
    )

    @api.constrains('template_attachment_ids')
    def _check_template_attachment_limit(self):
        for record in self:
            if len(record.template_attachment_ids) > 1:
                raise ValidationError("Only one template file is allowed.")

    def _get_preview_html(self):
        self.ensure_one()
        if not self.generated_file:
            return """
                <div style="height: calc(100vh - 210px); min-height: 680px; border: 1px solid #d8dadd; display: flex; align-items: center; justify-content: center; color: #6b7280; background: #f8f9fa;">
                    Generate preview to see the HTML page here.
                </div>
            """
        return f"""
            <iframe
                src="/bsi_index_generator/preview/{self.id}"
                style="width: 100%; height: calc(100vh - 210px); min-height: 680px; border: 1px solid #d8dadd; border-radius: 4px; background: #fff;"
                sandbox="allow-same-origin allow-scripts allow-popups allow-forms">
            </iframe>
        """

    def _compute_preview_html(self):
        for record in self:
            record.preview_html = record._get_preview_html()

    def _get_template_html(self):
        self.ensure_one()
        if self.template_attachment_ids:
            return base64.b64decode(self.template_attachment_ids[:1].datas).decode('utf-8')
        if self.template_file:
            return base64.b64decode(self.template_file).decode('utf-8')

        template_path = get_module_resource(
            'bsi_index_generator',
            'static',
            'description',
            'index.html',
        )
        if template_path:
            with open(template_path, 'rb') as template:
                return template.read().decode('utf-8')
        return ''

    def _get_image_src(self, image_data, mimetype='image/png'):
        if not image_data:
            return ''
        if isinstance(image_data, bytes):
            image_data = image_data.decode('utf-8')
        return "data:%s;base64,%s" % (mimetype, image_data)

    def _get_demo_embed_url(self):
        self.ensure_one()
        video_url = (self.demo_video_link or '').strip()
        if not video_url:
            return ''

        parsed_url = urlparse(video_url)
        if parsed_url.scheme not in ('http', 'https'):
            return ''

        hostname = (parsed_url.hostname or '').lower()
        if hostname in ('youtu.be', 'www.youtu.be'):
            video_id = parsed_url.path.strip('/')
            return video_id and f'https://www.youtube.com/embed/{video_id}' or ''

        if hostname in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
            if parsed_url.path == '/watch':
                video_id = parse_qs(parsed_url.query).get('v', [''])[0]
                return video_id and f'https://www.youtube.com/embed/{video_id}' or ''
            if parsed_url.path.startswith('/embed/'):
                return video_url

        return video_url

    def _set_text(self, soup, selector, value):
        element = soup.select_one(selector)
        if element is not None:
            element.string = value or ''

    def _set_link(self, soup, selector, url, label=None):
        element = soup.select_one(selector)
        if element is None:
            return
        element['href'] = url or '#'
        if label is not None:
            element.string = label or ''

    def _section_for(self, soup, selector):
        element = soup.select_one(selector)
        return element and element.find_parent('section')

    def _remove_section(self, soup, selector):
        section = self._section_for(soup, selector)
        if section is not None:
            section.decompose()

    def _inject_seo_and_theme(self, soup):
        title = soup.select_one('title')
        if title:
            title.string = self.seo_title or self.main_header or self.company_name or ''

        description = soup.select_one('meta[name="description"]')
        if not description:
            head = soup.select_one('head')
            if head:
                description = soup.new_tag('meta')
                description['name'] = 'description'
                head.append(description)
        if description:
            description['content'] = self.seo_description or self.main_des or ''

        accent = (self.accent_color or '').strip()
        highlight = (self.gold_color or '').strip()
        if accent or highlight:
            head = soup.select_one('head')
            if not head:
                return
            style = soup.new_tag('style')
            style.string = """
:root {
  --ink: %(accent)s;
  --ink-mid: %(accent)s;
  --gold: %(highlight)s;
  --gold-deep: %(highlight)s;
}
""" % {
                'accent': accent or '#9d4c90',
                'highlight': highlight or '#c49a42',
            }
            head.append(style)

    def _hide_tab(self, soup, pane_id):
        pane = soup.select_one(f'#{pane_id}')
        if pane:
            pane.decompose()
        nav_link = soup.select_one(f'[data-bs-target="#{pane_id}"]')
        if nav_link:
            li = nav_link.find_parent('li')
            if li:
                li.decompose()

    def _apply_section_visibility(self, soup):
        if self.hide_steps_section or (self.auto_hide_empty_sections and not self.module_steps):
            self._remove_section(soup, '#module_steps_section')
        if self.hide_demo_section:
            self._hide_tab(soup, 'bsi-videos')
        if self.hide_features_section or (self.auto_hide_empty_sections and not self.feature_ids):
            self._hide_tab(soup, 'bsi-features')
        if self.hide_screenshots_section or (self.auto_hide_empty_sections and not self.screenshot_ids):
            self._hide_tab(soup, 'bsi-screenshots')
        if self.hide_related_modules_section:
            related = soup.select_one('.module-card')
            section = related and related.find_parent('section')
            if section:
                section.decompose()
        if self.hide_languages_section:
            languages = soup.select_one('.language-card')
            section = languages and languages.find_parent('section')
            if section:
                section.decompose()
        if self.hide_services_section:
            services = soup.select_one('.service-card')
            section = services and services.find_parent('section')
            if section:
                section.decompose()
        if self.hide_support_section:
            self._remove_section(soup, '#contact_support')

    def _get_download_filename(self):
        name = self.main_header or self.company_name or 'generated_index'
        filename = re.sub(r'[^A-Za-z0-9_.-]+', '_', name).strip('_').lower()
        return f'{filename or "generated_index"}.html'

    def _replace_demo_video(self, soup):
        demo_iframes = soup.select('iframe#demo_video_link')
        if not demo_iframes:
            return

        embed_url = self._get_demo_embed_url()
        if embed_url:
            demo_iframes[0]['src'] = embed_url
            for iframe in demo_iframes[1:]:
                iframe.decompose()
            return

        placeholder = BeautifulSoup("""
            <div style="
                width: 100%;
                min-height: 280px;
                border-radius: 20px;
                border: 1px dashed rgba(0,0,0,0.18);
                display: flex;
                align-items: center;
                justify-content: center;
                color: #805a76;
                background: rgba(255,255,255,0.72);
                text-align: center;
                padding: 32px;
                font-weight: 600;">
                Add a valid video URL to show the product demo.
            </div>
        """, 'html.parser')
        demo_iframes[0].replace_with(placeholder)
        for iframe in demo_iframes[1:]:
            iframe.decompose()

    def _prepare_generated_html(self):
        self.ensure_one()
        html = self._get_template_html()
        if not html:
            return ''

        soup = BeautifulSoup(
            html,
            'html.parser'
        )
        self._inject_seo_and_theme(soup)

        logo = soup.select_one('.brand-mark .logo-wrap img')
        if logo and self.module_logo:
            logo['src'] = self._get_image_src(self.module_logo)
            logo['alt'] = self.main_header or self.company_name or 'Module Logo'
        
        # Company name
        company_name = soup.select_one(
            '#company_name'
        )
        if company_name:
            company_name_strong = company_name.select_one('strong')
            if company_name_strong:
                company_name_strong.string = self.company_name or ''
            else:
                company_name.string = self.company_name or ''
            
        if self.topbar_text or self.main_header:
            self._set_text(soup, '.topbar-right', self.topbar_text or self.main_header)
        self._set_link(
            soup,
            '#company_email',
            f'mailto:{self.company_email or ""}',
            self.company_email or '',
        )
        
        # version 
        version_div = soup.select_one(
            '#hero_eyebrow'
        )
        version = soup.select_one('#right_side_content_version')
        if version_div:
            version_div.string = (
                f'Odoo Module · Version {self.version or ""}'
            )
        if version:
            version_code = f'<span class="check"><svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg></span> Compatible with Odoo {self.version or ""}'
            version.append(BeautifulSoup(version_code, 'html.parser'))
            
           
        # main header 
        header_div = soup.select_one(
            '#hero_heading'
        )
        if header_div:

            header_div.string = (
                self.main_header or ''
            )

        #  module description
        header_div = soup.select_one(
            '#hero_description'
        )
        if header_div:

            header_div.string = (
                self.main_des or ''
            )

        footer_brand = soup.select_one('.footer-brand strong')
        if footer_brand:
            footer_brand.string = self.company_name or ''

        footer_copy = soup.select_one('.footer-copy')
        if footer_copy:
            footer_copy.string = f'© {self.copyright_year or ""} {self.company_name or ""}. All rights reserved.'

        footer_tagline = soup.select_one('.footer-tagline')
        if footer_tagline:
            footer_tagline.string = self.footer_tagline or f'{self.main_header or ""} · Version {self.version or ""}'
            
        website_label = (self.website or '').replace('https://', '').replace('http://', '').strip('/')
        self._set_link(soup, '#company_website', self.website or '#', website_label)
        self._set_link(
            soup,
            '.language-note a',
            f'mailto:{self.company_email or ""}',
            self.company_email or '',
        )

        primary_cta = soup.select_one('.btn-primary-cta')
        if primary_cta:
            primary_cta['href'] = '#demo_video_link' if not self.hide_demo_section else '#contact_support'
            primary_icon = primary_cta.select_one('svg')
            primary_icon_html = str(primary_icon) if primary_icon else ''
            primary_cta.clear()
            if primary_icon_html:
                primary_cta.append(BeautifulSoup(primary_icon_html, 'html.parser'))
            primary_cta.append(f'\n            {self.primary_cta_label or "Watch Demo"}\n          ')
        secondary_cta = soup.select_one('.btn-ghost-cta')
        if secondary_cta:
            secondary_cta.string = self.secondary_cta_label or 'Get Support'
            
        # Module sub heading
        sub_heading = soup.select_one(
            '#section_title'
        )
        if sub_heading:

            sub_heading.string = (
                self.sub_heading or ''
            ) 
            
        # Module sub description
        sub_description = soup.select_one(
            '#sub_description'
        )
        if sub_description:

            sub_description.string = (
                self.sub_des or ''
            ) 
            
        
        # Module Steps
        if self.module_steps:

            step_row = soup.select_one(
                '#module_steps_section'
            )

            if step_row:

                # Create new cards dynamically
                for index, step in enumerate(self.module_steps, start=1):

                    # Convert binary image
                    image_src = ""

                    # Create card HTML
                    card_html = f"""
                    <div class="col-md-4">
                        <div class="h-100" style="background-color: #fdf8ff; border: 2px solid #875A7B; border-radius: 18px; box-shadow: 0 4px 16px #d4b8cc; padding: 28px 22px;">
                            <div style="font-size: 36px; font-weight: 900; color: #875A7B; line-height: 1; margin-bottom: 10px;">{index:02d}</div>
                            <h4 style="font-size: 14px; font-weight: 700; color: #1a1025; margin-bottom: 8px; white-space: normal; word-wrap: break-word; overflow-wrap: break-word;">{step.module_step_heading or ''}</h4>
                            <p style="font-size: 13px; color: #7a6b76; line-height: 1.7; margin: 0; white-space: normal; word-wrap: break-word; overflow-wrap: break-word;">{step.module_step_des or ''}</p>
                        </div>
                    </div>
                    """

                    step_row.append(
                        BeautifulSoup(card_html, 'html.parser')
                    )
            
        # Module Demo Heading
        demo_heading = soup.select_one(
            '#demo_heading'
        )
        if demo_heading:

            demo_heading.string = (
                self.demo_heading or ''
            ) 
            
        # Module Demo Description
        demo_des = soup.select_one(
            '#demo_description'
        )
        if demo_des:

            demo_des.string = (
                self.demo_des or ''
            ) 
            
          
        # Demo video link
        demo_video_link = soup.select_one(
            '#demo_video_link'
        )
        
        if demo_video_link:
            self._replace_demo_video(soup)
            # demo_video_link.append(BeautifulSoup(self.demo_video_link, 'html.parser'))
            
            
        # Feature main description
        feature_main_description = soup.select_one(
            '#feature_main_description'
        )
        if feature_main_description:

            feature_main_description.string = (
                self.feature_main_des or ''
            ) 
            
        # Features Details
        if self.feature_ids:

            feature_row = soup.select_one(
                '#features_listing_section'
            )

            if feature_row:
                # Create new cards dynamically
                for index, feature in enumerate(self.feature_ids, start=1):
                    # Create card HTML
                    card_html = f"""
                    <div class="col-md-4">
                        <div class="card h-100" style="background-color: #f5edf8; border: 2px solid #875A7B; border-radius: 18px; box-shadow: 0 4px 16px #d4b8cc; padding: 24px 20px;">
                            <div style="font-size: 10px; font-weight: 800; letter-spacing: .15em; text-transform: uppercase; color: #c9a8be; margin-bottom: 8px;">{index:02d} &nbsp;/&nbsp;  {feature.feature_title}</div>
                            <h4 style="font-size: 14px; font-weight: 700; color: #1a1025; margin-bottom: 6px; white-space: normal; word-wrap: break-word; overflow-wrap: break-word;">{feature.feature_heading or ''}</h4>
                            <p style="font-size: 13px; color: #7a6b76; line-height: 1.7; margin: 0; white-space: normal; word-wrap: break-word; overflow-wrap: break-word;">{feature.feature_des or ''}</p>
                        </div>
                    </div>
                    """
                    feature_row.append(
                        BeautifulSoup(card_html, 'html.parser')
                    )
        
        
        
         # Screenshot description
        ss_des = soup.select_one(
            '#screenshot_description'
        )
        if ss_des:

            ss_des.string = (
                self.screenshot_ids.ss_des or ''
            ) 
            
        if self.screenshot_ids:
            
            
            for index, screenshot in enumerate(self.screenshot_ids, start=1):
                screenshot_select = soup.select_one(
                    '#screenshot_section'
                )

                if screenshot_select:

                    # Create card HTML
                    card_html = f"""
                    <div class="card overflow-hidden mb-4" style="border: 2px solid #875A7B; border-radius: 18px;">
                        <div class="card-header bg-white d-flex align-items-center gap-3 py-3 px-4" style="border-bottom: 1.5px solid #e4d0dc;">
                            <span style="min-width: 32px; height: 32px; font-size: 11px; background-color: #875A7B; color: #ffffff; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center; font-weight: bold;">{index:02d}</span>
                            <h3 style="margin: 0; font-weight: bold; font-size: 14px; color: #1a1025;">{screenshot.ss_heading}</h3>
                        </div>
                        <img src="{screenshot}" alt="Screenshot {index}" class="img-fluid d-block w-100">
                        <div class="card-body px-4 py-3" style="border-top: 1.5px solid #e4d0dc;">
                            <p class="mb-0" style="font-size: 13px; color: #7a6b76; line-height: 1.7;"><strong style="color: #3d2e3a;">{screenshot.ss_des}</strong></p>
                        </div>
                    </div>
                    """

                    screenshot_select.append(
                        BeautifulSoup(card_html, 'html.parser')
                    )

        self._apply_section_visibility(soup)
                  
        final_html = str(soup)
        return final_html

    def action_generate_html(self):
        self.ensure_one()
        final_html = self._prepare_generated_html()
        if not final_html:
            raise UserError("No HTML template was found for generating the preview.")

        self.write({
            'generated_file': base64.b64encode(final_html.encode('utf-8')),
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'HTML Generated',
                'message': 'Preview generated successfully.',
                'type': 'success',
                'sticky': False,
                'next': self._reload_form(),
            },
        }

    def action_download_html(self):
        self.ensure_one()
        final_html = self._prepare_generated_html()
        if not final_html:
            raise UserError("No HTML template was found for downloading the HTML.")
        self.write({
            'generated_file': base64.b64encode(final_html.encode('utf-8')),
        })
        
        attachment = self.env[
            'ir.attachment'
        ].create({
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

    def action_open_preview(self):
        self.ensure_one()
        if not self.generated_file:
            raise UserError("Please generate the preview before opening it in a new window.")
        return {
            'type': 'ir.actions.act_url',
            'url': f'/bsi_index_generator/preview/{self.id}',
            'target': 'new',
        }

    def action_hide_preview(self):
        self.ensure_one()
        self.show_preview = False
        return self._reload_form()

    def action_show_preview(self):
        self.ensure_one()
        self.show_preview = True
        return self._reload_form()

    def _reload_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'views': [(False, 'form')],
            'view_mode': 'form',
            'target': 'current',
        }
