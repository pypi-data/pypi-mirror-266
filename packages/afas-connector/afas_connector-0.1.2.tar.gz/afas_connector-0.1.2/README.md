## AfasConnector

The `AfasConnector` class provides a convenient interface for interacting with AFAS Connectors via HTTP requests. It simplifies the process of sending GET, POST, and PUT requests to your AFAS Connectors and handling their responses.

### Features

- Easy configuration through environment variables.
- Support for GET, POST, and PUT requests.
- Integrated filtering, ordering, and pagination for GET requests.
- Automatic handling of AFAS token authentication.

## Usage
First, set the necessary environment variables:

AFAS_CONNECTORS_URL: The base URL for your AFAS Connectors.
AFAS_TOKEN: Your AFAS token.
Here's an example of how to use AfasConnector in your Python code:

```python
from afas import AfasConnector

# Initialize the connector
connector = AfasConnector()

# GET request example
status_code, response = connector.get(endpoint='Profit_OData/SomeEndpoint', filters=[...])
if status_code == 200:
    print(response)

# PUT request example
payload = {...}
status_code, response = connector.put(endpoint='Profit_OData/SomeEndpoint', payload=payload)
if status_code == 200:
    print(response)

# POST request example
payload = {...}
status_code, response = connector.post(endpoint='Profit_OData/SomeEndpoint', payload=payload)
if status_code == 200:
    print(response)

```

## Handling Responses and Errors
Each method returns a tuple containing the HTTP status code and the response from the AFAS Connector. A successful request will return a status code of 200. If the request is unsuccessful, the status code can be used to diagnose the issue. The second element of the tuple will be the JSON response for successful requests or None in case of an error.

### AfasFilter

The `AfasFilter` class provides a way to define filters for the AFAS Connectors. It allows you to specify the field, value(s), and operator for the filter.

#### Usage

Here's an example of how to use the `AfasFilter` class:

```python
# Create an example of using the AfasFilter class
filter = AfasFilter(field='Itemcode', value='1234', operator=AfasFilter.EQUAL_TO)
filter_OR = AfasFilter(field='Itemcode', value=['1234', '4321'], operator=[AfasFilter.EQUAL_TO, AfasFilter.EQUAL_TO])

# Convert the filters to a query string
query = afas_filters_to_query([filter, filter_OR])

# Print the query string
print(query)

```


### AfasObject
The `AfasObject` is a wrapper for updating an item in Afas. The object has an `update` method that uses the `AfasConnector` class to update an item in a single line.

#### Usage

Here's an exampke of how to use the `AfasObject` class:

```python
from afas.afas_object import AfasObject

# Create an instance of AfasObject
obj = AfasObject('FbItemArticle', {'Field1': 'Value1', 'Field2': 'Value2'})

# Update the object in AFAS Profit
status_code, response = obj.update()
if status_code == 200:
    print("Object updated successfully")
else:
    print("Failed to update object")

# Get a string representation of the object
print(str(obj))
```
