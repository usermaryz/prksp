"""
Money Value Object
==================

Value Object для работы с денежными суммами.
Иммутабельный объект, идентифицируемый по значению.

Принципы:
- Неизменяемость (frozen=True)
- Валидация при создании
- Операции возвращают новый объект
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Union


@dataclass(frozen=True)
class Money:
    """
    Value Object для денежных сумм.
    
    Примеры использования:
        >>> price = Money(Decimal("99.99"), "RUB")
        >>> total = price * 3
        >>> total.amount
        Decimal('299.97')
    """
    amount: Decimal
    currency: str = "RUB"
    
    def __post_init__(self):
        """Валидация при создании"""
        if not isinstance(self.amount, Decimal):
            # Конвертируем в Decimal если передано число
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        
        if self.amount < 0:
            raise ValueError("Сумма не может быть отрицательной")
        
        # Округляем до 2 знаков
        rounded = self.amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        object.__setattr__(self, 'amount', rounded)
    
    def __add__(self, other: 'Money') -> 'Money':
        """Сложение денежных сумм"""
        self._check_same_currency(other)
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: 'Money') -> 'Money':
        """Вычитание денежных сумм"""
        self._check_same_currency(other)
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Результат не может быть отрицательным")
        return Money(result, self.currency)
    
    def __mul__(self, multiplier: Union[int, Decimal]) -> 'Money':
        """Умножение на число"""
        return Money(self.amount * Decimal(str(multiplier)), self.currency)
    
    def __eq__(self, other: object) -> bool:
        """Сравнение по значению (ключевое свойство Value Object)"""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __hash__(self) -> int:
        """Хеш для использования в множествах и словарях"""
        return hash((self.amount, self.currency))
    
    def _check_same_currency(self, other: 'Money') -> None:
        """Проверка одинаковой валюты"""
        if self.currency != other.currency:
            raise ValueError(f"Разные валюты: {self.currency} и {other.currency}")
    
    def is_zero(self) -> bool:
        """Проверка на нулевую сумму"""
        return self.amount == Decimal('0')
    
    def format(self) -> str:
        """Форматированный вывод"""
        return f"{self.amount:,.2f} {self.currency}"
    
    @classmethod
    def zero(cls, currency: str = "RUB") -> 'Money':
        """Фабричный метод для нулевой суммы"""
        return cls(Decimal('0'), currency)
    
    @classmethod
    def from_float(cls, amount: float, currency: str = "RUB") -> 'Money':
        """Создание из float (безопасная конвертация)"""
        return cls(Decimal(str(amount)), currency)



