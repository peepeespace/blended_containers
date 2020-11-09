from django.contrib import admin

from data.models import (
    General,
    Price,
    Buysell,
    ETF,
    Factor,
    Index,
    MarketCap
)


admin.site.register(General)
admin.site.register(Price)
admin.site.register(Buysell)
admin.site.register(ETF)
admin.site.register(Factor)
admin.site.register(Index)
admin.site.register(MarketCap)
