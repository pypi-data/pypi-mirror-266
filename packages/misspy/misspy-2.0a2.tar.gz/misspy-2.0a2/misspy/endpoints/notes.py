from typing import List, Union
import traceback

import pydantic
import orjson

from ..core.exception import NotFound
from ..core.http import AsyncHttpHandler
from ..core.types.note import Note
from mitypes.poll import Poll
from mitypes.drive import DriveFile
from ..utils.internaltool import nonecheck

class notes:
    def __init__(
        self, address: str, i: Union[str, None], ssl: bool, endpoints: List[str], handler: AsyncHttpHandler=None
    ) -> None:
        self.http = handler
        if handler is None:
            self.http = AsyncHttpHandler(address, i, ssl)
        self.endpoints = endpoints

    async def create(
        self,
        text: Union[str, None] = None,
        visibility: str = "public",
        visibleUserIds: List[str] = [],
        cw: Union[str, None] = None,
        localOnly: bool = False,
        noExtractMentions: bool = False,
        noExtractHashtags: bool = False,
        noExtractEmojis: bool = False,
        fileIds: Union[List[DriveFile], None] = None,
        replyId: Union[str, None] = None,
        renoteId: Union[str, None] = None,
        channelId: Union[str, None] = None,
        poll: Union[Poll, None] = None,
    ) -> Note:
        """Create a post. Replies and Renotes are also made using this function.

        Args:
            text (Union[str, None], optional): The text of the post. Defaults to None.
            visibility (str, optional): Publication range of posts. Defaults to visibility.public.
            visibleUserIds (List[str], optional): A list of user IDs that can view the post. Applies only when visibility is 'specified'.
            cw (Union[str, None], optional): CW (Content Warning) of the post. Defaults to None.
            localOnly (bool, optional): If set to True, posts will only be posted locally. Defaults to False.
            noExtractMentions (bool, optional): If set to True, mentions will not be expanded from the body. Defaults to False.
            noExtractHashtags (bool, optional): If set to True, hashtags will not be expanded from the body. Defaults to False.
            noExtractEmojis (bool, optional): If set to True, emojis will not be expanded from the body. Defaults to False.
            fileIds (List[str], optional): The id of the file to attach to the post.
            replyId (Union[str, None], optional): The id of the post to reply to. Defaults to None.
            renoteId (Union[str, None], optional): ID of the post targeted for Renote. Defaults to None.
            channelId (Union[str, None], optional): ID of the channel to post to. Defaults to None.
            poll (Union[Poll, None], optional): Voting parameters. Defaults to None.

        Returns:
            Note: created Post.
        """
        endpoint = "notes/create"
        if endpoint not in self.endpoints:
            raise NotFound('endpoint "notes/create" is not found.')

        data = {
            "text": text,
            "visibility": visibility,
            "visibleUserIds": visibleUserIds,
            "cw": cw,
            "localOnly": localOnly,
            "noExtractMentions": noExtractMentions,
            "noExtractHashtags": noExtractHashtags,
            "noExtractEmojis": noExtractEmojis,
            "replyId": replyId,
            "renoteId": renoteId,
            "channelId": channelId,
        }
        if fileIds:
            fid = []
            for file in fileIds:
                fid.append(file.id)
            data["fileIds"] = fid
        if poll:
            data["poll"] = poll
        resp = await self.http.send(endpoint, data=data)
        try:
            return Note(**resp["createdNote"])
        except pydantic.ValidationError as e:
            exc = traceback.format_exc()
            raise ValueError(exc + "\n\nError JSON: " + orjson.dumps(resp).decode('utf-8'))

    async def delete(self, noteId: str) -> bool:
        """delete post.

        Args:
            noteId (str): Post id.

        Returns:
            bool: Hi
        """
        endpoint = "notes/delete"
        if endpoint not in self.endpoints:
            raise NotFound(f'endpoint "{endpoint}" is not found.')
        data = {"noteId": noteId}
        return await self.http.send(endpoint, data=data)

    async def conversation(self, noteId: str, limit: int = 10, offset: int = 0):
        """Retrieve relevant notes.

        Args:
            noteId (str): noteId.
            limit (int, optional): limit of Retrieve. Defaults to 10.
            offset (int, optional): Skip the first offset of the result. Defaults to 0.

        Returns:
            _type_: _description_
        """
        endpoint = "notes/conversation"
        if endpoint not in self.endpoints:
            raise NotFound(f'endpoint "{endpoint}" is not found.')
        return await self.http.send(
            endpoint,
            {"noteId": noteId, "limit": limit, "offset": offset},
        )
    
    async def global_timeline(
        self,
        withFiles=False,
        limit=10,
        sinceId=None,
        untilId=None,
        sinceDate=None,
        untilDate=None,
    ):
        """Get the Global Timeline (GTL). The global timeline contains all public posts received by the server.

        Args:
            withFiles (bool, optional): If set to true, only notes with files attached will be retrieved.
            limit (int, optional): Specifies the maximum number of notes to be retrieved. Defaults to 10.
            sinceId (str, optional): If specified, returns notes whose id is greater than its value. Defaults to None.
            untilId (str, optional): If specified, returns notes whose id is less than the value. Defaults to None.
            sinceDate (int, optional): If you specify a date and time in epoch seconds, it returns notes created after that date and time.
            untilDate (int, optional): If you specify a date and time in epoch seconds, it returns notes created before that date and time.

        Returns:
            List (in Note): notes dict
        """
        base = {"withFiles": withFiles, "limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        if nonecheck(sinceDate):
            base["sinceDate"] = sinceDate
        if nonecheck(untilDate):
            base["untilDate"] = untilDate
        n = []
        _notes = await self.http.send("notes/global-timeline", base)
        for note in _notes:
            n.append(Note(**note))
        return n


    async def hybrid_timeline(
        self,
        limit=10,
        sinceId=None,
        untilId=None,
        sinceDate=None,
        untilDate=None,
        includeMyRenotes=True,
        includeRenotedMyNotes=True,
        includeLocalRenotes=True,
        withFiles=False,
    ):
        """Get the social Timeline (STL). The social timeline includes all public notes in the server and those of users you follow.

        Args:
            limit (int, optional): Specifies the maximum number of notes to be retrieved. Defaults to 10.
            sinceId (str, optional): If specified, returns notes whose id is greater than its value. Defaults to None.
            untilId (str, optional): If specified, returns notes whose id is less than the value. Defaults to None.
            sinceDate (int, optional): If you specify a date and time in epoch seconds, it returns notes created after that date and time.
            untilDate (int, optional): If you specify a date and time in epoch seconds, it returns notes created before that date and time.
            includeMyRenotes (bool, optional): If true, include the renotes made by the currently logged in user.
            includeRenotedMyNotes (bool, optional): If true, include the Renotes posted by the currently logged in user.
            includeLocalRenotes (bool, optional): If true, include the renotes made by local users.
            withFiles (bool, optional): If set to true, only notes with files attached will be retrieved.

        Returns:
            List (in Dict): notes dict
        """
        base = {
            "withFiles": withFiles,
            "limit": limit,
            "includeMyRenotes": includeMyRenotes,
            "includeRenotedMyNotes": includeRenotedMyNotes,
            "includeLocalRenotes": includeLocalRenotes,
        }
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        if nonecheck(sinceDate):
            base["sinceDate"] = sinceDate
        if nonecheck(untilDate):
            base["untilDate"] = untilDate
        n = []
        _notes = await self.http.send("notes/hybrid-timeline", base)
        for note in _notes:
            n.append(Note(**note))
        return n


    async def home_timeline(
        self,
        limit=10,
        sinceId=None,
        untilId=None,
        sinceDate=None,
        untilDate=None,
        includeMyRenotes=True,
        includeRenotedMyNotes=True,
        includeLocalRenotes=True,
        withFiles=False,
    ):
        """Get Home Timeline (HTL). The home timeline contains the notes of the users you follow.

        Args:
            limit (int, optional): Specifies the maximum number of notes to be retrieved. Defaults to 10.
            sinceId (str, optional): If specified, returns notes whose id is greater than its value. Defaults to None.
            untilId (str, optional): If specified, returns notes whose id is less than the value. Defaults to None.
            sinceDate (int, optional): If you specify a date and time in epoch seconds, it returns notes created after that date and time.
            untilDate (int, optional): If you specify a date and time in epoch seconds, it returns notes created before that date and time.
            includeMyRenotes (bool, optional): If true, include the renotes made by the currently logged in user.
            includeRenotedMyNotes (bool, optional): If true, include the Renotes posted by the currently logged in user.
            includeLocalRenotes (bool, optional): If true, include the renotes made by local users.
            withFiles (bool, optional): If set to true, only notes with files attached will be retrieved.

        Returns:
            List (in Dict): notes dict
        """
        base = {
            "withFiles": withFiles,
            "limit": limit,
            "includeMyRenotes": includeMyRenotes,
            "includeRenotedMyNotes": includeRenotedMyNotes,
            "includeLocalRenotes": includeLocalRenotes,
        }
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        if nonecheck(sinceDate):
            base["sinceDate"] = sinceDate
        if nonecheck(untilDate):
            base["untilDate"] = untilDate
        n = []
        _notes = await self.http.send("notes/timeline", base)
        for note in _notes:
            n.append(Note(**note))
        return n

    async def local_timeline(
        self,
        withFiles=False,
        fileType=None,
        excludeNsfw=False,
        limit=10,
        sinceId=None,
        untilId=None,
        sinceDate=None,
        untilDate=None,
    ):
        """Get the Local Timeline (LTL). The local timeline contains all public notes in the server.
        
        Args:
            withFiles (bool, optional): If set to true, only notes with files attached will be retrieved.
            fileType (bool, optional): Retrieve only those posts with files of the specified type attached.
            excludeNsfw (bool, optional): If true, excludes notes with CWs and notes with NSFW-specified files attached, effective only if fileType is specified (notes with CWs without attachments are not excluded).
            limit (int, optional): Specifies the maximum number of notes to be retrieved. Defaults to 10.
            sinceId (str, optional): If specified, returns notes whose id is greater than its value. Defaults to None.
            untilId (str, optional): If specified, returns notes whose id is less than the value. Defaults to None.
            sinceDate (int, optional): If you specify a date and time in epoch seconds, it returns notes created after that date and time.
            untilDate (int, optional): If you specify a date and time in epoch seconds, it returns notes created before that date and time.
            includeMyRenotes (bool, optional): If true, include the renotes made by the currently logged in user.
            includeRenotedMyNotes (bool, optional): If true, include the Renotes posted by the currently logged in user.
            includeLocalRenotes (bool, optional): If true, include the renotes made by local users.

        Returns:
            List (in Dict): notes dict
        """
        base = {"withFiles": withFiles, "limit": limit, "excludeNsfw": excludeNsfw}
        if nonecheck(fileType):
            base["fileType"] = fileType
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        if nonecheck(sinceDate):
            base["sinceDate"] = sinceDate
        if nonecheck(untilDate):
            base["untilDate"] = untilDate
        n = []
        _notes = await self.http.send("notes/local-timeline", base)
        for note in _notes:
            n.append(Note(**note))
        return n


    async def featured(self, limit=10, offset=0):
        """Retrieves highlighted notes. Results are sorted in descending order of note creation time (latest first).

        Args:
            limit (int, optional): Maximum number of notes to be retrieved. Defaults to 10.
            offset (int, optional): The first offset of the search result is skipped. Defaults to 0.

        Returns:
            List (Dict): _description_
        """
        n = []
        _notes = await self.http.send("notes/featured", {"limit": limit, "offset": offset})
        for note in _notes:
            n.append(Note(**note))
        return n

    async def favorites_create(self, noteId):
        """create favorites.

        Args:
            noteId (str): noteId.

        Returns:
            Dict: _description_
        """
        return await self.http.send("notes/favorites/create", {"noteId": noteId})


    async def favorites_delete(self, noteId):
        """delete favorites

        Args:
            noteId (str): noteId.

        Returns:
            Dict: _description_
        """
        return await self.http.send("notes/favorites/delete", {"noteId": noteId})


    async def polls_recommendation(self, limit=10, offset=0):
        """Get a list of recommended notes with a survey.

        Args:
            limit (int, optional): Maximum number of notes to be retrieved. Defaults to 10.
            offset (int, optional): The first offset of the search result is skipped. Defaults to 0.

        Returns:
            _type_: _description_
        """
        return await self.http.send("notes/polls/recommendation", {"limit": limit, "offset": offset}
        )


    async def polls_vote(self, noteId, choice):
        """Vote in the notebook poll. To vote for multiple choices, change the choice and make multiple requests.

        Args:
            noteId (str): ID of the note to which the survey is attached.
            choice (str): Choices to vote on.

        Returns:
            _type_: _description_
        """
        return await self.http.send("notes/polls/vote", {"noteId": noteId, "choice": choice})


    async def reactions(
        self,
        noteId: str,
        type: str = None,
        limit: int = 10,
        offset: int = 0,
        sinceId: str = None,
        untilId: str = None,
    ):
        base = {"noteId": noteId, "type": type, "limit": limit, "offset": offset}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        return await self.http.send("notes/reactions", base)


    async def replies(
        self, noteId: str, sinceId: str = None, untilId: str = None, limit: int = 10
    ):
        base = {"noteId": noteId, "limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        return await self.http.send("notes/replies", base)


    async def search(
        self,
        reply=False,
        renote=False,
        withFiles=False,
        poll=False,
        sinceId=None,
        untilId=None,
        limit=10,
    ):
        base = {
            "reply": reply,
            "renote": renote,
            "withFiles": withFiles,
            "poll": poll,
            "limit": limit,
        }
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        return await self.http.send("notes/search-by-tag", base)


    async def search_by_tag(
        self,
        query,
        sinceId=None,
        untilId=None,
        limit=10,
        offset=0,
        host=None,
        userId=None,
        channelId=None,
    ):
        base = {
            "query": query,
            "offset": offset,
            "limit": limit,
            "host": host,
            "userId": userId,
            "channelId": channelId,
        }
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        return await self.http.send("notes/search", base)


    async def state(self, noteId):
        return await self.http.send("notes/state", {"noteId": noteId})


    async def show(self, noteId):
        return await self.http.send("notes/show", {"noteId": noteId})


    async def thread_muting_create(self, noteId):
        return await self.http.send("notes/thread-muting/create", {"noteId": noteId})


    async def thread_muting_delete(self, noteId):
        return await self.http.send("notes/thread-muting/delete", {"noteId": noteId})


    async def translate(self, noteId, targetLang):
        return await self.http.send("notes/translate", {"noteId": noteId, "targetLang": targetLang}
        )


    async def unrenote(self, noteId):
        return await self.http.send("notes/unrenote", {"noteId": noteId})


    async def user_list_timeline(
        self,
        listId,
        limit=10,
        sinceId=None,
        untilId=None,
        sinceDate=0,
        untilDate=0,
        includeMyRenotes=True,
        includeRenotedMyNotes=True,
        includeLocalRenotes=True,
        withFiles=False,
    ):
        base = {
            "listId": listId,
            "limit": limit,
            "sinceDate": sinceDate,
            "untilDate": untilDate,
            "includeMyRenotes": includeMyRenotes,
            "includeRenotedMyNotes": includeRenotedMyNotes,
            "includeLocalRenotes": includeLocalRenotes,
            "withFiles": withFiles,
        }
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        n = []
        _notes = await self.http.send("notes/user-list-timeline", base)
        for note in _notes:
            n.append(Note(**note))
        return n

    async def watching_create(self, noteId):
        return await self.http.send("notes/watching/create", {"noteId": noteId})


    async def watching_delete(self, noteId):
        return await self.http.send("notes/watching/delete", {"noteId": noteId})


    async def mentions(
        self, following=False, limit=10, sinceId=None, untilId=None, visibility=None
    ):
        base = {"following": following, "limit": limit}
        if nonecheck(sinceId):
            base["sinceId"] = sinceId
        if nonecheck(untilId):
            base["untilId"] = untilId
        if nonecheck(visibility):
            base["visibility"] = visibility
        return await self.http.send("notes/mentions", base)
