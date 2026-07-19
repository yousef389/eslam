"""initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('username', sa.String(50), unique=True, index=True),
        sa.Column('email', sa.String(255), unique=True, index=True),
        sa.Column('full_name', sa.String(255)),
        sa.Column('password_hash', sa.String(255)),
        sa.Column('role', sa.String(20), server_default='staff'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('last_login', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('categories',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255)),
        sa.Column('description', sa.Text, server_default=''),
        sa.Column('parent_id', sa.String(36), nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('products',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255)),
        sa.Column('sku', sa.String(100), unique=True, index=True),
        sa.Column('barcode', sa.String(100), nullable=True),
        sa.Column('description', sa.Text, server_default=''),
        sa.Column('category_id', sa.String(36), nullable=True),
        sa.Column('unit_price', sa.Numeric(12, 2), server_default='0'),
        sa.Column('cost_price', sa.Numeric(12, 2), server_default='0'),
        sa.Column('quantity_in_stock', sa.Integer, server_default='0'),
        sa.Column('minimum_stock_level', sa.Integer, server_default='0'),
        sa.Column('maximum_stock_level', sa.Integer, server_default='1000'),
        sa.Column('unit', sa.String(20), server_default='piece'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('customers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255)),
        sa.Column('phone', sa.String(50)),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('tax_number', sa.String(50), nullable=True),
        sa.Column('credit_limit', sa.Numeric(12, 2), server_default='0'),
        sa.Column('current_balance', sa.Numeric(12, 2), server_default='0'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('notes', sa.Text, server_default=''),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('suppliers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255)),
        sa.Column('phone', sa.String(50)),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('tax_number', sa.String(50), nullable=True),
        sa.Column('payment_terms_days', sa.Integer, server_default='30'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('notes', sa.Text, server_default=''),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('sale_orders',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('order_number', sa.String(50), unique=True, index=True),
        sa.Column('customer_id', sa.String(36)),
        sa.Column('user_id', sa.String(36)),
        sa.Column('status', sa.String(20), server_default='draft'),
        sa.Column('subtotal', sa.Numeric(12, 2), server_default='0'),
        sa.Column('discount', sa.Numeric(12, 2), server_default='0'),
        sa.Column('tax_amount', sa.Numeric(12, 2), server_default='0'),
        sa.Column('total', sa.Numeric(12, 2), server_default='0'),
        sa.Column('payment_method', sa.String(20), nullable=True),
        sa.Column('notes', sa.Text, server_default=''),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('sale_order_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('order_id', sa.String(36)),
        sa.Column('product_id', sa.String(36)),
        sa.Column('quantity', sa.Integer),
        sa.Column('unit_price', sa.Numeric(12, 2)),
        sa.Column('discount', sa.Numeric(12, 2), server_default='0'),
        sa.Column('total', sa.Numeric(12, 2)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('purchase_orders',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('order_number', sa.String(50), unique=True, index=True),
        sa.Column('supplier_id', sa.String(36)),
        sa.Column('user_id', sa.String(36)),
        sa.Column('status', sa.String(20), server_default='draft'),
        sa.Column('subtotal', sa.Numeric(12, 2), server_default='0'),
        sa.Column('discount', sa.Numeric(12, 2), server_default='0'),
        sa.Column('tax_amount', sa.Numeric(12, 2), server_default='0'),
        sa.Column('total', sa.Numeric(12, 2), server_default='0'),
        sa.Column('payment_method', sa.String(20), nullable=True),
        sa.Column('notes', sa.Text, server_default=''),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('purchase_order_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('order_id', sa.String(36)),
        sa.Column('product_id', sa.String(36)),
        sa.Column('quantity', sa.Integer),
        sa.Column('unit_price', sa.Numeric(12, 2)),
        sa.Column('discount', sa.Numeric(12, 2), server_default='0'),
        sa.Column('total', sa.Numeric(12, 2)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('customer_debts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('customer_id', sa.String(36)),
        sa.Column('amount', sa.Numeric(12, 2)),
        sa.Column('paid_amount', sa.Numeric(12, 2), server_default='0'),
        sa.Column('remaining', sa.Numeric(12, 2)),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('description', sa.Text, server_default=''),
        sa.Column('due_date', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('supplier_debts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('supplier_id', sa.String(36)),
        sa.Column('amount', sa.Numeric(12, 2)),
        sa.Column('paid_amount', sa.Numeric(12, 2), server_default='0'),
        sa.Column('remaining', sa.Numeric(12, 2)),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('description', sa.Text, server_default=''),
        sa.Column('due_date', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('debt_payments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('debt_id', sa.String(36)),
        sa.Column('debt_type', sa.String(20)),
        sa.Column('amount', sa.Numeric(12, 2)),
        sa.Column('payment_method', sa.String(20), server_default='cash'),
        sa.Column('notes', sa.Text, server_default=''),
        sa.Column('user_id', sa.String(36)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('cashboxes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100)),
        sa.Column('balance', sa.Numeric(12, 2), server_default='0'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('cashbox_transactions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('cashbox_id', sa.String(36)),
        sa.Column('transaction_type', sa.String(20)),
        sa.Column('amount', sa.Numeric(12, 2)),
        sa.Column('description', sa.Text, server_default=''),
        sa.Column('reference_id', sa.String(36), nullable=True),
        sa.Column('user_id', sa.String(36)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('transactions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('transaction_number', sa.String(50), unique=True, index=True),
        sa.Column('type', sa.String(20)),
        sa.Column('amount', sa.Numeric(12, 2)),
        sa.Column('description', sa.Text, server_default=''),
        sa.Column('reference_id', sa.String(36), nullable=True),
        sa.Column('reference_type', sa.String(50), nullable=True),
        sa.Column('user_id', sa.String(36)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('extractions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('image_url', sa.String(500), server_default=''),
        sa.Column('source', sa.String(50), server_default='api'),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('raw_text', sa.Text, server_default=''),
        sa.Column('extracted_data', postgresql.JSON, nullable=True),
        sa.Column('review_notes', sa.Text, server_default=''),
        sa.Column('reviewed_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36)),
        sa.Column('action', sa.String(100)),
        sa.Column('resource_type', sa.String(50)),
        sa.Column('resource_id', sa.String(36), nullable=True),
        sa.Column('details', postgresql.JSON, nullable=True),
        sa.Column('ip_address', sa.String(45), server_default=''),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table('system_settings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('key', sa.String(100), unique=True, index=True),
        sa.Column('value', sa.Text, server_default=''),
        sa.Column('group', sa.String(50), index=True),
        sa.Column('description', sa.Text, server_default=''),
        sa.Column('is_secret', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('system_settings')
    op.drop_table('audit_logs')
    op.drop_table('extractions')
    op.drop_table('transactions')
    op.drop_table('cashbox_transactions')
    op.drop_table('cashboxes')
    op.drop_table('debt_payments')
    op.drop_table('supplier_debts')
    op.drop_table('customer_debts')
    op.drop_table('purchase_order_items')
    op.drop_table('purchase_orders')
    op.drop_table('sale_order_items')
    op.drop_table('sale_orders')
    op.drop_table('suppliers')
    op.drop_table('customers')
    op.drop_table('products')
    op.drop_table('categories')
    op.drop_table('users')
