from presidio_analyzer import (
    AnalyzerEngine, 
    RecognizerRegistry, 
    PatternRecognizer
    )
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.predefined_recognizers import (
    PhoneRecognizer, 
    SpacyRecognizer, 
    #ItFiscalCodeRecognizer, 
    #ItVatCodeRecognizer
    )

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from anon_testo import it_fiscal_code_recognizer, it_vat_code

import json, re

def validateGateNLP(input:dict):
#REQUIRES: GateNLP Document as input
#MODIFIES: input
#EFFECTS: Checks wheter the provided GateNLP documents is properly formatted and m
    with open(input) as documento:
            parsedText = json.load(documento)

    if "entities" not in list(parsedText["annotation_sets"].keys()):
                    print("Entities non presente, correzione GateNLP in corso")
                    parsedText["annotation_sets"]["entities"] = {}
                    parsedText["annotation_sets"]["entities"]["name"] = "entities"
                    parsedText["annotation_sets"]["entities"]["annotations"] = []
                    parsedText['annotation_sets']["entities"]["next_annid"] = 1
                    
    if "annotations" not in list(parsedText["annotation_sets"]['entities'].keys()):
                    print("Nessuna annotazione presente nel campo Entities, correzione GateNLP in corso")
                    parsedText["annotation_sets"]["entities"] = {}
                    parsedText["annotation_sets"]["entities"]["name"] = "entities"
                    parsedText["annotation_sets"]["entities"]["annotations"] = []
                    parsedText['annotation_sets']["entities"]["next_annid"] = 1

    return parsedText

def nlpInput(input:dict):
#REQUIRES: Valid GateNLP document as input
#MODIFIES: input
#EFFECTS: Deletes PII from the annotations and returns them in a DenyList ready to be used by Presidio
    parsedText = input
    denyList = []
    try:
        text = parsedText['annotation_sets']["entities"]["annotations"]
        for annotazione in text:
            if annotazione["features"]["ner"]["type"] != "articolo_di_legge" and annotazione["features"]["ner"]["type"] != "data":
                for parola in annotazione["features"]["ner"]["normalized_text"].split():
                    if parola not in denyList:
                        parola = re.sub(r'[^a-zA-Z0-9]', ' ', parola)
                        denyList.append(parola)
                annotazione["features"]["title"] = ""
                annotazione["features"]["ner"]["normalized_text"]= "" 
        parsedText['annotation_sets']["entities"]["annotations"] = text
                
        for parola in parsedText['features']["parte"].lower().split():
            parola = re.sub(r'[^a-zA-Z0-9]', ' ', parola)
            denyList.append(parola)

        for parola in parsedText['features']["controparte"].lower().split():
            parola = re.sub(r'[^a-zA-Z0-9]', ' ', parola)
            denyList.append(parola)

        for parolaGiudice in parsedText['features']["nomegiudice"].lower().split():
            parolaGiudice = re.sub(r'[^a-zA-Z0-9]', ' ', parolaGiudice)
            denyList.append(parolaGiudice)   

        codFiscaleGiudice = parsedText['features']["cf_giudice"]
        denyList.append(codFiscaleGiudice)

        codFiscaleSender = parsedText['features']["senderid"]    
        denyList.append(codFiscaleSender)

    except:
        print("L'input non è in un formato supportato")
    
    return [denyList, parsedText]

def analisiTesto(denyList:list,testo:dict):
#REQUIRES: Validated GateNLP document and DenyList as inputs
#MODIFIES: //
#EFFECTS: Creates the Analyzer and identifies PII via DenyList and other Recognizers
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [
        {"lang_code": "it", "model_name": "it_core_news_lg"},
        ],
    }
    registry = RecognizerRegistry()

    if not len(denyList):
        telephone_recognizer_italian = PhoneRecognizer(supported_language= "it")
        spacyDefault_recognizer_italian = SpacyRecognizer(supported_language= "it", context= ["avv. ", "sig. "])
        fiscalCode_italian = it_fiscal_code_recognizer.ItFiscalCodeRecognizer(context="C.F. ")
        pIva_italian = it_vat_code.ItVatCodeRecognizer(context="C.F. ")
    
        registry.add_recognizer(telephone_recognizer_italian)
        registry.add_recognizer(spacyDefault_recognizer_italian)
        registry.add_recognizer(fiscalCode_italian)
        registry.add_recognizer(pIva_italian)

        entity_list = ["PERSON","LIST","IT_FISCAL_CODE","IT_VAT_CODE", "ORGANIZATION", "LOCATION"]
    else:
        annotationList_recognizer = PatternRecognizer(supported_language="it", supported_entity= "LIST", deny_list= denyList)
        registry.add_recognizer(annotationList_recognizer)

        entity_list = ["LIST"]

    provider = NlpEngineProvider(nlp_configuration = configuration)
    nlp_engine_with_italian = provider.create_engine()

    # Passiamo il provider all'engine
    analyzer = AnalyzerEngine(
        nlp_engine = nlp_engine_with_italian,
        registry = registry,
        supported_languages = "it")

    try:
        results = analyzer.analyze(text = testo["text"], 
                           language = "it", 
                           entities = entity_list,
                           score_threshold = 0.45,
                           )
        return (results)
    except:
        print("Analisi fallita")
        return []

def anonimTesto(testo:dict, risultatiAnalisi:list):
#REQUIRES: Validated GateNLP document text and analysis result as input
#MODIFIES: Validated GateNLP document
#EFFECTS: Creates the Anonymizer and masks the identified PIIs
    engine = AnonymizerEngine()
    # Rinomino gli operatori da quelli di Default ad una versione in italiano
    it_operators = {
        "PERSON": OperatorConfig("mask", {"masking_char": "-", "chars_to_mask": 30, "from_end": False}),
        "LIST": OperatorConfig("mask", {"masking_char": "-", "chars_to_mask": 30, "from_end": False}),
        "LOCATION": OperatorConfig("mask", {"masking_char": "-", "chars_to_mask": 30, "from_end": True}),
        "ORGANIZATION": OperatorConfig("mask", {"masking_char": "-", "chars_to_mask": 30, "from_end": False}),
        "PHONE_NUMBER": OperatorConfig("mask", {"masking_char": "-", "chars_to_mask": 18, "from_end": True}),
        "IT_FISCAL_CODE": OperatorConfig("mask", {"masking_char": "-", "chars_to_mask": 16, "from_end": True}),
        "IT_VAT_CODE": OperatorConfig("mask", {"masking_char": "-", "chars_to_mask": 11, "from_end": True}),
        }

    result = engine.anonymize(testo["text"], risultatiAnalisi, operators = it_operators)

    return result.text

def nlpOutput(nlpRipulito:json, anonimTesto:str):
#REQUIRES: Validated GateNLP document text and anonymized result as input
#MODIFIES: inputNLP
#EFFECTS: Returns the new anonymized GateNLP
    try:
        documentoAnonimizzato = nlpRipulito
        documentoAnonimizzato["text"] = anonimTesto

        return documentoAnonimizzato
    except:
        print("Ritorno del gateNLP modificato fallito")

