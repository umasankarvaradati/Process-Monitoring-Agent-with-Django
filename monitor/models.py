from django.db import models

class ProcessSnapshot(models.Model):
    hostname = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    # new system fields
    os = models.CharField(max_length=100, blank=True, null=True)
    processor = models.CharField(max_length=200, blank=True, null=True)
    cores = models.IntegerField(default=0)
    threads = models.IntegerField(default=0)
    ram_gb = models.FloatField(default=0.0)
    used_ram_gb = models.FloatField(default=0.0)
    free_ram_gb = models.FloatField(default=0.0)
    storage_free_gb = models.FloatField(default=0.0)
    storage_total_gb = models.FloatField(default=0.0)
    storage_used_gb = models.FloatField(default=0.0)



class Process(models.Model):
    """
    A single process entry tied to a ProcessSnapshot.
    - memory: stored in MB (float) as sent by the agent
    - cpu: percent (float)
    - cmdline and username for additional details
    """
    snapshot = models.ForeignKey(
        ProcessSnapshot,
        on_delete=models.CASCADE,
        related_name="processes",
        db_index=True
    )
    pid = models.IntegerField(db_index=True)
    ppid = models.IntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    cpu = models.FloatField(help_text="CPU usage in percent (e.g. 2.5)")
    memory = models.FloatField(help_text="Memory in MB (e.g. 324.66)")
    cmdline = models.TextField(blank=True, default="")
    username = models.CharField(max_length=150, blank=True, default="")

    class Meta:
        # ensure there is only one Process row per (snapshot, pid)
        unique_together = ('snapshot', 'pid')
        indexes = [
            models.Index(fields=['pid']),
            models.Index(fields=['ppid']),
            models.Index(fields=['snapshot', 'pid']),
        ]
        ordering = ['-memory']  # default ordering (largest memory first)

    def __str__(self):
        return f"{self.name} (pid={self.pid})"
