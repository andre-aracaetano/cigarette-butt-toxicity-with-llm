# -*- coding: utf-8 -*-
 
import pandas as pd
import ollama
import numpy as np
import random
from pathlib import Path
import os
import time
import unicodedata
import json
import re
import ast
import glob

print()

pasta = "../df_articles"
arquivos = glob.glob(os.path.join(pasta, "*.xlsx"))

df = pd.concat([pd.read_excel(arq) for arq in arquivos], ignore_index=True)

keywords = ['']

pattern = re.compile(r'\b(?:' + '|'.join(keywords) + r')\b', flags=re.IGNORECASE)

df_selection = df[df['text'].apply(lambda x: bool(pattern.search(x)))]

model = 'mistral-large:123b'
 
def model_extrator(abstract, titulo):
    response = ollama.chat(
        model=model,
        messages = [            
        {
        "role": "system",
        "content": (
            """ROLE
            You are a scientific data extractor specialized in retrieving test organisms and materials used in toxicological experiments from scientific articles about cigarette butt toxicology

            OBJECTIVE
            For each organism tested in the experiments performed by the authors of the current article extract exactly two elements species and material used

            STRICT OUTPUT CONTRACT
            - Output a single JSON object with exactly these keys species and material
            - species and material must be arrays of the same length
            - Index i across arrays refers to the same experimental test species[i] was tested with material[i]
            - Use null without quotes when a field is missing or unknown
            - Do not include any text outside the JSON object
            - Do not infer or guess any species or material not explicitly reported in the experiments
            - Only extract species that were directly tested by the authors in the current article
            - Only extract material if it is linked to a reported species

            SPECIES RULES
            - Extract exactly two word scientific names Genus species or abbreviated genus with species like T agglutinans
            - Ignore terms like spp sp cf or other non specific species indications
            - Ignore species mentioned with citations or references to other studies or authors
            - If no valid species is reported for a test use null

            MATERIAL RULES
            - Extract the material used in the toxicological test only if there is a species associated
            - Materials can be terms like SCB USF SF leachate or any explicitly reported experimental material
            - If no material is reported for a species use null
            - Ignore materials mentioned in literature review introduction discussion or other studies

            IGNORING EXTERNAL DATA
            - Do not extract species or materials reported in other studies
            - Ignore any values with in text citations e g Smith et al 2020 or phrases like as reported by according to in previous studies in a study by was found by was reported by
            - Ignore information in introduction discussion that clearly cites other authors

            OUTPUT FORMAT
            - Return a single JSON object
            - Each index i in the arrays represents a single experiment reported by the authors
            - Do not include numbers concentrations times measurements only species and material
            - Ensure the JSON is valid and can be parsed by a standard JSON parser

            EXAMPLES

            Example 1
            Input The EC50 value for Daphnia magna was 0 3 mg L after 96 h of exposure using SCB
            Output
            {
            "species": ["Daphnia magna"],
            "material": ["SCB"]
            }

            Example 2
            Input EC50 for Danio rerio was determined as 15 cigarette butts L for SCB and 0 25 mg L for USF
            Output
            {
            "species": ["Danio rerio","Danio rerio"],
            "material": ["SCB","USF"]
            }

            Example 3
            Input As observed for the species T tenuissima by van Dijk et al 2017 no effect was seen
            Output
            {
            "species": [null],
            "material": [null]
            }

            Example 4
            Input Cellular death in both calcareous species R globularis and Quinqueloculina spp at the highest concentration of leachate The vitality observed for the species T agglutinans was not affected
            Output
            {
            "species": ["R globularis","T agglutinans"],
            "material": ["leachate","leachate"]
            }

            Example 5
            Input No species or material were reported
            Output
            {
            "species": [null],
            "material": [null]
            }"""
        )},
        {"role": "user","content": f"Title: {titulo}\nSection: {abstract}\nExtract the toxicological features mentioned in the study. Follow the previous instructions and return the results in the specified format."}
        ],
        options={"temperature": temp, 'num_ctx': 20000,}
    )

    conteudo_bruto = response.message.content.strip()
    pensamento = str(response)
    
    return conteudo_bruto, pensamento

temp = 0
tp = 0.25
tk = 0
results = []
 
print("~~~~~~~~~~~~~~~~~~ EXTRACTION ~~~~~~~~~~~~~~~~~~")
pro = 0

len_articles = len(df_selection)

try:
    for x_sentence, x_abstract, x_title, x_doi, x_year, x_wos, x_sec, article_id, sec_id in zip(df_selection['text'],df_selection["abstract"], df_selection["title"], df_selection["doi"], df_selection["year"], df_selection["authors"], df_selection["section"], df_selection["article_id"], df_selection["sentence_id"]):
 
        title_article = x_title
        pro += 1
        p = pro/len_articles
        print(f"Progress: {pro}/{len_articles} ({p:.3%})")
        pre_abstract = []
 
        abstract = x_abstract
 
        print("Title:", title_article, " / Secao:", x_sec)
        print("Sentence:", x_sentence)

        extraction, think_x = model_extrator(x_sentence, title_article)
        print("Extraction:", extraction)

        results.append({
        "title": title_article,
        "article_id": article_id,
        "sentence_id": sec_id,
        "model": model,
        "abstract": abstract,
        "section": x_sec,
        "text": x_sentence,
        "extraction": extraction,
        "thinking": think_x,
        "DOI":x_doi,
        "year":x_year,
        "authors":x_wos,
        })

        try:
            df_extraction = pd.DataFrame(results)
            df_extraction.to_excel('species.xlsx', index=False)
        except:
            print("Erro salvamento")

        print()
                           
except Exception as e:
    df_extraction = pd.DataFrame(results)
    df_extraction.to_excel('species.xlsx', index=False)
    print("Erro", e)
 
df_extraction = pd.DataFrame(results)
df_extraction.to_excel('species.xlsx', index=False)

print("~~~~~~~~~~~~~~~~~~ COMPLET ~~~~~~~~~~~~~~~~~~")
