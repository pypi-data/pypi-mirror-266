from typing import List, Union

from ..core.exception import NotFound
from ..core.http import AsyncHttpHandler
from ..core.types.drive import DriveFile


class drive:
    def __init__(
        self,
        address: str,
        i: Union[str, None],
        ssl: bool,
        endpoints: List[str],
        handler: AsyncHttpHandler = None,
    ) -> None:
        self.http = handler
        if handler is None:
            self.http = AsyncHttpHandler(address, i, ssl)
        self.endpoints = endpoints

    async def files(
        self,
        limit: int = 10,
        sinceId: str = None,
        untilId: str = None,
        folderId: Union[str, None] = None,
        type: Union[str, None] = None,
    ) -> List[DriveFile]:
        """Obtains a list of files in the specified folder or root hierarchy under the logged-in user's drive.

        Args:
            limit (int, optional): Maximum number of files to retrieve. Defaults to 10.
            sinceId (str, optional): If specified, returns files whose id is greater than that value. Defaults to None.
            untilId (str, optional): If specified, returns files whose id is less than that value. Defaults to None.
            folderId (Union[str, None], optional): If the id of the parent folder is null (default), files in the root hierarchy are retrieved. Defaults to None.
            type (Union[str, None], optional): The MIME type of the file. Defaults to None.

        Returns:
            List[DriveFile]: Files
        """
        endpoint = "drive/files"
        if endpoint not in self.endpoints:
            raise NotFound('endpoint "drive/files" is not found.')
        data = {"limit": limit, "folderId": folderId, "type": type}
        if sinceId:
            data["sinceId"] = sinceId
        if untilId:
            data["untilId"] = untilId
        resp = await self.http.send(endpoint, data=data)
        dfiles = []
        for res in resp:
            dfiles.append(DriveFile(**res))
        return dfiles

    async def files_create(self, path: str) -> DriveFile:
        """Uploads files to the drive of the currently logged-in user.

        Args:
            path (str): file path.

        Returns:
            DriveFile: created file.
        """
        endpoint = "drive/files/create"
        if endpoint not in self.endpoints:
            raise NotFound('endpoint "drive/files/create" is not found.')
        with open(path, "rb") as f:
            return DriveFile(**await self.http.send(endpoint, data={"file": f}))

    async def files_delete(self, fileId: str) -> bool:
        """delete files.

        Args:
            fileId (str): drive file id.

        Returns:
            bool: Hi
        """
        endpoint = "drive/files/delete"
        if endpoint not in self.endpoints:
            raise NotFound('endpoint "drive/files/delete" is not found.')
        return await self.http.send(endpoint, data={"fileId": fileId})
