"""Regressions for inactive weak edges observed in SQLx Cargo metadata."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'sbom'))
from augment_spdx import selected_graph, target_matches


class CargoGraphTest(unittest.TestCase):
    def metadata(self):
        packages, nodes = {}, {}

        def package(name, features=None, resolved=()):
            packages[name] = {'id': name, 'name': name, 'features': features or {},
                              'dependencies': [], 'targets': [{'kind': ['lib']}]}
            nodes[name] = {'id': name, 'features': list(resolved), 'deps': []}

        def edge(parent, child, optional=False, features=(), rename=None, library=None):
            packages[parent]['dependencies'].append({'name': child, 'rename': rename,
                'optional': optional, 'kind': None, 'target': None,
                'features': list(features), 'uses_default_features': False})
            nodes[parent]['deps'].append({'pkg': child, 'name': (library or rename or child).replace('-', '_'),
                                         'dep_kinds': [{'kind': None, 'target': None}]})

        package('root', {'pg18': ['backend/postgres', 'backend/any']}, ['pg18'])
        package('backend', {'postgres': ['dep:postgres'], 'mysql': ['dep:mysql'],
                            'any': ['mysql?/json']}, ['postgres', 'any'])
        package('postgres')
        package('mysql')
        package('digest', {'oid': ['dep:const-oid']}, ['oid'])
        package('const-oid')
        package('md-5')
        packages['md-5']['targets'][0]['name'] = 'md5'
        edge('root', 'backend', rename='backend')
        edge('backend', 'postgres', optional=True)
        edge('backend', 'mysql', optional=True)
        edge('postgres', 'digest')
        edge('mysql', 'digest', features=['oid'])
        edge('digest', 'const-oid', optional=True)
        edge('postgres', 'md-5', library='md5')
        return {'version': 1, 'packages': list(packages.values()),
                'resolve': {'nodes': list(nodes.values())}}

    def test_weak_edge_does_not_activate_backend_or_shared_features(self):
        selected, edges = selected_graph(self.metadata(), 'root')
        self.assertEqual(set(selected), {'root', 'backend', 'postgres', 'digest', 'md-5'})
        self.assertIn(('postgres', 'md-5'), edges)

    def test_strong_dependency_feature_activates_optional_and_transitive_features(self):
        metadata = self.metadata()
        metadata['packages'][0]['features']['pg18'].append('backend/mysql')
        selected, edges = selected_graph(metadata, 'root')
        self.assertEqual(set(selected), {p['id'] for p in metadata['packages']})
        self.assertIn(('digest', 'const-oid'), edges)

    def test_renamed_optional_dependency_and_default_features(self):
        metadata = self.metadata()
        root = metadata['packages'][0]
        root['dependencies'][0].update(optional=True, rename='renamed', uses_default_features=True)
        root['features']['pg18'] = ['dep:renamed']
        metadata['resolve']['nodes'][0]['deps'][0]['name'] = 'renamed'
        metadata['packages'][1]['features']['default'] = ['postgres']
        selected, _ = selected_graph(metadata, 'root')
        self.assertEqual(set(selected), {'root', 'backend', 'postgres', 'digest', 'md-5'})

    def test_retained_foreign_condition_does_not_enable_features(self):
        metadata = self.metadata()
        postgres = next(p for p in metadata['packages'] if p['name'] == 'postgres')
        normal = next(d for d in postgres['dependencies'] if d['name'] == 'digest')
        normal['target'] = 'cfg(not(target_arch = "wasm32"))'
        foreign = {**normal, 'target': 'cfg(target_arch = "wasm32")', 'features': ['oid']}
        postgres['dependencies'].append(foreign)
        node = next(n for n in metadata['resolve']['nodes'] if n['id'] == 'postgres')
        edge = next(d for d in node['deps'] if d['pkg'] == 'digest')
        edge['dep_kinds'] = [{'kind': None, 'target': d['target']} for d in (normal, foreign)]
        selected, _ = selected_graph(metadata, 'root', target_cfg=['target_arch="x86_64"'], rust_target='x86_64-unknown-linux-gnu')
        self.assertNotIn('const-oid', selected)

    def test_target_condition_operators_and_invalid_input(self):
        facts = ['unix', 'target_arch="aarch64"', 'target_os="linux"']
        triple = 'aarch64-unknown-linux-gnu'
        self.assertTrue(target_matches('cfg(all(unix, any(target_arch="aarch64", target_arch="x86_64"), not(target_os="windows")))', facts, triple))
        self.assertTrue(target_matches(triple, facts, triple))
        self.assertFalse(target_matches('x86_64-unknown-linux-gnu', facts, triple))
        for condition in ['cfg(not(unix, unix))', 'cfg(all(unix)', 'cfg(unix) junk']:
            with self.subTest(condition=condition), self.assertRaises(ValueError):
                target_matches(condition, facts, triple)


if __name__ == '__main__':
    unittest.main()
