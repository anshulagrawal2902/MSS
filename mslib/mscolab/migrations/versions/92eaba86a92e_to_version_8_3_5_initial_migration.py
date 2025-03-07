"""To version 8.3.5 - Initial migration

Revision ID: 92eaba86a92e
Revises:
Create Date: 2024-07-08 15:47:24.916851

"""
from alembic import op
import sqlalchemy as sa
import mslib.mscolab.custom_migration_types as cu


# revision identifiers, used by Alembic.
revision = '92eaba86a92e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('operations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('path', sa.String(length=255), nullable=True),
    sa.Column('category', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('last_used', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_operations')),
    sa.UniqueConstraint('path', name=op.f('uq_operations_path'))
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=255), nullable=True),
    sa.Column('emailid', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('registered_on', sa.DateTime(), nullable=False),
    sa.Column('confirmed', sa.Boolean(), nullable=False),
    sa.Column('confirmed_on', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('emailid', name=op.f('uq_users_emailid')),
    sa.UniqueConstraint('password', name=op.f('uq_users_password'))
    )
    op.create_table('changes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('op_id', sa.Integer(), nullable=True),
    sa.Column('u_id', sa.Integer(), nullable=True),
    sa.Column('commit_hash', sa.String(length=255), nullable=True),
    sa.Column('version_name', sa.String(length=255), nullable=True),
    sa.Column('comment', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['op_id'], ['operations.id'], name=op.f('fk_changes_op_id_operations')),
    sa.ForeignKeyConstraint(['u_id'], ['users.id'], name=op.f('fk_changes_u_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_changes'))
    )
    op.create_table('messages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('op_id', sa.Integer(), nullable=True),
    sa.Column('u_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('message_type', sa.Enum('TEXT', 'SYSTEM_MESSAGE', 'IMAGE', 'DOCUMENT', name='messagetype'), nullable=True),
    sa.Column('reply_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['op_id'], ['operations.id'], name=op.f('fk_messages_op_id_operations')),
    sa.ForeignKeyConstraint(['reply_id'], ['messages.id'], name=op.f('fk_messages_reply_id_messages')),
    sa.ForeignKeyConstraint(['u_id'], ['users.id'], name=op.f('fk_messages_u_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_messages'))
    )
    op.create_table('permissions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('op_id', sa.Integer(), nullable=True),
    sa.Column('u_id', sa.Integer(), nullable=True),
    sa.Column('access_level', sa.Enum('admin', 'collaborator', 'viewer', 'creator', name='access_level'), nullable=True),
    sa.ForeignKeyConstraint(['op_id'], ['operations.id'], name=op.f('fk_permissions_op_id_operations')),
    sa.ForeignKeyConstraint(['u_id'], ['users.id'], name=op.f('fk_permissions_u_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_permissions'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('permissions')
    sa.Enum(name='access_level').drop(op.get_bind(), checkfirst=False)
    op.drop_table('messages')
    sa.Enum(name='messagetype').drop(op.get_bind(), checkfirst=False)
    op.drop_table('changes')
    op.drop_table('users')
    op.drop_table('operations')
    # ### end Alembic commands ###
