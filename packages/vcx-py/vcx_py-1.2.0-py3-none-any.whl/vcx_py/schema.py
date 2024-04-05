#  Copyright (c) 2024 Aaron Janeiro Stone
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
"""Dataclass-based representation of the VirgoCX API schema."""

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Optional

from .constants import KLineType, OrderStatus, OrderDirection


@dataclass
class VirgoCXSchema(ABC):
    """Base class for all schema classes."""
    _SUBCLASS_MAPPINGS = None

    @classmethod
    def from_dict(cls, dct: dict):
        """Create an instance from a dictionary."""
        out = {}
        for k, v in cls._SUBCLASS_MAPPINGS.items():
            out[k] = dct[v]
        return cls(**out)

    def to_dict(self) -> dict:
        """Convert the instance to a dictionary."""
        out = {}
        for k, v in self._SUBCLASS_MAPPINGS.items():
            out[v] = getattr(self, k)
        return out


@dataclass
class KLine(VirgoCXSchema):
    """Dataclass for the kline data."""
    open: float
    high: float
    low: float
    close: float
    time: int
    volume: float = 0.0  # not always present

    _SUBCLASS_MAPPINGS = {
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "time": "createTime",
        "volume": "volume"
    }
