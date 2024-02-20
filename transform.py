"""Script which converts data from an xml file and puts it into a csv file."""

import re
import xml.etree.ElementTree as ET

import geonamescache
import pandas as pd
from rapidfuzz.distance import Levenshtein
import redis
import spacy

pd.options.mode.chained_assignment = None  # default='warn'

ZIPCODE_REGEX = "([A-Z]{1,2}[\d]{1,2}[A-Z]{0,1} [\d]{1}[A-Z]{2})|([\d]{5})|([A-Z][\d][A-Z] [\d][A-Z][\d])"
EMAIL_REGEX = "([a-zA-Z1-9-.]+@[a-z-]+.[a-z.-]+)"

def get_article_info(article: ET.Element) -> dict:
    """Gets all the required information about a certain article"""
    keywords = []
    mesh_list = []

    title = article.find(".//ArticleTitle")
    year = article.find(".//Year")
    PMID = article.find(".//PMID")
    for word in article.findall("./KeywordList/Keyword"):
        keywords.append(word.text)
    for mesh in article.findall("./MeshHeadingList/MeshHeading/DescriptorName"):
        mesh_list.append(mesh.get("UI"))

    return {"title": title.text, "year": year.text, "PMID": PMID.text, "keywords": keywords, "mesh": mesh_list}


def get_author_info(author: ET.Element) -> dict:
    """Gets all the required information about a certain author"""
    first_name = author.find('.//ForeName')
    if first_name is not None:
        first_name = first_name.text
    last_name = author.find('.//LastName')
    if last_name is not None:
        last_name = last_name.text
    initials = author.find(".//Initials")
    if initials is not None:
        initials = initials.text

    return {"first_name": first_name, "last_name": last_name, "initials": initials}


def get_affiliation_country(doc: spacy.language, countries: dict) -> str:
    """Retrieves the affiliation country"""
    for ent in doc.ents:
        for country in countries.values():
            if ent.label_ == "GPE" and ent.text == country['name']:
                return ent.text
            
    return ""


def get_affiliation_name(doc: spacy.language) -> str:
    """Retrieves the a list of affiliation names"""
    affiliation_name = [""]
    for ent in doc.ents:
        if ent.label_ == "ORG":
            affiliation_name.append(ent.text)

    return affiliation_name[-1]


def get_affiliation_zipcode(affiliation: str) -> str:
    """Retrieves the affiliation zipcode"""
    codes = re.findall(ZIPCODE_REGEX, affiliation)
    if codes:
        for code in codes[0]:
            if code:
                return code
            
def find_similarity(x, affiliation_name: str) -> pd.Series:
    return Levenshtein.normalized_similarity(
            affiliation_name, x)


def search_affiliation_matches(affiliation_name: str, country: str, institutes: pd.DataFrame, addresses: pd.DataFrame, r: redis.Connection) -> list[str]:
    """Uses the institutes csv file to try find any matching institutes and their grid ID"""

    if country is not None:
        limit_addresses = addresses[addresses['country'] == country]
        grid_IDs = []
        for index, address in limit_addresses.iterrows():
            grid_IDs.append(address["grid_id"])
        institutes = institutes[institutes.grid_id.isin(grid_IDs)]

    institutes['similarity'] = institutes['name'].apply(find_similarity, affiliation_name=affiliation_name)
    place = institutes[institutes['similarity'] > 0.9]
    if not place.empty:
        name = place['name'].iloc[0]
        grid_id = place['grid_id'].iloc[0]
        r.hset(affiliation_name, mapping={"name": name, "grid_id": grid_id})
        return [name, grid_id]
        
    return [affiliation_name, ""]


def get_affiliation_info(affiliation: str, doc: spacy.language, list_of_countries: list[str], institutes: pd.DataFrame, addresses: pd.DataFrame, r: redis.connection) -> dict:
    """Uses the affiliation text to retrieve all the required data about the affiliation"""
    affiliation_text = affiliation.text

    email = re.search(EMAIL_REGEX, affiliation_text)
    country = get_affiliation_country(doc, list_of_countries)
    affiliation_name = get_affiliation_name(doc)
    zipcode = get_affiliation_zipcode(affiliation_text)

    if r.hgetall(affiliation_name):
        grid_id = r.hget(affiliation_name, "grid_id")
        affiliation_name = r.hget(affiliation_name, "name")
    else:
        affiliation_name, grid_id = search_affiliation_matches(
            affiliation_name, country, institutes, addresses, r)

    return {"affiliation_text": affiliation.text, "email": email, "country": country, "name": affiliation_name, "zipcode": zipcode, "grid_id": grid_id}


def load_xml_data():
    """Retrieves all important data from the xml file and converts it into a dataframe"""
    root = ET.parse("./limited_data.xml").getroot()
    rows = []
    gc = geonamescache.GeonamesCache()
    list_of_countries = gc.get_countries()
    nlp_model = spacy.load("en_core_web_sm")
    institutes = pd.read_csv("./institutes.csv")
    addresses = pd.read_csv("./addresses.csv")
    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    for article in root.findall("./PubmedArticle/MedlineCitation"):
        article_dict = get_article_info(article)

        for author in article.findall(".//Article/AuthorList/Author"):
            author_dict = get_author_info(author)

            affiliation = author.find(".//AffiliationInfo/Affiliation")
            if affiliation is not None:
                doc = nlp_model(affiliation.text)
                affiliation_dict = get_affiliation_info(
                    affiliation, doc, list_of_countries, institutes, addresses, r)
            row = {
                "article_title": article_dict['title'],
                "article_PMID": article_dict['PMID'],
                "article_year": article_dict['year'],
                "article_keywords": article_dict['keywords'],
                "article_mesh": article_dict['mesh'],
                "affiliation": affiliation_dict["affiliation_text"],
                "affiliation_name": affiliation_dict["name"],
                "affiliation_email": affiliation_dict["email"],
                "affiliation_country": affiliation_dict["country"],
                "affiliation_zipcode": affiliation_dict["zipcode"],
                "affiliation_gridID": affiliation_dict["grid_id"],
                "author_first_name": author_dict['first_name'],
                "author_surname": author_dict['last_name'],
                "author_initials": author_dict['initials']
            }
            rows.append(row)
    base_df = pd.DataFrame(rows)
    base_df.to_csv("./output.csv")
