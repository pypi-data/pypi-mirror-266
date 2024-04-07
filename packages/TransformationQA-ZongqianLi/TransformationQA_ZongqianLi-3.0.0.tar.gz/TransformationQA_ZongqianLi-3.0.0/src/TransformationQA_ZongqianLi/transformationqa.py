def find_index(answer, paragraphs):
    """
    Find the index of the answer in the paragraphs.
    
    Args:
        answer (str): the answer for the QA pair
        paragraphs (str): the reference paper extracted by ChemDataExtractor
    
    Returns:
        indices (List[int]): a list of indices for the answer in the paragraphs
    """
    beg = 0
    indices = []
    while True:
        try:
            indices.append(paragraphs.index(answer, beg))
            beg = paragraphs.index(answer, beg) + 1
        except:
            break
    return indices



def determine_context(answer, paragraphs, num1, num2):
    """
    Find the context for the QA pair.
    
    Args:
        answer (str): the answer for the QA pair
        paragraphs (str): the paragraphs of the paper
        num1 (int): the number of additional sentences before the context
        num2 (int): the number of additional sentences after the context
    
    Returns:
        contexts (List[str]): a list of contexts for the QA pair
    """
    dot_indices = []
    paragraphs = paragraphs + " "
    for n in list(range(0, len(paragraphs))):
        if paragraphs[n:n+2] == ". ":
            dot_indices.append(n)
    if dot_indices[0] != 0:
        dot_indices = [0] + dot_indices
    if dot_indices[-1] != len(paragraphs)-1:
        dot_indices.append(len(paragraphs)-1)
    
    contexts = []
    answer_indices = find_index(answer, paragraphs)
    for answer_index in answer_indices:
        first = 0
        second = len(dot_indices)-1
        for m in list(range(0, len(dot_indices))):
            if dot_indices[m] > dot_indices[first] and dot_indices[m] < answer_index:
                first = m
            if dot_indices[m] < dot_indices[second] and dot_indices[m] > answer_index:
                second = m
                break
        if first-num1 < 0:
            first = 0
        else:
            first = first-num1
        if second+num2 > len(dot_indices)-1:
            second = len(dot_indices)-1
        else:
            second = second+num2
        contexts.append(paragraphs[dot_indices[first]:dot_indices[second]+1].lstrip(".").strip(" "))
        
    return contexts



def secondqa(materials, qa):
    num = 0
    # the number of materials in qa
    for material in materials:
        if material in qa["context"]:
            num += 1
        answermaterial = material
    if num == 1:
        secondqa = {"answers":{}}
        secondqa["answers"]["text"] = [answermaterial]
        secondqa["title"] = qa["title"]
        secondqa["context"] = qa["context"] 
        secondqa["answers"]["answer_start"] = [int(secondqa["context"].index(secondqa["answers"]["text"][0]))]
        secondqa["question"] = "What material has " + qa["specifier"] + " of " + str(qa["answers"]["text"][0]) + "?"
        secondqa["specifier"] = qa["specifier"]
    return secondqa



