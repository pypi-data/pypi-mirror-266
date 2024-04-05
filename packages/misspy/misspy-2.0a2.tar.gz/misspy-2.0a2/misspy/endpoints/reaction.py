from typing import List, Union

from ..core.http import AsyncHttpHandler

class reactions:
    def __init__(
        self, address: str, i: Union[str, None], ssl: bool, endpoints: List[str], handler: AsyncHttpHandler=None
    ) -> None:
        self.http = handler
        if handler is None:
            self.http = AsyncHttpHandler(address, i, ssl)
        self.endpoints = endpoints

    async def create(self, reaction: str, noteId: str) -> None:
        """create reaction.

        Args:
            address (string): instance address
            i (string): user token
            noteId (string): noteId
            reaction (string): Specify reaction. Reactions are Unicode emojis or custom emojis. For custom emoji, enclose the emoji name with a colon.

        Returns:
            dict: Misskey API response
        """
        return await self.http.send(
            "notes/reactions/create", {"noteId": noteId, "reaction": reaction}
        )


    async def delete(self, noteId) -> None:
        """delete reaction.

        Args:
            address (string): instance address
            i (string): user token
            noteId (string): noteId

        Returns:
            dict: Misskey API response
        """
        return await self.http.send("notes/reactions/delete", {"noteId": noteId})