for org in Organization.objects.all():
    org.slug = org.name.replace("& ","").replace("&","").replace("'","").replace(".","_").replace(" ","_").lower()
    org.save()