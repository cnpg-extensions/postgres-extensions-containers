import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from verify import validate_layout, fresh_output

class GraphTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); (self.root/'blobs/sha256').mkdir(parents=True)
        config=self.blob({'os':'linux','architecture':'amd64'})
        layer=self.blob({'payload':'test'})
        self.child=self.blob({'schemaVersion':2,'config':config,'layers':[layer]})
        self.child['platform']={'os':'linux','architecture':'amd64'}
        self.spdx={'spdxVersion':'SPDX-2.3','SPDXID':'SPDXRef-DOCUMENT','files':[],'packages':[],'relationships':[]}
        subjects=[{'name':'fixture','digest':{'sha256':self.child['digest'][7:]}}]
        self.statements=[{'_type':'https://in-toto.io/Statement/v1','subject':subjects,'predicateType':kind,'predicate':predicate}
            for kind,predicate in [('https://spdx.dev/Document',self.spdx),('https://slsa.dev/provenance/v1',{'buildDefinition':{},'runDetails':{}})]]
        self.att={'schemaVersion':2,'subject':{k:v for k,v in self.child.items() if k!='platform'},'config':self.blob({}),'layers':[self.blob(s) for s in self.statements]}
        self.write_index()

    def blob(self,obj):
        raw=json.dumps(obj,sort_keys=True).encode(); hexdigest=hashlib.sha256(raw).hexdigest()
        (self.root/'blobs/sha256'/hexdigest).write_bytes(raw)
        return {'digest':'sha256:'+hexdigest,'size':len(raw),'mediaType':'application/vnd.oci.image.manifest.v1+json'}

    def write_index(self):
        att=self.blob(self.att); att.update(platform={'os':'unknown','architecture':'unknown'},annotations={'vnd.docker.reference.type':'attestation-manifest','vnd.docker.reference.digest':self.child['digest']})
        self.index={'schemaVersion':2,'mediaType':'application/vnd.oci.image.index.v1+json','manifests':[self.child,att]}
        self.index_desc=self.blob(self.index)

    def check(self):
        return validate_layout(self.root,self.index_desc['digest'],['linux/amd64'])

    def test_valid_complete_graph(self):
        result=self.check()
        self.assertEqual(result['platforms']['linux/amd64']['spdx'],self.spdx)

    def test_corruption_fails(self):
        path=self.root/'blobs/sha256'/self.child['digest'][7:]; path.write_text('{}')
        with self.assertRaisesRegex(ValueError,'hash|size'):self.check()

    def test_wrong_subject_and_missing_predicate(self):
        self.statements[0]['subject'][0]['digest']['sha256']='0'*64
        self.att['layers']=[self.blob(s) for s in self.statements]; self.write_index()
        with self.assertRaisesRegex(ValueError,'subject'):self.check()
        self.att['layers']=self.att['layers'][1:]; self.write_index()
        with self.assertRaises(ValueError):self.check()

    def test_wrong_platform(self):
        with self.assertRaises(ValueError):validate_layout(self.root,self.index_desc['digest'],['linux/arm64'])

    def test_stale_outputs_rejected(self):
        path=self.root/'verified';path.mkdir();(path/'sbom.spdx.json').write_text('stale')
        with self.assertRaises(ValueError):fresh_output(path)

    def test_two_platforms_are_independent_data(self):
        arm=self.blob({'schemaVersion':2,'config':self.blob({'os':'linux','architecture':'arm64'}),'layers':[]})
        arm['platform']={'os':'linux','architecture':'arm64'}
        statements=json.loads(json.dumps(self.statements))
        for statement in statements:statement['subject'][0]['digest']['sha256']=arm['digest'][7:]
        att=self.blob({'schemaVersion':2,'subject':{k:v for k,v in arm.items() if k!='platform'},'config':self.blob({}),'layers':[self.blob(s) for s in statements]})
        att.update(platform={'os':'unknown','architecture':'unknown'},annotations={'vnd.docker.reference.type':'attestation-manifest','vnd.docker.reference.digest':arm['digest']})
        self.index['manifests'] += [arm,att];descriptor=self.blob(self.index)
        result=validate_layout(self.root,descriptor['digest'],['linux/amd64','linux/arm64'])
        self.assertEqual(len(result['platforms']),2)
        statements[0]['subject'][0]['digest']['sha256']=self.child['digest'][7:]
        wrong=self.blob({'schemaVersion':2,'subject':{k:v for k,v in arm.items() if k!='platform'},'config':self.blob({}),'layers':[self.blob(s) for s in statements]})
        wrong.update(platform=att['platform'],annotations=att['annotations']);self.index['manifests'][-1]=wrong
        with self.assertRaisesRegex(ValueError,'subject'):validate_layout(self.root,self.blob(self.index)['digest'],['linux/amd64','linux/arm64'])

    def test_symlinked_blob_rejected(self):
        file=self.root/'blobs/sha256'/self.child['digest'][7:]
        outside=self.root/'original';file.rename(outside);file.symlink_to(outside)
        with self.assertRaisesRegex(ValueError,'symlink'):self.check()
