#  Pyroru - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyroru.
#
#  Pyroru is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyroru is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyroru.  If not, see <http://www.gnu.org/licenses/>.

import inspect
import re
from typing import Callable, Union, List, Pattern

import pyroru
from pyroru import enums
from pyroru.types import Message, CallbackQuery, InlineQuery, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update


class Filter:
    async def __call__(self, client: "pyroru.Client", update: Update):
        raise NotImplementedError

    def __invert__(self):
        return InvertFilter(self)

    def __and__(self, other):
        return AndFilter(self, other)

    def __or__(self, other):
        return OrFilter(self, other)


class InvertFilter(Filter):
    def __init__(self, base):
        self.base = base

    async def __call__(self, client: "pyroru.Client", update: Update):
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(client, update)
        else:
            x = await client.loop.run_in_executor(
                client.executor,
                self.base,
                client, update
            )

        return not x


class AndFilter(Filter):
    def __init__(self, base, other):
        self.base = base
        self.other = other

    async def __call__(self, client: "pyroru.Client", update: Update):
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(client, update)
        else:
            x = await client.loop.run_in_executor(
                client.executor,
                self.base,
                client, update
            )

        # short circuit
        if not x:
            return False

        if inspect.iscoroutinefunction(self.other.__call__):
            y = await self.other(client, update)
        else:
            y = await client.loop.run_in_executor(
                client.executor,
                self.other,
                client, update
            )

        return x and y


class OrFilter(Filter):
    def __init__(self, base, other):
        self.base = base
        self.other = other

    async def __call__(self, client: "pyroru.Client", update: Update):
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(client, update)
        else:
            x = await client.loop.run_in_executor(
                client.executor,
                self.base,
                client, update
            )

        # short circuit
        if x:
            return True

        if inspect.iscoroutinefunction(self.other.__call__):
            y = await self.other(client, update)
        else:
            y = await client.loop.run_in_executor(
                client.executor,
                self.other,
                client, update
            )

        return x or y


CUSTOM_FILTER_NAME = "CustomFilter"


def create(func: Callable, name: str = None, **kwargs) -> Filter:
    return type(
        name or func.__name__ or CUSTOM_FILTER_NAME,
        (Filter,),
        {"__call__": func, **kwargs}
    )()


# region all_filter
async def all_filter(_, __, ___):
    return True


all = create(all_filter)


# endregion

# region me_filter
async def me_filter(_, __, m: Message):
    return bool(m.from_user and m.from_user.is_self or getattr(m, "outgoing", False))


me = create(me_filter)

# endregion

# region bot_filter
async def bot_filter(_, __, m: Message):
    return bool(m.from_user and m.from_user.is_bot)


bot = create(bot_filter)


# endregion

# region incoming_filter
async def incoming_filter(_, __, m: Message):
    return not m.outgoing


incoming = create(incoming_filter)


# endregion

# region outgoing_filter
async def outgoing_filter(_, __, m: Message):
    return m.outgoing


outgoing = create(outgoing_filter)

# endregion

# region text_filter
async def text_filter(_, __, m: Message):
    return bool(m.text)


text = create(text_filter)

# endregion

# region reply_filter
async def reply_filter(_, __, m: Message):
    return bool(m.reply_to_message_id)


reply = create(reply_filter)

# endregion

# region forwarded_filter
async def forwarded_filter(_, __, m: Message):
    return bool(m.forward_date)


forwarded = create(forwarded_filter)

# endregion

# region caption_filter
async def caption_filter(_, __, m: Message):
    return bool(m.caption)


caption = create(caption_filter)

# endregion


# region audio_filter
async def audio_filter(_, __, m: Message):
    return bool(m.audio)


audio = create(audio_filter)

# endregion

# region document_filter
async def document_filter(_, __, m: Message):
    return bool(m.document)


document = create(document_filter)

# endregion

# region photo_filter
async def photo_filter(_, __, m: Message):
    return bool(m.photo)


photo = create(photo_filter)

# endregion

# region sticker_filter
async def sticker_filter(_, __, m: Message):
    return bool(m.sticker)


