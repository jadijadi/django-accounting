from datetime import date

from django.views import generic
from django.core.urlresolvers import reverse
from django.utils import timezone

from dateutil.relativedelta import relativedelta

from accounting.apps.books.utils import organization_manager
from .models import (
    BusinessSettings,
    FinancialSettings,
    PayRunSettings)
from .forms import (
    BusinessSettingsForm,
    FinancialSettingsForm,
    PayRunSettingsForm)
from .wrappers import TaxReport, ProfitAndLossReport


class ReportListView(generic.TemplateView):
    template_name = "reports/report_list.html"


class SettingsListView(generic.TemplateView):
    template_name = "reports/settings_list.html"


class GenericSettingsMixin(object):

    def get_object(self):
        orga = organization_manager.get_selected_organization(self.request)
        try:
            settings = self.model.objects.get(organization=orga)
        except self.model.DoesNotExist:
            settings = self.model.objects.create(organization=orga)
        return settings

    def get_success_url(self):
        return reverse("reports:settings-list")


class BusinessSettingsUpdateView(GenericSettingsMixin,
                                  generic.UpdateView):
    template_name = "reports/financial_settings_update.html"
    model = BusinessSettings
    form_class = BusinessSettingsForm


class FinancialSettingsUpdateView(GenericSettingsMixin,
                                  generic.UpdateView):
    template_name = "reports/financial_settings_update.html"
    model = FinancialSettings
    form_class = FinancialSettingsForm


class PayRunSettingsUpdateView(GenericSettingsMixin,
                               generic.UpdateView):
    template_name = "reports/payrun_settings_update.html"
    model = PayRunSettings
    form_class = PayRunSettingsForm


class TaxReportView(generic.TemplateView):
    template_name = "reports/tax_report.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        orga = organization_manager.get_selected_organization(self.request)
        report = TaxReport(orga,
                           start=date(2014, 1, 1),
                           end=date(2014, 12, 1))
        report.generate()
        ctx['tax_summaries'] = report.tax_summaries.values()
        return ctx


class ProfitAndLossReportView(generic.TemplateView):
    template_name = "reports/profit_and_loss_report.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        orga = organization_manager.get_selected_organization(self.request)

        # currrent quarter
        now = timezone.now()
        start = date(year=now.year, month=(now.month - ((now.month-1) % 3)), day=1)
        end = start + relativedelta(months=3)

        report = ProfitAndLossReport(orga, start=start, end=end)
        report.generate()
        ctx['summaries'] = report.summaries
        ctx['total_summary'] = report.total_summary
        return ctx
