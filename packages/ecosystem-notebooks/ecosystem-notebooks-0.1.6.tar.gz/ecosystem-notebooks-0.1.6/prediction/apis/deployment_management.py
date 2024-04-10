from typing import Dict, Any

from prediction.apis import prediction_engine as pe
from prediction.apis import algorithm_client_pulse as cp
from prediction.apis import data_management_engine as d

from datetime import datetime
from json import JSONDecodeError
import json
import pymongo


def get_budget_tracker_default():
    return {
        "budget_parameters_database": "",
        "budget_parameters_datasource": "mongodb",
        "budget_id": "",
        "description": "",
        "budget_parameters_table_collection": "",
        "x_axis_datasource": "offer_matrix",
        "x_axis_name": "",
        "acc_namesource": "",
        "y_axis_name": "",
        "y_axis_namesource": "",
        "acc_name": "",
        "budget_strategy": "",
        "x_axis_namesource": "",
        "acc_datasource": "offer_matrix",
        "y_axis_datasource": "offer_matrix"
    }


def get_model_configuration_default():
    return {}


def get_setup_offer_matrix_default():
    return {
        "offer_lookup_id": "",
        "database": "",
        "table_collection": "",
        "datasource": "mongodb"
    }


def get_multi_armed_bandit_default():
    return {
        "epsilon": "",
        "duration": 0,
        "pulse_responder_uuid": ""
    }


def get_whitelist_default():
    return {
        "table_collection": "",
        "datasource": "mongodb",
        "database": ""
    }


def get_model_selector_default():
    return {
        "selector_column": "",
        "lookup": "",
        "database": "",
        "selector": "",
        "table_collection": "",
        "datasource": "mongodb"
    }


def get_pattern_selector_default():
    return {
        "pattern": "",
        "duration": ""
    }


def get_corpora_default():
    return {
        "corpora": ""
    }

def get_parameter_access_default():
    return {}

def get_api_endpoint_code_default():
    return ""

def get_pre_score_code(pre_score, project_details):
    pre_score_code_options = {
        "": "package com.ecosystem.plugin.customer;\n\nimport com.datastax.oss.driver.api.core.CqlSession;\nimport org.json.JSONObject;\n\npublic class PrePredictCustomer {\n\n    public PrePredictCustomer() {\n    }\n\n    /**\n     * Pre-pre predict\n     */\n    public void getPrePredict() {\n    }\n\n    /**\n     * getPostPredict\n     * @param params\n     * @param session\n     * @return\n     */\n    public static JSONObject getPrePredict(JSONObject params, CqlSession session) {\n\n        /*\n        Manipulate params that will be used by scoring and post-scoring\n         */\n\n        return params;\n    }\n\n}\n",
    }
    version_list = [i["version"] for i in project_details["deployment_step"] if
                    i["plugins"]["pre_score_class_text"] == pre_score]
    if version_list:
        max_version = max(version_list)
        pre_score_logic = [i["plugins"]["pre_score_class_code"] for i in project_details["deployment_step"] if
                            (i["plugins"]["pre_score_class_text"] == pre_score and i["version"] == max_version)][0]
    elif pre_score in pre_score_code_options:
        pre_score_logic = pre_score_code_options[pre_score]
    else:
        print(
            "WARNING: pre_score_class not found in default options. Empty class saved to the deployment. To edit the class use the ecosystem.Ai plugin for IntelliJ or the ecosystem.Ai workbench")
        pre_score_logic = ""
    return pre_score_logic

