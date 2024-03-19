from datetime import datetime, timedelta
from logging import config

from selenium import webdriver

from finextra import FINEXTRA
from src.spp.types import SPP_document

config.fileConfig('dev.logger.conf')

options = webdriver.ChromeOptions()
# Параметр для того, чтобы браузер не открывался.
options.add_argument('headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

driver = webdriver.Chrome(options)

# driver = webdriver.Chrome()

# doc = SPP_document(id=1023, title='Bitstring Status List v1.0', abstract='Abstract\nThis specification describes a privacy-preserving, space-efficient, and high-performance mechanism for publishing status information such as suspension or revocation of Verifiable Credentials through use of bitstrings.', text=None, web_link='https://www.w3.org/TR/2024/WD-vc-bitstring-status-list-20240303/', local_link=None, other_data={'doc_type': 'W3C Working Draft', 'devilverers': ['Verifiable Credentials Working Group'], 'authors': ['Dave Longley (Digital Bazaar)', 'Manu Sporny (Digital Bazaar)', 'Orie Steele (Transmute)'], 'tags': ['Privacy', 'Security'], 'commits': [], 'family': 'Verifiable Credentials', 'editors': ['Manu Sporny (Digital Bazaar)', 'Dave Longley (Digital Bazaar)', 'Mike Prorock (mesur.io)', 'Mahmoud Alkhraishi (Mavennet)', 'Dave Longley (Digital Bazaar)', 'Manu Sporny (Digital Bazaar)', 'Orie Steele (Transmute)']}, pub_date=datetime(2024, 3, 3, 0, 0), load_date=None)

# doc = SPP_document(id=407, title='WebGPU Shading Language', abstract=None, text=None, web_link='https://www.w3.org/TR/2024/WD-WGSL-20240317/', local_link=None, other_data=None, pub_date=datetime(2024, 3, 17, 0, 0), load_date=None)

doc = SPP_document(id=None, title='Shift4 Payments unimpressed by suitor bids', abstract="Shift4 Payments' CEO is Jared Isaacman is said to be distinctly unimpressed by the valuations placed on the firm from potential acquirers.", text=None, web_link='https://www.finextra.com/newsarticle/43865/shift4-payments-unimpressed-by-suitor-bids', local_link=None, other_data={'article_type': 'newsarticle', 'related_comp': 'Shift4 Payments, Shift4 Payments', 'lead_ch': 'Payments, Payments', 'channels': 'Retail banking, Retail banking', 'keywords': 'Mergers and acquisitions, Mergers and acquisitions', 'category_name': 'Editorial', 'category_desc': 'This content has been selected, created and edited by the Finextra editorial team based upon its relevance and interest to our community.', 'tw_count': '', 'li_count': '', 'fb_count': '', 'comment_count': '0'}, pub_date=datetime(2024, 3, 18, 15, 7, 15, 895695), load_date=None)

parser = FINEXTRA(driver, timedelta(1), 10, doc)
docs = parser.content()

print(len(docs))
print(*docs, sep='\n\n\n')

