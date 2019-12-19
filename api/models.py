#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from ocom.models import OcomModel, ListModel, ActiveModel, HashModel

import os
import uuid
from django.utils import timezone


ALLOW_EMPTY_CONFIG = {
    'blank': True,
    'null': True,
}

DISALLOW_EMPTY_CONFIG = {
    'blank': False,
    'null': False,
}

MONEY_CONFIG = {
    'max_digits': 12,
    'decimal_places': 2,
    'default': 0,
}

# YEAR_IN_SCHOOL_CHOICES = [
#     ('Footpath ', 'Footpath '),
#     ('Patching ', 'Patching '),
#     ('Warranty', 'Warranty'),
#     ]


def upload_path_by_prefix(instance, filename):
    if instance.prefix:
        return os.path.join(slugify(instance.prefix), filename)

    return filename


class NameActiveModel(ActiveModel):
    name = models.TextField(**DISALLOW_EMPTY_CONFIG)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(NameActiveModel, self).__init__(*args, **kwargs)
        self._meta.get_field('name').verbose_name = "{} Name".format(self._meta.verbose_name)

    def __str__(self):
        return "{}".format(self.name)


class DescriptionActiveModel(ActiveModel):
    description = models.TextField(**DISALLOW_EMPTY_CONFIG)

    class Meta:
        abstract = True

    def __str__(self):
        return "{}".format(self.description)


class CodeDescriptionActiveModel(DescriptionActiveModel):
    code = models.CharField(unique=True, max_length=255, **ALLOW_EMPTY_CONFIG)

    class Meta:
        abstract = True


class CodeFileType(CodeDescriptionActiveModel):
    can_email = models.BooleanField(default=False, verbose_name='Can Email')
    is_internal = models.BooleanField(default=False, verbose_name="Is Internal")

    class Meta:
        db_table = "code_file_type"
        verbose_name = "File Type"
        verbose_name_plural = "File Types"


class CodeJobType(CodeDescriptionActiveModel):
    background_colour = models.CharField(max_length=128, default='#ffffff', **DISALLOW_EMPTY_CONFIG)
    foreground_colour = models.CharField(max_length=128, default='#8080ff', **DISALLOW_EMPTY_CONFIG)

    class Meta:
        db_table = 'code_job_type'
        verbose_name = "Job Type"
        verbose_name_plural = "Job Types"


class CodeMix(CodeDescriptionActiveModel):
    class Meta:
        db_table = 'code_mix'
        verbose_name = "Mix"
        verbose_name_plural = "Mixes"


class CodeRepairType(CodeDescriptionActiveModel):
    class Meta:
        db_table = 'code_repair_type'
        verbose_name = "Repair Type"
        verbose_name_plural = "Repair Types"