def get_post_score_code(post_score, project_details):
    post_score_code_options = {
        "PlatformDynamicEngagement.java": "package com.ecosystem.plugin.customer;\n\nimport com.datastax.oss.driver.api.core.CqlSession;\nimport com.ecosystem.utils.DataTypeConversions;\nimport com.ecosystem.utils.JSONArraySort;\nimport hex.genmodel.easy.EasyPredictModelWrapper;\nimport com.ecosystem.utils.log.LogManager;\nimport com.ecosystem.utils.log.Logger;\nimport org.json.JSONArray;\nimport org.json.JSONObject;\n\n/**\n * ECOSYSTEM.AI INTERNAL PLATFORM SCORING\n * Use this class to score with dynamic sampling configurations. This class is configured to work with no model.\n */\npublic class PlatformDynamicEngagement extends PostScoreSuper {\n\tprivate static final Logger LOGGER = LogManager.getLogger(PlatformDynamicEngagement.class.getName());\n\n\tpublic PlatformDynamicEngagement() {\n\t}\n\n\t/**\n\t * Pre-post predict logic\n\t */\n\tpublic void getPostPredict () {\n\t}\n\n\t/**\n\t * getPostPredict\n\t * Example params:\n\t *    {\"contextual_variable_one\":\"Easy Income Gold|Thin|Senior\", \"contextual_variable_two\":\"\", \"batch\": true}\n\t *\n\t * @param predictModelMojoResult Result from scoring\n\t * @param params                 Params carried from input\n\t * @param session                Session variable for Cassandra\n\t * @return JSONObject result to further post-scoring logic\n\t */\n\tpublic static JSONObject getPostPredict(JSONObject predictModelMojoResult, JSONObject params, CqlSession session, EasyPredictModelWrapper[] models) {\n\t\tdouble startTimePost = System.nanoTime();\n\t\ttry {\n\t\t\t/** Setup JSON objects for specific prediction case */\n\t\t\tJSONObject featuresObj = predictModelMojoResult.getJSONObject(\"featuresObj\");\n\t\t\t//JSONObject domainsProbabilityObj = predictModelMojoResult.getJSONObject(\"domainsProbabilityObj\");\n\n\t\t\tJSONObject offerMatrixWithKey = new JSONObject();\n\t\t\tboolean om = false;\n\t\t\tif (params.has(\"offerMatrixWithKey\")) {\n\t\t\t\tofferMatrixWithKey = params.getJSONObject(\"offerMatrixWithKey\");\n\t\t\t\tom = true;\n\t\t\t}\n\n\t\t\tJSONObject work = params.getJSONObject(\"in_params\");\n\n\t\t\t/***************************************************************************************************/\n\t\t\t/** Standardized approach to access dynamic datasets in plugin.\n\t\t\t * The options array is the data set/feature_store that's keeping track of the dynamic changes.\n\t\t\t * The optionParams is the parameter set that will influence the real-time behavior through param changes.\n\t\t\t */\n\t\t\t/***************************************************************************************************/\n\t\t\tJSONArray options = (JSONArray) ((\n\t\t\t\t\t(JSONObject) params.getJSONObject(\"dynamicCorpora\")\n\t\t\t\t\t\t\t.get(\"dynamic_engagement_options\")).get(\"data\"));\n\t\t\tJSONObject optionParams = (JSONObject) ((\n\t\t\t\t\t(JSONObject) params.getJSONObject(\"dynamicCorpora\")\n\t\t\t\t\t\t\t.get(\"dynamic_engagement\")).get(\"data\"));\n\n\t\t\tJSONObject contextual_variables = optionParams.getJSONObject(\"contextual_variables\");\n\t\t\tJSONObject randomisation = optionParams.getJSONObject(\"randomisation\");\n\n\t\t\t/***************************************************************************************************/\n\t\t\t/** Test if contextual variable is coming via api or feature store: API takes preference... */\n\t\t\tif (!work.has(\"contextual_variable_one\")) {\n\t\t\t\tif (featuresObj.has(contextual_variables.getString(\"contextual_variable_one_name\")))\n\t\t\t\t\twork.put(\"contextual_variable_one\", featuresObj.get(contextual_variables.getString(\"contextual_variable_one_name\")));\n\t\t\t\telse\n\t\t\t\t\twork.put(\"contextual_variable_one\", \"\");\n\t\t\t}\n\t\t\tif (!work.has(\"contextual_variable_two\")) {\n\t\t\t\tif (featuresObj.has(contextual_variables.getString(\"contextual_variable_two_name\")))\n\t\t\t\t\twork.put(\"contextual_variable_two\", featuresObj.get(contextual_variables.getString(\"contextual_variable_two_name\")));\n\t\t\t\telse\n\t\t\t\t\twork.put(\"contextual_variable_two\", \"\");\n\t\t\t}\n\t\t\t/***************************************************************************************************/\n\n\t\t\tJSONArray finalOffers = new JSONArray();\n\t\t\tint offerIndex = 0;\n\t\t\tint explore;\n\t\t\tString contextual_variable_one = String.valueOf(work.get(\"contextual_variable_one\"));\n\t\t\tString contextual_variable_two = String.valueOf(work.get(\"contextual_variable_two\"));\n\t\t\tfor (int j = 0; j < options.length(); j++) {\n\t\t\t\tJSONObject option = options.getJSONObject(j);\n\t\t\t\tString contextual_variable_one_Option = \"\";\n\t\t\t\tif (option.has(\"contextual_variable_one\") && !contextual_variable_one.equals(\"\"))\n\t\t\t\t\tcontextual_variable_one_Option = String.valueOf(option.get(\"contextual_variable_one\"));\n\t\t\t\tString contextual_variable_two_Option = \"\";\n\t\t\t\tif (option.has(\"contextual_variable_two\") && !contextual_variable_two.equals(\"\"))\n\t\t\t\t\tcontextual_variable_two_Option = String.valueOf(option.get(\"contextual_variable_two\"));\n\n\t\t\t\tif (contextual_variable_one_Option.equals(contextual_variable_one) && contextual_variable_two_Option.equals(contextual_variable_two)) {\n\n\t\t\t\t\tdouble alpha = (double) DataTypeConversions.getDoubleFromIntLong(option.get(\"alpha\"));\n\t\t\t\t\tdouble beta = (double) DataTypeConversions.getDoubleFromIntLong(option.get(\"beta\"));\n\t\t\t\t\tdouble accuracy = 0.001;\n\t\t\t\t\tif (option.has(\"accuracy\"))\n\t\t\t\t\t\taccuracy = (double) DataTypeConversions.getDoubleFromIntLong(option.get(\"accuracy\"));\n\n\t\t\t\t\t/***************************************************************************************************/\n\t\t\t\t\t/* r IS THE RANDOMIZED SCORE VALUE */\n\t\t\t\t\tdouble p = 0.0;\n\t\t\t\t\tdouble arm_reward = 0.001;\n\t\t\t\t\tif (randomisation.getString(\"approach\").equals(\"epsilonGreedy\")) {\n\t\t\t\t\t\t// params.put(\"explore\", 0);\n\t\t\t\t\t\texplore = 0;\n\t\t\t\t\t\tp = DataTypeConversions.getDouble(option, \"arm_reward\");\n\t\t\t\t\t\tarm_reward = p;\n\t\t\t\t\t} else {\n\t\t\t\t\t\t/** REMEMBER THAT THIS IS HERE BECAUSE OF BATCH PROCESS, OTHERWISE IT REQUIRES THE TOTAL COUNTS */\n\t\t\t\t\t\t/* Phase 2: sampling - calculate the arms and rank them */\n\t\t\t\t\t\t// params.put(\"explore\", 0); // force explore to zero and use Thompson Sampling only!!\n\t\t\t\t\t\texplore = 0; // set as explore as the dynamic responder is exploration based...\n\t\t\t\t\t\tp = DataTypeConversions.getDouble(option, \"arm_reward\");\n\t\t\t\t\t\tarm_reward = p;\n\n\t\t\t\t\t}\n\t\t\t\t\t/** Check if values are correct */\n\t\t\t\t\tif (p != p) p = 0.0;\n\t\t\t\t\tif (alpha != alpha) alpha = 0.0;\n\t\t\t\t\tif (beta != beta) beta = 0.0;\n\t\t\t\t\tif (arm_reward != arm_reward) arm_reward = 0.0;\n\t\t\t\t\t/***************************************************************************************************/\n\n\t\t\t\t\tString offer = option.getString(\"optionKey\");\n\n\t\t\t\t\tJSONObject singleOffer = new JSONObject();\n\t\t\t\t\tdouble offer_value = 1.0;\n\t\t\t\t\tdouble offer_cost = 1.0;\n\t\t\t\t\tdouble modified_offer_score = p;\n\t\t\t\t\tif (om) {\n\t\t\t\t\t\tif (offerMatrixWithKey.has(offer)) {\n\n\t\t\t\t\t\t\tsingleOffer = offerMatrixWithKey.getJSONObject(offer);\n\n\t\t\t\t\t\t\tif (singleOffer.has(\"offer_price\"))\n\t\t\t\t\t\t\t\toffer_value = DataTypeConversions.getDouble(singleOffer, \"offer_price\");\n\t\t\t\t\t\t\tif (singleOffer.has(\"price\"))\n\t\t\t\t\t\t\t\toffer_value = DataTypeConversions.getDouble(singleOffer, \"price\");\n\n\t\t\t\t\t\t\tif (singleOffer.has(\"offer_cost\"))\n\t\t\t\t\t\t\t\toffer_cost = singleOffer.getDouble(\"offer_cost\");\n\t\t\t\t\t\t\tif (singleOffer.has(\"cost\"))\n\t\t\t\t\t\t\t\toffer_cost = singleOffer.getDouble(\"cost\");\n\n\t\t\t\t\t\t\tmodified_offer_score = p * ((double) offer_value - offer_cost);\n\t\t\t\t\t\t}\n\t\t\t\t\t}\n\n\t\t\t\t\tJSONObject finalOffersObject = new JSONObject();\n\n\t\t\t\t\tfinalOffersObject.put(\"offer\", offer);\n\t\t\t\t\tfinalOffersObject.put(\"offer_name\", offer);\n\t\t\t\t\tfinalOffersObject.put(\"offer_name_desc\", option.getString(\"option\"));\n\n\t\t\t\t\t/* process final */\n\t\t\t\t\tfinalOffersObject.put(\"score\", p);\n\t\t\t\t\tfinalOffersObject.put(\"final_score\", p);\n\t\t\t\t\tfinalOffersObject.put(\"modified_offer_score\", modified_offer_score);\n\t\t\t\t\tfinalOffersObject.put(\"offer_value\", offer_value);\n\t\t\t\t\tfinalOffersObject.put(\"price\", offer_value);\n\t\t\t\t\tfinalOffersObject.put(\"cost\", offer_cost);\n\n\t\t\t\t\tfinalOffersObject.put(\"p\", p);\n\t\t\t\t\tif (option.has(\"contextual_variable_one\"))\n\t\t\t\t\t\tfinalOffersObject.put(\"contextual_variable_one\", option.getString(\"contextual_variable_one\"));\n\t\t\t\t\telse\n\t\t\t\t\t\tfinalOffersObject.put(\"contextual_variable_one\", \"\");\n\n\t\t\t\t\tif (option.has(\"contextual_variable_two\"))\n\t\t\t\t\t\tfinalOffersObject.put(\"contextual_variable_two\", option.getString(\"contextual_variable_two\"));\n\t\t\t\t\telse\n\t\t\t\t\t\tfinalOffersObject.put(\"contextual_variable_two\", \"\");\n\n\t\t\t\t\tfinalOffersObject.put(\"alpha\", alpha);\n\t\t\t\t\tfinalOffersObject.put(\"beta\", beta);\n\t\t\t\t\tfinalOffersObject.put(\"weighting\", (double) DataTypeConversions.getDoubleFromIntLong(option.get(\"weighting\")));\n\t\t\t\t\tfinalOffersObject.put(\"explore\", explore);\n\t\t\t\t\tfinalOffersObject.put(\"uuid\", params.get(\"uuid\"));\n\t\t\t\t\tfinalOffersObject.put(\"arm_reward\", arm_reward);\n\n\t\t\t\t\t/* Debugging variables */\n\t\t\t\t\tif (!option.has(\"expected_takeup\"))\n\t\t\t\t\t\tfinalOffersObject.put(\"expected_takeup\", -1.0);\n\t\t\t\t\telse\n\t\t\t\t\t\tfinalOffersObject.put(\"expected_takeup\", (double) DataTypeConversions.getDoubleFromIntLong(option.get(\"expected_takeup\")));\n\n\t\t\t\t\tif (!option.has(\"propensity\"))\n\t\t\t\t\t\tfinalOffersObject.put(\"propensity\", -1.0);\n\t\t\t\t\telse\n\t\t\t\t\t\tfinalOffersObject.put(\"propensity\", (double) DataTypeConversions.getDoubleFromIntLong(option.get(\"propensity\")));\n\n\t\t\t\t\tif (!option.has(\"epsilon_nominated\"))\n\t\t\t\t\t\tfinalOffersObject.put(\"epsilon_nominated\", -1.0);\n\t\t\t\t\telse\n\t\t\t\t\t\tfinalOffersObject.put(\"epsilon_nominated\", (double) DataTypeConversions.getDoubleFromIntLong(option.get(\"epsilon_nominated\")));\n\n\t\t\t\t\tfinalOffers.put(offerIndex, finalOffersObject);\n\t\t\t\t\tofferIndex = offerIndex + 1;\n\t\t\t\t}\n\t\t\t}\n\n\t\t\tJSONArray sortJsonArray = JSONArraySort.sortArray(finalOffers, \"arm_reward\", \"double\", \"d\");\n\t\t\tpredictModelMojoResult.put(\"final_result\", sortJsonArray);\n\n\t\t\tpredictModelMojoResult = getTopScores(params, predictModelMojoResult);\n\n\t\t\tdouble endTimePost = System.nanoTime();\n\t\t\tLOGGER.info(\"PlatformDynamicEngagement:I001: time in ms: \".concat( String.valueOf((endTimePost - startTimePost) / 1000000) ));\n\n\t\t} catch (Exception e) {\n\t\t\te.printStackTrace();\n\t\t\tLOGGER.error(e);\n\t\t}\n\n\t\treturn predictModelMojoResult;\n\n\t}\n\n}\n",
        "PostScoreBasic.java": "package com.ecosystem.plugin.customer;\n\nimport com.datastax.oss.driver.api.core.CqlSession;\nimport com.ecosystem.utils.DataTypeConversions;\nimport com.ecosystem.utils.JSONArraySort;\nimport hex.genmodel.easy.EasyPredictModelWrapper;\nimport com.ecosystem.utils.log.LogManager;\nimport com.ecosystem.utils.log.Logger;\nimport org.json.JSONArray;\nimport org.json.JSONObject;\n\nimport java.util.ArrayList;\n\nimport static com.ecosystem.EcosystemResponse.obtainBudget;\n\n/**\n * This the ecosystem/Ai generic post-score template.\n * Customer plugin for specialized logic to be added to the runtime engine.\n * This class is loaded through the plugin loader system.\n */\npublic class PostScoreBasic extends PostScoreSuper {\n\tprivate static final Logger LOGGER = LogManager.getLogger(PostScoreBasic.class.getName());\n\n\tpublic PostScoreBasic() {\n\t}\n\n\t/**\n\t * Pre-post predict logic\n\t */\n\tpublic void getPostPredict () {\n\t}\n\n\t/**\n\t * getPostPredict\n\t *\n\t * @param predictModelMojoResult Result from scoring\n\t * @param params                 Params carried from input\n\t * @param session                Session variable for Cassandra\n\t * @param models \t\t\t\t Preloaded H2O Models\n\t * @return JSONObject result to further post-scoring logic\n\t */\n\tpublic static JSONObject getPostPredict(JSONObject predictModelMojoResult, JSONObject params, CqlSession session, EasyPredictModelWrapper[] models) {\n\t\tdouble startTimePost = System.nanoTime();\n\t\ttry {\n\t\t\t/* Setup JSON objects for specific prediction case */\n\t\t\tJSONObject featuresObj = predictModelMojoResult.getJSONObject(\"featuresObj\");\n\t\t\tJSONObject domainsProbabilityObj = new JSONObject();\n\t\t\tif (predictModelMojoResult.has(\"domainsProbabilityObj\"))\n\t\t\t\tdomainsProbabilityObj = predictModelMojoResult.getJSONObject(\"domainsProbabilityObj\");\n\n\t\t\t/* If whitelist settings then only allow offers on list */\n\t\t\tboolean whitelist = false;\n\t\t\tArrayList<String> offerWhiteList = new ArrayList<>();\n\t\t\tif (params.has(\"whitelist\")) {\n\t\t\t\tif (!params.getJSONObject(\"whitelist\").isEmpty()) {\n\t\t\t\t\tofferWhiteList = (ArrayList<String>) params.getJSONObject(\"whitelist\").get(\"whitelist\");\n\t\t\t\t\tparams.put(\"resultcount\", offerWhiteList.size());\n\t\t\t\t\twhitelist = DataTypeConversions.getBooleanFromString(params.getJSONObject(\"whitelist\").get(\"logicin\"));\n\t\t\t\t}\n\t\t\t}\n\n\t\t\tif (params.has(\"preloadCorpora\")) {\n\t\t\t\tif (params.getJSONObject(\"preloadCorpora\").has(\"network\")) {\n\t\t\t\t\tJSONObject a = params.getJSONObject(\"preloadCorpora\");\n\t\t\t\t\tJSONObject preloadCorpora = a.getJSONObject(\"network\");\n\t\t\t\t}\n\t\t\t}\n\n\t\t\tJSONArray finalOffers = new JSONArray();\n\t\t\tint resultcount = (int) params.get(\"resultcount\");\n\t\t\t/* For each offer in offer matrix determine eligibility */\n\t\t\t/* get selector field from properties: predictor.selector.setup */\n\t\t\t// String s = new JSONObject(settings.getSelectorSetup()).getJSONObject(\"lookup\").getString(\"fields\");\n\n\t\t\t/** This loop can be used to add number of offers/options to return result */\n\t\t\tJSONObject finalOffersObject = new JSONObject();\n\t\t\tint offerIndex = 0;\n\t\t\tfor (int i = 0; i < resultcount; i++) {\n\n\t\t\t\t/** Model type based approaches */\n\t\t\t\tString type = \"\";\n\t\t\t\tboolean explainability = false;\n\t\t\t\t// LOGGER.info(\"predictModelMojoResult: \" + predictModelMojoResult.toString());\n\t\t\t\tif (predictModelMojoResult.get(\"type\").getClass().getName().toLowerCase().contains(\"array\")) {\n\t\t\t\t\ttype = predictModelMojoResult\n\t\t\t\t\t\t\t.getJSONArray(\"type\")\n\t\t\t\t\t\t\t.get(0)\n\t\t\t\t\t\t\t.toString().toLowerCase().trim();\n\t\t\t\t\tif (predictModelMojoResult.has(\"shapley_contributions\"))\n\t\t\t\t\t\texplainability = true;\n\t\t\t\t} else {\n\t\t\t\t\ttype = ((String) predictModelMojoResult.get(\"type\")).toLowerCase().trim();\n\t\t\t\t}\n\n\t\t\t\t/** Offer name, defaults to type (replace with offer matrix etc) */\n\t\t\t\tif (featuresObj.has(\"offer_name_final\"))\n\t\t\t\t\tfinalOffersObject.put(\"offer_name\", featuresObj.get(\"offer_name_final\"));\n\t\t\t\telse\n\t\t\t\t\tfinalOffersObject.put(\"offer_name\", type);\n\n\t\t\t\tif (featuresObj.has(\"offer\"))\n\t\t\t\t\tfinalOffersObject.put(\"offer\", featuresObj.get(\"offer\"));\n\t\t\t\telse\n\t\t\t\t\tfinalOffersObject.put(\"offer\", type);\n\n\t\t\t\tif (featuresObj.has(\"offer_id\"))\n\t\t\t\t\tfinalOffersObject.put(\"offer\", featuresObj.get(\"offer_id\"));\n\t\t\t\telse\n\t\t\t\t\tfinalOffersObject.put(\"offer_id\", type);\n\n\t\t\t\tif (featuresObj.has(\"price\"))\n\t\t\t\t\tfinalOffersObject.put(\"price\", featuresObj.get(\"price\"));\n\t\t\t\telse\n\t\t\t\t\tfinalOffersObject.put(\"price\", 1.0);\n\n\t\t\t\tif (featuresObj.has(\"cost\"))\n\t\t\t\t\tfinalOffersObject.put(\"cost\", featuresObj.get(\"cost\"));\n\t\t\t\telse\n\t\t\t\t\tfinalOffersObject.put(\"cost\", 1.0);\n\n\t\t\t\t/** Score based on model type */\n\t\t\t\tif (type.contains(\"clustering\")) {\n\t\t\t\t\tfinalOffersObject.put(\"cluster\", predictModelMojoResult.getJSONArray(\"cluster\").get(0));\n\t\t\t\t\tfinalOffersObject.put(\"score\", DataTypeConversions.getDouble(domainsProbabilityObj, \"score\"));\n\t\t\t\t\tfinalOffersObject.put(\"modified_offer_score\", DataTypeConversions.getDouble(domainsProbabilityObj, \"score\"));\n\t\t\t\t} else if (type.contains(\"anomalydetection\")) {\n\t\t\t\t\tdouble[] score = (double[]) domainsProbabilityObj.get(\"score\");\n\t\t\t\t\tfinalOffersObject.put(\"score\", score[0]);\n\t\t\t\t\tfinalOffersObject.put(\"modified_offer_score\", score[0]);\n\t\t\t\t} else if (type.contains(\"regression\")) {\n\t\t\t\t\tObject score = predictModelMojoResult.getJSONArray(\"value\").get(0);\n\t\t\t\t\tfinalOffersObject.put(\"score\", score);\n\t\t\t\t\tfinalOffersObject.put(\"modified_offer_score\", score);\n\t\t\t\t} else if (type.contains(\"multinomial\")) {\n\t\t\t\t\tObject probability = predictModelMojoResult.getJSONArray(\"probability\").get(0);\n\t\t\t\t\tObject label = null;\n\t\t\t\t\ttry {\n\t\t\t\t\t\tlabel = predictModelMojoResult.getJSONArray(\"label\").get(0);\n\t\t\t\t\t} catch (Exception e) {\n\t\t\t\t\t\tLOGGER.error(\"PostScoreBasic:getPostPredict:E001: Error relates to scoring your model. The model wasn't loaded or is not accessible.\");\n\t\t\t\t\t\te.printStackTrace();\n\t\t\t\t\t}\n\t\t\t\t\tObject response = predictModelMojoResult.getJSONArray(\"response\").get(0);\n\t\t\t\t\tfinalOffersObject.put(\"score\", probability);\n\t\t\t\t\tfinalOffersObject.put(\"modified_offer_score\", probability);\n\t\t\t\t\tfinalOffersObject.put(\"offer\", label);\n\t\t\t\t\tfinalOffersObject.put(\"offer_name\", response);\n\t\t\t\t} else if (type.contains(\"coxph\")) {\n\t\t\t\t\tObject score = predictModelMojoResult.getJSONArray(\"value\").get(0);\n\t\t\t\t\tfinalOffersObject.put(\"score\", score);\n\t\t\t\t\tfinalOffersObject.put(\"modified_offer_score\", score);\n\t\t\t\t} else if (type.contains(\"wordembedding\")) {\n\t\t\t\t\tfloat[] score = (float[]) predictModelMojoResult.getJSONArray(\"_text_word2vec\").get(0);\n\t\t\t\t\tfinalOffersObject.put(\"score\", Double.valueOf(String.valueOf(score[0])));\n\t\t\t\t\tfinalOffersObject.put(\"embedding\", score);\n\t\t\t\t\tfinalOffersObject.put(\"modified_offer_score\", 0.0);\n\t\t\t\t} else if (type.contains(\"deeplearning\")) {\n\t\t\t\t\t/** From TensorFlow or PyTorch */\n\t\t\t\t\tObject score = domainsProbabilityObj.getDouble(\"1\");\n\t\t\t\t\tfinalOffersObject.put(\"score\", score);\n\t\t\t\t\tfinalOffersObject.put(\"modified_offer_score\", score);\n\t\t\t\t\tObject response = predictModelMojoResult.getJSONArray(\"response\").get(0);\n\t\t\t\t\tfinalOffersObject.put(\"offer_name\", response);\n\t\t\t\t} else if (type.contains(\"empty score\")) {\n\t\t\t\t\t/** This is typically used for data lookup only, obtain values from feature store! */\n\t\t\t\t\tif (featuresObj.has(\"offer_name\"))\n\t\t\t\t\t\tfinalOffersObject.put(\"offer_name\", featuresObj.get(\"offer_name\"));\n\n\t\t\t\t\tif (featuresObj.has(\"offer\"))\n\t\t\t\t\t\tfinalOffersObject.put(\"offer\", featuresObj.get(\"offer\"));\n\n\t\t\t\t\tif (featuresObj.has(\"score\"))\n\t\t\t\t\t\tfinalOffersObject.put(\"score\", Double.valueOf(String.valueOf(featuresObj.get(\"score\"))));\n\t\t\t\t\telse\n\t\t\t\t\t\tfinalOffersObject.put(\"score\", 1.0);\n\n\t\t\t\t\tif (featuresObj.has(\"modified_offer_score\"))\n\t\t\t\t\t\tfinalOffersObject.put(\"modified_offer_score\", Double.valueOf(String.valueOf(featuresObj.get(\"modified_offer_score\"))));\n\t\t\t\t\telse\n\t\t\t\t\t\tfinalOffersObject.put(\"modified_offer_score\", 1.0);\n\n\t\t\t\t\tif (featuresObj.has(\"cost\"))\n\t\t\t\t\t\tfinalOffersObject.put(\"cost\", Double.valueOf(String.valueOf(featuresObj.get(\"cost\"))));\n\t\t\t\t\telse\n\t\t\t\t\t\tfinalOffersObject.put(\"cost\", 0.0);\n\n\t\t\t\t} else {\n\t\t\t\t\tfinalOffersObject.put(\"score\", 1.0);\n\t\t\t\t\tfinalOffersObject.put(\"modified_offer_score\", 1.0);\n\t\t\t\t}\n\n\t\t\t\tfinalOffersObject.put(\"offer_details\", domainsProbabilityObj);\n\t\t\t\tif (explainability) {\n\t\t\t\t\tfinalOffersObject.put(\"shapley_contributions\", predictModelMojoResult.get(\"shapley_contributions\"));\n\t\t\t\t\tfinalOffersObject.put(\"shapley_contributions_names\", predictModelMojoResult.get(\"shapley_contributions_names\"));\n\t\t\t\t}\n\n\t\t\t\t/** Default value, could be replaced by offer matrix or feature store */\n\t\t\t\tdouble offer_value = 1.0;\n\t\t\t\tfinalOffersObject.put(\"offer_value\", offer_value);\n\t\t\t\tfinalOffersObject.put(\"uuid\", params.get(\"uuid\"));\n\n\t\t\t\t/** Add other structures to the final result */\n\t\t\t\tfinalOffersObject.put(\"offer_matrix\", featuresObj);\n\n\t\t\t\t/** Budget processing option, if it's set in the properties */\n\t\t\t\tif (settings.getPredictorOfferBudget() != null) {\n\t\t\t\t\tJSONObject budgetItem = obtainBudget(featuresObj, params.getJSONObject(\"featuresObj\"), offer_value);\n\t\t\t\t\tdouble budgetSpendLimit = budgetItem.getDouble(\"spend_limit\");\n\t\t\t\t\tfinalOffersObject.put(\"spend_limit\", budgetSpendLimit);\n\t\t\t\t}\n\n\t\t\t\t/** Prepare offer array before final sorting */\n\t\t\t\tfinalOffers.put(offerIndex, finalOffersObject);\n\t\t\t\tofferIndex = offerIndex + 1;\n\t\t\t}\n\n\t\t\t/** Sort final offer list based on score */\n\t\t\tJSONArray sortJsonArray = JSONArraySort.sortArray(finalOffers, \"score\", \"double\", \"d\");\n\t\t\tpredictModelMojoResult.put(\"final_result\", sortJsonArray);\n\n\t\t} catch (Exception e) {\n\t\t\tLOGGER.error(e);\n\t\t}\n\n\t\t/** Get top scores and test for explore/exploit randomization */\n\t\tpredictModelMojoResult = getTopScores(params, predictModelMojoResult);\n\n\t\tdouble endTimePost = System.nanoTime();\n\t\tLOGGER.info(\"getPostPredict:I001: execution time in ms: \".concat( String.valueOf((endTimePost - startTimePost) / 1000000) ));\n\t\treturn predictModelMojoResult;\n\t}\n\n}\n",
        "PostScoreRecommender.java": "package com.ecosystem.plugin.customer;\n\nimport com.datastax.oss.driver.api.core.CqlSession;\nimport com.ecosystem.utils.GlobalSettings;\nimport com.ecosystem.utils.JSONArraySort;\nimport com.ecosystem.utils.MathRandomizer;\nimport hex.genmodel.easy.EasyPredictModelWrapper;\nimport com.ecosystem.utils.log.LogManager;\nimport com.ecosystem.utils.log.Logger;\nimport org.json.JSONArray;\nimport org.json.JSONObject;\n\nimport java.io.IOException;\n\n/**\n * ECOSYSTEM.AI INTERNAL PLATFORM SCORING\n * Use this class to perform generic scoring based on model and generic settings with label from scoring.\n */\npublic class PostScoreRecommender {\n\tprivate static final Logger LOGGER = LogManager.getLogger(PostScoreRecommender.class.getName());\n\n\tstatic GlobalSettings settings;\n\tstatic {\n\t\ttry {\n\t\t\tsettings = new GlobalSettings();\n\t\t} catch (IOException e) {\n\t\t\te.printStackTrace();\n\t\t} catch (Exception e) {\n\t\t\te.printStackTrace();\n\t\t}\n\t}\n\n\tpublic PostScoreRecommender() {\n\t}\n\n\t/**\n\t * Pre-post predict logic\n\t */\n\tpublic void getPostPredict () {\n\t}\n\n\t/**\n\t * getPostPredict\n\t * Example params:\n\t *    {\"contextual_variable_one\":\"Easy Income Gold|Thin|Senior\", \"contextual_variable_two\":\"\", \"batch\": true}\n\t *\n\t * @param predictModelMojoResult Result from scoring\n\t * @param params                 Params carried from input\n\t * @param session                Session variable for Cassandra\n\t * @return JSONObject result to further post-scoring logic\n\t */\n\tpublic static JSONObject getPostPredict(JSONObject predictModelMojoResult, JSONObject params, CqlSession session, EasyPredictModelWrapper[] models) {\n\t\tdouble startTimePost = System.nanoTime();\n\t\ttry {\n\t\t\t/* Setup JSON objects for specific prediction case */\n\t\t\tJSONObject featuresObj = predictModelMojoResult.getJSONObject(\"featuresObj\");\n\t\t\tif (predictModelMojoResult.has(\"ErrorMessage\")) {\n\t\t\t\tLOGGER.error(\"getPostPredict:E001a:\" + predictModelMojoResult.get(\"ErrorMessage\"));\n\t\t\t\treturn null;\n\t\t\t}\n\n\t\t\tJSONArray offerMatrix = new JSONArray();\n\t\t\tif (params.has(\"offerMatrix\"))\n\t\t\t\tofferMatrix = params.getJSONArray(\"offerMatrix\");\n\n\t\t\tJSONObject work = params.getJSONObject(\"in_params\");\n\n\t\t\tJSONObject domainsProbabilityObj = predictModelMojoResult.getJSONObject(\"domainsProbabilityObj\");\n\t\t\tString label = predictModelMojoResult.getJSONArray(\"label\").getString(0);\n\n\t\t\tJSONArray probabilities = new JSONArray();\n\t\t\tif (predictModelMojoResult.has(\"probability\"))\n\t\t\t\tprobabilities = predictModelMojoResult.getJSONArray(\"probability\");\n\t\t\telse\n\t\t\t\tprobabilities = predictModelMojoResult.getJSONArray(\"probabilities\");\n\n\t\t\tJSONArray domains = predictModelMojoResult.getJSONArray(\"domains\");\n\n\t\t\tJSONArray finalOffers = new JSONArray();\n\t\t\tint resultcount = (int) params.get(\"resultcount\");\n\t\t\tint offerIndex = 0;\n\n\t\t\t/** Select top items based on number of offers to present */\n\t\t\tfor (int i = 0; i < resultcount; i++) {\n\t\t\t\tint explore = (int) params.get(\"explore\");\n\t\t\t\tJSONObject finalOffersObject = new JSONObject();\n\n\t\t\t\tfinalOffersObject.put(\"offer\", label);\n\t\t\t\tfinalOffersObject.put(\"offer_name\", label);\n\t\t\t\tfinalOffersObject.put(\"offer_name_desc\", label + \" - \" + i);\n\n\t\t\t\t/** process final */\n\t\t\t\tdouble p = domainsProbabilityObj.getDouble(label);\n\t\t\t\tfinalOffersObject.put(\"score\", p);\n\t\t\t\tfinalOffersObject.put(\"final_score\", p);\n\t\t\t\tfinalOffersObject.put(\"modified_offer_score\", p);\n\t\t\t\tfinalOffersObject.put(\"offer_value\", 1.0); // use value from offer matrix\n\t\t\t\tfinalOffersObject.put(\"price\", 1.0);\n\t\t\t\tfinalOffersObject.put(\"cost\", 1.0);\n\n\t\t\t\tfinalOffersObject.put(\"p\", p);\n\t\t\t\tfinalOffersObject.put(\"explore\", explore);\n\n\t\t\t\t/** Prepare array before final sort */\n\t\t\t\tfinalOffers.put(offerIndex, finalOffersObject);\n\t\t\t\tofferIndex = offerIndex + 1;\n\t\t\t}\n\n\t\t\tJSONArray sortJsonArray = JSONArraySort.sortArray(finalOffers, \"score\", \"double\", \"d\");\n\t\t\tpredictModelMojoResult.put(\"final_result\", sortJsonArray);\n\n\t\t} catch (Exception e) {\n\t\t\te.printStackTrace();\n\t\t\tLOGGER.error(e);\n\t\t}\n\n\t\tpredictModelMojoResult = getTopScores(params, predictModelMojoResult);\n\n\t\tdouble endTimePost = System.nanoTime();\n\t\tLOGGER.info(\"PlatformDynamicEngagement:I001: time in ms: \".concat( String.valueOf((endTimePost - startTimePost) / 1000000) ));\n\n\t\treturn predictModelMojoResult;\n\n\t}\n\n\tprivate static JSONObject getExplore(JSONObject params, double epsilonIn, String name) {\n\t\tdouble rand = MathRandomizer.getRandomDoubleBetweenRange(0, 1);\n\t\tdouble epsilon = epsilonIn;\n\t\tparams.put(name + \"_epsilon\", epsilon);\n\t\tif (rand <= epsilon) {\n\t\t\tparams.put(name, 1);\n\t\t} else {\n\t\t\tparams.put(name, 0);\n\t\t}\n\t\treturn params;\n\t}\n\n\t/**\n\t * Get random results for MAB\n\t * @param predictResult\n\t * @param numberOffers\n\t * @return\n\t */\n\tpublic static JSONArray getSelectedPredictResultRandom(JSONObject predictResult, int numberOffers) {\n\t\treturn getSelectedPredictResultExploreExploit(predictResult, numberOffers, 1);\n\t}\n\n\t/**\n\t * Get result based on score\n\t * @param predictResult\n\t * @param numberOffers\n\t * @return\n\t */\n\tpublic static JSONArray getSelectedPredictResult(JSONObject predictResult, int numberOffers) {\n\t\treturn getSelectedPredictResultExploreExploit(predictResult, numberOffers, 0);\n\t}\n\n\tprivate static JSONObject setValues(JSONObject work) {\n\t\tJSONObject result = new JSONObject();\n\t\tresult.put(\"score\", work.get(\"score\"));\n\t\tif (work.has(\"price\"))\n\t\t\tresult.put(\"price\", work.get(\"price\"));\n\t\tif (work.has(\"cost\"))\n\t\t\tresult.put(\"cost\", work.get(\"cost\"));\n\t\tresult.put(\"final_score\", work.get(\"score\"));\n\t\tresult.put(\"offer\", work.get(\"offer\"));\n\t\tresult.put(\"offer_name\", work.get(\"offer_name\"));\n\t\tresult.put(\"modified_offer_score\", work.get(\"modified_offer_score\"));\n\t\tresult.put(\"offer_value\", work.get(\"offer_value\"));\n\t\treturn result;\n\t}\n\n\t/**\n\t * Set values JSONObject that will be used in final\n\t * @param work\n\t * @param rank\n\t * @return\n\t */\n\tprivate static JSONObject setValuesFinal(JSONObject work, int rank) {\n\t\tJSONObject offer = new JSONObject();\n\n\t\toffer.put(\"rank\", rank);\n\t\toffer.put(\"result\", setValues(work));\n\t\toffer.put(\"result_full\", work);\n\n\t\treturn offer;\n\t}\n\n\t/**\n\t * Review this: Master version in EcosystemMaster class. {offer_treatment_code: {$regex:\"_A\"}}\n\t *\n\t * @param predictResult\n\t * @param numberOffers\n\t * @return\n\t */\n\tpublic static JSONArray getSelectedPredictResultExploreExploit(JSONObject predictResult, int numberOffers, int explore) {\n\t\tJSONArray offers = new JSONArray();\n\t\tint resultLength = predictResult.getJSONArray(\"final_result\").length();\n\n\t\tfor (int j = 0, k = 0; j < resultLength; j++) {\n\t\t\tJSONObject work = new JSONObject();\n\t\t\tif (explore == 1) {\n\t\t\t\tint rand = MathRandomizer.getRandomIntBetweenRange(0, resultLength - 1);\n\t\t\t\twork = predictResult.getJSONArray(\"final_result\").getJSONObject(rand);\n\t\t\t} else {\n\t\t\t\twork = predictResult.getJSONArray(\"final_result\").getJSONObject(j);\n\t\t\t}\n\n\t\t\t/* test if budget is enabled && spend_limit is greater than 0, if budget is disabled, then this will be 1.0 */\n\t\t\tif (settings.getPredictorOfferBudget() != null) {\n\t\t\t\t/* if budget setting and there is budget to spend */\n\t\t\t\tif (work.has(\"spend_limit\")) {\n\t\t\t\t\tif ((work.getDouble(\"spend_limit\") > 0.0) | work.getDouble(\"spend_limit\") == -1) {\n\t\t\t\t\t\toffers.put(k, setValuesFinal(work, k + 1));\n\t\t\t\t\t\tif ((k + 1) == numberOffers) break;\n\t\t\t\t\t\tk = k + 1;\n\t\t\t\t\t}\n\t\t\t\t} else {\n\t\t\t\t\tbreak;\n\t\t\t\t}\n\t\t\t} else {\n\t\t\t\t/* no budget setting present */\n\t\t\t\toffers.put(k, setValuesFinal(work, k + 1));\n\t\t\t\tif ((k + 1) == numberOffers) break;\n\t\t\t\tk = k + 1;\n\t\t\t}\n\t\t}\n\n\t\treturn offers;\n\t}\n\n\t/**\n\t * @param params\n\t * @param predictResult\n\t * @return\n\t */\n\tprivate static JSONObject getTopScores(JSONObject params, JSONObject predictResult) {\n\t\tint resultCount = 1;\n\t\tif (params.has(\"resultcount\")) resultCount = params.getInt(\"resultcount\");\n\t\tif (predictResult.getJSONArray(\"final_result\").length() <= resultCount)\n\t\t\tresultCount = predictResult.getJSONArray(\"final_result\").length();\n\n\t\t/* depending on epsilon and mab settings */\n\t\tif (params.getInt(\"explore\") == 0) {\n\t\t\tpredictResult.put(\"final_result\", getSelectedPredictResult(predictResult, resultCount));\n\t\t\tpredictResult.put(\"explore\", 0);\n\t\t} else {\n\t\t\tpredictResult.put(\"final_result\", getSelectedPredictResultRandom(predictResult, resultCount));\n\t\t\tpredictResult.put(\"explore\", 1);\n\t\t}\n\t\treturn predictResult;\n\t}\n\n}\n",
        "PostScoreRecommenderOffers.java": "package com.ecosystem.plugin.customer;\n\nimport com.datastax.oss.driver.api.core.CqlSession;\nimport com.ecosystem.utils.DataTypeConversions;\nimport com.ecosystem.utils.JSONArraySort;\nimport hex.genmodel.easy.EasyPredictModelWrapper;\nimport com.ecosystem.utils.log.LogManager;\nimport com.ecosystem.utils.log.Logger;\nimport org.json.JSONArray;\nimport org.json.JSONObject;\n\n/**\n * recommender_smp - Single model for all products with Offermatrix\n * Multiclass classifier trained on offer_name response column, offer matrix need to have all the offers loaded with offer_price.\n */\npublic class PostScoreRecommenderOffers extends PostScoreSuper {\n    private static final Logger LOGGER = LogManager.getLogger(PostScoreRecommenderOffers.class.getName());\n\n    public PostScoreRecommenderOffers() {\n    }\n\n    /**\n     * Pre-post predict logic\n     */\n    public void getPostPredict () {\n    }\n\n    /**\n     * getPostPredict\n     *\n     * @param predictModelMojoResult Result from scoring\n     * @param params                 Params carried from input\n     * @param session                Session variable for Cassandra\n     * @return JSONObject result to further post-scoring logic\n     */\n    public static JSONObject getPostPredict(JSONObject predictModelMojoResult, JSONObject params, CqlSession session, EasyPredictModelWrapper[] models) {\n        double startTimePost = System.nanoTime();\n        try {\n            /** Value obtained via API params */\n            JSONObject work = params.getJSONObject(\"in_params\");\n            double in_balance = 1000.0;\n            if (work.has(\"in_balance\"))\n                in_balance = DataTypeConversions.getDouble(work, \"in_balance\");\n            else\n                LOGGER.info(\"getPostPredict:I001aa: No in_balance specified, default used. (1000.00)\");\n\n            JSONArray sortJsonArray = new JSONArray();\n            JSONArray finalOffers = new JSONArray();\n\n            /* Setup JSON objects for specific prediction case */\n            JSONObject featuresObj = predictModelMojoResult.getJSONObject(\"featuresObj\");\n            if (predictModelMojoResult.has(\"ErrorMessage\")) {\n                LOGGER.error(\"getPostPredict:E001a:\" + predictModelMojoResult.get(\"ErrorMessage\"));\n                return null;\n            }\n\n            JSONArray offerMatrix = new JSONArray();\n            if (params.has(\"offerMatrix\"))\n                offerMatrix = params.getJSONArray(\"offerMatrix\");\n\n            JSONObject domainsProbabilityObj = predictModelMojoResult.getJSONObject(\"domainsProbabilityObj\");\n            String label = predictModelMojoResult.getJSONArray(\"label\").getString(0);\n            JSONArray domains = predictModelMojoResult.getJSONArray(\"domains\");\n\n            int resultcount = (int) params.get(\"resultcount\");\n            int offerIndex = 0;\n\n            /** Select top items based on number of offers to present */\n            for (int i = 0; i < offerMatrix.length(); i++) {\n                JSONObject singleOffer = offerMatrix.getJSONObject(i);\n\n                int explore = (int) params.get(\"explore\");\n                JSONObject finalOffersObject = new JSONObject();\n\n                double offer_value = 1.0;\n                if (singleOffer.has(\"offer_price\"))\n                    offer_value = DataTypeConversions.getDouble(singleOffer, \"offer_price\");\n                if (singleOffer.has(\"price\"))\n                    offer_value = DataTypeConversions.getDouble(singleOffer, \"price\");\n\n                double offer_cost = 1.0;\n                if (singleOffer.has(\"offer_cost\"))\n                    offer_cost = singleOffer.getDouble(\"offer_cost\");\n                if (singleOffer.has(\"cost\"))\n                    offer_cost = singleOffer.getDouble(\"cost\");\n\n                double p = 0.0;\n                String offer_id = \"\";\n                if (domainsProbabilityObj.has(singleOffer.getString(\"offer_id\"))) {\n                    offer_id = singleOffer.getString(\"offer_id\");\n                    p = domainsProbabilityObj.getDouble(offer_id);\n                } else {\n                    LOGGER.error(\"offerRecommender:E002-1: \" + params.get(\"uuid\") + \" - Not available: \" + singleOffer.getString(\"offer_name\"));\n                }\n\n                double modified_offer_score = 1.0;\n                modified_offer_score = p * ((double) offer_value - offer_cost);\n\n                finalOffersObject.put(\"offer\", offer_id);\n                finalOffersObject.put(\"offer_name\", singleOffer.get(\"offer_name\"));\n                finalOffersObject.put(\"offer_name_desc\", singleOffer.get(\"offer_name\") + \" - \" + i);\n\n                /** process final */\n                // double p = domainsProbabilityObj.getDouble(label);\n                finalOffersObject.put(\"score\", p);\n                finalOffersObject.put(\"final_score\", p);\n                finalOffersObject.put(\"modified_offer_score\", modified_offer_score);\n                finalOffersObject.put(\"offer_value\", offer_value); // use value from offer matrix\n                finalOffersObject.put(\"price\", offer_value);\n                finalOffersObject.put(\"cost\", offer_cost);\n                finalOffersObject.put(\"uuid\", params.get(\"uuid\"));\n\n                finalOffersObject.put(\"p\", p);\n                finalOffersObject.put(\"explore\", explore);\n\n                /** Prepare array before final sort */\n                finalOffers.put(offerIndex, finalOffersObject);\n                offerIndex = offerIndex + 1;\n            }\n\n            sortJsonArray = JSONArraySort.sortArray(finalOffers, \"modified_offer_score\", \"double\", \"d\");\n            predictModelMojoResult.put(\"final_result\", sortJsonArray);\n\n            /** Select the correct number of offers */\n            predictModelMojoResult = getTopScores(params, predictModelMojoResult);\n\n        } catch (Exception e) {\n            e.printStackTrace();\n            LOGGER.error(e);\n        }\n\n        /** Top scores from final_result */\n        predictModelMojoResult = getTopScores(params, predictModelMojoResult);\n\n        double endTimePost = System.nanoTime();\n        LOGGER.info(\"PostScoreRecommenderOffers:I001: time in ms: \".concat( String.valueOf((endTimePost - startTimePost) / 1000000) ));\n\n        return predictModelMojoResult;\n\n    }\n\n}\n",
        "PostScoreRecommenderMulti.java": "package com.ecosystem.plugin.customer;\n\nimport com.datastax.oss.driver.api.core.CqlSession;\nimport com.ecosystem.plugin.lib.ScoreAsyncItems;\nimport com.ecosystem.utils.DataTypeConversions;\nimport com.ecosystem.utils.GlobalSettings;\nimport com.ecosystem.utils.JSONArraySort;\nimport com.ecosystem.utils.MathRandomizer;\nimport com.ecosystem.worker.h2o.ModelPredictWorkerH2O;\nimport hex.genmodel.easy.EasyPredictModelWrapper;\nimport hex.genmodel.easy.RowData;\nimport com.ecosystem.utils.log.LogManager;\nimport com.ecosystem.utils.log.Logger;\nimport org.json.JSONArray;\nimport org.json.JSONObject;\n\nimport java.io.IOException;\nimport java.util.concurrent.ExecutionException;\n\n/**\n * recommender_smp - Multiple models for per product with Offermatrix\n * Binomial model per product, all loaded into memory, scoring per offerMatrix line item.\n */\npublic class PostScoreRecommenderMulti {\n\n    private static final Logger LOGGER = LogManager.getLogger(PostScoreRecommenderMulti.class.getName());\n\n    ModelPredictWorkerH2O modelPredictWorkerH2O;\n    ScoreAsyncItems scoreAsyncItems;\n\n    static GlobalSettings settings;\n    static {\n        try {\n            settings = new GlobalSettings();\n        } catch (IOException e) {\n            e.printStackTrace();\n        } catch (Exception e) {\n            e.printStackTrace();\n        }\n    }\n\n    public PostScoreRecommenderMulti() {\n        modelPredictWorkerH2O = new ModelPredictWorkerH2O();\n        scoreAsyncItems = new ScoreAsyncItems(modelPredictWorkerH2O);\n    }\n\n    /**\n     * Pre-post predict logic\n     */\n    public void getPostPredict () {\n    }\n\n    /**\n     * getPostPredict\n     *\n     * @param predictModelMojoResult Result from scoring\n     * @param params                 Params carried from input\n     * @param session                Session variable for Cassandra\n     * @return JSONObject result to further post-scoring logic\n     */\n    public JSONObject getPostPredict(JSONObject predictModelMojoResult, JSONObject params, CqlSession session, EasyPredictModelWrapper[] models) {\n\n        double startTimePost = System.nanoTime();\n\n        /** Value obtained via API params */\n        JSONObject work = params.getJSONObject(\"in_params\");\n        double in_balance = 100.0;\n        if (work.has(\"in_balance\"))\n            in_balance = DataTypeConversions.getDouble(work, \"in_balance\");\n        else\n            LOGGER.info(\"getPostPredict:I001aa: No in_balance specified, default used. (1000.00)\");\n\n        JSONArray finalOffers = new JSONArray();\n\n        /* Setup JSON objects for specific prediction case */\n        JSONObject featuresObj = predictModelMojoResult.getJSONObject(\"featuresObj\");\n        if (predictModelMojoResult.has(\"ErrorMessage\")) {\n            LOGGER.error(\"getPostPredict:E001a:\" + predictModelMojoResult.get(\"ErrorMessage\"));\n            return null;\n        }\n\n        JSONArray offerMatrix = new JSONArray();\n        if (params.has(\"offerMatrix\"))\n            offerMatrix = params.getJSONArray(\"offerMatrix\");\n\n        // JSONObject domainsProbabilityObj = predictModelMojoResult.getJSONObject(\"domainsProbabilityObj\");\n        // String label = predictModelMojoResult.getJSONArray(\"label\").getString(0);\n        // JSONArray domains = predictModelMojoResult.getJSONArray(\"domains\");\n\n        int resultcount = (int) params.get(\"resultcount\");\n        int offerIndex = 0;\n\n        /** Async processing scoring across all models loaded per offer */\n        JSONObject domainsProbabilityObj = new JSONObject();\n        if (predictModelMojoResult.has(\"domainsProbabilityObj\"))\n            domainsProbabilityObj = predictModelMojoResult.getJSONObject(\"domainsProbabilityObj\");\n\n        JSONObject resultScore = new JSONObject();\n        try {\n            double startTimePost1 = System.nanoTime();\n\n            RowData row = modelPredictWorkerH2O.toRowData((JSONObject) predictModelMojoResult.get(\"features\"));\n            resultScore = scoreAsyncItems.allOfAsyncScoring(offerMatrix, params, models, row, domainsProbabilityObj);\n\n            double endTimePost1 = System.nanoTime();\n            LOGGER.info(\"scoreAsyncItems.allOfAsyncScoring:I0001a: Async process time in ms: \".concat( String.valueOf((double) ((endTimePost1 - startTimePost1) / 1000000)) ));\n        } catch (ExecutionException e) {\n            e.printStackTrace();\n        } catch (InterruptedException e) {\n            e.printStackTrace();\n        }\n\n        /** All items are excluded that are not active and no scores */\n        offerMatrix = resultScore.getJSONArray(\"newOfferMatrix\");\n\n        /** Select top items based on number of offers to present */\n        for (int i = 0; i < offerMatrix.length(); i++) {\n            JSONObject singleOffer = offerMatrix.getJSONObject(i);\n            String offer_id = String.valueOf(singleOffer.get(\"offer_id\"));\n\n            LOGGER.debug(\"singleOffer:D001-1: \" + singleOffer.toString());\n            LOGGER.debug(\"singleOffer:offer_id:D001-2: \" + offer_id);\n\n            /** Offer matrix needs item \"price\" for aggregator to work! */\n            double offer_price = 1.0;\n            if (singleOffer.has(\"offer_price\"))\n                offer_price = DataTypeConversions.getDouble(singleOffer, \"offer_price\");\n            else if (singleOffer.has(\"price\"))\n                offer_price = DataTypeConversions.getDouble(singleOffer, \"price\");\n            else\n                LOGGER.error(\"PostScoreRecommenderMultiSafaricom:E0011: price not in offerMatrix, value set to 1\");\n\n            double offer_cost = 1.0;\n            if (singleOffer.has(\"offer_cost\"))\n                offer_cost = singleOffer.getDouble(\"offer_cost\");\n            if (singleOffer.has(\"cost\"))\n                offer_cost = singleOffer.getDouble(\"cost\");\n\n            int explore = (int) params.get(\"explore\");\n            JSONObject finalOffersObject = new JSONObject();\n\n            offer_id = DataTypeConversions.getString(singleOffer.getString(\"offer_id\"));\n\n            /*******************************************************************************/\n\n            double p = resultScore.getDouble(offer_id);\n\n            /*******************************************************************************/\n\n            /** Multi-model needs to store the model for logging - DO NOT REMOVE THIS!*/\n            finalOffersObject.put(\"model_name\", offer_id + \".zip\");\n            finalOffersObject.put(\"model_index\", resultScore.get(offer_id + \"_model_index\"));\n\n            finalOffersObject.put(\"offer\", singleOffer.get(\"offer_id\"));\n            finalOffersObject.put(\"offer_name\", singleOffer.get(\"offer_name\"));\n            // finalOffersObject.put(\"offer_name_desc\", offer_name + \" - \" + i);\n\n            /** process final */\n            // double p = domainsProbabilityObj.getDouble(label);\n            finalOffersObject.put(\"score\", p);\n            finalOffersObject.put(\"final_score\", p);\n            finalOffersObject.put(\"modified_offer_score\", p);\n            finalOffersObject.put(\"offer_value\", offer_price); // use value from offer matrix\n            // finalOffersObject.put(\"offer_profit_probability\", offer_profit * p);\n            finalOffersObject.put(\"price\", offer_price);\n            finalOffersObject.put(\"cost\", offer_cost);\n\n            finalOffersObject.put(\"p\", p);\n            finalOffersObject.put(\"explore\", explore);\n\n            /** Prepare array before final sort */\n            finalOffers.put(offerIndex, finalOffersObject);\n            offerIndex = offerIndex + 1;\n        }\n\n        JSONArray sortJsonArray = JSONArraySort.sortArray(finalOffers, \"score\", \"double\", \"d\");\n        predictModelMojoResult.put(\"final_result\", sortJsonArray);\n\n        predictModelMojoResult = getTopScores(params, predictModelMojoResult);\n\n        /** Multi-model needs to store the model for logging! - DO NOT REMOVE THIS! */\n        if (sortJsonArray.length() > 0) {\n            if (sortJsonArray.getJSONObject(0).has(\"model_index\")) {\n                String model_name = (String) sortJsonArray.getJSONObject(0).get(\"model_name\");\n                params.put(\"model_selected\", model_name);\n            }\n        } else {\n            LOGGER.error(\"PostScoreRecommenderMulti:E999: No result \");\n        }\n\n        double endTimePost = System.nanoTime();\n        LOGGER.info(\"PostScoreRecommenderMulti:I001: time in ms: \".concat( String.valueOf((endTimePost - startTimePost) / 1000000) ));\n\n        return predictModelMojoResult;\n\n    }\n\n    private static JSONObject getExplore(JSONObject params, double epsilonIn, String name) {\n        double rand = MathRandomizer.getRandomDoubleBetweenRange(0, 1);\n        double epsilon = epsilonIn;\n        params.put(name + \"_epsilon\", epsilon);\n        if (rand <= epsilon) {\n            params.put(name, 1);\n        } else {\n            params.put(name, 0);\n        }\n        return params;\n    }\n\n\n    /**\n     * Get random results for MAB\n     * @param predictResult\n     * @param numberOffers\n     * @return\n     */\n    public static JSONArray getSelectedPredictResultRandom(JSONObject predictResult, int numberOffers) {\n        return getSelectedPredictResultExploreExploit(predictResult, numberOffers, 1);\n    }\n\n    /**\n     * Get result based on score\n     * @param predictResult\n     * @param numberOffers\n     * @return\n     */\n    public static JSONArray getSelectedPredictResult(JSONObject predictResult, int numberOffers) {\n        return getSelectedPredictResultExploreExploit(predictResult, numberOffers, 0);\n    }\n\n    private static JSONObject setValues(JSONObject work) {\n        JSONObject result = new JSONObject();\n        result.put(\"score\", work.get(\"score\"));\n        if (work.has(\"price\"))\n            result.put(\"price\", work.get(\"price\"));\n        if (work.has(\"cost\"))\n            result.put(\"cost\", work.get(\"cost\"));\n        result.put(\"final_score\", work.get(\"score\"));\n        result.put(\"offer\", work.get(\"offer\"));\n        result.put(\"offer_name\", work.get(\"offer_name\"));\n        result.put(\"modified_offer_score\", work.get(\"modified_offer_score\"));\n        result.put(\"offer_value\", work.get(\"offer_value\"));\n        return result;\n    }\n\n    /**\n     * Set values JSONObject that will be used in final\n     * @param work\n     * @param rank\n     * @return\n     */\n    private static JSONObject setValuesFinal(JSONObject work, int rank) {\n        JSONObject offer = new JSONObject();\n\n        offer.put(\"rank\", rank);\n        offer.put(\"result\", setValues(work));\n        offer.put(\"result_full\", work);\n\n        return offer;\n    }\n\n\n    /**\n     * Review this: Master version in EcosystemMaster class. {offer_treatment_code: {$regex:\"_A\"}}\n     *\n     * @param predictResult\n     * @param numberOffers\n     * @return\n     */\n    public static JSONArray getSelectedPredictResultExploreExploit(JSONObject predictResult, int numberOffers, int explore) {\n        JSONArray offers = new JSONArray();\n        int resultLength = predictResult.getJSONArray(\"final_result\").length();\n\n        for (int j = 0, k = 0; j < resultLength; j++) {\n            JSONObject work = new JSONObject();\n            if (explore == 1) {\n                int rand = MathRandomizer.getRandomIntBetweenRange(0, resultLength - 1);\n                work = predictResult.getJSONArray(\"final_result\").getJSONObject(rand);\n            } else {\n                work = predictResult.getJSONArray(\"final_result\").getJSONObject(j);\n            }\n\n            /* test if budget is enabled && spend_limit is greater than 0, if budget is disabled, then this will be 1.0 */\n            if (settings.getPredictorOfferBudget() != null) {\n                /* if budget setting and there is budget to spend */\n                if (work.has(\"spend_limit\")) {\n                    if ((work.getDouble(\"spend_limit\") > 0.0) | work.getDouble(\"spend_limit\") == -1) {\n                        offers.put(k, setValuesFinal(work, k + 1));\n                        if ((k + 1) == numberOffers) break;\n                        k = k + 1;\n                    }\n                } else {\n                    break;\n                }\n            } else {\n                /* no budget setting present */\n                offers.put(k, setValuesFinal(work, k + 1));\n                if ((k + 1) == numberOffers) break;\n                k = k + 1;\n            }\n        }\n\n        return offers;\n    }\n\n    /**\n     * @param params\n     * @param predictResult\n     * @return\n     */\n    private static JSONObject getTopScores(JSONObject params, JSONObject predictResult) {\n        int resultCount = 1;\n        if (params.has(\"resultcount\")) resultCount = params.getInt(\"resultcount\");\n        if (predictResult.getJSONArray(\"final_result\").length() <= resultCount)\n            resultCount = predictResult.getJSONArray(\"final_result\").length();\n\n        /* depending on epsilon and mab settings */\n        if (params.getInt(\"explore\") == 0) {\n            predictResult.put(\"final_result\", getSelectedPredictResult(predictResult, resultCount));\n            predictResult.put(\"explore\", 0);\n        } else {\n            predictResult.put(\"final_result\", getSelectedPredictResultRandom(predictResult, resultCount));\n            predictResult.put(\"explore\", 1);\n        }\n        return predictResult;\n    }\n\n}\n",
        "PostScoreNetwork.java": "package com.ecosystem.plugin.customer;\n\nimport com.datastax.oss.driver.api.core.CqlSession;\nimport hex.genmodel.easy.EasyPredictModelWrapper;\nimport com.ecosystem.utils.log.LogManager;\nimport com.ecosystem.utils.log.Logger;\nimport org.json.JSONArray;\nimport org.json.JSONObject;\n\n/**\n */\npublic class PostScoreNetwork extends PostScoreNetworkSuper {\n\n    private static final Logger LOGGER = LogManager.getLogger(PostScoreNetwork.class.getName());\n\n    public PostScoreNetwork() {\n    }\n\n    /**\n     * Pre-post predict logic\n     */\n    public void getPostPredict () {\n    }\n\n    /**\n     * getPostPredict\n     *\n     * @param predictModelMojoResult Result from scoring\n     * @param params                 Params carried from input\n     * @param session                Session variable for Cassandra\n     * @param models                  Preloaded H2O Models\n     * @return JSONObject result to further post-scoring logic\n     */\n    public static JSONObject getPostPredict(JSONObject predictModelMojoResult, JSONObject params, CqlSession session, EasyPredictModelWrapper[] models) {\n        double startTimePost = System.nanoTime();\n        try {\n            /* Setup JSON objects for specific prediction case */\n            JSONObject featuresObj = predictModelMojoResult.getJSONObject(\"featuresObj\");\n\n            /** Final offer list based on score */\n            JSONArray sortJsonArray = new JSONArray();\n\n            /** Execute network based on settings in corpora */\n            /**\n             * Configure a network of client pulse responders bu changing configuration based on lookup, scoring and\n             * other criteria. Ensure that the lookup settings coordinate and that default have been set or removed.\n             * Example, if there's a customer, or other settings in the __network collection, it will use those.\n             * If you want customer to go straight through, then remove that default.\n             *\n             * Additional corpora settings in project:\n             * [\n             * {name:'network',database:'mongodb',db:'master',table:'bank_full_1__network', type:'static', key:'value' },\n             * {name:'network_config',database:'mongodb',db:'master',table:'bank_full_1__network_config', type:'static', key:'name' }\n             * ]\n             * Add this line to \"Additional Corpora\" in your project:\n             * [{name:'network',database:'mongodb',db:'master',table:'bank_full_1__network', type:'static', key:'value' },{name:'network_config',database:'mongodb',db:'master',table:'bank_full_1__network_config', type:'static', key:'name' }]\n             *\n             * bank_full_1__network_config, ensure that this document contains this: \"name\": \"network_config\":\n             * {\n             *   \"switch_key\": \"marital\",\n             *   \"name\": \"network_config\"\n             * }\n             *\n             *\n             * bank_full_1__network, all options will be setup here. Ensure that \"value\": \"\" contains a valid value as per switch_key:\n             * {\n             *   \"numberoffers\": 4,\n             *   \"subcampaign\": \"recommender_dynamic_bayes\",\n             *   \"channel\": \"app\",\n             *   \"campaign\": \"recommender_dynamic_bayes\",\n             *   \"params\": \"{}\",\n             *   \"value\": \"married\",\n             *   \"userid\": \"ecosystem_network\",\n             *   \"url\": \"http://customer.ecosystem.ai:8091\",\n             *   \"customer\": \"281db655-d667-4671-a715-8402c29d7d11\"\n             * }\n             */\n            sortJsonArray = handlePreloadCorpora(params, featuresObj);\n\n            predictModelMojoResult.put(\"final_result\", sortJsonArray);\n\n        } catch (Exception e) {\n            LOGGER.error(\"PostScoreNetwork:E001: \" + e);\n        }\n\n        /** Get top scores and test for explore/exploit randomization */\n        predictModelMojoResult = getTopScores(params, predictModelMojoResult);\n\n        double endTimePost = System.nanoTime();\n        LOGGER.info(\"PostScoreNetwork:I001: execution time in ms: \".concat( String.valueOf((endTimePost - startTimePost) / 1000000) ));\n        return predictModelMojoResult;\n    }\n\n}\n",
    }
    version_list = [i["version"] for i in project_details["deployment_step"] if i["plugins"]["post_score_class_text"] == post_score]
    if version_list:
        max_version = max(version_list)
        post_score_logic = [i["plugins"]["post_score_class_code"] for i in project_details["deployment_step"] if
                        (i["plugins"]["post_score_class_text"] == post_score and i["version"] == max_version)][0]
    elif post_score in post_score_code_options:
        post_score_logic = post_score_code_options[post_score]
    else:
        print(
            "WARNING: post_score_class not found in default options or existing deployments in project. Empty class saved to the deployment. To edit the class use the ecosystem.Ai plugin for IntelliJ or the ecosystem.Ai workbench")
        post_score_logic = ""
    return post_score_logic