sticker = create(sticker_filter)

# endregion

# region animation_filter
async def animation_filter(_, __, m: Message):
    return bool(m.animation)


animation = create(animation_filter)

# endregion

# region game_filter
async def game_filter(_, __, m: Message):
    return bool(m.game)


game = create(game_filter)

# endregion

# region video_filter
async def video_filter(_, __, m: Message):
    return bool(m.video)


video = create(video_filter)

# endregion

# region media_group_filter
async def media_group_filter(_, __, m: Message):
    return bool(m.media_group_id)


media_group = create(media_group_filter)

# endregion

# region voice_filter
async def voice_filter(_, __, m: Message):
    return bool(m.voice)


voice = create(voice_filter)

# endregion

# region video_note_filter
async def video_note_filter(_, __, m: Message):
    return bool(m.video_note)


video_note = create(video_note_filter)

# endregion

# region contact_filter
async def contact_filter(_, __, m: Message):
    return bool(m.contact)


contact = create(contact_filter)

# endregion

# region location_filter
async def location_filter(_, __, m: Message):
    return bool(m.location)


location = create(location_filter)

# endregion

# region venue_filter
async def venue_filter(_, __, m: Message):
    return bool(m.venue)


venue = create(venue_filter)

# endregion

# region web_page_filter
async def web_page_filter(_, __, m: Message):
    return bool(m.web_page)


web_page = create(web_page_filter)

# endregion

# region poll_filter
async def poll_filter(_, __, m: Message):
    return bool(m.poll)


poll = create(poll_filter)

# endregion

# region dice_filter
async def dice_filter(_, __, m: Message):
    return bool(m.dice)


dice = create(dice_filter)

# endregion

# region media_spoiler
async def media_spoiler_filter(_, __, m: Message):
    return bool(m.has_media_spoiler)


media_spoiler = create(media_spoiler_filter)

# endregion

# region private_filter
async def private_filter(_, __, m: Message):
    return bool(m.chat and m.chat.type in {enums.ChatType.PRIVATE, enums.ChatType.BOT})


private = create(private_filter)

# endregion

# region group_filter
async def group_filter(_, __, m: Message):
    return bool(m.chat and m.chat.type in {enums.ChatType.GROUP, enums.ChatType.SUPERGROUP})


group = create(group_filter)

# endregion

# region channel_filter
async def channel_filter(_, __, m: Message):
    return bool(m.chat and m.chat.type == enums.ChatType.CHANNEL)


channel = create(channel_filter)

# endregion

# region new_chat_members_filter
async def new_chat_members_filter(_, __, m: Message):
    return bool(m.new_chat_members)


new_chat_members = create(new_chat_members_filter)

# endregion

# region left_chat_member_filter
async def left_chat_member_filter(_, __, m: Message):
    return bool(m.left_chat_member)


left_chat_member = create(left_chat_member_filter)

# endregion

# region new_chat_title_filter
async def new_chat_title_filter(_, __, m: Message):
    return bool(m.new_chat_title)


new_chat_title = create(new_chat_title_filter)

# endregion

# region new_chat_photo_filter
async def new_chat_photo_filter(_, __, m: Message):
    return bool(m.new_chat_photo)


new_chat_photo = create(new_chat_photo_filter)

# endregion

# region delete_chat_photo_filter
async def delete_chat_photo_filter(_, __, m: Message):
    return bool(m.delete_chat_photo)


delete_chat_photo = create(delete_chat_photo_filter)

# endregion

# region group_chat_created_filter
async def group_chat_created_filter(_, __, m: Message):
    return bool(m.group_chat_created)


group_chat_created = create(group_chat_created_filter)

# endregion

# region supergroup_chat_created_filter
async def supergroup_chat_created_filter(_, __, m: Message):
    return bool(m.supergroup_chat_created)


supergroup_chat_created = create(supergroup_chat_created_filter)

# endregion

# region channel_chat_created_filter
async def channel_chat_created_filter(_, __, m: Message):
    return bool(m.channel_chat_created)


