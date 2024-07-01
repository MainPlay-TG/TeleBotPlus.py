import inspect
import telebot
import telebot.async_telebot
# from datetime import datetime, timedelta
# from queue import Queue
# from threading import Thread
# from time import sleep
from . import utils
from .assets import Assets
from telebot.types import *
from typing import *
args_names: dict[str, tuple] = {}
for attr_name in dir(telebot.TeleBot):
  attr = getattr(telebot.TeleBot, attr_name)
  if callable(attr):
    try:
      attr_sign = inspect.signature(attr)
      args_names[attr_name] = []
      for i in attr_sign.parameters.keys():
        if i != "self":
          args_names[attr_name].append(i)
    except Exception:
      pass
del attr
del attr_name
del attr_sign


class _Action:
  def __init__(self, func, args=(), kwargs={}, is_async: bool = False):
    self.args = args
    self.func = func
    self.kwargs = kwargs
    if is_async:
      self.__call__ = self.async_run
    else:
      self.__call__ = self.run

  async def async_run(self):
    return await self.func(*self.args, **self.kwargs)

  def run(self):
    return self.func(*self.args, **self.kwargs)

  def set_args(self, *args, **kwargs):
    self.args = args
    self.kwargs = kwargs


class TeleBotPlus(telebot.TeleBot):
  TELEBOT_TESTED_VERSIONS = ()
  TELEBOT_COMPATIBLE_VERSIONS = ()

  def __init__(self,
               token: str,
               parse_mode: Optional[str] = None,
               threaded: Optional[bool] = True,
               skip_pending: Optional[bool] = False,
               num_threads: Optional[int] = 2,
               next_step_backend: Optional[telebot.HandlerBackend] = None,
               reply_backend: Optional[telebot.HandlerBackend] = None,
               exception_handler: Optional[telebot.ExceptionHandler] = None,
               last_update_id: Optional[int] = 0,
               suppress_middleware_excepions: Optional[bool] = False,
               state_storage: Optional[telebot.StateStorageBase] = telebot.StateMemoryStorage(),
               use_class_middlewares: Optional[bool] = False,
               disable_web_page_preview: Optional[bool] = None,
               disable_notification: Optional[bool] = None,
               protect_content: Optional[bool] = None,
               allow_sending_without_reply: Optional[bool] = None,
               colorful_logs: Optional[bool] = False,
               **kw):
    args = locals()
    for i in args_names["__init__"]:
      if i in args:
        kw[i] = args[i]
    kw["self"] = self
    # self.MAX_CHATMESSAGES_PER_MINUTE = 20  # Максимум сообщений в минуту на чат
    # self.MAX_REQUESTS_PER_SECOND = 30  # Максимум запросов в секунду
    self.stats = {}  # Статистика использования изменённых функций
    telebot.TeleBot.__init__(**kw)  # Создание оригинального бота
    self.assets = Assets(bot=self.bot)  # Загрузка ассетов
    # self.queue = Queue()  # Очередь
    # self.queue_thread = Thread(target=self._queue_sender, daemon=False)
    # self.queue_thread.start()  # Запуск обработчика очереди
    names = {
        "send_document": ["send_doc", "send_file"],
        "send_message": ["send_msg", "send_text"],
    }
    for k, v in names.items():
      if hasattr(self, k):
        for i in v:
          setattr(self, i, getattr(self, k))  # Сокращение названий функций

  def __getattr__(self, k: str):
    """Если функция отсутствует, будет использована из оригинального бота"""
    if k in self.__dict__:
      return self.__dict__[k]
    else:
      return getattr(self.bot, k)

  def __hasattr__(self, k: str):
    if k in self.__dict__:
      return True
    else:
      return hasattr(self.bot, k)

  def __dir__(self, *, original: bool = True, patched: bool = True):
    result = []
    if original:
      for i in dir(self.bot):
        if not i in result:
          result.append(i)
    if patched:
      for i in self.__dict__.keys():
        if not i in result:
          result.append(i)
    return result

  def _is_patched(self, k: str):
    """Изменён ли аттрибут или взят из оригинала"""
    if k in self.__dict__:
      return True
    return False

  def _call_original(self, _name, *args, **kwargs):
    """Вызвать функцию оригинального бота"""
    kwargs["self"] = self
    result = getattr(telebot.TeleBot, _name)(*args, **kwargs)
    if not _name in self.stats:
      self.stats[_name] = 0
    self.stats[_name] += 1
    return result

  # def _queue_sender(self):
    # """Пока что ограничения не установлены"""
    # while True:
    # if not self.queue.empty():
    # item = self.queue.get()
    # if item == exit:  # Прекратить обработку очереди
    # break
    # item()
    # sleep(1 / self.MAX_REQUESTS_PER_SECOND)

  def send_document(self,
                    chat_id: Union[int, str],
                    document: Union[Any, str],
                    reply_to_message_id: Optional[int] = None,
                    caption: Optional[str] = None,
                    reply_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None,
                    parse_mode: Optional[str] = None,
                    disable_notification: Optional[bool] = None,
                    timeout: Optional[int] = None,
                    thumbnail: Optional[Union[Any, str]] = None,
                    caption_entities: Optional[List[MessageEntity]] = None,
                    allow_sending_without_reply: Optional[bool] = None,
                    visible_file_name: Optional[str] = None,
                    disable_content_type_detection: Optional[bool] = None,
                    data: Optional[Union[Any, str]] = None,
                    protect_content: Optional[bool] = None,
                    message_thread_id: Optional[int] = None,
                    thumb: Optional[Union[Any, str]] = None,
                    reply_parameters: Optional[ReplyParameters] = None,
                    business_connection_id: Optional[str] = None,
                    message_effect_id: Optional[str] = None,
                    auto_close_file: bool = True,
                    **kw,
                    ) -> Message:
    args = locals()
    for i in args_names["send_document"]:
      if i in args:
        kw[i] = args[i]
    asset = None
    if type(chat_id) in [Chat, User]:
      kw["chat_id"] = chat_id.id
    if type(document) == "str":
      if len(document) == self.assets.ID_LEN:
        asset = self.assets.get(document, "document", bot=self.bot)
        if asset != None:
          kw["document"] = asset["file"]
          if visible_file_name == None:
            kw["visible_file_name"] = asset["name"]
    result: Message = self._call_original("send_document", **kw)
    if asset != None:
      self.assets.set_file_id(asset["id"], result.document.file_id, "document", bot=self.bot)
    if auto_close_file:
      if hasattr(kw["document"], "close"):
        if callable(kw["document"].close):
          kw["document"].close()
    return result

  def send_photo(self,
                 chat_id: Union[int, str],
                 photo: Union[Any, str],
                 caption: Optional[str] = None,
                 parse_mode: Optional[str] = None,
                 caption_entities: Optional[List[MessageEntity]] = None,
                 disable_notification: Optional[bool] = None,
                 protect_content: Optional[bool] = None,
                 reply_to_message_id: Optional[int] = None,
                 allow_sending_without_reply: Optional[bool] = None,
                 reply_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None,
                 timeout: Optional[int] = None,
                 message_thread_id: Optional[int] = None,
                 has_spoiler: Optional[bool] = None,
                 reply_parameters: Optional[ReplyParameters] = None,
                 business_connection_id: Optional[str] = None,
                 message_effect_id: Optional[str] = None,
                 show_caption_above_media: Optional[bool] = None,
                 auto_close_file: bool = True,
                 **kw,
                 ) -> Message:
    args = locals()
    for i in args_names["send_photo"]:
      if i in args:
        kw[i] = args[i]
    asset = None
    if type(chat_id) in [Chat, User]:
      kw["chat_id"] = chat_id.id
    if type(photo) == "str":
      if len(photo) == self.assets.ID_LEN:
        asset = self.assets.get(photo, "photo", bot=self.bot)
        if asset != None:
          kw["photo"] = asset["file"]
    result: Message = self._call_original("send_photo", **kw)
    if asset != None:
      self.assets.set_file_id(asset["id"], result.photo[-1].file_id, "photo", bot=self.bot)
    if auto_close_file:
      if hasattr(kw["photo"], "close"):
        if callable(kw["photo"].close):
          kw["photo"].close()
    return result
