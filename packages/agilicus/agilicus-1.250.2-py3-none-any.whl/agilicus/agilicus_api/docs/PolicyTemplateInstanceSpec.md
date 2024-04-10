# PolicyTemplateInstanceSpec

The definition of a PolicyTemplateInstance. `template` defines the concrete parameters of the template as well as its type. The org id defines the organisation to which the template applies. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | Unique identifier | 
**template** | [**PolicyTemplate**](PolicyTemplate.md) |  | 
**name** | **str** | A short name used to unqiuely identify this instance. May be descriptive, but primarily used for idempotency. Cannot be changed after creation.  | 
**description** | **str** | A brief description of the template | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


