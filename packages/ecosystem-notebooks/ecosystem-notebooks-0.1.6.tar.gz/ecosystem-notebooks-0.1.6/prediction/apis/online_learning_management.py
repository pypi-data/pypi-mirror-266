from prediction.apis import algorithm_client_pulse as cp
from prediction.apis import data_management_engine as d

from datetime import datetime
import json
import uuid

def online_learning_ecosystem_rewards_setup_feature_store(
    auth,
    offer_db,
    offer_collection,
    offer_name_column,
    contextual_variables,
    setup_feature_store_db,
    setup_feature_store_collection
):
    if not isinstance(offer_db, str):
        raise TypeError("offer_db should be a string")
    if not isinstance(offer_collection, str):
        raise TypeError("offer_collection should be a string")
    if not isinstance(offer_name_column, str):
        raise TypeError("offer_name_column should be a string")
    if not isinstance(contextual_variables, dict):
        raise TypeError("contextual_variables should be a dictionary")
    if not isinstance(setup_feature_store_db, str):
        raise TypeError("setup_feature_store_db should be a string")
    if not isinstance(setup_feature_store_collection, str):
        raise TypeError("setup_feature_store_collection should be a string")

    try:
        sample_offer_collection = d.get_data(auth, offer_db, offer_collection, {}, 1, {}, 0)
        if len(sample_offer_collection) == 0:
            raise ImportError(f"Mongo collection {offer_collection} in database {offer_db} appears to be empty")
        if offer_name_column not in sample_offer_collection:
            raise KeyError(f"{offer_name_column}, specified as the offer_name_colume, not found as a field in {offer_collection}")
    except Exception as error:
        print("Unexpected error occured while validating offer_db and offer_collection")
        raise
    
    if len(contextual_variables) > 2:
        raise KeyError("At most two contextual variables can be specified for the ecosystem rewards algorithm")
    for context_var_iter in contextual_variables:
        if not isinstance(contextual_variables[context_var_iter], list):
            raise TypeError("The value for each key in the contextual variables dictionary should be a list of possible segment values")    

    contextual_fields = list(contextual_variables.keys())
    if len(contextual_fields) == 2:
        d.post_mongo_db_aggregate_pipeline(auth, 
            {
            "database":offer_db
            ,"collection":offer_collection
            ,"pipeline":[
                {"$group":{"_id":"$"+offer_name_column}}
                ,{"$project":{offer_name_column:"$_id","_id":0}}
                ,{"$addFields":{contextual_fields[0]:contextual_variables[contextual_fields[0]]}}
                ,{"$unwind":"$"+contextual_fields[0]}
                ,{"$addFields":{contextual_fields[1]:contextual_variables[contextual_fields[1]]}}
                ,{"$unset":"_id"}
                ,{"$unwind":"$"+contextual_fields[1]}
                ,{"$out":{"db":setup_feature_store_db,"coll":setup_feature_store_collection}}
            ]
            }
        )
    elif len(contextual_fields) == 1:
        d.post_mongo_db_aggregate_pipeline(auth, 
            {
            "database":offer_db
            ,"collection":offer_collection
            ,"pipeline":[
                {"$group":{"_id":"$"+offer_name_column}}
                ,{"$project":{offer_name_column:"$_id","_id":0}}
                ,{"$addFields":{contextual_fields[0]:contextual_variables[contextual_fields[0]]}}
                ,{"$unwind":"$"+contextual_fields[0]}
                ,{"$out":{"db":setup_feature_store_db,"coll":setup_feature_store_collection}}
            ]
            }
        )

