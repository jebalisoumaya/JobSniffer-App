import scrapy
from ..items import JobListingItem

class HelloWorkSpider(scrapy.Spider):
    name = "hellowork"

    def __init__(self, job_title=None, location=None, max_pages=5, *args, **kwargs):
        super(HelloWorkSpider, self).__init__(*args, **kwargs)
        self.job_title = job_title
        self.location = location
        self.max_pages = int(max_pages)
        self.page = 1

    def start_requests(self):
        url = f"https://www.hellowork.com/fr-fr/emploi/recherche.html?k={self.job_title}&l={self.location}"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        job_listings = response.css("ul li[data-id-storage-target='item']")
        for job in job_listings:
            job_title = job.css("a[data-cy='offerTitle']::attr(title)").get()
            job_id = job.css("::attr(data-id-storage-item-id)").get()
            contract_type = job.css("div[data-cy='contractCard']::text").get()
            contract_tag = job.css("div[data-cy='contractTag']::text").get()
            location = job.css("div[data-cy='localisationCard']::text").get()
            salary = job.css("div.tw-tag-attractive-s::text").get()
            publication_date = job.css("div.tw-typo-s.tw-text-grey::text").get()
            parts = job_title.split('-')
            company_name = parts[-1].strip() if len(parts) > 1 else None
            job_url = response.urljoin(job.css("a[data-cy='offerTitle']::attr(href)").get())
            yield response.follow(job_url, callback=self.parse_job_details, meta={
                "job_title": '-'.join(parts[:-1]).strip(),
                "job_id": job_id,
                "contract_type": contract_type.strip() if contract_type else None,
                "contract_tag": contract_tag.strip() if contract_tag else None,
                "salary": salary.strip() if salary else None,
                "company_name": company_name,
                "location": location.strip() if location else None,
                "publication_date": publication_date.strip() if publication_date else None,
            })

        if self.max_pages > self.page:
            self.page += 1
            yield scrapy.Request(
                url=f"https://www.hellowork.com/fr-fr/emploi/recherche.html?k={self.job_title}&l={self.location}&page={self.page}",
                callback=self.parse
            )

    def parse_job_details(self, response):
        item = JobListingItem()
        item['job_title'] = response.meta['job_title']
        item['job_id'] = response.meta['job_id']
        item['contract_type'] = response.meta['contract_type']
        item['contract_tag'] = response.meta['contract_tag']
        item['salary'] = response.meta['salary']
        item['company_name'] = response.meta['company_name']
        item['location'] = response.meta['location']
        item['publication_date'] = response.meta['publication_date']
        item['job_url'] = response.url
        resume_de_loffre = response.css("section.tw-mb-8 div.tw-typo-xl::text").get().strip() if response.css("section.tw-mb-8 div.tw-typo-xl::text").get() else None
        qualifications = response.css("ul.tw-flex-wrap li::text").getall()
        mission_text = response.css("h2:contains('Les missions') ~ p::text").getall()
        mission_text = '\n'.join([t.strip() for t in mission_text])
        profil_recherche_text = response.css("h2:contains('Le profil') ~ p::text").getall()
        profil_recherche_text = '\n'.join([t.strip() for t in profil_recherche_text])
        item['resume_de_loffre'] = resume_de_loffre
        item['qualifications'] = [q.strip() for q in qualifications]
        item['missions'] = mission_text
        item['profil_recherche'] = profil_recherche_text
        yield item