channel_chat_created = create(channel_chat_created_filter)

# endregion

# region migrate_to_chat_id_filter
async def migrate_to_chat_id_filter(_, __, m: Message):
    return bool(m.migrate_to_chat_id)


migrate_to_chat_id = create(migrate_to_chat_id_filter)
"""Filter service messages that contain migrate_to_chat_id."""


# endregion

# region migrate_from_chat_id_filter
async def migrate_from_chat_id_filter(_, __, m: Message):
    return bool(m.migrate_from_chat_id)


migrate_from_chat_id = create(migrate_from_chat_id_filter)
"""Filter service messages that contain migrate_from_chat_id."""


# endregion

# region pinned_message_filter
async def pinned_message_filter(_, __, m: Message):
    return bool(m.pinned_message)


pinned_message = create(pinned_message_filter)
"""Filter service messages for pinned messages."""


# endregion

# region game_high_score_filter
async def game_high_score_filter(_, __, m: Message):
    return bool(m.game_high_score)


game_high_score = create(game_high_score_filter)
"""Filter service messages for game high scores."""


# endregion

# region reply_keyboard_filter
async def reply_keyboard_filter(_, __, m: Message):
    return isinstance(m.reply_markup, ReplyKeyboardMarkup)


reply_keyboard = create(reply_keyboard_filter)
"""Filter messages containing reply keyboard markups"""


# endregion

# region inline_keyboard_filter
async def inline_keyboard_filter(_, __, m: Message):
    return isinstance(m.reply_markup, InlineKeyboardMarkup)


inline_keyboard = create(inline_keyboard_filter)
"""Filter messages containing inline keyboard markups"""


# endregion

# region mentioned_filter
async def mentioned_filter(_, __, m: Message):
    return bool(m.mentioned)


mentioned = create(mentioned_filter)
"""Filter messages containing mentions"""


# endregion

# region via_bot_filter
async def via_bot_filter(_, __, m: Message):
    return bool(m.via_bot)


via_bot = create(via_bot_filter)
"""Filter messages sent via inline bots"""


# endregion

# region video_chat_started_filter
async def video_chat_started_filter(_, __, m: Message):
    return bool(m.video_chat_started)


video_chat_started = create(video_chat_started_filter)
"""Filter messages for started video chats"""


# endregion

# region video_chat_ended_filter
async def video_chat_ended_filter(_, __, m: Message):
    return bool(m.video_chat_ended)


video_chat_ended = create(video_chat_ended_filter)
"""Filter messages for ended video chats"""


# endregion

# region video_chat_members_invited_filter
async def video_chat_members_invited_filter(_, __, m: Message):
    return bool(m.video_chat_members_invited)


video_chat_members_invited = create(video_chat_members_invited_filter)
"""Filter messages for voice chat invited members"""


# endregion

# region service_filter
async def service_filter(_, __, m: Message):
    return bool(m.service)


service = create(service_filter)
"""Filter service messages.

A service message contains any of the following fields set: *left_chat_member*,
*new_chat_title*, *new_chat_photo*, *delete_chat_photo*, *group_chat_created*, *supergroup_chat_created*,
*channel_chat_created*, *migrate_to_chat_id*, *migrate_from_chat_id*, *pinned_message*, *game_score*,
*video_chat_started*, *video_chat_ended*, *video_chat_members_invited*.
"""


# endregion

# region media_filter
async def media_filter(_, __, m: Message):
    return bool(m.media)


media = create(media_filter)
"""Filter media messages.

A media message contains any of the following fields set: *audio*, *document*, *photo*, *sticker*, *video*,
*animation*, *voice*, *video_note*, *contact*, *location*, *venue*, *poll*.
"""


# endregion

# region scheduled_filter
async def scheduled_filter(_, __, m: Message):
    return bool(m.scheduled)


scheduled = create(scheduled_filter)
"""Filter messages that have been scheduled (not yet sent)."""


# endregion

# region from_scheduled_filter
async def from_scheduled_filter(_, __, m: Message):
    return bool(m.from_scheduled)


