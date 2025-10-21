#!/usr/bin/env python3

"""
Registers all API v1 blueprints and routes.
"""

from flask import Blueprint

app_views = Blueprint("app_views", __name__, url_prefix="/api/v1")

from api.v1.views.brands import *
from api.v1.views.categories import *
from api.v1.views.employees import *
from api.v1.views.products import *
from api.v1.views.purchase_order_items import *
from api.v1.views.purchase_orders import *
from api.v1.views.sales import *
from api.v1.views.stock_levels import *
from api.v1.views.session_auth import *
