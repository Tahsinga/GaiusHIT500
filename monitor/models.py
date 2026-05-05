from django.db import models


class Patient(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=64, unique=True)
    current_patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True, related_name='rooms')

    def __str__(self):
        return self.name


class Reading(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='readings')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='readings', null=True, blank=True)
    temp_c = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    temp_f = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    bpm = models.IntegerField(null=True, blank=True)
    spo2 = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        patient_name = self.patient.name if self.patient else 'No Patient'
        return f"{self.room.name} - {patient_name} @ {self.timestamp.isoformat()}"


class Monitor(models.Model):
    identifier = models.CharField(max_length=32, unique=True)
    room = models.OneToOneField(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='monitor')

    def __str__(self):
        return f"Monitor {self.identifier} -> {self.room.name if self.room else 'unassigned'}"
    
    def save(self, *args, **kwargs):
        # If this monitor is being assigned to a room, unassign any other monitor from that room
        if self.room:
            # Find any other monitor assigned to this room
            other_monitors = Monitor.objects.filter(room=self.room).exclude(pk=self.pk)
            for other in other_monitors:
                other.room = None
                other.save()
        super().save(*args, **kwargs)
