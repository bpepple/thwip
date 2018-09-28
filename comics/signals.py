
def pre_delete_image(sender, instance, **kwargs):
    if (instance.image):
        instance.image.delete(False)


def pre_delete_issue(sender, instance, **kwargs):
    if (instance.image):
        instance.image.delete(False)

    # Delete related arc if this is the only
    # issue related to that arc.
    for arc in instance.arcs.all():
        if arc.issue_set.count() == 1:
            arc.delete()
