from staze import orm


PostTagTable = orm.table(
    'post_tag',
    orm.column(
        'post_id', orm.integer, orm.foreign_key('post.id'), primary_key=True),
    orm.column(
        'tag_id', orm.integer, orm.foreign_key('tag.id'), primary_key=True))
