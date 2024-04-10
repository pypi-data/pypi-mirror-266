import copy

def updateAnnotazioni(gatenlpOriginale:dict, risultatoAnalisi:list, sovrascriviAnnotazioni):
#REQUIRES: Valid GateNLP and a List which contains the results of an analysis run by Presidio
#MODIFIES: input GateNLP
#EFFECTS: Returns a new GateNLP with updated annotations found via Presidio inside an annotation field

    if sovrascriviAnnotazioni == False:
        if "presidio_entities" not in (gatenlpOriginale["annotation_sets"].keys()):
            gatenlpOriginale["annotation_sets"]["presidio_entities"] = {}
            gatenlpOriginale["annotation_sets"]["presidio_entities"]["name"] = "presidio_entities"
            gatenlpOriginale["annotation_sets"]["presidio_entities"]["annotations"] = copy.deepcopy(gatenlpOriginale['annotation_sets']["entities"]["annotations"])
            gatenlpOriginale["annotation_sets"]["presidio_entities"]["next_annid"] = copy.deepcopy(gatenlpOriginale["annotation_sets"]["entities"]["next_annid"])

        nextID = gatenlpOriginale['annotation_sets']["presidio_entities"]["next_annid"]
        annotazioni = gatenlpOriginale['annotation_sets']["presidio_entities"]["annotations"]
    
    else:
        nextID = gatenlpOriginale['annotation_sets']["entities"]["next_annid"]
        annotazioni = gatenlpOriginale['annotation_sets']["entities"]["annotations"]

    # Mappiamo le entità per rinominarle
    entity_type_mapping = {
        'PERSON': 'persona_presidio',
        'LOCATION': 'indirizzo',
        'ORGANIZATION': 'persona_presidio',
        'IT_FISCAL_CODE':'codice_fiscale',
        'IT_VAT_CODE':'partita_iva',
        'LIST':'lista'
    }

    for nuovaAnnotazione in risultatoAnalisi:
        flagPresenza = False

        for annotazioneOriginale in annotazioni:
            if annotazioneOriginale["start"] == nuovaAnnotazione.start and annotazioneOriginale["end"] == nuovaAnnotazione.end:
                print("La seguente annotazione non è stata inserita in quanto doppione:")
                print(nuovaAnnotazione)
                flagPresenza = True,
                break
        
        if flagPresenza == False:
            mapped_entity_type = entity_type_mapping.get(nuovaAnnotazione.entity_type)
            
            if (mapped_entity_type) == 'lista':
                mapped_entity_type = 'persona_presidio'
                for annotazioneOriginale in annotazioni:
                    if annotazioneOriginale["features"]["title"] == gatenlpOriginale["text"][nuovaAnnotazione.start:nuovaAnnotazione.end]:
                        mapped_entity_type = annotazioneOriginale["features"]["ner"]["type"]
                        break

            testoAnnotazione = {"type": "Word",
                                "start": nuovaAnnotazione.start,
                                "end": nuovaAnnotazione.end,
                                "id": nextID,
                                "features": {
                                    "title": gatenlpOriginale["text"][nuovaAnnotazione.start:nuovaAnnotazione.end],
                                    "url": "",
                                    "ner": {
                                        "type": mapped_entity_type,
                                        "normalized_text": gatenlpOriginale["text"][nuovaAnnotazione.start:nuovaAnnotazione.end],
                                    },
                                    "entity_registry": {
                                        "er_name": None,
                                        "entity_type": None,
                                        "entity_id": None
                                    }
                                },
                            }
            annotazioni.append(testoAnnotazione)
            nextID += 1

    if sovrascriviAnnotazioni == False:
        gatenlpOriginale['annotation_sets']["presidio_entities"]["next_annid"] = nextID
        
    else:
        gatenlpOriginale['annotation_sets']["entities"]["next_annid"] = nextID

    return gatenlpOriginale