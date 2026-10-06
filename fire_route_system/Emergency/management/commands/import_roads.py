import json
import urllib.request
import urllib.parse
from pathlib import Path
from django.core.management.base import BaseCommand,CommandError
from django.db import transaction
from django.conf import settings
from DataAccess.models import FireStation
from Emergency.models import RoadNode,RoadEdge
from Emergency.routing import distance


class Command(BaseCommand):
    help='Import drivable Mandalay OSM roads from an Overpass JSON file or download once.'
    def add_arguments(self,parser):
        parser.add_argument('--file',type=str)
        parser.add_argument('--download',action='store_true')
    def handle(self,*args,**options):
        cache=Path(settings.BASE_DIR)/'runtime'/'mandalay-roads.json'
        source=Path(options['file']) if options['file'] else cache
        if options['download']:
            stations=list(FireStation.objects.filter(status='Active',latitude__gte=21.75,latitude__lte=22.2,longitude__gte=95.85,longitude__lte=96.35).values_list('latitude','longitude'))
            invalid=FireStation.objects.filter(status='Active').exclude(latitude__gte=21.75,latitude__lte=22.2,longitude__gte=95.85,longitude__lte=96.35).count()
            if invalid:self.stdout.write(self.style.WARNING(f'{invalid} station(s) outside the Mandalay demo area; correct their coordinates before routing.'))
            south=min([21.8]+[p[0] for p in stations])-0.025;north=max([22.08]+[p[0] for p in stations])+0.025
            west=min([95.99]+[p[1] for p in stations])-0.025;east=max([96.16]+[p[1] for p in stations])+0.025
            query=f'[out:json][timeout:180];way["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|service|living_street|motorway_link|trunk_link|primary_link|secondary_link|tertiary_link)$"]({south},{west},{north},{east});(._;>;);out body;'
            request=urllib.request.Request('https://overpass-api.de/api/interpreter',data=urllib.parse.urlencode({'data':query}).encode(),headers={'User-Agent':'MandalayFireEmergencyDemo/1.0 (local educational project)'})
            try:
                with urllib.request.urlopen(request,timeout=210) as result:payload=result.read()
            except Exception as error:raise CommandError(f'Road download failed: {error}. Supply --file with an Overpass JSON export.')
            source.parent.mkdir(parents=True,exist_ok=True);source.write_bytes(payload)
        if not source.exists():raise CommandError('Provide --download or --file with OSM Overpass JSON.')
        try:elements=json.loads(source.read_text(encoding='utf-8'))['elements']
        except (ValueError,KeyError):raise CommandError('Invalid Overpass JSON')
        nodes={e['id']:e for e in elements if e['type']=='node'}
        ways=[e for e in elements if e['type']=='way' and e.get('tags',{}).get('highway')]
        edges=[];used=set()
        for way in ways:
            tags=way.get('tags',{})
            if tags.get('access') in ['no','private'] or tags.get('motor_vehicle') in ['no','private'] or tags.get('motorcar') in ['no','private']:continue
            if tags['highway'] in ['footway','path','pedestrian','cycleway','steps','construction']:continue
            oneway=tags.get('oneway','yes' if tags.get('junction')=='roundabout' else 'no')
            for a,b in zip(way['nodes'],way['nodes'][1:]):
                if a not in nodes or b not in nodes:continue
                length=distance((nodes[a]['lat'],nodes[a]['lon']),(nodes[b]['lat'],nodes[b]['lon']))
                name=tags.get('name:my',tags.get('name',''))[:255]
                if oneway!='-1':edges.append((a,b,length,name))
                if oneway not in ['yes','1','true']:edges.append((b,a,length,name))
                used.update([a,b])
        if not edges:raise CommandError('No drivable edges found; existing road graph preserved.')
        with transaction.atomic():
            RoadEdge.objects.all().delete();RoadNode.objects.all().delete()
            RoadNode.objects.bulk_create([RoadNode(osm_id=n,latitude=nodes[n]['lat'],longitude=nodes[n]['lon']) for n in used],batch_size=1000)
            mapping=dict(RoadNode.objects.values_list('osm_id','pk'))
            RoadEdge.objects.bulk_create([RoadEdge(source_id=mapping[a],target_id=mapping[b],metres=length,name=name) for a,b,length,name in edges],batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f'Imported {len(used)} OSM nodes and {len(edges)} directed edges. © OpenStreetMap contributors.'))