def create_online_learning(
        auth,
        name,
        description,
        feature_store_collection,
        feature_store_database,
        options_store_database,
        options_store_collection,
        contextual_variables_offer_key,
        score_connection = "http://ecosystem-runtime:8091",
        score_database = "ecosystem_meta",
        score_collection = "dynamic_engagement",
        algorithm = "ecosystem_rewards",
        options_store_connection = "",
        batch = "false",       
        feature_store_connection = "",
        contextual_variables_contextual_variable_one_from_data_source = False,
        contextual_variables_contextual_variable_one_lookup = "",
        contextual_variables_contextual_variable_one_name = "",
        contextual_variables_contextual_variable_two_from_data_source = False,
        contextual_variables_contextual_variable_two_name = "",
        contextual_variables_contextual_variable_two_lookup = "",
        contextual_variables_tracking_key = "",
        contextual_variables_take_up = "",
        batch_database_out = "",
        batch_collection_out = "",
        batch_threads = 1,
        batch_collection = "",
        batch_userid = "",
        batch_contextual_variables = "",
        batch_number_of_offers = 1,
        batch_database = "",
        batch_pulse_responder_list = "",
        batch_find = "{}",
        batch_options = "",
        batch_campaign = "",
        batch_execution_type = "",
        randomisation_calendar = "None",
        randomisation_test_options_across_segment = "",
        randomisation_processing_count = 1000,
        randomisation_discount_factor = 0.75,
        randomisation_batch = "false",
        randomisation_prior_fail_reward = 0.1,
        randomisation_cross_segment_epsilon = 0,
        randomisation_success_reward = 1,
        randomisation_interaction_count = "0",
        randomisation_epsilon = 0,
        randomisation_prior_success_reward = 1,
        randomisation_fail_reward = 0.1,
        randomisation_max_reward = 10,
        randomisation_cache_duration = 0,
        randomisation_processing_window = 86400000,
        randomisation_random_action = 0.2,
        randomisation_decay_gamma = "1",
        randomisation_learning_rate = 0.25,
        replace = False
):
    #TODO add error checking and handling
    #Check for existence of online learning configuration with the same name
    existing_configurations = cp.list_pulse_responder_dynamic(auth)
    if not replace:
        if len([d for d in existing_configurations["data"] if d["name"] == name]) > 0:
            raise ValueError(f"There is an existing online learning configuration named {name} and replace is False")      
    
    #Initialise configuration document and store input parameters
    config_doc = {}
    config_doc["name"] = name
    config_doc["description"] = description
    
    config_doc["feature_store_collection"] = feature_store_collection
    config_doc["feature_store_database"] = feature_store_database
    config_doc["feature_store_connection"] = feature_store_connection
    
    config_doc["options_store_database"] = options_store_database
    config_doc["options_store_collection"] = options_store_collection
    config_doc["options_store_connection"] = options_store_connection
    
    config_doc["score_collection"] = score_collection
    config_doc["score_database"] = score_database
    config_doc["score_connection"] = score_connection
    
    config_doc["batch"] = batch
    config_doc["options"] = []
    config_doc["date_updated"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    config_doc["description"] = description
    config_doc["uuid"] = str(uuid.uuid4())
    
    #Get values for contextual variables
    if contextual_variables_contextual_variable_one_name != "":
        contextual_variable_one_values_pipeline = [
            {"$group":{"_id":"None","values":{"$addToSet":"$"+contextual_variables_contextual_variable_one_name}}}
        ]
        contextual_variable_one_values = d.post_mongo_db_aggregate_pipeline(
                auth,
                {"database": feature_store_database, "collection": feature_store_collection, "pipeline": contextual_variable_one_values_pipeline}
        )[0]["values"]
    else:
        contextual_variable_one_values = []
    
    if contextual_variables_contextual_variable_two_name != "":
        contextual_variable_two_values_pipeline = [
            {"$group":{"_id":"None","values":{"$addToSet":"$"+contextual_variables_contextual_variable_two_name}}}
        ]
        contextual_variable_two_values = d.post_mongo_db_aggregate_pipeline(
                auth,
                {"database": feature_store_database, "collection": feature_store_collection, "pipeline": contextual_variable_two_values_pipeline}
        )[0]["values"]
    else:
        contextual_variable_two_values = []
    
    contextual_variables = {
        "offer_key": contextual_variables_offer_key,
        "offer_values": [],
        "contextual_variable_one_from_data_source": contextual_variables_contextual_variable_one_from_data_source,
        "contextual_variable_one_lookup": contextual_variables_contextual_variable_one_lookup,
        "contextual_variable_one_name": contextual_variables_contextual_variable_one_name,
        "contextual_variable_one_values": contextual_variable_one_values,
        "contextual_variable_two_from_data_source": contextual_variables_contextual_variable_two_from_data_source,
        "contextual_variable_two_name": contextual_variables_contextual_variable_two_name,
        "contextual_variable_two_lookup": contextual_variables_contextual_variable_two_lookup,
        "contextual_variable_two_values": contextual_variable_two_values,
        "tracking_key": contextual_variables_tracking_key,
        "take_up": contextual_variables_take_up
    }    
    config_doc["contextual_variables"] = contextual_variables
    
    batch_settings = {
        "database_out": batch_database_out,
        "collection_out": batch_collection_out,
        "batchUpdateMessage": "",
        "threads": batch_threads,
        "collection": batch_collection,
        "userid": batch_userid,
        "contextual_variables": batch_contextual_variables,
        "number_of_offers": batch_number_of_offers,
        "batch_outline": "",
        "pulse_responder_list": batch_pulse_responder_list,
        "database": batch_database,
        "find": batch_find,
        "options": batch_options,
        "campaign": batch_campaign,
        "execution_type": batch_execution_type
    }
    config_doc["batch_settings"] = batch_settings
    
    if algorithm not in ["ecosystem_rewards"]:
        raise ValueError("algorithm must be ecosystem_rewards algorithm for other algorithms please use the ecosystem.Ai workbench")
    else:
        randomisation = {
            "calendar": randomisation_calendar,
            "test_options_across_segment": randomisation_test_options_across_segment,
            "processing_count": randomisation_processing_count,
            "discount_factor": randomisation_discount_factor,
            "batch": randomisation_batch,
            "prior_fail_reward": randomisation_prior_fail_reward,
            "approach": "binaryThompson",
            "cross_segment_epsilon": randomisation_cross_segment_epsilon,
            "success_reward": randomisation_success_reward,
            "interaction_count": randomisation_interaction_count,
            "epsilon": randomisation_epsilon,
            "prior_success_reward": randomisation_prior_success_reward,
            "fail_reward": randomisation_fail_reward,
            "max_reward": randomisation_max_reward,
            "cache_duration": randomisation_cache_duration,
            "processing_window": randomisation_processing_window,
            "random_action": randomisation_random_action,
            "decay_gamma": randomisation_decay_gamma,
            "learning_rate": randomisation_learning_rate
        }
        config_doc["randomisation"] = randomisation
  
    config_doc["lookup_fields"] = []
    config_doc["virtual_variables"] = []
    
    properties_list = [
        {"uuid":config_doc["uuid"], "type":"dynamic_engagement", "name":"dynamic_engagement", "database":"mongodb", "db":config_doc["score_database"], "table":config_doc["score_collection"], "update":True}
        ,{"uuid":config_doc["uuid"], "type":"dynamic_engagement_options", "name":"dynamic_engagement", "database":"mongodb", "db":config_doc["options_store_database"], "table":config_doc["options_store_collection"], "update":True}
    ]
    config_doc["properties"] = json.dumps(properties_list)
    
    if len([d for d in existing_configurations["data"] if d["name"] == name]) > 0:
        cp.delete_pulse_responder_dynamic(auth,score_database,score_collection,{"name":name})
        
    d.add_documents(auth, {"database": config_doc["score_database"], "collection": config_doc["score_collection"], "document": config_doc})
    
    doc_delete = {
        "database": config_doc["options_store_database"]
        ,"collection": config_doc["options_store_collection"]
    }
    d.delete_all_documents(auth, doc_delete)
    cp_update_doc = {
        "type":"generateDefaultOptions"
        ,"name":config_doc["name"]
        ,"uuid":config_doc["uuid"]
        ,"engagement_type":"binaryThompson"
        ,"feature_store_database":config_doc["feature_store_database"]
        ,"feature_store_collection":config_doc["feature_store_collection"]
        ,"contextual_variable_one_values":contextual_variable_one_values
        ,"contextual_variable_two_values":contextual_variable_two_values
        ,"contextual_variable_one_name":config_doc["contextual_variables"]["contextual_variable_one_name"]
        ,"contextual_variable_two_name":config_doc["contextual_variables"]["contextual_variable_two_name"]
        ,"contextual_variable_one_from_data_source":config_doc["contextual_variables"]["contextual_variable_one_from_data_source"]
        ,"contextual_variable_two_from_data_source":config_doc["contextual_variables"]["contextual_variable_two_from_data_source"]
        ,"contextual_variable_one_lookup":config_doc["contextual_variables"]["contextual_variable_one_lookup"]
        ,"contextual_variable_two_lookup":config_doc["contextual_variables"]["contextual_variable_two_lookup"]
        ,"offer_key":config_doc["contextual_variables"]["offer_key"]
        ,"tracking_key":config_doc["contextual_variables"]["tracking_key"]
        ,"options_store_database":config_doc["options_store_database"]
        ,"options_store_collection":config_doc["options_store_collection"]
        ,"prior_success_reward":config_doc["randomisation"]["prior_success_reward"]
        ,"prior_fail_reward":config_doc["randomisation"]["prior_fail_reward"]
        ,"take_up":config_doc["contextual_variables"]["take_up"]
    }
    cp.update_client_pulse_responder(auth, cp_update_doc)
    
    print("MESSAGE: Online learning configuration created")
    return config_doc["uuid"]