def create_deployment(
        auth,
        project_id,
        deployment_id,
        description,
        plugin_pre_score_class,
        plugin_post_score_class,
        version,
        project_status,
        budget_tracker="default",
        complexity="Low",
        performance_expectation="High",
        model_configuration="default",
        setup_offer_matrix="default",
        multi_armed_bandit="default",
        whitelist="default",
        model_selector="default",
        pattern_selector="default",
        logging_collection_response="ecosystemruntime_response",
        logging_collection="ecosystemruntime",
        logging_database="logging",
        mongo_connect="mongodb://ecosystem_user:EcoEco321@ecosystem-server:54445/?authSource=admin",
        mongo_server_port="ecosystem-server:54445",
        mongo_ecosystem_password="EcoEco321",
        mongo_ecosystem_user="ecosystem_user",
        scoring_engine_path_dev="http://ecosystem-runtime:8091",
        scoring_engine_path_test="http://ecosystem-runtime2:8091",
        scoring_engine_path_prod="http://ecosystem-runtime3:8091",
        models_path="/data/deployed/",
        data_path="/data/",
        build_server_path="",
        git_repo_path_branch="",
        download_path="",
        git_repo_path="",
        parameter_access="default",
        corpora="default",
        extensive_validation=False
):
    #######################################################################################################################
    # Check inputs have the required format and get default values where relevant
    #######################################################################################################################
    # Get prediction project details and check that project exists
    try:
        project_details = pe.get_prediction_project(auth, project_id)
    except JSONDecodeError as error:
        raise ValueError(
            "No project found with the given project ID. Please create your project before allocating deployments to it") from error

    # Get the dynamic confiugration details and check that the dynamic configuration exists
    if multi_armed_bandit == "default":
        multi_armed_bandit = get_multi_armed_bandit_default()
        is_multi_armed_bandit = False
    else:
        is_multi_armed_bandit = True
        if not isinstance(multi_armed_bandit, dict):
            raise TypeError("multi_armed_bandit should be a dictionary")
        if "epsilon" not in multi_armed_bandit:
            raise KeyError("multi_armed_bandit must contain epsilon")
        if "duration" not in multi_armed_bandit:
            raise KeyError("multi_armed_bandit must contain duration")
        if "pulse_responder_uuid" not in multi_armed_bandit:
            raise KeyError("multi_armed_bandit must contain pulse_responder_uuid")
        if not isinstance(multi_armed_bandit["epsilon"], (int, float)):
            raise TypeError("epsilon in multi_armed_bandit should be a number")
        if multi_armed_bandit["epsilon"] < 0 or multi_armed_bandit["epsilon"] > 1:
            raise ValueError("epsilon in multi_armed_bandit should be between 0 and 1")
        if not isinstance(multi_armed_bandit["duration"], (int, float)):
            raise TypeError("duration in multi_armed_bandit should be a number")
        if multi_armed_bandit["duration"] < 0:
            raise ValueError("duration in multi_armed_bandit should be greater than 0")
        if multi_armed_bandit["pulse_responder_uuid"] == "":
            dynamic_config = {}
        else:
            all_dynamic_configurations = cp.list_pulse_responder_dynamic(auth)
            found_pulse_responder = False
            for dynamic_config_iter in all_dynamic_configurations["data"]:
                if dynamic_config_iter["uuid"] == multi_armed_bandit["pulse_responder_uuid"]:
                    found_pulse_responder = True
                    dynamic_config = dynamic_config_iter
            if not found_pulse_responder:
                raise ValueError(
                    "pulse_responder_id in multi_armed_bandit not linked to a dynamic recommender configuration")

    # Check that deployment_id is a string that doens't contain spaces and matches the dynamic configuration name if it exists
    if not isinstance(deployment_id, str):
        raise TypeError("deployment_id should be a string")
    if multi_armed_bandit["pulse_responder_uuid"] != "":
        if deployment_id != dynamic_config["name"]:
            raise ValueError("deployment step and dynamic recommender should have the same name")

    # Check whether version already exists and that it is a string
    if not isinstance(version, str):
        raise TypeError("version should be a string")
    if "deployment_step" in project_details:
        for deployment_iter in project_details["deployment_step"]:
            if (version == deployment_iter["version"]) and (deployment_id == deployment_iter["deployment_id"]):
                raise ValueError("The version specified for this deployment already exists, deployment not updated. Please update the version to update the deployment")

    # Check that description is a string
    if not isinstance(description, str):
        raise TypeError("description should be a string")

    # Check that project status has an allowed value
    if project_status not in ["experiment", "validate", "production", "disable"]:
        raise ValueError("project_status must be one of experiment, validate, production or disable")

    # Get pre and post score logic and return warnings if the requested logic is not found
    if not isinstance(plugin_pre_score_class, str):
        raise TypeError("plugin_pre_score_class should be a string")
    if not isinstance(plugin_post_score_class, str):
        raise TypeError("plugin_post_score_class should be a string")
    if (".java" not in plugin_pre_score_class) and ("" not in plugin_pre_score_class):
        raise TypeError("plugin_pre_score_class should be a java class")
    if ".java" not in plugin_post_score_class:
        raise TypeError("plugin_post_score_class should be a java class")
    pre_score_code = get_pre_score_code(plugin_pre_score_class,project_details)
    post_score_code = get_post_score_code(plugin_post_score_class,project_details)

    # Check that complexity and performance_expectation have one of the required values
    if complexity not in ["Low", "Medium", "High"]:
        raise ValueError("complexity must be one of Low, Medium or High")
    if performance_expectation not in ["Low", "Medium", "High"]:
        raise ValueError("performance_expectation must be one of Low, Medium or High")

    # Check format of mongo_connect string and check if connection to database can be made
    if not isinstance(mongo_connect, str):
        raise TypeError("mongo_connect should be a string")
    try:
        test_client = pymongo.MongoClient(mongo_connect)
        with pymongo.timeout(2):
            test_client.admin.command("ping")
        test_mongo_connection = True
    except:
        test_mongo_connection = False
        print("WARNING: Test connection to mongo database failed")

    if not isinstance(mongo_server_port, str):
        raise TypeError("mongo_server_port should be a string")
    if not isinstance(mongo_ecosystem_password, str):
        raise TypeError("mongo_ecosystem_password should be a string")
    if not isinstance(mongo_ecosystem_user, str):
        raise TypeError("mongo_ecosystem_user should be a string")
    if mongo_server_port not in mongo_connect:
        print(
            "WARNING: mongo_server_port looks like it doesn't correspond with the mongo connection string in mongo_connect")
    if mongo_ecosystem_password not in mongo_connect:
        print(
            "WARNING: mongo_ecosystem_password looks like it doesn't correspond with the mongo connection string in mongo_connect")
    if mongo_ecosystem_user not in mongo_connect:
        print(
            "WARNING: mongo_ecosystem_user looks like it doesn't correspond with the mongo connection string in mongo_connect")

    # TODO Get validation rules/logic from Jay
    if budget_tracker == "default":
        budget_tracker = get_budget_tracker_default()
        is_budget_tracking = False
    else:
        is_budget_tracking = True

    # Check that model configuration has the required format and display a warning if the listed models cannot be found in list of deployed models
    if model_configuration == "default":
        model_configuration = get_model_configuration_default()
        is_prediction_model = False
    else:
        is_prediction_model = True
        if not isinstance(model_configuration, dict):
            raise TypeError("model_configuration should be a dictionary")
        if "models_load" not in model_configuration:
            raise ValueError("model_configuration must contain models_load")
        if not isinstance(model_configuration["models_load"], str):
            raise TypeError("models_load in model_configuration should be a string")
        model_list = model_configuration["models_load"].split(",")
        # TODO Ask Jay for a better version of getting a list of deployed models
        list_of_deployed_models = pe.get_user_models(auth, "ecosystem")
        for model_iter in model_list:
            if model_iter not in list_of_deployed_models:
                print(
                    "WARNING: " + model_iter + " cannot be found on the list of deployed models managed in the ecosystem.ai workbench")

    # Indicator of whether a connection to Cassandra has been checked
    test_cassandra_connection = True
    test_presto_connection = True

    # Check that the offer matrix set up has the required format and whether the offer matrix can be found using the connections available to the server
    if setup_offer_matrix == "default":
        setup_offer_matrix = get_setup_offer_matrix_default()
        is_offer_matrix = False
    else:
        is_offer_matrix = True
        if not isinstance(setup_offer_matrix, dict):
            raise TypeError("setup_offer_matrix should be a dictionary")
        if "datasource" not in setup_offer_matrix:
            raise KeyError("setup_offer_matrix must contain datasource")
        if "database" not in setup_offer_matrix:
            raise KeyError("setup_offer_matrix must contain database")
        if "table_collection" not in setup_offer_matrix:
            raise KeyError("table_setup_offer_matrix must contain collection")
        if "offer_lookup_id" not in setup_offer_matrix:
            raise KeyError("setup_offer_matrix must contain offer_lookup_id")
        if setup_offer_matrix["datasource"] not in ["mongodb", "cassandra", "presto"]:
            raise ValueError("datasource in setup_offer_matrix must be cassandra, mongodb or presto")
        if not isinstance(setup_offer_matrix["database"], str):
            raise TypeError("database in setup_offer_matrix should be a string")
        if not isinstance(setup_offer_matrix["table_collection"], str):
            raise TypeError("table_collection in setup_offer_matrix should be a string")
        if setup_offer_matrix["offer_lookup_id"] not in ["offer", "offer_id", "offer_name"]:
            raise ValueError("offer_lookup_id in setup_offer_matrix must be offer, offer_name or presto")
        if setup_offer_matrix["datasource"] == "mongodb" and test_mongo_connection:
            db_offer_matrix = test_client[setup_offer_matrix["database"]]
            if db_offer_matrix[setup_offer_matrix["collection"]].estimated_document_count() == 0:
                print("WARNING: It looks like the offer matrix is empty")
            else:
                test_offer_matrix_row = db_offer_matrix[setup_offer_matrix["collection"]].find_one().next()
                if setup_offer_matrix["offer_lookup_id"] not in test_offer_matrix_row:
                    print("WARNING: It looks like the specified offer_lookup_id is not a field in the offer matrix")
        elif setup_offer_matrix["datasource"] == "cassandra" and test_cassandra_connection:
            # TODO: Implement cassandra checks once Ramsay has added APIs
            print("WARNING: cassandra connection could not be tested")
        elif setup_offer_matrix["datasource"] == "presto" and test_presto_connection:
            # TODO: Ask Jay how Presto connection works and figure our how to implement test on Presto Connection
            print("WARNING: presto connection could not be tested")

    # Check that the whitelist has the required format
    if whitelist == "default":
        whitelist = get_whitelist_default()
        is_whitelist = False
    else:
        is_whitelist = True
        if not isinstance(whitelist, dict):
            raise TypeError("whitelist should be a dictionary")
        if "datasource" not in whitelist:
            raise KeyError("whitelist must contain datasource")
        if "database" not in whitelist:
            raise KeyError("whitelist must contain database")
        if "collection" not in whitelist:
            raise KeyError("whitelist must contain collection")
        if whitelist["datasource"] not in ["mongodb", "cassandra", "presto"]:
            raise ValueError("datasource in whitelist must be cassandra, mongodb or presto")
        if not isinstance(whitelist["database"], str):
            raise TypeError("database in whitelist should be a string")
        if not isinstance(whitelist["collection"], str):
            raise TypeError("collection in whitelist should be a string")
        if whitelist["datasource"] == "mongodb" and test_mongo_connection:
            db_whitelist = test_client[whitelist["database"]]
            if db_whitelist[whitelist["collection"]].estimated_document_count() == 0:
                print("WARNING: It looks like the whitelist is empty")
            else:
                test_whitelist_row = db_whitelist[whitelist["collection"]].find_one().next()
                if "customer_key" not in test_whitelist_row:
                    print("WARNING: It looks like customer_key is not a field in the white list")
                if "white_list" not in test_whitelist_row:
                    print("WARNING: It looks like white_list is not a field in the white list")
        elif whitelist["datasource"] == "cassandra" and test_cassandra_connection:
            # TODO: Implement cassandra checks once Ramsay has added APIs
            print("WARNING: cassandra connection could not be tested")
        elif whitelist["datasource"] == "presto" and test_presto_connection:
            # TODO: Ask Jay how Presto connection works and figure our how to implement test on Presto Connection
            print("WARNING: presto connection could not be tested")

    # Check that the model selector has the required format
    if model_selector == "default":
        model_selector = get_model_selector_default()
        is_model_selector = False
    else:
        is_model_selector = True
        if not isinstance(model_selector, dict):
            raise TypeError("model_selector should be a dictionary")
        if "datasource" not in model_selector:
            raise KeyError("model_selector must contain datasource")
        if "database" not in model_selector:
            raise KeyError("model_selector must contain database")
        if "table_collection" not in model_selector:
            raise KeyError("model_selector must contain table_collection")
        if "selector_column" not in model_selector:
            raise KeyError("model_selector must contain selector_column")
        if "selector" not in model_selector:
            raise KeyError("model_selector must contain selector")
        if "lookup" not in model_selector:
            raise KeyError("model_selector must contain lookup")
        if not isinstance(model_selector["lookup"], dict):
            raise TypeError("lookup in model_selector should be a dictionary")
        if "key" not in model_selector["lookup"]:
            raise KeyError("lookup in model_selector must contain key")
        if "value" not in model_selector["lookup"]:
            raise KeyError("lookup in model_selector must contain value")
        if "fields" not in model_selector["lookup"]:
            raise KeyError("lookup in model_selector must contain fields")
        if not isinstance(model_selector["selector"], dict):
            raise TypeError("selector in model_selector should be a dictionary")
        if model_selector["datasource"] not in ["mongodb", "cassandra", "presto"]:
            raise ValueError("datasource in model_selector must be cassandra, mongodb or presto")
        if not isinstance(model_selector["database"], str):
            raise TypeError("database in model_selector should be a string")
        if not isinstance(model_selector["table_collection"], str):
            raise TypeError("table_collection in model_selector should be a string")
        if model_selector["datasource"] == "mongodb" and test_mongo_connection:
            db_model_selector = test_client[model_selector["database"]]
            if db_model_selector[model_selector["table_collection"]].estimated_document_count() == 0:
                print("WARNING: It looks like the model_selector is empty")
            else:
                test_model_selector_row = db_model_selector[model_selector["table_collection"]].find_one().next()
                if model_selector["selector_column"] not in test_model_selector_row:
                    print("WARNING: It looks like selector_column is not a field in the model selector collection")
                elif extensive_validation:
                    selector_values_cursor = db_model_selector[model_selector["table_collection"]].aggregate([{
                                                                                                                  "$group": {
                                                                                                                      "_id": "None",
                                                                                                                      "selector_values": {
                                                                                                                          "$addToSet": "$" +
                                                                                                                                       model_selector[
                                                                                                                                           "selector_column"]}}}]).next()
                    selector_values_in_dataset = selector_values_cursor["selector_values"]
                    selector_values_in_args = model_selector["selector"].keys()
                    for selector_value_in_dataset_iter in selector_values_in_dataset:
                        if selector_value_in_dataset_iter not in selector_values_in_args:
                            print("WARNING: " + str(
                                selector_value_in_dataset_iter) + " in the model selector database but not in the selector in the model_selector. If this row is looked up by the runtime a default value will be returned")
                    for selector_value_in_args_iter in model_selector["selector"]:
                        if selector_value_in_args_iter not in selector_values_in_dataset:
                            print("WARNING: " + str(
                                selector_value_in_args_iter) + " in the selector in the model_selector is not present in the model selector dataset")
                if model_selector["lookup"]["key"] not in test_model_selector_row:
                    print(
                        "WARNING: It looks like key in the lookup in model_seelector is not a field in the model selector collection")
        elif whitelist["datasource"] == "cassandra" and test_cassandra_connection:
            # TODO: Implement cassandra checks once Ramsay has added APIs
            print("WARNING: cassandra connection could not be tested")
        elif whitelist["datasource"] == "presto" and test_presto_connection:
            # TODO: Ask Jay how Presto connection works and figure our how to implement test on Presto Connection
            print("WARNING: presto connection could not be tested")

    # Check whether pattern selector contains the required parameters
    if pattern_selector == "default":
        pattern_selector = get_pattern_selector_default()
        is_pattern_selector = False
    else:
        is_pattern_selector = True
        if not isinstance(pattern_selector, dict):
            raise TypeError("pattern_selector should be a dictionary")
        if "pattern" not in model_selector:
            raise KeyError("pattern_selector must contain pattern")
        if "duration" not in model_selector:
            raise KeyError("pattern_selector must contain duration")
        if not isinstance(pattern_selector["pattern"], str):
            raise TypeError("pattern in pattern_selector should be a string of comma separated numbers")
        if not isinstance(pattern_selector["duration"], (int, float)):
            raise TypeError("duration in pattern_selector should be a number")

    # Check whether corpora has the required format and checks if the loaded corpora can be found
    if corpora == "default":
        corpora = get_corpora_default()
        is_corpora = False
    else:
        is_corpora = True
        if not isinstance(corpora, list):
            raise TypeError("corpora should be a list of dictionaries giving details of the corpora to be linked")
        for corpora_iter in corpora:
            if not isinstance(corpora_iter, dict):
                raise TypeError("corpora should be a list of dictionaries giving details of the corpora to be linked")
            if "name" not in corpora_iter:
                raise KeyError("corpora dictionaries must contain name")
            if "database" not in corpora_iter:
                raise KeyError("corpora dictionaries must contain database")
            if "db" not in corpora_iter:
                raise KeyError("corpora dictionaries must contain db")
            if "table" not in corpora_iter:
                raise KeyError("corpora dictionaries must contain table")
            if "type" not in corpora_iter:
                raise KeyError("corpora dictionaries must contain type")
            for corpora_key in corpora_iter:
                if corpora_key not in ["name", "database", "db", "table", "type", "key"]:
                    raise KeyError("corpora dictionaries can only contain name, database, db, table, type and key")
            if corpora_iter["database"] not in ["mongodb", "cassandra"]:
                raise ValueError("database in corpora must be cassandra or mongodb")
            if corpora_iter["type"] not in ["static", "dynamic", "experiment"]:
                raise ValueError("type in corpora must be static, dynamic or experiment")
            if corpora_iter["database"] == "mongodb" and test_mongo_connection:
                db_corpora = test_client[corpora_iter["database"]]
                if db_corpora[corpora_iter["table"]].estimated_document_count() == 0:
                    print("WARNING: It looks like the corpora is empty")
                elif "key" in corpora_iter:
                    test_corpora_row = db_corpora[corpora_iter["table"]].find_one().next()
                    if corpora_iter["key"] not in test_corpora_row:
                        print("WARNING: It looks like the specified key is missing from the corpora")
            elif corpora_iter["database"] == "cassandra" and test_cassandra_connection:
                # TODO: Implement cassandra checks once Ramsay has added APIs
                print("WARNING: cassandra connection could not be tested")
        corpora = {"corpora": json.dumps(corpora)}

    if parameter_access == "default":
        parameter_access = get_parameter_access_default()
        is_params_from_data_source = False
    else:
        is_params_from_data_source = True
        if not isinstance(parameter_access, dict):
            raise TypeError("parameter_access should be a dictionary")
        if "datasource" not in parameter_access:
            raise KeyError("parameter_access must contain datasource")
        if "database" not in parameter_access:
            raise KeyError("parameter_access must contain database")
        if "table_collection" not in parameter_access:
            raise KeyError("parameter_access must contain table_collection")
        if "lookup" not in parameter_access:
            raise KeyError("parameter_access must contain lookup")
        # if "fields" not in parameter_access:
        #     raise KeyError("parameter_access must contain fields")
        if "lookup_defaults" not in parameter_access:
            raise KeyError("parameter_access must contain lookup_defaults")
        if "lookup_fields" not in parameter_access:
            raise KeyError("parameter_access must contain lookup_fields")
        if "create_virtual_variables" not in parameter_access:
            raise KeyError("parameter_access must contain create_virtual_variables")
        if "virtual_variables" not in parameter_access:
            raise KeyError("parameter_access must contain virtual_variables")
        if parameter_access["datasource"] not in ["mongodb", "cassandra", "presto"]:
            raise ValueError("datasource in parameter_access must be cassandra, mongodb or presto")
        if not isinstance(parameter_access["database"], str):
            raise TypeError("database in parameter_access should be a string")
        if not isinstance(parameter_access["table_collection"], str):
            raise TypeError("table_collection in parameter_access should be a string")
        if not isinstance(parameter_access["lookup"], dict):
            raise TypeError("lookup in parameter_access should be a dictionary")
        if "key" not in parameter_access["lookup"]:
            raise KeyError("lookup in parameter_access must contain key")
        if "value" not in parameter_access["lookup"]:
            raise KeyError("lookup in parameter_access must contain value")
        # if not isinstance(parameter_access["fields"], str):
        #     raise TypeError("fields in parameter_access should be a string")
        if not isinstance(parameter_access["create_virtual_variables"], bool):
            raise TypeError("create_virtual_variables in parameter_access should be a boolean value")
        if not isinstance(parameter_access["virtual_variables"], list):
            raise TypeError("virtual_variables in parameter_access should be a list")
        if parameter_access["datasource"] == "mongodb" and test_mongo_connection:
            db_parameter_access = test_client[parameter_access["database"]]
            if db_parameter_access[parameter_access["table_collection"]].estimated_document_count() == 0:
                print("WARNING: It looks like the parameter_access collection is empty")
            else:
                test_parameter_access_row = db_parameter_access[parameter_access["collection"]].find_one().next()
                if parameter_access["lookup"]["key"] not in test_parameter_access_row:
                    print("WARNING: It looks like the specified key is not a field in the parameter_access collection")
                if type(test_parameter_access_row[parameter_access["lookup"]["key"]]) != type(
                        parameter_access["lookup"]["value"]):
                    print(
                        "WARNING: It looks like value specified in the lookup in parameter_access does not match the type found in the collection")
        elif parameter_access["datasource"] == "cassandra" and test_cassandra_connection:
            # TODO: Implement cassandra checks once Ramsay has added APIs
            print("WARNING: cassandra connection could not be tested")
        elif parameter_access["datasource"] == "presto" and test_presto_connection:
            # TODO: Ask Jay how Presto connection works and figure our how to implement test on Presto Connection
            print("WARNING: presto connection could not be tested")

    #######################################################################################################################
    # Define constructs needed to create the deployment and add the deployment to the project
    #######################################################################################################################
    multi_armed_bandit["epsilon"] = str(multi_armed_bandit["epsilon"])

    options = {
        "is_offer_matrix": is_offer_matrix,
        "is_multi_armed_bandit": is_multi_armed_bandit,
        "is_enable_plugins": True,
        "is_whitelist": is_whitelist,
        "is_corpora": is_corpora,
        "is_custom_api": False,
        "is_budget_tracking": is_budget_tracking,
        "is_params_from_data_source": is_params_from_data_source,
        "is_model_selector": is_model_selector,
        "is_generate_dashboards": False,
        "is_pattern_selector": is_pattern_selector,
        "is_prediction_model": is_prediction_model
    }

    api_endpoint_code = get_api_endpoint_code_default()
    plugins = {
        "post_score_class_text": plugin_post_score_class,
        "post_score_class_code": post_score_code,
        "api_endpoint_code": api_endpoint_code,
        "pre_score_class_text": plugin_pre_score_class,
        "pre_score_class_code": pre_score_code
    }

    updated_by = auth.get_username()
    updated_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

    paths = {
        "logging_collection_response": logging_collection_response,
        "logging_collection": logging_collection,
        "logging_database": logging_database,
        "mongo_server_port": mongo_server_port,
        "scoring_engine_path_prod": scoring_engine_path_prod,
        "models_path": models_path,
        "mongo_connect": mongo_connect,
        "data_path": data_path,
        "build_server_path": build_server_path,
        "scoring_engine_path_dev": scoring_engine_path_dev,
        "aws_container_resource": "",
        "scoring_engine_path_test": scoring_engine_path_test,
        "git_repo_path_branch": git_repo_path_branch,
        "download_path": download_path,
        "mongo_ecosystem_password": mongo_ecosystem_password,
        "mongo_ecosystem_user": mongo_ecosystem_user,
        "git_repo_path": git_repo_path
    }

    if "lookup_fields" in parameter_access:
        fields = ""
        for field_iter in parameter_access["lookup_fields"]: fields = fields + "," + field_iter
        parameter_access["fields"] = fields[1::]

    # Define deployment step
    deployment_step = {}
    deployment_step["version"] = version
    deployment_step["deployment_id"] = deployment_id
    deployment_step["project_status"] = project_status
    deployment_step["description"] = description
    deployment_step["complexity"] = complexity
    deployment_step["plugins"] = plugins
    deployment_step["model_configuration"] = model_configuration
    deployment_step["setup_offer_matrix"] = setup_offer_matrix
    deployment_step["multi_armed_bandit"] = multi_armed_bandit
    deployment_step["whitelist"] = whitelist
    deployment_step["model_selector"] = model_selector
    deployment_step["performance_expectation"] = performance_expectation
    deployment_step["pattern_selector"] = pattern_selector
    deployment_step["paths"] = paths
    # deployment_step["Build"] = Build
    deployment_step["updated_by"] = updated_by
    deployment_step["updated_date"] = updated_date
    deployment_step["options"] = options
    deployment_step["corpora"] = corpora
    deployment_step["parameter_access"] = parameter_access
    deployment_step["budget_tracker"] = budget_tracker
    # Add deployment step to project
    if "deployment_step" in project_details:
        project_details["deployment_step"].append(deployment_step)
    else:
        project_details["deployment_step"] = [deployment_step]

    # Save project with newly created deployment
    pe.save_prediction_project(auth, project_details)

    #Update dynamic pulse responder if linked and relevant
    if "pulse_responder_uuid" in multi_armed_bandit:
        if multi_armed_bandit["pulse_responder_uuid"] != "":
            existing_configurations = cp.list_pulse_responder_dynamic(auth)
            client_pulse_list = [d for d in existing_configurations["data"] if
                                 d["uuid"] == multi_armed_bandit["pulse_responder_uuid"]]
            client_pulse_doc = client_pulse_list[0]
            if "fields" in parameter_access:
                client_pulse_doc["lookup_fields"] = parameter_access["fields"]
            if "virtual_variables" in parameter_access:
                client_pulse_doc["virtual_variables"] = parameter_access["virtual_variables"]
            d.add_documents(auth, {"database": "ecosystem_meta", "collection": "dynamic_engagement",
                                   "document": client_pulse_doc, "update": "uuid"})

    print("MESSAGE: Project deployment created")
    return deployment_step


