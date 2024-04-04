import json
import os
import jsonschema
from .ref_Resolver import ExtendedRefResolver
from .configs import mappingObject
from pkg_resources import resource_filename


def executeValidateJson(data, schema):
    try:
        jsonschema.validate(
            data,
            schema,
            resolver=ExtendedRefResolver(
                base_uri=resource_filename(__name__, '/Schema'),
                referrer=schema,
            ),
        )
    except jsonschema.exceptions.ValidationError as err:
        validation_msg = err.message
        if err.validator == "type" and len(err.path) > 0:
            key = err.path[len(err.path) - 1]
            validation_msg = f"{key} field should be a {err.validator_value}"
        return {"status": "SCHEMA_VALIDATION_FAILED", "message": validation_msg}   
    except Exception as err:
        return {"status": "SCHEMA_VALIDATION_FAILED", "message": err}    
    return {
        "status": "SCHEMA_VALIDATION_SUCCESS",
        "message": "Schema successfully validated",
    }


def extract_data_from_file(schema_file):
    path_for_schema = resource_filename(__name__, '/Schema')
    
    with open(f"{path_for_schema}/{schema_file}.json", "r") as schema_file:
        schemaObj = json.load(schema_file)

    return schemaObj


def validateJson(dataJsonString, reportType):
    # Temporary fix for report type exceptions
    arrExceptions = [
        "amazon_onsiteSponsoredProductsCampaign",
        "amazon_storeKeyMetrics",
        "amazon_storeKeyMetricsMonthly",
        "amazon_storeKeyMetricsMonthlyBackFill",
        "shopee_productSponsoredAffiliateReport",
        "shopee_onsiteKeyword",
        "shopee_marketingShippingFeePromotion",
        "shopee_marketingShippingFeePromotionMonthly",
        "shopee_marketingShippingFeePromotionMonthlyBackFill",
        "shopee_storeKeyMetricsMonthlyBackFill",
        "lazada_storeKeyMetrics",
        "lazada_storeKeyMetricsMonthly",
        "lazada_storeKeyMetricsMonthlyBackFill",
        "lazada_onsiteKeyword",
        "flipkart_storeRevenue",
        "flipkart_PLAConsolidatedFSNSellerPortal",
        "flipkart_BrandAdsCampaign",
        "flipkart_DisplayAdsCampaign",
        "flipkart_PLAConsolidatedFSN",
        "flipkart_PCACampaign",
        "flipkart_PLACampaign",
        "flipkart_PLACampaignSellerPortal",
        "flipkart_searchTrafficReport",
        "flipkart_PCAProductPagePerformance"
    ]

    if reportType is None or not reportType:
        return {
            "status": "SCHEMA_VALIDATION_FAILED",
            "message": "Report type is Empty or None please enter valid string value!"
        }
    elif reportType in arrExceptions:
        return {
            "status": "SCHEMA_VALIDATION_SUCCESS",
            "message": "Schema successfully validated"
        }

    schema_file = mappingObject.get(reportType, "")

    if schema_file:
        try:
            jsonObject = json.loads(dataJsonString)
        except Exception as err:
            print("Error in converting data from string to json", err)
            return {
                "status": "FILE_FAILED_TO_CONVERT_JSON",
                "message": "Invalid JSON format"
            }
        if jsonObject:
            schemaObject = extract_data_from_file(schema_file)
            isValidated = executeValidateJson(jsonObject, schemaObject)
            return isValidated
        else:
            return {
                "status": "SCHEMA_VALIDATION_FAILED",
                "message": "Object is empty please enter correct object"
            }
    else:
        # Temporary fix
        return {
            "status": "SCHEMA_VALIDATION_SUCCESS",
            "message": "Schema successfully validated"
        }
