import scrapy

class JobListingItem(scrapy.Item):
    job_title = scrapy.Field()
    job_id = scrapy.Field()
    contract_type = scrapy.Field()
    contract_tag = scrapy.Field()
    salary = scrapy.Field()
    company_name = scrapy.Field()
    location = scrapy.Field()
    publication_date = scrapy.Field()
    job_url = scrapy.Field()
    resume_de_loffre = scrapy.Field()
    qualifications = scrapy.Field()
    missions = scrapy.Field()
    profil_recherche = scrapy.Field()