class CodeTaskType(CodeDescriptionActiveModel):
    background_colour = models.CharField(max_length=128, default='#ffffff', **DISALLOW_EMPTY_CONFIG)
    foreground_colour = models.CharField(max_length=128, default='#8080ff', **DISALLOW_EMPTY_CONFIG)
    # point to the name of the job field that will be affected by this Task Type i.e. any changes in date will have this
    # date field value changed as well
    job_date_field = models.CharField(max_length=128, default='', verbose_name="Job Date Field",
                                      **ALLOW_EMPTY_CONFIG)
    subbie_field = models.CharField(max_length=128, default='', verbose_name="Job Subbie Field",
                                      **ALLOW_EMPTY_CONFIG)

    # The higher the Job Date Order, the earlier it is to be checked i.e. validation will check if the job_date_order is
    # filled in has a date equal or after another CodeTaskType whose date order is higher; if value is 0, no validation
    # is done
    job_date_order = models.IntegerField(verbose_name="Jobs Date Order", default=0, validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'code_task_type'
        verbose_name = "Task Type"
        verbose_name_plural = "Task Types"


class CodePavingType(CodeDescriptionActiveModel):
    class Meta:
        db_table = 'code_paving_type'
        verbose_name = "Paving Type"
        verbose_name_plural = "Paving Types"


class CodePavingColour(CodeDescriptionActiveModel):
    class Meta:
        db_table = 'code_paving_colour'
        verbose_name = "Paving Colour"
        verbose_name_plural = "Paving Colours"


class CodePurchaseOrderType(CodeDescriptionActiveModel):
    class Meta:
        db_table = 'code_purchase_order_type'
        verbose_name = "Purchase Order Type"
        verbose_name_plural = "Purchase Order Types"


class CodeDrainType(CodeDescriptionActiveModel):
    class Meta:
        db_table = 'code_drain_type'
        verbose_name = "Drain Type"
        verbose_name_plural = "Drain Types"

class CodeDepotType(CodeDescriptionActiveModel):
    background_colour = models.CharField(max_length=128, default='#ffffff', **ALLOW_EMPTY_CONFIG)
    foreground_colour = models.CharField(max_length=128, default='#8080ff', **ALLOW_EMPTY_CONFIG)

    class Meta:
        db_table = 'code_depot_type'
        verbose_name = "Depot Type"
        verbose_name_plural = "Depot Types"

class CodeSubbieType(CodeDescriptionActiveModel):
    class Meta:
        db_table = 'code_subbie_type'
        verbose_name = "Subbie Type"
        verbose_name_plural = "Subbie Types"


class CodeTimeOfDay(CodeDescriptionActiveModel):
    class Meta:
        db_table = 'code_time_of_day'
        verbose_name = "Time Of Day"
        verbose_name_plural = "Times Of Day"


class FileUpload(ListModel):    # shared by Job File / Repair File
    file = models.FileField(max_length=512, upload_to=upload_path_by_prefix, **ALLOW_EMPTY_CONFIG)
    name = models.CharField(max_length=250, **ALLOW_EMPTY_CONFIG)
    who_uploaded = models.CharField(max_length=255, verbose_name="Who Uploaded", **ALLOW_EMPTY_CONFIG)
    when_uploaded = models.DateTimeField(auto_now_add=True, **ALLOW_EMPTY_CONFIG)
    prefix = models.CharField(max_length=20, default='')
    file_type = models.ForeignKey("CodeFileType", on_delete=models.PROTECT, **ALLOW_EMPTY_CONFIG)
    url_guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    send_notification = models.DateTimeField(**ALLOW_EMPTY_CONFIG)

    class Meta:
        db_table = "file_upload"


class Note(ListModel):
    note = models.TextField(**ALLOW_EMPTY_CONFIG)
    who = models.CharField(max_length=255, verbose_name="Who", **ALLOW_EMPTY_CONFIG)
    when = models.DateTimeField(auto_now_add=True, **ALLOW_EMPTY_CONFIG)
    hide = models.BooleanField(default=False)
    send_notification = models.DateTimeField(**ALLOW_EMPTY_CONFIG)

    class Meta:
        db_table = "note"
        verbose_name = "Note"
        verbose_name_plural = "Notes"

    def __str__(self):
        return "{}".format(self.note)


class UserBaseModel(NameActiveModel):
    username = models.CharField(max_length=100, verbose_name="Username", **DISALLOW_EMPTY_CONFIG)
    password = models.CharField(max_length=255, verbose_name="Password", **DISALLOW_EMPTY_CONFIG)
    email = models.EmailField(**ALLOW_EMPTY_CONFIG)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Subbie(UserBaseModel):
    username = models.CharField(max_length=100, verbose_name="Username", unique=True, **ALLOW_EMPTY_CONFIG)
    password = models.CharField(max_length=255, verbose_name="Password", **ALLOW_EMPTY_CONFIG)
    email = models.EmailField(unique=True, **ALLOW_EMPTY_CONFIG)
    type = models.ForeignKey("CodeSubbieType", on_delete=models.PROTECT, **ALLOW_EMPTY_CONFIG)
    xero_supplier = models.CharField(max_length=100, verbose_name="Xero Supplier", **ALLOW_EMPTY_CONFIG)
    rate_per_m = models.DecimalField(verbose_name="Rate Per Meter", **MONEY_CONFIG)
    jobs_per_day = models.IntegerField(verbose_name="Jobs Per Day", default=1)
    can_see_plans_before_accept = models.BooleanField(verbose_name="Can See Plans Before Accept", default=False)
    display_order = models.IntegerField("Display Order", name="display_order", **ALLOW_EMPTY_CONFIG)

    class Meta:
        db_table = 'subbie'
        verbose_name = "Subbie"
        verbose_name_plural = "Subbies"


class Supervisor(UserBaseModel):
    phone_number = models.CharField(max_length=100, verbose_name="Phone Number", **ALLOW_EMPTY_CONFIG)
    client = models.ForeignKey("Client", on_delete=models.PROTECT, verbose_name="Client", **ALLOW_EMPTY_CONFIG)

    class Meta:
        db_table = 'supervisor'
        verbose_name = "Supervisor"
        verbose_name_plural = "Supervisors"

# derivative of Supervisor with additional access rights
class ClientManager(UserBaseModel):
    phone_number = models.CharField(max_length=100, verbose_name="Phone Number", **ALLOW_EMPTY_CONFIG)
    client = models.ForeignKey("Client", on_delete=models.PROTECT, verbose_name="Client", **ALLOW_EMPTY_CONFIG)

    class Meta:
        db_table = 'client_manager'
        verbose_name = "Client Manager"
        verbose_name_plural = "Client Managers"


class Job(DescriptionActiveModel):
    code = models.CharField(unique=False, max_length=255, blank=True, null=True)

    date_received = models.DateField(verbose_name="Date Received", **DISALLOW_EMPTY_CONFIG)
    job_type = models.ForeignKey("CodeJobType", on_delete=models.PROTECT, verbose_name="Job Type", **DISALLOW_EMPTY_CONFIG)
    depot_type = models.ForeignKey("CodeDepotType", on_delete=models.PROTECT, verbose_name="Depot Type")
    # description on inherited model
    comments = models.TextField(**ALLOW_EMPTY_CONFIG)
    address = models.TextField(**DISALLOW_EMPTY_CONFIG)
    suburb = models.CharField(max_length=255, verbose_name="Suburb", **ALLOW_EMPTY_CONFIG)
    client = models.ForeignKey("Client", on_delete=models.PROTECT, verbose_name="Client", **DISALLOW_EMPTY_CONFIG)
    purchase_order_number = models.TextField(**ALLOW_EMPTY_CONFIG)  # TODO This will be a summary of table for Searching
    job_number = models.CharField(max_length=50, verbose_name="Job Number", unique=True, **ALLOW_EMPTY_CONFIG)
    purchase_order_value = models.DecimalField(verbose_name="Purchase Order Value", **MONEY_CONFIG)
    sqm = models.DecimalField(verbose_name="SQM", max_digits=12, decimal_places=4, **ALLOW_EMPTY_CONFIG)
    sub_contractor = models.ForeignKey("Subbie", on_delete=models.PROTECT, verbose_name="SubContractor", **ALLOW_EMPTY_CONFIG)
    # est. cost will be a serializer field

    set_out_date = models.DateField(verbose_name="Set Out Date", **ALLOW_EMPTY_CONFIG)
    drain_date = models.DateField(verbose_name="Drain Date", **ALLOW_EMPTY_CONFIG)
    wanted_pour_date = models.DateField(verbose_name="Wanted Pour Date", **ALLOW_EMPTY_CONFIG)
    wanted_pour_date_notes = models.TextField(**ALLOW_EMPTY_CONFIG)
    type_list = models.TextField(**ALLOW_EMPTY_CONFIG)
    # models.IntegerField(choices=((1, _("Footpath")),
    #                                             (2, _("Patching")),
    #                                             (3, _("Warranty"))), default="SELECT AN OPTION")
    pour_date = models.DateField(verbose_name="Proposed Pour Date", **ALLOW_EMPTY_CONFIG)
    pour_date_notes = models.TextField(**ALLOW_EMPTY_CONFIG)
    pour_date_time_of_day = models.ForeignKey("CodeTimeOfDay", on_delete=models.PROTECT, verbose_name="Time Of Day",
                                              related_name='pour_date_time_of_day', **ALLOW_EMPTY_CONFIG)
    supervisor = models.ForeignKey("Supervisor", on_delete=models.PROTECT, verbose_name="Supervisor", **ALLOW_EMPTY_CONFIG)
    # supervisor mobile will be a serielizer field
    # supervisor email will be a serielizer field
    base_inspection_date = models.DateField(verbose_name="Base Inspection Date", **ALLOW_EMPTY_CONFIG)
    base_inspection_date_notes = models.TextField(**ALLOW_EMPTY_CONFIG)
    base_inspection_time_of_day = models.ForeignKey("CodeTimeOfDay", on_delete=models.PROTECT, verbose_name="Time Of Day",
                                                    related_name='base_inspection_time_of_day', **ALLOW_EMPTY_CONFIG)

    base_inspector = models.ForeignKey("Subbie", on_delete=models.PROTECT, verbose_name="Base Inspector", related_name="job_base_inspector_supplier",
                                      **ALLOW_EMPTY_CONFIG)
    pump_inspector = models.ForeignKey("Subbie", on_delete=models.PROTECT, verbose_name="Pump Supplier", related_name="job_pump_inspector_supplier",
                                      **ALLOW_EMPTY_CONFIG)

    base_inspection_done = models.BooleanField(default=False, verbose_name="Base Inspection Done")

    steel_inspection_date = models.DateField(verbose_name="Steel Inspection Date", **ALLOW_EMPTY_CONFIG)
    steel_inspection_date_notes = models.TextField(**ALLOW_EMPTY_CONFIG)
    steel_inspection_time_of_day = models.ForeignKey("CodeTimeOfDay", on_delete=models.PROTECT, verbose_name="Time Of Day",
                                                     related_name='steel_inspection_time_of_day', **ALLOW_EMPTY_CONFIG)
    steel_inspection_done = models.BooleanField(default=False, verbose_name="Steel Inspection Done")

    building_inspector_supplier = models.ForeignKey("CodeSupplier", on_delete=models.PROTECT, verbose_name="Building Inspector Supplier", related_name="job_building_inspector_supplier",
                                      **ALLOW_EMPTY_CONFIG)

    #building_inspector = models.ForeignKey("Subbie", on_delete=models.PROTECT, verbose_name="Building Inspector", related_name='building_inspector', **ALLOW_EMPTY_CONFIG)

    rock_m3 = models.DecimalField(verbose_name="Rock (m3)", max_digits=12, decimal_places=4, **ALLOW_EMPTY_CONFIG)
    rock_booked_date = models.DateField(verbose_name="Rock Booked Date", **ALLOW_EMPTY_CONFIG)
    rock_booked_date_notes = models.TextField(**ALLOW_EMPTY_CONFIG)
    rock_booked_time_of_day = models.ForeignKey("CodeTimeOfDay", on_delete=models.PROTECT, verbose_name="Time Of Day",
                                                related_name='rock_booked_time_of_day', **ALLOW_EMPTY_CONFIG)
    materials = models.DateField(verbose_name="Materials", **ALLOW_EMPTY_CONFIG)
    materials_time = models.CharField(max_length=255, verbose_name="Materials Time", **ALLOW_EMPTY_CONFIG)
    steel_delivery_date = models.DateField(verbose_name="Steel Delivery Date", **ALLOW_EMPTY_CONFIG)
    steel_delivery_date_notes = models.TextField(**ALLOW_EMPTY_CONFIG)
    steel_delivery_time_of_day = models.ForeignKey("CodeTimeOfDay", on_delete=models.PROTECT, verbose_name="Time Of Day",
                                                   related_name='steel_delivery_time_of_day', **ALLOW_EMPTY_CONFIG)
    pod_delivery_date = models.DateField(verbose_name="Pod Delivery Date", **ALLOW_EMPTY_CONFIG)
    pod_delivery_date_notes = models.TextField(**ALLOW_EMPTY_CONFIG)
    pod_delivery_time_of_day = models.ForeignKey("CodeTimeOfDay", on_delete=models.PROTECT, verbose_name="Time Of Day",
                                                 related_name='pod_delivery_time_of_day', **ALLOW_EMPTY_CONFIG)
    has_part_a = models.BooleanField(default=False, verbose_name="Has Part A")  # default depends on the selected client
    part_a_date = models.DateField(verbose_name="Part A Date", **ALLOW_EMPTY_CONFIG)
    part_a_date_notes = models.TextField(**ALLOW_EMPTY_CONFIG)
    part_a_time_of_day = models.ForeignKey("CodeTimeOfDay", on_delete=models.PROTECT, verbose_name="Time Of Day",
                                           related_name='part_a_time_of_day', **ALLOW_EMPTY_CONFIG)
    part_a_booking_number = models.CharField(max_length=100, verbose_name="Part A Booking Number", **ALLOW_EMPTY_CONFIG)
    termite_supplier = models.ForeignKey("CodeSupplier", on_delete=models.PROTECT, verbose_name="Termite Inspector Supplier",
                                                    related_name="job_termite_supplier",
                                                    **ALLOW_EMPTY_CONFIG)
    # termite_supplier = models.ForeignKey("Subbie", on_delete=models.PROTECT, verbose_name="Termite Supplier",
    #                                      related_name='termite_supplier', **ALLOW_EMPTY_CONFIG)

    waste_date = models.DateField(verbose_name="Waste Date", **ALLOW_EMPTY_CONFIG)
    waste_time_of_day = models.ForeignKey("CodeTimeOfDay", on_delete=models.PROTECT, verbose_name="Time Of Day",
                                          related_name='waste_time_of_day', **ALLOW_EMPTY_CONFIG)

    piers = models.IntegerField(default=0, verbose_name="Piers", **ALLOW_EMPTY_CONFIG)
    piers_date = models.DateField(verbose_name="Proposed Piers Date", **ALLOW_EMPTY_CONFIG)
    piers_date_notes = models.TextField(**ALLOW_EMPTY_CONFIG)
    piers_time_of_day = models.ForeignKey("CodeTimeOfDay", on_delete=models.PROTECT, verbose_name="Time Of Day",
                                          related_name='piers_time_of_day', **ALLOW_EMPTY_CONFIG)
    piers_inspection_date = models.DateField(verbose_name="Piers Inspection Date", **ALLOW_EMPTY_CONFIG)
    piers_inspection_date_notes = models.TextField(**ALLOW_EMPTY_CONFIG)
    pier_inspection_done = models.BooleanField(default=False, verbose_name="Pier Inspection Done")
    pier_concrete = models.DateField(verbose_name="Pier Concrete", **ALLOW_EMPTY_CONFIG)
    pier_concrete_notes = models.TextField(**ALLOW_EMPTY_CONFIG)
    piers_inspection_time_of_day = models.ForeignKey("CodeTimeOfDay", on_delete=models.PROTECT, verbose_name="Time Of Day",
                                                     related_name='piers_inspection_time_of_day', **ALLOW_EMPTY_CONFIG)

    piers_concrete_date = models.DateField(verbose_name="Piers Concrete Date", **ALLOW_EMPTY_CONFIG)

    piers_concrete_time_of_day = models.ForeignKey("CodeTimeOfDay", on_delete=models.PROTECT, verbose_name="Time Of Day",
                                                     related_name='piers_concrete_time_of_day', **ALLOW_EMPTY_CONFIG)

    concrete_date = models.DateField(verbose_name="Concrete Date", **ALLOW_EMPTY_CONFIG)
    concrete_date_notes = models.TextField(**ALLOW_EMPTY_CONFIG)
    
    concrete_mix = models.CharField(max_length=100, verbose_name="Concrete Mix", **ALLOW_EMPTY_CONFIG)

    slab_schedule_notes = models.TextField(**ALLOW_EMPTY_CONFIG)
    # multiple files model here
    start_date = models.DateField(verbose_name="Start Date", **ALLOW_EMPTY_CONFIG)
    call_up_date = models.DateField(verbose_name="Call Up Date", **ALLOW_EMPTY_CONFIG)
    call_up_date_notes = models.TextField(**ALLOW_EMPTY_CONFIG)
    take_off_sent = models.DateField(verbose_name="Take Off Sent", **ALLOW_EMPTY_CONFIG)
    proposed_start_date = models.DateField(verbose_name="Proposed Start Date", **ALLOW_EMPTY_CONFIG)
    paving_colour = models.ForeignKey("CodePavingColour", on_delete=models.PROTECT, verbose_name="Paving Colour", **ALLOW_EMPTY_CONFIG)
    excavation_allowance = models.DecimalField(verbose_name="Excavation Allowance", **MONEY_CONFIG)
    paving_type = models.ForeignKey("CodePavingType", on_delete=models.PROTECT, verbose_name="Paving Type", **ALLOW_EMPTY_CONFIG)
    date_cancelled = models.DateField(verbose_name="Date Cancelled", **ALLOW_EMPTY_CONFIG)
    has_conduit = models.BooleanField(default=False, verbose_name="Has Conduit")
    drains = models.IntegerField(default=0, verbose_name="Drains (m)")
    drain_type = models.ForeignKey("CodeDrainType", on_delete=models.PROTECT, verbose_name="Drain Type", **ALLOW_EMPTY_CONFIG)
    mix = models.ForeignKey("CodeMix", on_delete=models.PROTECT, verbose_name="Mix", **ALLOW_EMPTY_CONFIG)
    # dollars_difference = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    files = models.ManyToManyField("FileUpload")
    notes = models.ManyToManyField("Note")
    job_costs = models.ManyToManyField("JobCost")
    job_drains = models.ManyToManyField("JobDrains")
    purchase_orders = models.ManyToManyField("JobPurchaseOrder")
    xero_purchase_order = models.ForeignKey("ocom_xero.XeroEntity", on_delete=models.PROTECT, verbose_name="Xero Purchase Order",
                                            **ALLOW_EMPTY_CONFIG)

    dug_date = models.DateTimeField("Dug Date", **ALLOW_EMPTY_CONFIG)
    prepared_date = models.DateTimeField("Prepared Date", **ALLOW_EMPTY_CONFIG)
    poured_date = models.DateTimeField("Poured Date", **ALLOW_EMPTY_CONFIG)
    cut_date = models.DateTimeField("Cut Date", **ALLOW_EMPTY_CONFIG)
    sealed_date = models.DateTimeField("Sealed Date", **ALLOW_EMPTY_CONFIG)
    notifications = models.ManyToManyField("JobNotification")
    # Checklist fields
    down_pipes_installed = models.NullBooleanField(verbose_name="Down Pipes Installed")
    down_pipes_comment = models.CharField(max_length=255, verbose_name="Down Pipes Comment", **ALLOW_EMPTY_CONFIG)
    gas_line_installed = models.NullBooleanField(default=None, verbose_name="Gas Line Installed")
    gas_line_comment = models.CharField(max_length=255, verbose_name="Gas Line Comment", **ALLOW_EMPTY_CONFIG)
    rebates_brickwork = models.NullBooleanField(verbose_name="Rebates Flush With Brickwork")
    rebates_brickwork_comment = models.CharField(max_length=255, verbose_name="Gas Line Comment", **ALLOW_EMPTY_CONFIG)
    risers_correct_location = models.NullBooleanField(verbose_name="Risers in Correct Location")
    risers_location_comment = models.CharField(max_length=255, verbose_name="Risers Location Comment",
                                               **ALLOW_EMPTY_CONFIG)
    good_access_rear_paving = models.NullBooleanField(verbose_name="Good Access for Rear Paving")
    rear_paving_comment = models.CharField(max_length=255, verbose_name="Rear Paving Comment", **ALLOW_EMPTY_CONFIG)
    pacing_within_tolerance = models.NullBooleanField(verbose_name="Paving Heights Within Tolerance")
    pacing_heights_comment = models.CharField(max_length=255, verbose_name="Paving Heights Comment",
                                              **ALLOW_EMPTY_CONFIG)

    rock_supplier = models.ForeignKey("CodeSupplier", on_delete=models.PROTECT, verbose_name="Rock Supplier", related_name="job_rock_supplier", **ALLOW_EMPTY_CONFIG)
    pod_supplier = models.ForeignKey("CodeSupplier", on_delete=models.PROTECT, verbose_name="POD Supplier",  related_name="job_pod_supplier", **ALLOW_EMPTY_CONFIG)
    steel_supplier = models.ForeignKey("CodeSupplier", on_delete=models.PROTECT, verbose_name="Steel Supplier",  related_name="job_steel_supplier", **ALLOW_EMPTY_CONFIG)

    contractor_swms = models.NullBooleanField("Contractor SWMS", **ALLOW_EMPTY_CONFIG)
    approved_date = models.DateTimeField(verbose_name="Approved Date", **ALLOW_EMPTY_CONFIG)

    base_date = models.DateTimeField(verbose_name="Base Date", **ALLOW_EMPTY_CONFIG)
    base_date_notes = models.TextField(**ALLOW_EMPTY_CONFIG)

    concrete_time_of_day = models.ForeignKey("CodeTimeOfDay", on_delete=models.PROTECT, verbose_name="Time Of Day",
                                                    related_name='concrete_time_of_day', **ALLOW_EMPTY_CONFIG)

    class Meta:
        db_table = 'job'
        verbose_name = "Job"
        verbose_name_plural = "Jobs"

    def save(self, *args, **kwargs):
        super(ActiveModel, self).save(*args, **kwargs)


        new_code = "%s-%s" % (str(self.id), (self.job_type.description if self.job_type else "?")[0])

        if self.code != new_code:
            self.code = new_code
            if "force_insert" in kwargs:
                del kwargs["force_insert"]

            self.save(*args, **kwargs) # try save again - as nothing changes next time it should be not recursive.


class JobCost(ActiveModel):
    details = models.CharField(max_length=255, verbose_name="Details", **DISALLOW_EMPTY_CONFIG)
    purchase_order_number = models.CharField(max_length=255, verbose_name="Purchase Order Number", **ALLOW_EMPTY_CONFIG)
    xero_item_code = models.CharField(max_length=100, verbose_name="Xero Item", **DISALLOW_EMPTY_CONFIG)
    quantity = models.DecimalField(default=0, verbose_name="Quantity", max_digits=12, decimal_places=3)
    unit_price = models.DecimalField(verbose_name="Unit Price", **MONEY_CONFIG)
    total_price = models.DecimalField(verbose_name="Total Price", **MONEY_CONFIG)
    invoiced = models.BooleanField(default=False, verbose_name="Invoiced")

    class Meta:
        db_table = 'job_cost'
        verbose_name = "Job Cost"
        verbose_name_plural = "Job Costs"


class JobDrains(ActiveModel):
    drain_type = models.ForeignKey("CodeDrainType", on_delete=models.PROTECT, verbose_name="Drain Type", **DISALLOW_EMPTY_CONFIG)
    metres = models.DecimalField(verbose_name="Metres", max_digits=12, decimal_places=4, default=0,
                                 **ALLOW_EMPTY_CONFIG)

    class Meta:
        db_table = 'job_drains'
        verbose_name = "Job Drains"
        verbose_name_plural = "Job Drains"


class Task(OcomModel):
    description = models.TextField(**ALLOW_EMPTY_CONFIG)
    task_type = models.ForeignKey("CodeTaskType", on_delete=models.PROTECT, verbose_name="Task Type", **ALLOW_EMPTY_CONFIG)
    depot_type = models.ForeignKey("CodeDepotType", on_delete=models.PROTECT, verbose_name="Depot Type", **ALLOW_EMPTY_CONFIG)
    date_scheduled = models.DateField(verbose_name="Date Scheduled", **ALLOW_EMPTY_CONFIG)
    supplier = models.ForeignKey("Subbie", on_delete=models.PROTECT, verbose_name="Supplier", **ALLOW_EMPTY_CONFIG)
    complete_date = models.DateTimeField(verbose_name="Complete Date", **ALLOW_EMPTY_CONFIG)
    slot_order = models.IntegerField(default=0, verbose_name="Slot Order")
    job = models.ForeignKey("Job", on_delete=models.PROTECT, verbose_name="Job", **ALLOW_EMPTY_CONFIG)
    accepted_date = models.DateTimeField(verbose_name="Accept Date", **ALLOW_EMPTY_CONFIG)
    rejected_date = models.DateTimeField(verbose_name="Reject Date", **ALLOW_EMPTY_CONFIG)

    class Meta:
        db_table = 'task'
        verbose_name = "Task"
        verbose_name_plural = "Tasks"


class JobPurchaseOrder(OcomModel):
    order_type = models.ForeignKey("CodePurchaseOrderType", on_delete=models.PROTECT, verbose_name="Order Type", **ALLOW_EMPTY_CONFIG)
    number = models.CharField(max_length=50, verbose_name="Purchase Order Number", **DISALLOW_EMPTY_CONFIG)
    value = models.DecimalField(verbose_name="Purchase Order Value", **MONEY_CONFIG)
    details = models.CharField(max_length=255, verbose_name="Purchase Order Number", **ALLOW_EMPTY_CONFIG)

    class Meta:
        db_table = 'job_purchase_order'
        verbose_name = "Job Purchase Order"
        verbose_name_plural = "Job Purchase Orders"


class JobNotification(OcomModel):
    to_email = models.CharField(max_length=255, verbose_name="To Email", **DISALLOW_EMPTY_CONFIG)
    subject = models.CharField(max_length=255, verbose_name="Subject", **DISALLOW_EMPTY_CONFIG)
    body = models.TextField(verbose_name="Body", **DISALLOW_EMPTY_CONFIG)
    when = models.DateTimeField("When", **ALLOW_EMPTY_CONFIG)
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        db_table = 'job_notification'
        verbose_name = "Job Notification"
        verbose_name_plural = "Job Notifications"


class Repair(DescriptionActiveModel):
    end_date = models.DateField(verbose_name="End Date", **ALLOW_EMPTY_CONFIG)
    end_date_notes = models.TextField(**ALLOW_EMPTY_CONFIG)
    repair_type = models.ForeignKey("CodeRepairType", on_delete=models.PROTECT, verbose_name="Repair Type", **DISALLOW_EMPTY_CONFIG)
    date_received = models.DateField(verbose_name="Date Received", **DISALLOW_EMPTY_CONFIG)
    job = models.ForeignKey("Job", on_delete=models.PROTECT, **ALLOW_EMPTY_CONFIG)
    comments = models.TextField(**ALLOW_EMPTY_CONFIG)
    # address will be a serializer field
    # subbie will be a serializer field
    po_number = models.CharField(max_length=255, verbose_name="PO Number", **ALLOW_EMPTY_CONFIG)
    repair_subbie = models.ForeignKey("Subbie", on_delete=models.PROTECT, verbose_name="Repair Subbie", **DISALLOW_EMPTY_CONFIG)
    accepted_date = models.DateField(verbose_name="Accepted Date", **ALLOW_EMPTY_CONFIG)
    rejected_date = models.DateField(verbose_name="Rejected Date", **ALLOW_EMPTY_CONFIG)
    back_charge = models.BooleanField(default=False)
    permit_number = models.CharField(max_length=255, verbose_name="Permit Number", **ALLOW_EMPTY_CONFIG)
    due_date = models.DateField(verbose_name="Due Date", **DISALLOW_EMPTY_CONFIG)
    start_by = models.DateField(verbose_name="Start By", **ALLOW_EMPTY_CONFIG)
    # status will be a serializer field
    amount = models.DecimalField(**MONEY_CONFIG)
    completed_date = models.DateField(verbose_name="Completed Date", **ALLOW_EMPTY_CONFIG)
    # ignore type for now
    files = models.ManyToManyField("FileUpload")
    notes = models.ManyToManyField("Note")
    repair_costs = models.ManyToManyField("RepairCost")
    xero_purchase_order = models.ForeignKey("ocom_xero.XeroEntity", on_delete=models.PROTECT, verbose_name="Xero Purchase Order",
                                            **ALLOW_EMPTY_CONFIG)
    

    # for Repairs without Jobs
    no_job = models.BooleanField(verbose_name="Has No Job", default=False)
    supervisor = models.ForeignKey("Supervisor", on_delete=models.PROTECT, verbose_name="Supervisor",
                                  **ALLOW_EMPTY_CONFIG)
    address = models.TextField(**ALLOW_EMPTY_CONFIG)
    suburb = models.CharField(max_length=255, verbose_name="Suburb", **ALLOW_EMPTY_CONFIG)
    repair_amount = models.DecimalField(verbose_name="Repair Amount", **MONEY_CONFIG)


    class Meta:
        db_table = 'repair'
        verbose_name = "Repair"
        verbose_name_plural = "Repairs"


class RepairCost(ActiveModel):
    details = models.CharField(max_length=100, verbose_name="Details", **DISALLOW_EMPTY_CONFIG)
    xero_item_code = models.CharField(max_length=100, verbose_name="Xero Item", **DISALLOW_EMPTY_CONFIG)
    quantity = models.DecimalField(default=0, verbose_name="Quantity", max_digits=12, decimal_places=3)
    unit_price = models.DecimalField(verbose_name="Unit Price", **MONEY_CONFIG)
    total_price = models.DecimalField(verbose_name="Total Price", **MONEY_CONFIG)
    invoiced = models.BooleanField(verbose_name="Invoiced", default=False)

    class Meta:
        db_table = 'repair_cost'
        verbose_name = "Repair Cost"
        verbose_name_plural = "Repair Costs"


class Client(NameActiveModel):
    xero_customer = models.CharField(max_length=255, verbose_name="Xero Customer", **ALLOW_EMPTY_CONFIG)
    send_invoices = models.BooleanField(verbose_name="Send Invoices", default=True)
    # many to many suppliers
    suppliers = models.ManyToManyField("Subbie", blank=True)
    required_part_a = models.BooleanField(verbose_name="Part A Required?", default=True)
    they_supply_pump = models.BooleanField(verbose_name="They Supply Pump", default=False)
    number_of_purchase_orders = models.IntegerField(verbose_name="Number of PO's to expect", default=1,
                                                    **DISALLOW_EMPTY_CONFIG)

    class Meta:
        db_table = 'client'


class Role(ActiveModel):
    user = models.OneToOneField(User, verbose_name="Username", on_delete=models.CASCADE)
    administrator = models.BooleanField(default=False)
    supervisor = models.BooleanField(default=False)
    subcontractor = models.BooleanField(default=False)
    client_manager = models.BooleanField(default=False, verbose_name="Client Manager")
    employee = models.BooleanField(default=False, verbose_name="Employee")

    class Meta:
        db_table = "role"
        verbose_name = "User and Role"
        verbose_name_plural = "Users and Roles"

    @staticmethod
    def user_has_no_role(user):
        """Returns True if user has no Role relationships"""
        try:
            if user.role.administrator or True:
                return False
        except (Role.DoesNotExist, AttributeError):
            return True


class Hash(HashModel):
    class Meta:
        db_table = 'hash'
        verbose_name = "Hash"
        verbose_name_plural = "Hashes"


class CodeSupplier(models.Model):
    class Meta:
        db_table = "code_supplier"
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ['-id', ]  # TODO

    def __unicode__(self):
        return "{}".format(self.description)

    code = models.CharField(verbose_name="Code", null=True, blank=True, default=None, editable=True, help_text="",
                            unique=False, db_index=False, max_length=255, )
    description = models.CharField(verbose_name="Description", null=True, blank=True, default='', editable=True,
                                   help_text="", unique=False, db_index=False, max_length=255, )
    active_start_date = models.DateTimeField(verbose_name="Active Start Date", null=True, blank=True,
                                             default=timezone.now, editable=True, help_text="", unique=False,
                                             db_index=False, )
    active_end_date = models.DateTimeField(verbose_name="Active End Date", null=True, blank=True, default=None,
                                           editable=True, help_text="", unique=False, db_index=False, )
    created_date = models.DateTimeField(verbose_name="Created Date", null=True, blank=True, default=timezone.now,
                                        editable=True, help_text="", unique=False, db_index=False, )
    modified_date = models.DateTimeField(verbose_name="Modified Date", null=True, blank=True, default=None,
                                         editable=True, help_text="", unique=False, db_index=False, )
    supplier_type = models.ForeignKey('CodeSupplierType', on_delete=models.PROTECT,
                                      related_name="code_supplier_type", verbose_name="Supplier Type",
                                      null=True, blank=True, default=None, editable=True, help_text="", unique=False,
                                      db_index=False, )
    def __str__(self):
        return "{}".format(self.description)

class CodeSupplierType(models.Model):
    class Meta:
        db_table = "code_supplier_type"
        verbose_name = "Supplier Type"
        verbose_name_plural = "Supplier Types"
        ordering = ['-id', ]  # TODO

    def __unicode__(self):
        return "{}".format(self.description)

    code = models.CharField(verbose_name="Code", null=True, blank=True, default=None, editable=True, help_text="",
                            unique=False, db_index=False, max_length=255, )
    description = models.CharField(verbose_name="Description", null=True, blank=True, default='', editable=True,
                                   help_text="", unique=False, db_index=False, max_length=255, )
    active_start_date = models.DateTimeField(verbose_name="Active Start Date", null=True, blank=True,
                                             default=timezone.now, editable=True, help_text="", unique=False,
                                             db_index=False, )
    active_end_date = models.DateTimeField(verbose_name="Active End Date", null=True, blank=True, default=None,
                                           editable=True, help_text="", unique=False, db_index=False, )
    created_date = models.DateTimeField(verbose_name="Created Date", null=True, blank=True, default=timezone.now,
                                        editable=True, help_text="", unique=False, db_index=False, )
    modified_date = models.DateTimeField(verbose_name="Modified Date", null=True, blank=True, default=None,
                                         editable=True, help_text="", unique=False, db_index=False, )

    def __str__(self):
        return "{}".format(self.description)

class JobSupply(models.Model):
    class Meta:
        db_table = "job_supply"
        verbose_name = "Job Supply"
        verbose_name_plural = "Job Supplies"
        ordering = ['-id', ]  # TODO

    def __unicode__(self):
        return u'%s' % self.id  # TODO

    supplier_type = models.ForeignKey('CodeSupplierType', on_delete=models.PROTECT,
                                      related_name="job_supply_supplier_type", verbose_name="Supplier Type", null=True,
                                      blank=True, default=None, editable=True, help_text="", unique=False,
                                      db_index=False, )
    supplier = models.ForeignKey('CodeSupplier', on_delete=models.PROTECT, related_name="job_supply_supplier",
                                 verbose_name="Supplier", null=True, blank=True, default=None, editable=True,
                                 help_text="", unique=False, db_index=False, )
    book_date = models.DateField(verbose_name="Book Date", null=True, blank=True, default=None, editable=True,
                                 help_text="", unique=False, db_index=False, )
    book_time = models.ForeignKey('CodeTimeOfDay', on_delete=models.PROTECT, related_name="job_supply_book_time",
                                  verbose_name="Book Time", null=True, blank=True, default=None, editable=True,
                                  help_text="", unique=False, db_index=False, )
    booking_number = models.CharField(verbose_name="Booking Number", null=True, blank=True, default=None, editable=True,
                                      help_text="", unique=False, db_index=False, max_length=255, )

class XeroOAuth2Information (models.Model):
    """
    A class for storing the OAuth 2.0 access token and refresh token received from the sign-in with Xero.
    """

    # Columns
    access_token = models.TextField(null=False)
    refresh_token = models.TextField()