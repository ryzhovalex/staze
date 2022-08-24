from staze import Database


PostTagTable = Database.table(
    'post_tag',
    Database.column(
        '_post_id',
        Database.integer,
        Database.foreign_key('post_orm._id'),
        primary_key=True),
    Database.column(
        '_tag_id',
        Database.integer,
        Database.foreign_key('tag_orm._id'),
        primary_key=True))