def create_qa_database(extraction, database):
    """
    Create QA dataset from existed dataset extracted by ChemDataExtractor.

    Args:
        extractions (List[Dict]): list of dictionaries for papers including "doi" and "paragraphs"
        database (List[Dict]): list of dictionarys for properties

    Returns:
        qa_database (List[List[Dict]]): a list of dictionaries for first-turn and second-turn QA pairs with squad format
    """   
    # collect the kinds of materials in the database
    materials = []
    try:
        if len(database["psc_material_components"]) > 0:
            for value in list(database["psc_material_components"].values()):
                try:
                    materials.append(value["raw_value"])
                except:
                    None
                try:
                    materials.append(value[0]["raw_value"])
                except:
                    None
    except:
        None
    try:
        if len(database["dsc_material_components"]) > 0:
            for value in list(database["dsc_material_components"].values()):
                try:
                    materials.append(value["raw_value"])
                except:
                    None
                try:
                    materials.append(value[0]["raw_value"])
                except:
                    None
    except:
        None
    
    qa_database = []
    secondqa_database = []
    if extraction["doi"] == database["article_info"]["doi"]:
            
            # device_characteristics
            if len(list(database["device_characteristics"].keys()))>0:
                for key in list(database["device_characteristics"].keys()):
                    try:
                        qa = {"answers":{}}
                        # value is a range
                        if " ± " in database["device_characteristics"][key]["raw_value"]:
                            first_part = database["device_characteristics"][key]["raw_value"].split(" ± ")[0]
                            second_part = database["device_characteristics"][key]["raw_value"].split(" ± ")[1]
                            # range is float
                            if "." in second_part:
                                answers_0 = list(
                                    linspace(
                                        float(first_part)-float(second_part), 
                                        float(first_part)+float(second_part), 
                                        2*int(second_part.split(".")[1].strip("0"))+1
                                    )
                                )
                                # solve the problem of elimination of 0 at the end
                                answers = [database["device_characteristics"][key]["raw_value"], database["device_characteristics"][key]["raw_value"].replace(" ± ", "±")]
                                for answer in answers_0:
                                    answer = str(round(answer, len(second_part.split(".")[1])))
                                    if len(answer.split(".")[1]) != len(second_part.split(".")[1]):
                                        answer = answer + "0"
                                    answers.append(answer)
                            # range is int
                            elif ("." in first_part) and ("." not in second_part):
                                answers_0 = list(
                                    linspace(
                                        float(first_part)-float(second_part), 
                                        float(first_part)+float(second_part), 
                                        2*int(first_part.split(".")[1].strip("0"))+1
                                    )
                                )
                                # solve the problem of elimination of 0 at the end
                                answers = [database["device_characteristics"][key]["raw_value"], database["device_characteristics"][key]["raw_value"].replace(" ± ", "±")]
                                for answer in answers_0:
                                    answer = str(round(answer, len(first_part.split(".")[1])))
                                    if len(answer.split(".")[1]) != len(first_part.split(".")[1]):
                                        answer = answer + "0"
                                    answers.append(answer)
                            # range is int
                            elif ("." not in first_part) and ("." not in second_part):
                                answers_0 = list(
                                    range(
                                        int(first_part)-int(second_part), 
                                        int(first_part)+int(second_part)+1, 
                                        1
                                    )
                                )
                                answers = [database["device_characteristics"][key]["raw_value"], database["device_characteristics"][key]["raw_value"].replace(" ± ", "±")]
                                for answer in answers_0:
                                    answer = str(answer)
                                    answers.append(answer)
                            for answer in answers:
                                # add the unit
                                unit = database["device_characteristics"][key]["raw_units"].strip("(").strip(")").strip("[").strip("]")
                                answer_set = [answer+unit, answer+" "+unit, answer+"("+unit+")", answer+" ("+unit+")"]
                                for answer_item in answer_set:
                                    if answer_item in extraction["paragraphs"]:
                                        for context in determine_context(answer_item, extraction["paragraphs"], 0, 0):
                                            qa = {"answers":{}}
                                            qa["title"] = extraction["doi"]
                                            qa["answers"]["text"] = [answer_item]
                                            qa["context"] = context
                                            qa["answers"]["answer_start"] = [int(qa["context"].index(qa["answers"]["text"][0]))]
                                            try:
                                                qa["specifier"] = database["device_characteristics"][key]["specifier"].strip(" /")
                                                if qa["specifier"] == "/":
                                                    qa["specifier"] = str(key)
                                                qa["question"] = "What is the value of " + qa["specifier"] + "?"
                                            except:
                                                qa["specifier"] = str(key)
                                                qa["question"] = "What is the value of " + qa["specifier"] + "?"
                                            qa_database.append(qa)
                                            secondqa_database.append(secondqa(materials, qa))
                        
                        # value is not a range
                        if " ± " not in database["device_characteristics"][key]["raw_value"]:
                            # add the unit
                            unit = database["device_characteristics"][key]["raw_units"].strip("(").strip(")").strip("[").strip("]")
                            answer = database["device_characteristics"][key]["raw_value"]
                            answer_set = [answer+unit, answer+" "+unit, answer+"("+unit+")", answer+" ("+unit+")"]
                            for answer_item in answer_set:
                                if answer_item in extraction["paragraphs"]:
                                    for context in determine_context(answer_item, extraction["paragraphs"], 0, 0):
                                        qa = {"answers":{}}
                                        qa["title"] = extraction["doi"]
                                        qa["answers"]["text"] = [answer_item]
                                        qa["context"] = context
                                        qa["answers"]["answer_start"] = [int(qa["context"].index(qa["answers"]["text"][0]))]
                                        try:
                                            qa["specifier"] = database["device_characteristics"][key]["specifier"].strip(" /")
                                            if qa["specifier"] == "/":
                                                qa["specifier"] = str(key)
                                            qa["question"] = "What is the value of " + qa["specifier"] + "?"
                                        except:
                                            qa["specifier"] = str(key)
                                            qa["question"] = "What is the value of " + qa["specifier"] + "?"
                                        qa_database.append(qa)
                                        secondqa_database.append(secondqa(materials, qa))
                    except:
                        None
                        
            # psc_material_components
            try:
                if len(list(database["psc_material_components"].keys())) > 0:
                    for key in list(database["psc_material_components"].keys()):
                        try:
                            qa = {"answers":{}}
                            if database["psc_material_components"][key]["raw_value"] in extraction["paragraphs"]:
                                for context in determine_context(database["psc_material_components"][key]["raw_value"], extraction["paragraphs"], 0, 0):
                                    qa["title"] = extraction["doi"]
                                    qa["answers"]["text"] = [database["psc_material_components"][key]["raw_value"].split(" ± ")[0]]
                                    qa["context"] = context
                                    qa["answers"]["answer_start"] = [int(qa["context"].index(qa["answers"]["text"][0]))]
                                    try:
                                        qa["specifier"] = database["psc_material_components"][key]["specifier"].strip(" /")
                                        if qa["specifier"] == "/":
                                            qa["specifier"] = str(key).replace("_", " ")
                                        qa["question"] = "What is " + qa["specifier"] + "?"
                                    except:
                                        qa["specifier"] = str(key).replace("_", " ")
                                        qa["question"] = "What is " + qa["specifier"] + "?"
                                    qa_database.append(qa)
                        except:
                            None
            except:
                None
            
            # dsc_material_components
            try:
                if len(list(database["dsc_material_components"].keys())) > 0:
                    for key in list(database["dsc_material_components"].keys()):
                        try:
                            qa = {"answers":{}}
                            if database["dsc_material_components"][key]["raw_value"] in extraction["paragraphs"]:
                                for context in determine_context(database["dsc_material_components"][key]["raw_value"], extraction["paragraphs"], 0, 0):
                                    qa["title"] = extraction["doi"]
                                    qa["answers"]["text"] = [database["dsc_material_components"][key]["raw_value"].split(" ± ")[0]]
                                    qa["context"] = context
                                    qa["answers"]["answer_start"] = [int(qa["context"].index(qa["answers"]["text"][0]))]
                                    try:
                                        qa["specifier"] = database["dsc_material_components"][key]["specifier"].strip(" /")
                                        if qa["specifier"] == "/":
                                            qa["specifier"] = str(key).replace("_", " ")
                                        qa["question"] = "What is " + qa["specifier"] + "?"
                                    except:
                                        qa["specifier"] = str(key).replace("_", " ")
                                        qa["question"] = "What is " + qa["specifier"] + "?"
                                    qa_database.append(qa)
                        except:
                            None
            except:
                None
            
            # device_metrology
            if len(list(database["device_metrology"].keys())) > 0:
                for key in list(database["device_metrology"].keys()):
                    try:
                        unit = database["device_metrology"][key]["raw_units"].strip("(").strip(")").strip("[").strip("]")
                        answer = database["device_metrology"][key]["raw_value"]
                        answer_set = [answer+unit, answer+" "+unit, answer+"("+unit+")", answer+" ("+unit+")"]
                        for answer_item in answer_set:
                            if answer_item in extraction["paragraphs"]:
                                for context in determine_context(answer_item, extraction["paragraphs"], 0, 0):
                                    qa = {"answers":{}}
                                    qa["title"] = extraction["doi"]
                                    qa["answers"]["text"] = [answer_item]
                                    qa["context"] = context
                                    qa["answers"]["answer_start"] = [int(qa["context"].index(qa["answers"]["text"][0]))]
                                    try:
                                        qa["specifier"] = database["device_metrology"][key]["specifier"].strip(" /")
                                        if qa["specifier"] == "/":
                                            qa["specifier"] = str(key)
                                        qa["question"] = "What is the value of " + qa["specifier"] + "?"
                                    except:
                                        qa["specifier"] = str(key)
                                        qa["question"] = "What is the value of " + qa["specifier"] + "?"
                                    qa_database.append(qa)
                                    secondqa_database.append(secondqa(materials, qa))
                    except:
                        None
                        
            # psc_material_metrology
            try:    
                if len(list(database["psc_material_metrology"].keys())) > 0:
                    for key in list(database["psc_material_metrology"].keys()):
                        try:
                            unit = database["psc_material_metrology"][key]["raw_units"].strip("(").strip(")").strip("[").strip("]")
                            answer = database["psc_material_metrology"][key]["raw_value"]
                            answer_set = [answer+unit, answer+" "+unit, answer+"("+unit+")", answer+" ("+unit+")"]
                            for answer_item in answer_set:
                                if answer_item in extraction["paragraphs"]:
                                    for context in determine_context(answer_item, extraction["paragraphs"], 0, 0):
                                        qa = {"answers":{}}
                                        qa["title"] = extraction["doi"]
                                        qa["answers"]["text"] = [answer_item]
                                        qa["context"] = context
                                        qa["answers"]["answer_start"] = [int(qa["context"].index(qa["answers"]["text"][0]))]
                                        try:
                                            qa["specifier"] = database["psc_material_metrology"][key]["specifier"].strip(" /")
                                            if qa["specifier"] == "/":
                                                qa["specifier"] = str(key)
                                            qa["question"] = "What is the value of " + qa["specifier"] + "?"
                                        except:
                                            qa["specifier"] = str(key)
                                            qa["question"] = "What is the value of " + qa["specifier"] + "?"
                                        qa_database.append(qa)
                                        secondqa_database.append(secondqa(materials, qa))
                        except:
                            None
            except:
                None
                
            # dsc_material_metrology
            try:
                if len(list(database["dsc_material_metrology"].keys())) > 0:
                    for key in list(database["dsc_material_metrology"].keys()):
                        try:
                            unit = database["dsc_material_metrology"][key]["raw_units"].strip("(").strip(")").strip("[").strip("]")
                            answer = database["dsc_material_metrology"][key]["raw_value"]
                            answer_set = [answer+unit, answer+" "+unit, answer+"("+unit+")", answer+" ("+unit+")"]
                            for answer_item in answer_set:
                                if answer_item in extraction["paragraphs"]:
                                    for context in determine_context(answer_item, extraction["paragraphs"], 0, 0):
                                        qa = {"answers":{}}
                                        qa["title"] = extraction["doi"]
                                        qa["answers"]["text"] = [answer_item]
                                        qa["context"] = context
                                        qa["answers"]["answer_start"] = [int(qa["context"].index(qa["answers"]["text"][0]))]
                                        try:
                                            qa["specifier"] = database["dsc_material_metrology"][key]["specifier"].strip(" /")
                                            if qa["specifier"] == "/":
                                                qa["specifier"] = str(key).replace("_", " ")
                                            qa["question"] = "What is the value of " + qa["specifier"] + "?"
                                        except:
                                            qa["specifier"] = str(key).replace("_", " ")
                                            qa["question"] = "What is the value of " + qa["specifier"] + "?"
                                        qa_database.append(qa)
                                        secondqa_database.append(secondqa(materials, qa))
                        except:
                            None
            except:
                None
            
    return [qa_database, secondqa_database]

