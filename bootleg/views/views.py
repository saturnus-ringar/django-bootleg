from django.utils.translation import ugettext_lazy as _
from django_tables2 import tables

from bootleg.views.base import BaseTemplateView


def get_default_table(model):
    table_class = tables.table_factory(model, fields=model._meta.visible_fields + ["get_add_link"])
    table_class._meta.attrs["class"] = "table table-striped table-responsive table-hover w-100 d-block d-md-table"
    return table_class


class DevNullView(BaseTemplateView):
    title = _("dev/null")
    heading = _("dev/null")
    extra_text = "In some operating systems, the null device is a device file that discards all data written to it but " \
                 "reports that the write operation succeeded. This device is called /dev/null on Unix and Unix-like systems, " \
                 "NUL: or NUL on CP/M and DOS (internally \\DEV\\NUL), nul on newer Windows systems[1] " \
                 "(internally \\Device\\Null on Windows NT), NIL: on Amiga operating systems,[2] and NL: on OpenVMS.[3] In " \
                 "Windows Powershell, the equivalent is $null.[4] It provides no data to any process that reads from it, " \
                 "yielding EOF immediately.[5] In IBM DOS/360, OS/360 (MFT, MVT), OS/390 and z/OS operating systems, " \
                 "such files would be assigned in JCL to DD DUMMY."
