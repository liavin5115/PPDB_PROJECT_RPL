"""Add payment verification fields

Revision ID: d1a3f45e204d
Revises: 08466f23b97e
Create Date: 2025-05-08 10:17:41.402147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1a3f45e204d'
down_revision = '08466f23b97e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('form', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payment_status', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('payment_proof_data', sa.LargeBinary(), nullable=True))
        batch_op.add_column(sa.Column('payment_proof_filename', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('payment_proof_mimetype', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('payment_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('payment_amount', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('payment_bank', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('payment_account', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('form', schema=None) as batch_op:
        batch_op.drop_column('payment_account')
        batch_op.drop_column('payment_bank')
        batch_op.drop_column('payment_amount')
        batch_op.drop_column('payment_date')
        batch_op.drop_column('payment_proof_mimetype')
        batch_op.drop_column('payment_proof_filename')
        batch_op.drop_column('payment_proof_data')
        batch_op.drop_column('payment_status')

    # ### end Alembic commands ###
