from rest_framework import serializers
from .models import ProcessSnapshot, Process

class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ["pid", "ppid", "name", "cpu", "memory", "cmdline", "username"]


class ProcessSnapshotSerializer(serializers.ModelSerializer):
    processes = ProcessSerializer(many=True)

    class Meta:
        model = ProcessSnapshot
        fields = [
            "id",
            "hostname",
            "timestamp",
            "os",
            "processor",
            "cores",
            "threads",
            "ram_gb",
            "used_ram_gb",
            "free_ram_gb",
            "storage_free_gb",
            "storage_total_gb",
            "storage_used_gb",
            "processes",
        ]

    def create(self, validated_data):
        processes_data = validated_data.pop("processes")
        snapshot = ProcessSnapshot.objects.create(**validated_data)
        for proc in processes_data:
            Process.objects.create(snapshot=snapshot, **proc)
        return snapshot
