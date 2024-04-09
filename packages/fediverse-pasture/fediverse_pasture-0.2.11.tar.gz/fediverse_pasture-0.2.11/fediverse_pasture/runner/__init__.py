# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import asyncio
import logging

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, List
from secrets import token_urlsafe

from bovine import BovineActor
from bovine.activitystreams import (
    ActivityFactory,
    ObjectFactory,
    factories_for_actor_object,
)
from bovine.utils import now_isoformat

from fediverse_pasture.types import ApplicationAdapterForLastActivity

logger = logging.getLogger(__name__)


@dataclass
class ActivitySender:
    """The ActivitySender class serves as a way to coordinate the process
    of sending the same activity to multiple Fediverse applications.

    The basic process is

    * Create an Activity with a published timestamp stored in published
    * Send this activity to applications using `send`
    * Retrieve the result from said applications

    The usual way to create an ActivitySender is the `for_actor` method,
    i.e.

    ```python
    activity_sender = ActivitySender.for_actor(bovine_actor, actor_object)
    ```
    """

    activity_factory: ActivityFactory
    object_factory: ObjectFactory
    bovine_actor: BovineActor
    make_id: Callable

    published: datetime | None = None
    note: dict | None = None
    activity: dict | None = None
    object_id: str | None = None

    sleep_after_getting_inbox: bool = True

    def init_create_note(self, modifier: Callable[[dict], dict]):
        """Sets activity to a Create for a Note. Here the Note is
        constructed from a skeleton by applying `modifier` to it.
        To successfully send the note to most applications, modifier
        should set the Note's content, i.e.

        ```python
        sender.init_create_note(lambda x: {**x, "content": "text"})
        ```

        This method can be used to create objects of other types
        by overriding "type".
        """
        published = now_isoformat()
        self.object_id = self.make_id()

        note = self.object_factory.note(
            id=self.object_id,
            to={"as:Public"},
            published=published,
        ).build()
        del note["@context"]
        self.note = modifier(note)
        self.published = datetime.fromisoformat(published.removesuffix("Z"))

    async def send(self, remote: str):
        """Sends the activity to the remote user

        :param remote: Actor URI of the remote user"""

        try:
            note = {
                **self.note,
            }
            note["to"] = note["to"] + [remote]

            create = self.activity_factory.create(note, id=self.make_id()).build()

            create["@context"] = [
                create["@context"],
                {"Hashtag": "as:Hashtag", "sensitive": "as:sensitive"},
            ]
            self.activity = create

            remote_inbox = (await self.bovine_actor.get(remote))["inbox"]

            if self.sleep_after_getting_inbox:
                #
                # See https://codeberg.org/helge/funfedidev/issues/138#issuecomment-1640700
                #
                await asyncio.sleep(0.1)

            return await self.bovine_actor.post(remote_inbox, create)
        except Exception as e:
            logger.warning("Posting to inbox of %s failed with %s", remote, repr(e))
            return None

    @staticmethod
    def for_actor(bovine_actor, actor_object):
        """Initializes the Activity Sender object for a given BovineActor
        and the corresponding actor object"""
        activity_factory, object_factory = factories_for_actor_object(
            actor_object.build()
        )

        def make_id():
            return actor_object.id + "/" + token_urlsafe(8)

        return ActivitySender(
            activity_factory=activity_factory,
            object_factory=object_factory,
            bovine_actor=bovine_actor,
            make_id=make_id,
        )


@dataclass
class ActivityRunner:
    """Coordinates sending an activity to many applications through an ActivitySender
    instances

    :param activity_sender: an activity sender
    :param applications: list of applications to run against"""

    activity_sender: ActivitySender
    applications: List[ApplicationAdapterForLastActivity]

    wait_time: float = 0.5
    """Time in seconds between trying to fetch the activity from remote servers"""

    tries: int = 20
    """Number of tries to fetch activity from remote servers"""

    skip_fetch: bool = False
    """Skips fetching the result"""

    async def fetch_activity(self, application, object_id):
        for _ in range(self.tries):
            result = await application.fetch_activity(object_id)
            if result:
                return result
            await asyncio.sleep(self.wait_time)

    async def run_for_modifier(self, modifier: Callable[[dict], dict]):
        """modifier has the same format as for ActivitySender

        :param modifier: modifies the base object being send"""
        self.activity_sender.init_create_note(modifier)

        async with asyncio.TaskGroup() as tg:
            for application in self.applications:
                tg.create_task(self.activity_sender.send(application.actor_uri))

        if self.skip_fetch:
            return

        await asyncio.sleep(self.wait_time)

        result = {"activity": self.activity_sender.activity}

        for application in self.applications:
            result[application.application_name] = await self.fetch_activity(
                application, self.activity_sender.object_id
            )

        return result
