from django.db import models

class Bonos(models.Model):
    id = models.UUIDField(primary_key=True)
    evaluacion = models.ForeignKey('Evaluaciones', models.DO_NOTHING)
    salario_base_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    impacto_ebitda_logrado = models.DecimalField(max_digits=5, decimal_places=2)
    performance_index = models.DecimalField(max_digits=5, decimal_places=2)
    monto_final_bono = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_calculo = models.DateTimeField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'bonos'