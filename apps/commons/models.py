from django.db import models

def convert_to_str(dj_obj):
  """
  Convert a django object to a string of the form
  classname=X field1=val1 ...
  """
  try:
      fields = dj_obj._meta.get_fields()
      fields_str = " ".join(["%s=%s" % (field.name, field.value_to_string(dj_obj)) for field in fields if
                              hasattr(field, 'value_to_string') and field.value_from_object(dj_obj) is not None])
  except AttributeError:
      return dj_obj.__class__.__name__
  return " %s %s" % (dj_obj.__class__.__name__, fields_str)

class AuditModel(models.Model):
  created_by = models.CharField(max_length=128, default=None, null=True, blank=True)
  updated_by = models.CharField(max_length=128, default=None, null=True, blank=True)

  class Meta:
    abstract = True
  
  def __str__(self):
    return f"created by: {self.created_by}, updated by: {self.updated_by}"

class BaseModel(models.Model):
  created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
  updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

  class Meta:
    abstract = True
  
  def __str__(self):
    return convert_to_str(self)
  
  def save(self, *args, **kwargs):
    if 'update_fields' in kwargs and 'updated_at' not in kwargs['update_fields']:
      kwargs['update_fields'] = frozenset(list(kwargs['updated_fields']) + ['updated_at'])
    super(BaseModel, self).save(*args, **kwargs)