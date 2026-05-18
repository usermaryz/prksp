"""
Infrastructure Layer - Реализация внешних зависимостей
======================================================

Этот слой содержит:
- Repository Implementations (SQLAlchemy)
- External Service Clients (HTTP)
- Event Publishers (Kafka/RabbitMQ/HTTP)
- Database Models (ORM)

Принципы:
- Реализует интерфейсы из Domain Layer
- Изолирует технические детали
- Зависит от Domain (не наоборот)
"""



