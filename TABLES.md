# Quick Cheque Entities

## User

- ID (PK)
- Name (varchar(50))
- Email (UNIQUE)
- Password (varchar(16), min 8, eng letters + numbers)
- Photo Url (varchar(100))

## Room

- ID (PK)
- Name (varchar(30))
- OwnerID (FK -> User)

## Room <-> User

- RoomID
- UserID

## Cheque

- ID
- RoomID (FK -> Room)
- OwnerID (FK -> User)
- Name (varchar(30))

## ProductItem

- ID
- Name (varchar(30))
- Price
- Count
- RoomId (FK -> Room)

## ProductItem <-> User

- ProductID
- UserID
