# views.py
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from.serializers import ProcessSnapshotSerializer
from .models import ProcessSnapshot, Process

# Use env var in production; hard-coded for now to match your agent.
import os
API_KEY = os.environ.get("PROCESS_MONITOR_API_KEY",
                         "django-insecure-=402zvk_$qvoqrv2d7^6+mi7d_st#&md6y3_ft3m!e)lp@-3!2")


def frontend(request):
    """
    Serve the frontend page (index.html). Ensure your template exists.
    """
    return render(request, "index.html")

@api_view(["POST"])
def receive_process_data(request):
    auth = request.headers.get("Authorization", "")
    if auth != f"Token {API_KEY}":
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    # Flatten "system" block into top-level snapshot fields
    data = request.data.copy()
    system = data.pop("system", {})
    if system:
        data.update({
            "os": system.get("os"),
            "processor": system.get("processor"),
            "cores": system.get("cores"),
            "threads": system.get("threads"),
            "ram_gb": system.get("ram_gb"),
            "used_ram_gb": system.get("used_ram_gb"),
            "free_ram_gb": system.get("free_ram_gb"),
            "storage_free_gb": system.get("storage_free_gb"),
            "storage_total_gb": system.get("storage_total_gb"),
            "storage_used_gb": system.get("storage_used_gb"),
        })

    serializer = ProcessSnapshotSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Data saved"}, status=201)
    else:
        return Response(serializer.errors, status=400)


@api_view(["GET"])
def latest_snapshot(request):
    """
    Return the latest ProcessSnapshot in a shape expected by the UI:
    {
      "hostname": "...",
      "timestamp": "ISO8601",
      "system": {...},
      "processes": [
         {"pid":..., "ppid":..., "name":"...", "memory":..., "cpu":..., "cmdline":"...", "username":"..."},
         ...
      ]
    }
    """
    snapshot = ProcessSnapshot.objects.order_by("-timestamp").first()
    if not snapshot:
        return Response({"error": "No data"}, status=status.HTTP_404_NOT_FOUND)

    # get processes for this snapshot, sorted by memory desc (largest first)
    qs = snapshot.processes.all().order_by("-memory", "-cpu", "pid")
    processes = []
    for p in qs:
        processes.append({
            "pid": p.pid,
            "ppid": p.ppid,
            "name": p.name,
            "memory": float(p.memory),
            "cpu": float(p.cpu),
            "cmdline": p.cmdline,
            "username": p.username
        })

    # Build system info from snapshot fields
    system_info = {
        "os": snapshot.os,
        "processor": snapshot.processor,
        "cores": snapshot.cores,
        "threads": snapshot.threads,
        "ram_gb": snapshot.ram_gb,
        "used_ram_gb": snapshot.used_ram_gb,
        "free_ram_gb": snapshot.free_ram_gb,
        "storage_free_gb": snapshot.storage_free_gb,
        "storage_total_gb": snapshot.storage_total_gb,
        "storage_used_gb": snapshot.storage_used_gb,
    }

    resp = {
        "hostname": snapshot.hostname,
        "timestamp": snapshot.timestamp.isoformat(),
        "system": system_info,
        "processes": processes
    }
    return Response(resp, status=status.HTTP_200_OK)
