from staze import Database


PostTagTable = Database.table(
    'post_tag',
    Database.column(
        'post_id', Database.integer, Database.foreign_key('post.id'), primary_key=True),
    Database.column(
        'tag_id', Database.integer, Database.foreign_key('tag.id'), primary_key=True))