def create_project(
        auth,
        project_id,
        project_description,
        project_type,
        purpose,
        project_start_date,
        project_end_date,
        data_science_lead,
        data_lead,
        module_name="",
        module_module_owner="",
        module_description="",
        module_created_by="",
        module_version="",
):
    if not isinstance(project_id, str):
        raise TypeError("project_id should be a string")
    if not isinstance(project_description, str):
        raise TypeError("project_description should be a string")
    if not isinstance(project_type, str):
        raise TypeError("project_type should be a string")
    if not isinstance(purpose, str):
        raise TypeError("purpose should be a string")
    if not isinstance(data_science_lead, str):
        raise TypeError("data_science_lead should be a string")
    if not isinstance(data_lead, str):
        raise TypeError("data_lead should be a string")
    if not isinstance(module_name, str):
        raise TypeError("module_name should be a string")
    if not isinstance(module_module_owner, str):
        raise TypeError("module_module_owner should be a string")
    if not isinstance(module_description, str):
        raise TypeError("module_description should be a string")
    if not isinstance(module_created_by, str):
        raise TypeError("module_created_by should be a string")
    if not isinstance(module_version, str):
        raise TypeError("module_version should be a string")

    project_exists = True
    try:
        pe.get_prediction_project(auth, project_id)
    except:
        project_exists = False

    if project_exists:
        raise ValueError(
            "project_id already exists. Use either update_project or delete_project to change project parameters")

    updated_by = auth.get_username()
    updated_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

    if module_name == "":
        module_name = project_id
    if module_module_owner == "":
        module_module_owner = data_science_lead
    if module_description == "":
        module_description = project_description
    if module_created_by == "":
        module_created_by = updated_by
    if module_version == "":
        module_version = "001"

    project_doc = {
        "project_id": project_id
        , "project_description": project_description
        , "project_type": project_type
        , "purpose": purpose
        , "configuration": ""
        , "project_start_date": project_start_date
        , "project_end_date": project_end_date
        , "project_owner": data_science_lead
        , "project_data": data_lead
        , "module_metadata": {
            "reviewed_by": "",
            "image_path": "",
            "icon_path": "",
            "name": module_name,
            "module_owner": module_module_owner,
            "description": module_description,
            "created_by": module_created_by,
            "version": module_version,
            "contact_email": "",
            "status": ""
        }
        , "preview_detail": {
            "heading": project_id
            , "summary": project_description
            , "detail": purpose
            , "active": True
        }
        , "created_by": updated_by
        , "created_date": updated_date
        , "updated_by": updated_by
        , "updated_date": updated_date
        , "userid": "ecosystem"
    }
    pe.save_prediction_project(auth, project_doc)

    print("MESSAGE: Project created")
    return project_doc
