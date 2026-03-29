# Generated migration to remove tasks without users and make user field required

from django.db import migrations, models
import django.db.models.deletion

def remove_orphaned_tasks(apps, schema_editor):
    """Remove tasks that don't have a user assigned"""
    TaskModel = apps.get_model('scheduler', 'TaskModel')
    TaskModel.objects.filter(user__isnull=True).delete()

def reverse_remove_orphaned_tasks(apps, schema_editor):
    """Reverse migration - nothing to do"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0002_taskmodel_user'),
    ]

    operations = [
        migrations.RunPython(remove_orphaned_tasks, reverse_remove_orphaned_tasks),
        migrations.AlterField(
            model_name='taskmodel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='auth.user'),
        ),
    ]
