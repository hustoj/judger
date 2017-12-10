#!/bin/env python
# coding: utf8


from peewee import *

db = MySQLDatabase(host='localhost', user='root', password='root', database='openjudge', charset='utf8')

database = MySQLDatabase('qiming', **{'host': 'localhost', 'password': 'qimingjudge', 'user': 'qiming'})


class UnknownField(object):
    pass


class BaseModel(Model):
    class Meta:
        database = database


class Roles(BaseModel):
    created_at = DateTimeField()
    name = CharField(max_length=255)
    updated_at = DateTimeField()

    class Meta:
        db_table = 'roles'


class Users(BaseModel):
    access_at = DateField(null=True)
    confirmation_code = CharField(max_length=255)
    confirmed = IntegerField()
    created_at = DateTimeField()
    deleted_at = DateTimeField(null=True)
    email = CharField(max_length=255)
    group = IntegerField(db_column='group_id')
    language = IntegerField(null=True)
    last_ip = CharField(max_length=255, null=True)
    locale = CharField(max_length=255, null=True)
    nick = CharField(max_length=255)
    password = CharField(max_length=255)
    remember_token = CharField(max_length=255, null=True)
    school = CharField(max_length=255, null=True)
    solved = IntegerField()
    student = CharField(db_column='student_id', max_length=255, null=True)
    submit = IntegerField()
    updated_at = DateTimeField()
    username = CharField(max_length=255)

    class Meta:
        db_table = 'users'


class AssignedRoles(BaseModel):
    role = ForeignKeyField(db_column='role_id', rel_model=Roles, to_field='id')
    user = ForeignKeyField(db_column='user_id', rel_model=Users, to_field='id')

    class Meta:
        db_table = 'assigned_roles'


class Posts(BaseModel):
    content = TextField()
    created_at = DateTimeField()
    group = IntegerField(db_column='group_id')
    meta_description = CharField(max_length=255)
    meta_keywords = CharField(max_length=255)
    meta_title = CharField(max_length=255)
    slug = CharField(max_length=255)
    title = CharField(max_length=255)
    updated_at = DateTimeField()
    user = ForeignKeyField(db_column='user_id', rel_model=Users, to_field='id')

    class Meta:
        db_table = 'posts'


class Comments(BaseModel):
    content = TextField()
    created_at = DateTimeField()
    post = ForeignKeyField(db_column='post_id', rel_model=Posts, to_field='id')
    updated_at = DateTimeField()
    user = ForeignKeyField(db_column='user_id', rel_model=Users, to_field='id')

    class Meta:
        db_table = 'comments'


class ContestProblem(BaseModel):
    contest = IntegerField(db_column='contest_id')
    order = IntegerField()
    problem = IntegerField(db_column='problem_id')

    class Meta:
        db_table = 'contest_problem'


class Contests(BaseModel):
    created_at = DateTimeField()
    deleted_at = DateTimeField(null=True)
    description = TextField()
    end_time = DateTimeField()
    group = IntegerField(db_column='group_id')
    private = IntegerField()
    start_time = DateTimeField()
    title = CharField(max_length=255)
    updated_at = DateTimeField()
    user = IntegerField(db_column='user_id')

    class Meta:
        db_table = 'contests'


class Groups(BaseModel):
    activated = IntegerField()
    created_at = DateTimeField()
    deleted_at = DateTimeField(null=True)
    description = CharField(max_length=255)
    name = CharField(max_length=255)
    updated_at = DateTimeField()
    user = IntegerField(db_column='user_id')

    class Meta:
        db_table = 'groups'


class Migrations(BaseModel):
    batch = IntegerField()
    migration = CharField(max_length=255)

    class Meta:
        db_table = 'migrations'


class Options(BaseModel):
    category = CharField(max_length=255)
    desc = CharField(max_length=255)
    name = CharField(max_length=255)
    type = CharField(max_length=255)
    value = TextField()

    class Meta:
        db_table = 'options'


class PasswordReminders(BaseModel):
    created_at = DateTimeField()
    email = CharField(max_length=255)
    token = CharField(max_length=255)

    class Meta:
        db_table = 'password_reminders'


class Permissions(BaseModel):
    display_name = CharField(max_length=255)
    name = CharField(max_length=255)

    class Meta:
        db_table = 'permissions'


class PermissionRole(BaseModel):
    permission = ForeignKeyField(db_column='permission_id', rel_model=Permissions, to_field='id')
    role = ForeignKeyField(db_column='role_id', rel_model=Roles, to_field='id')

    class Meta:
        db_table = 'permission_role'


class Problems(BaseModel):
    created_at = DateTimeField()
    deleted_at = DateTimeField(null=True)
    description = TextField()
    hint = TextField()
    input = TextField()
    memo = TextField()
    memory_limit = IntegerField()
    output = TextField()
    sample_input = TextField()
    sample_output = TextField()
    solved = IntegerField()
    source = TextField()
    submit = IntegerField()
    time_limit = IntegerField()
    title = CharField(max_length=255)
    updated_at = DateTimeField()
    user = IntegerField(db_column='user_id')

    class Meta:
        db_table = 'problems'


class Replies(BaseModel):
    content = CharField(max_length=255)
    created_at = DateTimeField()
    deleted_at = DateTimeField(null=True)
    topic = IntegerField(db_column='topic_id')
    updated_at = DateTimeField()
    user = IntegerField(db_column='user_id')

    class Meta:
        db_table = 'replies'


class Solutions(BaseModel):
    code = TextField()
    compile_info = TextField()
    contest = IntegerField(db_column='contest_id')
    created_at = DateTimeField()
    ip = CharField(max_length=255)
    language = IntegerField()
    memory_cost = IntegerField()
    origin_problem = IntegerField(db_column='origin_problem_id')
    problem = IntegerField(db_column='problem_id')
    result = IntegerField()
    runtime_info = TextField()
    time_cost = IntegerField()
    updated_at = DateTimeField()
    user = IntegerField(db_column='user_id')

    PENDING = 0
    PENDING_REJUDGE = 1
    COMPILING = 2
    REJUDGING = 3
    ACCEPTED = 4
    PRESENTATION_ERROR = 5
    WRONG_ANSWER = 6
    TIME_LIMIT = 7
    MEMORY_LIMIT = 8
    OUTPUT_LIMIT = 9
    RUNTIME_ERROR = 10
    COMPILE_ERROR = 11

    class Meta:
        db_table = 'solutions'

    _lang_mapping = {
        1: 'c',
        2: 'cpp'
    }

    def get_type(self):
        return self._lang_mapping[self.language]

    def __repr__(self):
        return "ID:%s, PID:%s, RESULT:%s" % (self.id, self.problem, self.result)


class Tags(BaseModel):
    created_at = DateTimeField()
    problem = IntegerField(db_column='problem_id')
    updated_at = DateTimeField()
    value = CharField(max_length=255)

    class Meta:
        db_table = 'tags'


class Topics(BaseModel):
    content = TextField()
    contest = IntegerField(db_column='contest_id')
    created_at = DateTimeField()
    deleted_at = DateTimeField(null=True)
    title = CharField(max_length=255)
    updated_at = DateTimeField()
    user = IntegerField(db_column='user_id')

    class Meta:
        db_table = 'topics'
