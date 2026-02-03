# Generated migration for adding soft delete to Message model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0013_add_conversation_and_message_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True, help_text='Soft delete timestamp - message is hidden but not removed'),
        ),
        migrations.AddField(
            model_name='message',
            name='deleted_by',
            field=models.ForeignKey(blank=True, help_text='User who deleted this message', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deleted_messages', to='auth.user'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['deleted_at'], name='listings_me_deleted_idx'),
        ),
    ]
