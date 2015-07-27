from lxml import html
import requests
import csv
import abc

BIRD_GENOMES_DB_HOME = 'http://avian.genomics.cn/en/jsp/database.shtml'

class PageParserFactory (object) :
  def __init__(self) :
    pass

  def getPageParser(self, url) :
    if url.startswith('http://dx.doi.org/10.5524'):
      return DOIPageParser(url)
    #if url.startswith('ftp://climb.genomics.cn/'):
    raise(ValueError('Unsuported URL found'))

class AbstractPageParser (object) :
  __metaclass__ = abc.ABCMeta

  def __init__(self, url) :
    self.url = url

  @abc.abstractmethod
  def __parse__(self) :
    pass 
  
  def parse(self) :
    return self.__parse__()

class DOIPageParser (AbstractPageParser) :
  def __init__(self, url) :
    super(DOIPageParser, self).__init__(url)
  
  def __parse__(self):
    inner_page = requests.get(species[2]) #The internal link
    inner_tree = html.fromstring(inner_page.text)

    file_link = inner_tree.xpath('//td[contains(@title, "peptide") or contains(@title, "amino acid")]//p//a/@href')
    file_name = inner_tree.xpath('//td[contains(@title, "peptide") or contains(@title, "amino acid")]//p//a/text()')
    return (file_name, file_link)

AbstractPageParser.register(DOIPageParser)

page = requests.get(BIRD_GENOMES_DB_HOME)
tree = html.fromstring(page.text)
species_sci_names = tree.xpath('//td[@class="latin_name"]/text()')
species_common_names = tree.xpath('//td[@class="ch_name"]/text()')
species_gaias = tree.xpath('//td[@class="gaia"]//a/@href')

all_species = zip(species_sci_names, species_common_names, species_gaias)
species_table = []
parserFactory = PageParserFactory()

for species in all_species :
  species = list(species)
  print(species[1])
  try :
    species.extend(parserFactory.getPageParser(species[2]).parse())
  except ValueError as e:
    print('Unsuported URL found for {}'.format(species[1],))
  species_table.append(species)
  print(species)

with open('bird_genomes.tsv', 'w') as tsvfile:
  t_writer = csv.writer(tsvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
  t_writer.writerow(('Latin_Name', 'Common_Name', 'Gaia', 'File_Name', 'File_URL'))
  for species in species_table :
    t_writer.writerow(species)

