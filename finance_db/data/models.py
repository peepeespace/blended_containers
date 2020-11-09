from django.db import models


class General(models.Model):
    date = models.CharField(max_length=10, blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    stk_kind = models.CharField(max_length=200, blank=True, null=True)  # 산업 구분
    mkt_gb = models.CharField(max_length=50, blank=True, null=True)  # 코스피, 코스닥 시장
    mkt_cap = models.IntegerField(blank=True, null=True)  # 시가총액
    mkt_cap_size = models.CharField(max_length=50, blank=True, null=True)  # 대형주, 중형주, 소형주, 제외
    frg_hlg = models.FloatField(blank=True, null=True) # 외인 지분 (foreign holding)
    mgt_gb = models.CharField(max_length=50, blank=True, null=True)  # 정상, 정지, 관리 등

    def __str__(self):
        return '{} {} {}'.format(self.date, self.code, self.name)


class Price(models.Model):
    ### GICODE, ITEMABBRNM, STRT_PRC, HIGH_PRC, LOW_PRC, CLS_PRC, ADJ_PRC, TRD_QTY, TRD_AMT, SHTSALE_TRD_QTY
    date = models.CharField(max_length=10, blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    strt_prc = models.IntegerField(blank=True, null=True)
    high_prc = models.IntegerField(blank=True, null=True)
    low_prc = models.IntegerField(blank=True, null=True)
    cls_prc = models.IntegerField(blank=True, null=True)
    adj_prc = models.BigIntegerField(blank=True, null=True,)
    trd_qty = models.FloatField(blank=True, null=True)  # (x1000)
    trd_amt = models.FloatField(blank=True, null=True)  # (x1000000)
    shtsale_trd_qty = models.FloatField(blank=True, null=True)  # (x1000)

    def __str__(self):
        return '{} {} {}'.format(self.date, self.code, self.name)


class Buysell(models.Model):
    ### GICODE, GINAME, FORGN_B/S/N, PRIVATE_B/S/N, INST_SUM_B/S/N, TRUST_B/S/N, PENSTION_B/S/N, ETC_INST_B/S/B (x1000)
    date = models.CharField(max_length=10, blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    forgn_b = models.IntegerField(blank=True, null=True)
    forgn_s = models.IntegerField(blank=True, null=True)
    forgn_n = models.IntegerField(blank=True, null=True)
    private_b = models.IntegerField(blank=True, null=True)
    private_s = models.IntegerField(blank=True, null=True)
    private_n = models.IntegerField(blank=True, null=True)
    inst_sum_b = models.IntegerField(blank=True, null=True)
    inst_sum_s = models.IntegerField(blank=True, null=True)
    inst_sum_n = models.IntegerField(blank=True, null=True)
    trust_b = models.IntegerField(blank=True, null=True)  # 투자신탁
    trust_s = models.IntegerField(blank=True, null=True)
    trust_n = models.IntegerField(blank=True, null=True)
    pension_b = models.IntegerField(blank=True, null=True)  # 연기금
    pension_s = models.IntegerField(blank=True, null=True)
    pension_n = models.IntegerField(blank=True, null=True)
    etc_inst_b = models.IntegerField(blank=True, null=True)
    etc_inst_s = models.IntegerField(blank=True, null=True)
    etc_inst_n = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return '{} {} {}'.format(self.date, self.code, self.name)


class ETF(models.Model):
    ### GICODE, ITEMABBRNM, CLS_PRC, TRD_QTY, TRD_AMT, ETF_NAV, SPREAD
    date = models.CharField(max_length=10, blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    cls_prc = models.FloatField(blank=True, null=True)
    trd_qty = models.IntegerField(blank=True, null=True)
    trd_amt = models.IntegerField(blank=True, null=True)  # (x1000)
    etf_nav = models.FloatField(blank=True, null=True)
    spread = models.FloatField(blank=True, null=True)

    def __str__(self):
        return '{} {} {}'.format(self.date, self.code, self.name)


class Factor(models.Model):
    ### GICODE, ITEMABBRNM, PER, PBR, PCR, PSR, DIVID_YIELD
    date = models.CharField(max_length=10, blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    per = models.FloatField(blank=True, null=True)
    pbr = models.FloatField(blank=True, null=True)
    pcr = models.FloatField(blank=True, null=True)
    psr = models.FloatField(blank=True, null=True)
    divid_yield = models.FloatField(blank=True, null=True)

    def __str__(self):
        return '{} {} {}'.format(self.date, self.code, self.name)


class Index(models.Model):
    ### U_CD, U_NM, STRT_PRC, HIGH_PRC, LOW_PRC, CLS_PRC, TRD_QTY, TRD_AMT
    date = models.CharField(max_length=10, blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    strt_prc = models.FloatField(blank=True, null=True)  # 시가
    high_prc = models.FloatField(blank=True, null=True)  # 고가
    low_prc = models.FloatField(blank=True, null=True)  # 저가
    cls_prc = models.FloatField(blank=True, null=True)  # 종가
    trd_qty = models.FloatField(blank=True, null=True)  # 거래량 (x1000)
    trd_amt = models.FloatField(blank=True, null=True)  # 거래대금 (x1000000)

    def __str__(self):
        return '{} {} {}'.format(self.date, self.code, self.name)


class MarketCap(models.Model):
    ### GICODE, ITEMABBRNM, COMM_STK_QTY, PREF_STK_QTY
    date = models.CharField(max_length=10, blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    comm_stk_qty = models.IntegerField(blank=True, null=True)  # (x1000)
    pref_stk_qty = models.IntegerField(blank=True, null=True)  # (x1000)

    def __str__(self):
        return '{} {} {}'.format(self.date, self.code, self.name)


class Financial(models.Model):
    pass
