# FastAPI ORM Helper

FastAPI ORM Helper helps us to work with SQLAlchemy easier with lots of useful functions

## How to use

```python
from fastapi_orm_helper import BaseRepository
from users.entities.user import UserEntity

class UserRepository(BaseRepository[UserEntity]):
    _entity = UserEntity
```
