# Celitech Python SDK 1.0.0

A Python SDK for Celitech.

- API version: 1.1.0
- SDK version: 1.0.0

Welcome to the CELITECH API documentation! Useful links: [Homepage](https://www.celitech.com) | [Support email](mailto:support@celitech.com) | [Blog](https://www.celitech.com/blog/)

## Table of Contents

- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Services](#services)

## Installation

```bash
pip install celitech
```

## Environment Variables

You will need the following environment variables in order to access all the features of this SDK:

| Name          | Description             |
| :------------ | :---------------------- |
| CLIENT_ID     | Client ID parameter     |
| CLIENT_SECRET | Client Secret parameter |

You can set these environment variables on the command line or you can use whatever tooling your project has in place to manage environment variables. If you are using a `.env` file, we have provided a template with the variable names in the `.env.example` file in the same directory as this readme.

## Services

A list of all SDK services. Click on the service name to access its corresponding service methods.

| Service                                     |
| :------------------------------------------ |
| [DestinationsService](#destinationsservice) |
| [PackagesService](#packagesservice)         |
| [PurchasesService](#purchasesservice)       |
| [ESimService](#esimservice)                 |

### DestinationsService

A list of all methods in the `DestinationsService` service. Click on the method name to view detailed information about that method.

| Methods                                 | Description              |
| :-------------------------------------- | :----------------------- |
| [list_destinations](#list_destinations) | Name of the destinations |

#### **list_destinations**

Name of the destinations

- HTTP Method: `GET`
- Endpoint: `/destinations`

**Parameters**
| Name | Type| Required | Description |
| :-------- | :----------| :----------:| :----------|

**Return Type**

`ListDestinationsOkResponse`

**Example Usage Code Snippet**

```py
from celitech import Celitech, Environment

sdk = Celitech(
    base_url=Environment.DEFAULT.value
)

result = sdk.destinations.list_destinations()

print(result)
```

### PackagesService

A list of all methods in the `PackagesService` service. Click on the method name to view detailed information about that method.

| Methods                         | Description                |
| :------------------------------ | :------------------------- |
| [list_packages](#list_packages) | List of available packages |

#### **list_packages**

List of available packages

- HTTP Method: `GET`
- Endpoint: `/packages`

**Parameters**
| Name | Type| Required | Description |
| :-------- | :----------| :----------:| :----------|
| destination | str | ❌ | List of available packages |
| startDate | str | ❌ | List of available packages |
| endDate | str | ❌ | List of available packages |
| afterCursor | str | ❌ | List of available packages |
| limit | float | ❌ | List of available packages |
| startTime | int | ❌ | List of available packages |
| endTime | int | ❌ | List of available packages |
| duration | float | ❌ | List of available packages |

**Return Type**

`ListPackagesOkResponse`

**Example Usage Code Snippet**

```py
from celitech import Celitech, Environment

sdk = Celitech(
    base_url=Environment.DEFAULT.value
)

result = sdk.packages.list_packages(
    destination="FRA",
    start_date="2023-11-01",
    end_date="2023-11-20",
    after_cursor="Y3JlYXRlZEF0OjE1OTk0OTMwOTgsZGVzdGluYXRpb246QVVTLG1pbkRheXM6MCxkYXRhTGltaXRJbkJ5dGVzOjUzNjg3MDkxMjA",
    limit=20,
    start_time=8,
    end_time=2,
    duration=8.44
)

print(result)
```

### PurchasesService

A list of all methods in the `PurchasesService` service. Click on the method name to view detailed information about that method.

| Methods                                               | Description                                                                                                                                                                                                                                                                                                            |
| :---------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [list_purchases](#list_purchases)                     | This endpoint can be used to list all the successful purchases made between a given interval.                                                                                                                                                                                                                          |
| [create_purchase](#create_purchase)                   | This endpoint is used to purchase a new eSIM by providing the package details.                                                                                                                                                                                                                                         |
| [top_up_esim](#top_up_esim)                           | This endpoint is used to top-up an eSIM with the previously associated destination by providing an existing ICCID and the package details. The top-up is not feasible for eSIMs in "DELETED" or "ERROR" state.                                                                                                         |
| [edit_purchase](#edit_purchase)                       | This endpoint allows you to modify the dates of an existing package with a future activation start time. Editing can only be performed for packages that have not been activated, and it cannot change the package size. The modification must not change the package duration category to ensure pricing consistency. |
| [get_purchase_consumption](#get_purchase_consumption) | This endpoint can be called for consumption notifications (e.g. every 1 hour or when the user clicks a button). It returns the data balance (consumption) of purchased packages.                                                                                                                                       |

#### **list_purchases**

This endpoint can be used to list all the successful purchases made between a given interval.

- HTTP Method: `GET`
- Endpoint: `/purchases`

**Parameters**
| Name | Type| Required | Description |
| :-------- | :----------| :----------:| :----------|
| iccid | str | ❌ | This endpoint can be used to list all the successful purchases made between a given interval. |
| afterDate | str | ❌ | This endpoint can be used to list all the successful purchases made between a given interval. |
| beforeDate | str | ❌ | This endpoint can be used to list all the successful purchases made between a given interval. |
| afterCursor | str | ❌ | This endpoint can be used to list all the successful purchases made between a given interval. |
| limit | float | ❌ | This endpoint can be used to list all the successful purchases made between a given interval. |
| after | float | ❌ | This endpoint can be used to list all the successful purchases made between a given interval. |
| before | float | ❌ | This endpoint can be used to list all the successful purchases made between a given interval. |

**Return Type**

`ListPurchasesOkResponse`

**Example Usage Code Snippet**

```py
from celitech import Celitech, Environment

sdk = Celitech(
    base_url=Environment.DEFAULT.value
)

result = sdk.purchases.list_purchases(
    iccid="1111222233334444555",
    after_date="2023-11-01",
    before_date="2023-11-20",
    after_cursor="Y3JlYXRlZEF0OjE1OTk0OTMwOTgsZGVzdGluYXRpb246QVVTLG1pbkRheXM6MCxkYXRhTGltaXRJbkJ5dGVzOjUzNjg3MDkxMjA",
    limit=20,
    after=2.38,
    before=3.34
)

print(result)
```

#### **create_purchase**

This endpoint is used to purchase a new eSIM by providing the package details.

- HTTP Method: `POST`
- Endpoint: `/purchases`

**Parameters**
| Name | Type| Required | Description |
| :-------- | :----------| :----------:| :----------|
| request_body | CreatePurchaseRequest | ❌ | The request body. |

**Return Type**

`CreatePurchaseOkResponse`

**Example Usage Code Snippet**

```py
from celitech import Celitech, Environment
from celitech.models import CreatePurchaseRequest

sdk = Celitech(
    base_url=Environment.DEFAULT.value
)

request_body = CreatePurchaseRequest(**{
    "destination": "FRA",
    "data_limit_in_gb": 1,
    "start_date": "2023-11-01",
    "end_date": "2023-11-20",
    "email": "example@domain.com",
    "network_brand": "CELITECH",
    "start_time": 2.37,
    "end_time": 8.12
})

result = sdk.purchases.create_purchase(request_body=request_body)

print(result)
```

#### **top_up_esim**

This endpoint is used to top-up an eSIM with the previously associated destination by providing an existing ICCID and the package details. The top-up is not feasible for eSIMs in "DELETED" or "ERROR" state.

- HTTP Method: `POST`
- Endpoint: `/purchases/topup`

**Parameters**
| Name | Type| Required | Description |
| :-------- | :----------| :----------:| :----------|
| request_body | TopUpEsimRequest | ❌ | The request body. |

**Return Type**

`TopUpEsimOkResponse`

**Example Usage Code Snippet**

```py
from celitech import Celitech, Environment
from celitech.models import TopUpEsimRequest

sdk = Celitech(
    base_url=Environment.DEFAULT.value
)

request_body = TopUpEsimRequest(**{
    "iccid": "1111222233334444555",
    "data_limit_in_gb": 1,
    "start_date": "2023-11-01",
    "end_date": "2023-11-20",
    "email": "example@domain.com",
    "start_time": 8.12,
    "end_time": 4.35
})

result = sdk.purchases.top_up_esim(request_body=request_body)

print(result)
```

#### **edit_purchase**

This endpoint allows you to modify the dates of an existing package with a future activation start time. Editing can only be performed for packages that have not been activated, and it cannot change the package size. The modification must not change the package duration category to ensure pricing consistency.

- HTTP Method: `POST`
- Endpoint: `/purchases/edit`

**Parameters**
| Name | Type| Required | Description |
| :-------- | :----------| :----------:| :----------|
| request_body | EditPurchaseRequest | ❌ | The request body. |

**Return Type**

`EditPurchaseOkResponse`

**Example Usage Code Snippet**

```py
from celitech import Celitech, Environment
from celitech.models import EditPurchaseRequest

sdk = Celitech(
    base_url=Environment.DEFAULT.value
)

request_body = EditPurchaseRequest(**{
    "purchase_id": "ae471106-c8b4-42cf-b83a-b061291f2922",
    "start_date": "2023-11-01",
    "end_date": "2023-11-20",
    "start_time": 8.76,
    "end_time": 4.68
})

result = sdk.purchases.edit_purchase(request_body=request_body)

print(result)
```

#### **get_purchase_consumption**

This endpoint can be called for consumption notifications (e.g. every 1 hour or when the user clicks a button). It returns the data balance (consumption) of purchased packages.

- HTTP Method: `GET`
- Endpoint: `/purchases/{purchaseId}/consumption`

**Parameters**
| Name | Type| Required | Description |
| :-------- | :----------| :----------:| :----------|
| purchaseId | str | ✅ | This endpoint can be called for consumption notifications (e.g. every 1 hour or when the user clicks a button). It returns the data balance (consumption) of purchased packages. |

**Return Type**

`GetPurchaseConsumptionOkResponse`

**Example Usage Code Snippet**

```py
from celitech import Celitech, Environment

sdk = Celitech(
    base_url=Environment.DEFAULT.value
)

result = sdk.purchases.get_purchase_consumption(purchase_id="4973fa15-6979-4daa-9cf3-672620df819c")

print(result)
```

### ESimService

A list of all methods in the `ESimService` service. Click on the method name to view detailed information about that method.

| Methods                               | Description                            |
| :------------------------------------ | :------------------------------------- |
| [get_esim](#get_esim)                 | Get status from eSIM                   |
| [get_esim_device](#get_esim_device)   | Get device info from an installed eSIM |
| [get_esim_history](#get_esim_history) | Get history from an eSIM               |
| [get_esim_mac](#get_esim_mac)         | Get MAC from eSIM                      |

#### **get_esim**

Get status from eSIM

- HTTP Method: `GET`
- Endpoint: `/esim`

**Parameters**
| Name | Type| Required | Description |
| :-------- | :----------| :----------:| :----------|
| iccid | str | ✅ | Get status from eSIM |

**Return Type**

`GetEsimOkResponse`

**Example Usage Code Snippet**

```py
from celitech import Celitech, Environment

sdk = Celitech(
    base_url=Environment.DEFAULT.value
)

result = sdk.e_sim.get_esim(iccid="1111222233334444555")

print(result)
```

#### **get_esim_device**

Get device info from an installed eSIM

- HTTP Method: `GET`
- Endpoint: `/esim/{iccid}/device`

**Parameters**
| Name | Type| Required | Description |
| :-------- | :----------| :----------:| :----------|
| iccid | str | ✅ | Get device info from an installed eSIM |

**Return Type**

`GetEsimDeviceOkResponse`

**Example Usage Code Snippet**

```py
from celitech import Celitech, Environment

sdk = Celitech(
    base_url=Environment.DEFAULT.value
)

result = sdk.e_sim.get_esim_device(iccid="1111222233334444555")

print(result)
```

#### **get_esim_history**

Get history from an eSIM

- HTTP Method: `GET`
- Endpoint: `/esim/{iccid}/history`

**Parameters**
| Name | Type| Required | Description |
| :-------- | :----------| :----------:| :----------|
| iccid | str | ✅ | Get history from an eSIM |

**Return Type**

`GetEsimHistoryOkResponse`

**Example Usage Code Snippet**

```py
from celitech import Celitech, Environment

sdk = Celitech(
    base_url=Environment.DEFAULT.value
)

result = sdk.e_sim.get_esim_history(iccid="1111222233334444555")

print(result)
```

#### **get_esim_mac**

Get MAC from eSIM

- HTTP Method: `GET`
- Endpoint: `/esim/{iccid}/mac`

**Parameters**
| Name | Type| Required | Description |
| :-------- | :----------| :----------:| :----------|
| iccid | str | ✅ | Get MAC from eSIM |

**Return Type**

`GetEsimMacOkResponse`

**Example Usage Code Snippet**

```py
from celitech import Celitech, Environment

sdk = Celitech(
    base_url=Environment.DEFAULT.value
)

result = sdk.e_sim.get_esim_mac(iccid="1111222233334444555")

print(result)
```
