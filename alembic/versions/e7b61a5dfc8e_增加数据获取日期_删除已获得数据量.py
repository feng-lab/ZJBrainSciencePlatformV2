"""增加数据获取日期，删除已获得数据量

Revision ID: e7b61a5dfc8e
Revises: 6c54801bec54
Create Date: 2024-04-29 17:20:58.106767

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e7b61a5dfc8e'
down_revision = '6c54801bec54'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dataset', sa.Column('start_acquisition_time', sa.Date(), nullable=True, comment='开始获取的日期'))
    op.add_column('dataset', sa.Column('planed_acquisition_time', sa.Date(), nullable=True, comment='计划完成日期'))
    op.drop_column('dataset', 'file_acquired_size_gb')
    op.alter_column('eeg_data', 'data_update_year',
               existing_type=mysql.DATETIME(),
               type_=sa.Date(),
               existing_comment='数据上传时间',
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('eeg_data', 'data_update_year',
               existing_type=sa.Date(),
               type_=mysql.DATETIME(),
               existing_comment='数据上传时间',
               existing_nullable=False)
    op.add_column('dataset', sa.Column('file_acquired_size_gb', mysql.FLOAT(), nullable=True, comment='已获取数据(GB)'))
    op.drop_column('dataset', 'planed_acquisition_time')
    op.drop_column('dataset', 'start_acquisition_time')
    # ### end Alembic commands ###