from_scheduled = create(from_scheduled_filter)
"""Filter new automatically sent messages that were previously scheduled."""


# endregion

# region linked_channel_filter
async def linked_channel_filter(_, __, m: Message):
    return bool(m.forward_from_chat and not m.from_user)


linked_channel = create(linked_channel_filter)

# endregion


# region command_filter
def command(commands: Union[str, List[str]], prefixes: Union[str, List[str]] = "/", case_sensitive: bool = False):
    command_re = re.compile(r"([\"'])(.*?)(?<!\\)\1|(\S+)")

    async def func(flt, client: pyroru.Client, message: Message):
        username = client.me.username or ""
        text = message.text or message.caption
        message.command = None

        if not text:
            return False

        for prefix in flt.prefixes:
            if not text.startswith(prefix):
                continue

            without_prefix = text[len(prefix):]

            for cmd in flt.commands:
                if not re.match(rf"^(?:{cmd}(?:@?{username})?)(?:\s|$)", without_prefix,
                                flags=re.IGNORECASE if not flt.case_sensitive else 0):
                    continue

                without_command = re.sub(rf"{cmd}(?:@?{username})?\s?", "", without_prefix, count=1,
                                         flags=re.IGNORECASE if not flt.case_sensitive else 0)

                # match.groups are 1-indexed, group(1) is the quote, group(2) is the text
                # between the quotes, group(3) is unquoted, whitespace-split text

                # Remove the escape character from the arguments
                message.command = [cmd] + [
                    re.sub(r"\\([\"'])", r"\1", m.group(2) or m.group(3) or "")
                    for m in command_re.finditer(without_command)
                ]

                return True

        return False

    commands = commands if isinstance(commands, list) else [commands]
    commands = {c if case_sensitive else c.lower() for c in commands}

    prefixes = [] if prefixes is None else prefixes
    prefixes = prefixes if isinstance(prefixes, list) else [prefixes]
    prefixes = set(prefixes) if prefixes else {""}

    return create(
        func,
        "CommandFilter",
        commands=commands,
        prefixes=prefixes,
        case_sensitive=case_sensitive
    )


# endregion

def regex(pattern: Union[str, Pattern], flags: int = 0):

    async def func(flt, _, update: Update):
        if isinstance(update, Message):
            value = update.text or update.caption
        elif isinstance(update, CallbackQuery):
            value = update.data
        elif isinstance(update, InlineQuery):
            value = update.query
        else:
            raise ValueError(f"Фильтр регулярных выражений не работает с {type(update)}")

        if value:
            update.matches = list(flt.p.finditer(value)) or None

        return bool(update.matches)

    return create(
        func,
        "RegexFilter",
        p=pattern if isinstance(pattern, Pattern) else re.compile(pattern, flags)
    )


# noinspection PyPep8Naming
class user(Filter, set):
    def __init__(self, users: Union[int, str, List[Union[int, str]]] = None):
        users = [] if users is None else users if isinstance(users, list) else [users]

        super().__init__(
            "me" if u in ["me", "self"]
            else u.lower().strip("@") if isinstance(u, str)
            else u for u in users
        )

    async def __call__(self, _, message: Message):
        return (message.from_user
                and (message.from_user.id in self
                     or (message.from_user.username
                         and message.from_user.username.lower() in self)
                     or ("me" in self
                         and message.from_user.is_self)))


# noinspection PyPep8Naming
class chat(Filter, set):

    def __init__(self, chats: Union[int, str, List[Union[int, str]]] = None):
        chats = [] if chats is None else chats if isinstance(chats, list) else [chats]

        super().__init__(
            "me" if c in ["me", "self"]
            else c.lower().strip("@") if isinstance(c, str)
            else c for c in chats
        )

    async def __call__(self, _, message: Message):
        return (message.chat
                and (message.chat.id in self
                     or (message.chat.username
                         and message.chat.username.lower() in self)
                     or ("me" in self
                         and message.from_user
                         and message.from_user.is_self
                         and not message.outgoing)))
