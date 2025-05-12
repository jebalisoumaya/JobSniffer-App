import scrapy
from scrapy_selenium import SeleniumRequest
 
class WelcomeToTheJungleSpider(scrapy.Spider):
    name = "wttj"
 
    def __init__(self, job_title=None, location=None, max_pages=5, *args, **kwargs):
        super(WelcomeToTheJungleSpider, self).__init__(*args, **kwargs)
        self.job_title = job_title
        self.location = location
        self.max_pages = int(max_pages)
        self.page = 1
 
    def start_requests(self):
       
        url = f"https://www.welcometothejungle.com/fr/jobs?query={self.job_title}&page={self.page}&aroundQuery={self.location}&refinementList%5Boffices.country_code%5D%5B%5D=FR&aroundLatLng=48.85341%2C2.3488&aroundRadius=20"
        yield SeleniumRequest(url=url, callback=self.parse)
 
    def parse(self, response):
       
        job_cards = response.css('div[data-role="jobs:thumb"]')
 
        for job in job_cards:
            job_title = job.css('h4::text').get()  
            company_name = job.css('span.wui-text::text').get()  
            location = job.css('p.wui-text span::text').get()  
            contract_type = job.css('div[variant="default"] span::text').get()  
            remote = job.css('div[variant="default"] + div span::text').get()  
            job_url = response.urljoin(job.css('a::attr(href)').get())  
 
           
            yield response.follow(job_url, callback=self.parse_job_details, meta={
                "job_title": job_title,
                "company_name": company_name,
                "location": location,
                "contract_type": contract_type,
                "remote": remote,
            })
 
        # Pagination
        if self.page < self.max_pages:
            self.page += 1
            next_page = response.css('a.pagination-next::attr(href)').get()
            if next_page:
                yield SeleniumRequest(url=response.urljoin(next_page), callback=self.parse)
 
    def parse_job_details(self, response):
       
        job_details = response.meta
 
       
        description = response.css("section.tw-mb-8 div.tw-typo-xl::text").get()
        description = description.strip() if description else None
 
        qualifications = response.css("ul.tw-flex-wrap li::text").getall()
        qualifications = [q.strip() for q in qualifications]
 
       
        missions = response.css("h2:contains('Les missions') ~ p::text").getall()
        missions = '\n'.join([m.strip() for m in missions])
 
       
        profile = response.css("h2:contains('Le profil') ~ p::text").getall()
        profile = '\n'.join([p.strip() for p in profile])
 
       
        job_details['description'] = description
        job_details['qualifications'] = qualifications
        job_details['missions'] = missions
        job_details['profile'] = profile
 
       
        yield job_details