# Standard Library
from typing import List

# 1st Party Libraries
import open_exchange
from open_exchange.types.data import property_details_fetch_params, property_details_response

client = open_exchange.OpenExchangeClient(
    # Set API key below or set the OPEN_EXCHANGE_API_KEY environment variable.
    # api_key="my-api-key"
)

addresses: List[property_details_fetch_params.Address] = [
    {
        "street": "5201 South 44th St",
        "city": "Omaha",
        "state": "NE",
        "postal_code": "68107",
        "token": "client-provided-token-0",  # This client-provided token is optional and can be any string.
    }
]

# Type hints
address: property_details_fetch_params.Address
result: property_details_response.Result

for (address, result) in zip(addresses, client.data.property_details.fetch(addresses=addresses)):
    print("input address:", address)
    print("token:", result.token)

    if result.property_details:
        output_address = {
            "street": result.property_details.street,
            "city": result.property_details.city,
            "state": result.property_details.state,
            "postal_code": result.property_details.postal_code,
        }
        print("Output address:", output_address)
        print("Subject property details:", result.property_details.json(indent=2))
    else:
        print("No property details available for this address.")
