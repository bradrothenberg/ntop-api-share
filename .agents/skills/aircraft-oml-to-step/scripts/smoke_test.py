"""Small synthetic checks for the bundled measurement helpers.

Run: uv run --with cadquery-ocp --with numpy python smoke_test.py
"""
import csv
import math
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeVertex
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.TopoDS import TopoDS_Compound
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
from audit_step import audit, failures
from compare_points import summarize
from audit_surface_contract import audit as surface_audit


class HelperChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def export(self, shape, name):
        path = self.root / (name + '.step')
        writer = STEPControl_Writer()
        self.assertEqual(writer.Transfer(shape, STEPControl_AsIs), IFSelect_RetDone)
        self.assertEqual(writer.Write(str(path)), IFSelect_RetDone)
        return path

    def test_box_dimensions_and_requirements(self):
        report = audit(self.export(BRepPrimAPI_MakeBox(10, 20, 30).Shape(), 'box'))
        self.assertEqual(failures(report, 1, True), [])
        self.assertEqual(report['kernel_check']['status'], 'pass')
        self.assertEqual(report['topology']['faces'], 6)
        self.assertAlmostEqual(report['closed_solid_volume_mm3'], 6000, places=6)
        for value, expected in zip(report['bounds_mm'][1], [10, 20, 30]):
            self.assertAlmostEqual(value, expected, places=6)
        self.assertTrue(failures(report, 2, True))
        self.assertTrue(failures(report, 1, True, 1e-10))

    def test_cylinder_seam_is_not_an_open_edge(self):
        report = audit(self.export(BRepPrimAPI_MakeCylinder(5, 20).Shape(), 'cylinder'))
        self.assertEqual(failures(report, 1, True), [])
        self.assertAlmostEqual(report['closed_solid_volume_mm3'], math.pi * 500, places=5)

    def test_surface_is_rejected_when_closed_solid_required(self):
        face = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(), gp_Dir(0, 0, 1)), 0, 10, 0, 10).Face()
        report = audit(self.export(face, 'surface'), kernel=False)
        self.assertEqual(report['kernel_check']['status'], 'skipped')
        self.assertEqual(report['nondegenerate_edge_uses'], {'1': 4})
        self.assertTrue(failures(report, require_closed=True))

    def test_loose_edge_is_not_hidden_by_a_valid_solid(self):
        builder = BRep_Builder()
        compound = TopoDS_Compound()
        builder.MakeCompound(compound)
        builder.Add(compound, BRepPrimAPI_MakeBox(10, 10, 10).Shape())
        builder.Add(compound, BRepBuilderAPI_MakeEdge(gp_Pnt(20, 0, 0), gp_Pnt(30, 0, 0)).Edge())
        report = audit(self.export(compound, 'loose_edge'), kernel=False)
        self.assertEqual(report['nondegenerate_edge_uses'].get('0'), 1)
        self.assertTrue(failures(report, 1, True))

    def test_loose_vertex_is_not_hidden_by_a_valid_solid(self):
        builder = BRep_Builder()
        compound = TopoDS_Compound()
        builder.MakeCompound(compound)
        builder.Add(compound, BRepPrimAPI_MakeBox(10, 20, 30).Shape())
        builder.Add(compound, BRepBuilderAPI_MakeVertex(gp_Pnt(100, 100, 100)).Vertex())
        report = audit(self.export(compound, 'loose_vertex'))
        self.assertEqual(report['vertices_outside_edges'], 1)
        self.assertEqual(report['kernel_check']['status'], 'pass')
        self.assertTrue(failures(report, 1, True))

    def pairs(self, rows):
        path = self.root / 'pairs.csv'
        with path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['cad_x', 'cad_y', 'cad_z', 'source_x', 'source_y', 'source_z', 'region', 'source_residual_mm'])
            writer.writerows(rows)
        return path

    def test_known_distances_regions_and_projection_failure(self):
        path = self.pairs([[0, 0, 0, 3, 4, 0, 'wing', 0], [1, 2, 3, 1, 2, 3, 'wing', 0],
                           [0, 0, 0, 0, 0, 12, 'inlet', .2]])
        report = summarize(path, residual_limit=.1)
        self.assertEqual(report['global']['count'], 3)
        self.assertEqual(report['global']['median_mm'], 5)
        self.assertEqual(report['global']['max_mm'], 12)
        self.assertAlmostEqual(report['global']['rms_mm'], math.sqrt(169 / 3))
        self.assertEqual(report['regions']['inlet']['max_mm'], 12)
        self.assertEqual(report['source_residual_exceedances'], 1)
        self.assertFalse(report['residual_requirement_passed'])
        self.assertEqual(report['worst_samples'][0]['csv_line'], 4)

    def test_nonfinite_projection_is_rejected(self):
        path = self.pairs([[0, 0, 0, 'nan', 0, 0, 'fin', 0]])
        with self.assertRaises(ValueError):
            summarize(path)

    def test_audit_rejects_file_changed_during_read(self):
        path = self.export(BRepPrimAPI_MakeBox(10, 20, 30).Shape(), 'changing_box')
        initial = path.read_bytes()
        with patch.object(Path, 'read_bytes', side_effect=[initial, initial + b'changed']):
            with self.assertRaisesRegex(ValueError, 'changed during'):
                audit(path, kernel=False)

    def test_surface_inventory_reports_analytic_geometry(self):
        path = self.export(BRepPrimAPI_MakeCylinder(5, 20).Shape(), 'analytic_cylinder')
        result = surface_audit(path, max_degree=4)
        self.assertTrue(result['requirements_passed'])
        self.assertTrue(result['unchanged'])
        kinds = {r['geometry']['type'] for r in result['representations'] if r['kind'] == 'surface'}
        self.assertIn('Geom_CylindricalSurface', kinds)
        self.assertIn('Geom_Plane', kinds)

    def test_surface_inventory_rejects_stale_join_plan(self):
        import json
        path = self.export(BRepPrimAPI_MakeBox(10, 20, 30).Shape(), 'plan_box')
        plan = self.root / 'joins.json'
        plan.write_text(json.dumps({'step_sha256': '0' * 64, 'joins': []}))
        with self.assertRaisesRegex(ValueError, 'different STEP'):
            surface_audit(path, max_degree=4, joins_path=plan)


if __name__ == '__main__':
    unittest.main(verbosity=2)
