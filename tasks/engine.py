from mongoengine import *

connect('project1', host='mongodb://localhost/engt')

class Page(DynamicDocument):
    ref = StringField(primary_key=True, required=True)
    title = StringField(max_length=200, required=True)
_ref = '/Applications/IntelliJ IDEA CE.app/Contents/plugins/android/lib/layoutlib/data/res/drawable/seekbar_thumb_unpressed_to_pressed.xml'
# '/tmp/1.json'
page = Page(ref=_ref, title='Using MongoEngine')
page.tags = ['mongodb', 'mongoengine']
page.save()
Page.objects(tags='mongoengine').count()
