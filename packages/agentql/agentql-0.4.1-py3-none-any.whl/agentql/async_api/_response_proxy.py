import asyncio
import json
import logging
from typing import Generic, Union

from agentql import AttributeNotFoundError, ContainerListNode, ContainerNode, IdListNode, IdNode

from ._web_driver import InteractiveItemTypeT, WebDriver

log = logging.getLogger("agentql")


class AQLResponseProxy(Generic[InteractiveItemTypeT]):
    """
    AQLResponseProxy class acts as a dynamic proxy to the response received from AgentQL server. It allows users to interact with resulting web elements and to retrieve their text contents. This class is designed to work with the web driver to fetch and process query results.
    """

    def __init__(
        self,
        data: dict,
        web_driver: "WebDriver[InteractiveItemTypeT]",
        query_tree: ContainerNode,
    ):
        self._response_data = data
        self._web_driver = web_driver
        self._query_tree_node = query_tree

    def __getattr__(
        self, name
    ) -> Union["AQLResponseProxy[InteractiveItemTypeT]", InteractiveItemTypeT]:
        if self._response_data is None:
            raise AttributeError("Response data is None")
        if name not in self._response_data:
            raise AttributeNotFoundError(name, self._response_data)
        return self._resolve_item(
            self._response_data[name], self._query_tree_node.get_child_by_name(name)
        )

    def __getitem__(
        self, index: int
    ) -> Union[InteractiveItemTypeT, "AQLResponseProxy[InteractiveItemTypeT]"]:
        if not isinstance(self._response_data, list):
            raise ValueError("This node is not a list")
        return self._resolve_item(self._response_data[index], self._query_tree_node)

    def _resolve_item(
        self, item, query_tree_node
    ) -> Union[InteractiveItemTypeT, "AQLResponseProxy[InteractiveItemTypeT]"]:
        if item is None:
            return None

        if isinstance(item, list):
            return AQLResponseProxy[InteractiveItemTypeT](item, self._web_driver, query_tree_node)

        if isinstance(query_tree_node, IdNode) or isinstance(query_tree_node, IdListNode):
            return self._web_driver.locate_interactive_element(item)

        return AQLResponseProxy[InteractiveItemTypeT](item, self._web_driver, query_tree_node)

    def __len__(self):
        if self._response_data is None:
            return 0
        return len(self._response_data)

    def __str__(self):
        return json.dumps(self._response_data, indent=2)

    async def to_data(self) -> dict:
        """Converts the response data into a structured dictionary based on the query tree.

        Returns:
        --------
        dict: A structured dictionary representing the processed response data, with fact nodes replaced by name (values) from the response data. It will have the following structure:

        ```py
        {
        "query_field": "text content of the corresponding web element"
        }
        ```
        """
        return await self._to_data_node(self._response_data, self._query_tree_node)

    async def _to_data_node(self, response_data, query_tree_node) -> dict:
        if isinstance(query_tree_node, ContainerListNode):
            return await self._to_data_container_list_node(response_data, query_tree_node)
        elif isinstance(query_tree_node, ContainerNode):
            return await self._to_data_container_node(response_data, query_tree_node)
        elif isinstance(query_tree_node, IdListNode):
            return await self._to_data_id_list_node(response_data)
        elif isinstance(query_tree_node, IdNode):
            return await self._to_data_id_node(response_data)
        else:
            raise TypeError("Unsupported query tree node type")

    async def _to_data_container_node(
        self, response_data: dict, query_tree_node: ContainerNode
    ) -> dict:
        tasks = []
        children = []

        for child_name, child_data in response_data.items():
            child_query_tree = query_tree_node.get_child_by_name(child_name)

            task = asyncio.create_task(self._to_data_node(child_data, child_query_tree))
            tasks.append(task)
            children.append(child_name)

        # run all tasks concurrently.
        results = await asyncio.gather(*tasks)

        return {child_name: result for result, child_name in zip(results, children)}

    async def _to_data_container_list_node(
        self, response_data: dict, query_tree_node: ContainerListNode
    ) -> list:
        tasks = [self._to_data_container_node(item, query_tree_node) for item in response_data]
        result_list = await asyncio.gather(*tasks)
        return result_list

    async def _to_data_id_node(self, response_data: dict) -> dict:
        if response_data is None:
            return None
        name = response_data.get("name")
        if not name or not name.strip():
            web_element = self._web_driver.locate_interactive_element(response_data)
            if not web_element:
                log.warning(f"Could not locate web element for item {response_data}")
                return None
            element_text = await self._web_driver.get_text_content(web_element)
            name = element_text.strip()
        return name

    async def _to_data_id_list_node(self, response_data: list) -> list:
        tasks = [self._to_data_id_node(item) for item in response_data]
        res = await asyncio.gather(*tasks)
        return [node for node in res if node is not None]
