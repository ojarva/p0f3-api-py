"""
This is a complete Django ORM model for p0f data.

The easiest way to add new data is something along the lines of


   del data_from_p0f["magic"]
   del data_from_p0f["uptime"]
   del data_from_p0f["uptime_min"]
   P0fRecord.objects.create(**data_from_p0f)

"""

from django.db import models


class P0fRecord(models.Model):
    OS_NORMAL = 0
    OS_FUZZY = 1
    OS_GENERIC = 2
    OS_BOTH = 3

    OS_MATCH = (
        (OS_NORMAL, "Normal"),
        (OS_FUZZY, "Fuzzy"),
        (OS_GENERIC, "Generic signature"),
        (OS_BOTH, "Using both"),
    )

    BAD_SW_OS_MISMATCH = 1
    BAD_SW_MISMATCH = 2

    BAD_SW = (
        (BAD_SW_OS_MISMATCH, "OS mismatch"),
        (BAD_SW_MISMATCH, "Mismatch"),
    )

    class Meta:
        ordering = ["first_seen", "last_seen"]
        get_latest_by = "last_seen"

    def __unicode__(self):
        return u"%s: %s @ %s" % (self.remote_ip, self.os_name, self.first_seen)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    remote_ip = models.GenericIPAddressField()

    first_seen = models.DateTimeField(help_text="First observation of the host")
    last_seen = models.DateTimeField(help_text="Most recent observation of the host")
    total_conn = models.IntegerField(help_text="Total number of connections seen")
    uptime_sec = models.IntegerField(
        null=True, blank=True, help_text="Calculated system uptime in seconds, None if not available"
    )
    up_mod_days = models.IntegerField(null=True, blank=True, help_text="Uptime wrap-around time in days")
    last_nat = models.DateTimeField(
        null=True, blank=True, help_text="Time of the most recent detection of IP sharing, None if never detected"
    )
    last_chg = models.DateTimeField(
        null=True, blank=True, help_text="Time of the most recent OS mismatch (e.g multiboot or IP reuse)"
    )
    distance = models.IntegerField(null=True, blank=True, help_text="System distance (from TTL). None if no data")
    bad_sw = models.CharField(
        max_length=1, choices=BAD_SW, null=True, help_text="Whether user-agent and/or Server string are accurate"
    )
    os_match_q = models.CharField(max_length=1, choices=OS_MATCH, help_text="OS match quality")

    os_name = models.CharField(max_length=32, null=True, blank=True, help_text="Name of the most recently matched OS")
    os_flavor = models.CharField(max_length=32, null=True, blank=True, help_text="OS version")
    http_name = models.CharField(
        max_length=32, null=True, blank=True, help_text="Name of the most recently identified HTTP application"
    )
    http_flavor = models.CharField(
        max_length=32, null=True, blank=True, help_text="Flavor of the most recently identified HTTP application"
    )
    link_type = models.CharField(max_length=32, null=True, blank=True, help_text="Network link type, if autodetected")
    language = models.CharField(max_length=32, null=True, blank=True, help_text="Remote system language, if recognized")
