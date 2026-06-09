from abc import ABC, abstractmethod
from typing import Optional
import pygame


class BaseScene(ABC):
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """이벤트 처리. 전환할 씬 이름 또는 None 반환."""

    def update(self) -> Optional[str]:
        """프레임 업데이트. 전환할 씬 이름 또는 None 반환."""
        return None

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        pass
