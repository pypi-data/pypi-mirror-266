# Author    : Nathan Chen
# Date      : 08-Apr-2024


from typing import Literal, Dict


EventInfo = Literal['signin', 'cancelSignin', 'signout', 'cancelSignout', 'changePassword', 'cancelChangePassword']


class Event:
    event: EventInfo

    def __init__(self, event: EventInfo) -> None:
        self.event = event

    def setattr(self, dict: Dict):
        for key, val in dict.items():
            self.__setattr__(key, val)


class SigninEvent(Event):
    event: EventInfo = 'signin'
    username: str
    password: str
    remember: bool

    def __init__(self) -> None:
        super().__init__('signin')
        self.remember = False

class CancelSigninEvent(Event):
    event: EventInfo = 'cancelSignin'

    def __init__(self) -> None:
        super().__init__('cancelSignin')

class SignoutEvent(Event):
    event: EventInfo = 'signout'

    def __init__(self) -> None:
        super().__init__('signout')

class CancelSignoutEvent(Event):
    event: EventInfo = 'cancelSignout'

    def __init__(self) -> None:
        super().__init__('cancelSignout')

class ChangePasswordEvent(Event):
    event: EventInfo = 'changePassword'

    def __init__(self) -> None:
        super().__init__('changePassword')

class CancelChangePasswordEvent(Event):
    event: EventInfo = 'cancelChangePassword'
    current: str
    new: str

    def __init__(self) -> None:
        super().__init__('cancelChangePassword')


def getEvent(value):
    if type(value) is not dict: return None
    info: EventInfo = value.get('event', None)
    if info == SigninEvent.event:
        event = SigninEvent()
        event.setattr(value)
    elif info == CancelSigninEvent.event:
        event = CancelSignoutEvent()
    elif info == SignoutEvent.event:
        event = SignoutEvent()
    elif info == CancelSignoutEvent.event:
        event = CancelSignoutEvent()
    elif info == ChangePasswordEvent.event:
        event = ChangePasswordEvent()
        event.setattr(value)
    elif info == CancelChangePasswordEvent.event:
        event = CancelChangePasswordEvent()
    else:
        event = None

    return event