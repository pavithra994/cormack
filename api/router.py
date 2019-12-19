#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.conf.urls import url
from rest_framework import routers
from api import views
from . import viewsets

from api.resources.code_supplier_type import CodeSupplierTypeViewSet
from api.resources.code_supplier import CodeSupplierViewSet
from api.resources.job_supply import JobSupplyViewSet

from django.views.generic.base import RedirectView

router = routers.DefaultRouter()
router.register('job', viewsets.JobViewSet)
router.register('repair', viewsets.RepairViewSet)
router.register('subbie', viewsets.SubbieViewSet)
router.register('supervisor', viewsets.SupervisorViewSet)
# router.register('user', viewsets.UserViewSet)
router.register('client_manager', viewsets.ClientManagerViewSet)
router.register('client', viewsets.ClientViewSet)
router.register('files', viewsets.FileUploadViewSet)
router.register('notes', viewsets.NoteViewSet)
router.register('job_costs', viewsets.JobCostViewSet)
router.register('job_drains', viewsets.JobDrainsViewSet)
router.register('notifications', viewsets.JobNotificationViewSet)
router.register('tasks', viewsets.TaskViewSet)
router.register('repair_costs', viewsets.RepairCostViewSet)
router.register('code_mix', viewsets.CodeMixViewSet)
router.register('code_job_type', viewsets.CodeJobTypeViewSet)
router.register('code_subbie_type', viewsets.CodeSubbieTypeViewSet)
router.register('code_purchase_order_type', viewsets.CodePurchaseOrderTypeViewSet)
router.register('code_paving_colour', viewsets.CodePavingColourViewSet)
router.register('code_paving_type', viewsets.CodePavingTypeViewSet)
router.register('code_repair_type', viewsets.CodeRepairTypeViewSet)
router.register('code_drain_type', viewsets.CodeDrainTypeViewSet)
router.register('code_depot_type', viewsets.CodeDepotTypeViewSet)
router.register('code_file_type', viewsets.CodeFileTypeViewSet)
router.register('code_task_type', viewsets.CodeTaskTypeViewSet)
router.register('code_time_of_day', viewsets.CodeTimeOfDayViewSet)
# router.register('users', viewsets.UserViewSet)
router.register('roles', viewsets.RoleViewSet)
router.register('hash', viewsets.HashViewSet)
router.register('mail-messages', viewsets.MailMessagesViewSet)



router.register(r'code_supplier_type', CodeSupplierTypeViewSet)
router.register(r'code_supplier', CodeSupplierViewSet)
router.register(r'job_supply', JobSupplyViewSet)

urlpatterns = router.urls

urlpatterns += [
    url(r'^create_job_invoice/', views.CreateJobInvoiceView.as_view()),
    url(r'^create_repair_invoice/', views.CreateRepairInvoiceView.as_view()),
    url(r'^create_job_purchase_order/', views.CreateJobPurchaseOrderView.as_view()),
    url(r'^create_repair_purchase_order/', views.CreateRepairPurchaseOrderView.as_view()),

    url(r'^download_invoice/(?P<id>[0-9]+)/$', views.DownloadInvoice.as_view()),
    url(r'^download_purchase_order/(?P<id>[0-9]+)/$', views.DownloadPurchaseOrder.as_view()),

    # OAuth 2.0 support.
    url(r'^oauth2$', RedirectView.as_view(url="/", permanent=False)),
    url(r'^signin-redirect$', views.XeroOAuth2CallbackView.as_view())
]
