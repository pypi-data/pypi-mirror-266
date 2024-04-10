# Standard Library
import collections
import concurrent.futures
from typing import TYPE_CHECKING, Deque, Iterable

# 1st Party Libraries
from open_exchange.contants import MAX_ADDRESSES_PER_PROPERTY_VALUES_REQUEST, MAX_CONCURRENT_REQUESTS
from open_exchange.resource import APIResource
from open_exchange.types.data import property_values_fetch_params, property_values_response

if TYPE_CHECKING:
    # 1st Party Libraries
    from open_exchange.client import OpenExchangeClient


class PropertyValues(APIResource):
    def __init__(self, client: "OpenExchangeClient") -> None:
        super().__init__(client)
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS)

    def fetch(
        self,
        addresses: Iterable[property_values_fetch_params.Address],
        *,
        max_addresses_per_request: int = MAX_ADDRESSES_PER_PROPERTY_VALUES_REQUEST,
    ) -> Iterable[property_values_response.Result]:
        """
        Fetch property values for addresses

        Args:
          addresses: An array of address objects, each specifying a property location.

          max_addresses_per_request: The maximum number of addresses to include in each request.

        Returns:
          An iterator of property values results.
        """
        futures: Deque[concurrent.futures.Future] = collections.deque()
        address_iter = iter(addresses)

        def submit_request() -> None:
            chunked_addresses = []
            for address in address_iter:
                chunked_addresses.append(address)
                if len(chunked_addresses) >= max_addresses_per_request:
                    break
            if chunked_addresses:
                futures.append(
                    self._executor.submit(
                        self.request,
                        method="POST",
                        path="/data/property-values",
                        body={
                            "addresses": chunked_addresses,
                        },
                    )
                )

        # Submit initial requests. MAX_CONCURRENT_REQUESTS will be submitted and also queue up.
        for _ in range(MAX_CONCURRENT_REQUESTS * 2):
            submit_request()

        while futures:
            future = futures.popleft()
            response = future.result()
            submit_request()

            for result_dict in response["results"]:
                yield property_values_response.Result.parse_obj(result_dict)
