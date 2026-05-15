from odoo import models, fields, api
import base64
from bs4 import BeautifulSoup

class IndexFileGenerator(models.Model):
    _name = 'index.file.generator'
    _description = 'Index File Generator'
    _rec_name = 'company_name'
    
    company_name = fields.Char(string="Company name", help="Company name to show in header")
    # company_email = fields.Char(string="Company Email", help="Company email to show in Header/footer")
    version = fields.Char(string="Odoo Version", help="Odoo's Version")
    main_header = fields.Text(string="Module Heading", help="Add Module heading to display in module")
    main_des = fields.Text(string="Module description", help="Add Module Description For module")
    # website = fields.Char(string="Website", help="Set Your Company Website link")
    
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
    ss_des = fields.Char(string="SS Description")
    screenshot_attachment_ids = fields.Many2many('ir.attachment', string='Screenshots')
    
    
    template_file = fields.Binary()
    generated_filename = fields.Char()

    def action_generate_html(self):
        html = ''
        if not self.template_file:
            return
        
        html = base64.b64decode(self.template_file).decode('utf-8')
        soup = BeautifulSoup(
            html,
            'html.parser'
        )
        
        # Company name
        company_name = soup.select_one(
            '#company_name'
        )
        if company_name:
            company_name.string = (
                self.company_name or ''
            )
            
        # Company email
        # company_email = soup.select_one(
        #     '#company_email'
        # )
        # if company_email:
            
        #     company_email['href'] = (
        #         f"mailto:{self.company_email or ''}"
        #     )
        #     company_email.string = (
        #         self.company_email or ''
        #     )
        
        # version 
        version_div = soup.select_one(
            '#hero_eyebrow'
        )
        version = soup.select_one('#right_side_content_version')
        if version_div or version:
            version_div.string = (
                f'Odoo Module · Version {self.version or ""}'
            )
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
            
        # Comapny Website link
        # company_website_link = soup.select_one(
        #     '#company_website'
        # )
        # if company_website_link:
            
        #     company_website_link['href'] = (
        #         self.website or ''
        #     )
            
        #     company_website_link.string = (
        #         self.website or ''
        #     )
            
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
                    <div class="col-md-4 col-lg-3 reveal reveal-delay-{index}">

                        <div class="workflow-card">

                        <div class="workflow-number text-muted">0{index}</div>
                        
                        <h6 style="white-space: normal; word-wrap: break-word; overflow-wrap: break-word; word-break: break-word;">{step.module_step_heading or ''}</h6>
                        
                        <p style="white-space: normal; word-wrap: break-word; overflow-wrap: break-word; word-break: break-word;">{step.module_step_des or ''}</p>
                        
                        </div>

                    </div>
                    """

                    step_row.append(
                        BeautifulSoup(card_html, 'html.parser')
                    )
                    print("-- - /n/n/n/n-- -step_row added-----", step_row)
            
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

            # demo_video_link['src'] = (
            #     self.demo_video_link or ''
            # )  
            demo_video_link.append(BeautifulSoup(self.demo_video_link, 'html.parser'))
            
            
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

                    # Convert binary image
                    image_src = ""

                    if feature.feature_icon:
                        image_src = (
                            "data:image/png;base64,%s"
                            % feature.feature_icon.decode('utf-8')
                        )

                    # Create card HTML
                    card_html = f"""
                    <div class="col-md-6 col-xl-4 reveal reveal-delay-{index}">

                        <div class="feature-card">

                            <div class="feature-icon-wrap">

                                <img
                                    src="{image_src}"
                                    alt="Feature Icon"
                                    style="width:40px;height:40px;object-fit:contain;"
                                />

                            </div>

                            <h6 style="white-space: normal; word-wrap: break-word; overflow-wrap: break-word; word-break: break-word;">
                                {feature.feature_heading or ''}
                            </h6>

                            <p style="white-space: normal; word-wrap: break-word; overflow-wrap: break-word; word-break: break-word;">
                                {feature.feature_des or ''}
                            </p>

                        </div>

                    </div>
                    """

                    feature_row.append(
                        BeautifulSoup(card_html, 'html.parser')
                    )
                    # print("-- - /n/n/n/n-- -features added-----", feature_row)
        
        
        
         # Screenshot description
        ss_des = soup.select_one(
            '#screenshot_description'
        )
        if ss_des:

            ss_des.string = (
                self.ss_des or ''
            ) 
            
        if self.screenshot_attachment_ids:
            for index, screenshot in enumerate(self.screenshot_attachment_ids, start=1):
                screenshot_select = soup.select_one(
                    '#screenshot_section'
                )

                if screenshot_select:

                    # Convert binary image
                    image_src = (
                        "data:image/png;base64,%s"
                        % screenshot.datas.decode('utf-8')
                    )

                    # Create card HTML
                    card_html = f"""
                   <div class="screenshot-card" style="
                                width: 100%;
                                max-width: 900px;
                                height: auto;
                                max-height: 700px;
                                object-fit: contain;
                                border-radius: 16px;
                                border: 1px solid rgba(0,0,0,0.08);
                                box-shadow: 0 4px 16px rgba(0,0,0,0.08);
                                margin-top: 20px;
                            ">

                        <span class="step-badge">
                            Step {index}
                        </span>
                        
                        <img
                            src="{image_src}"
                            alt="Screenshot"
                            style="
                                width: 100%;
                                max-width: 900px;
                                height: auto;
                                max-height: 500px;
                                object-fit: contain;
                                border-radius: 16px;
                                border: 1px solid rgba(0,0,0,0.08);
                                box-shadow: 0 4px 16px rgba(0,0,0,0.08);
                                margin-top: 20px;
                            "
                        />

                    </div>
                    """

                    screenshot_select.append(
                        BeautifulSoup(card_html, 'html.parser')
                    )
                  
        final_html = str(soup)


        # DOWNLOADABLE FILE
        self.template_file = base64.b64encode(
            final_html.encode('utf-8')
        )

        self.generated_filename = (
            'generated_index.html'
        )
        
        attachment = self.env[
            'ir.attachment'
        ].create({
            'name': f'{self.company_name}.html',
            'type': 'binary',
            'datas': base64.b64encode(
                final_html.encode('utf-8')
            ),
            'mimetype': 'text/html',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }