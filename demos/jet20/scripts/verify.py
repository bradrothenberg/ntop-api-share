"""Numerical conservation and branch checks, independent of native geometry."""
import json, math, unittest
from cycle import ROOT,cycle,meanline,atmosphere,LBF

class Checks(unittest.TestCase):
    def setUp(self):self.c=json.loads((ROOT/'inputs/design.json').read_text())
    def test_standard_atmosphere(self):
        self.assertEqual(atmosphere(0),(288.15,101325.0))
        T,p=atmosphere(3048);self.assertAlmostEqual(T,268.338,places=6)
        self.assertTrue(69670<p<69690)
    def test_mass_energy_momentum(self):
        c=self.c;r=cycle(c);m=r['air_mass_flow_kg_s'];f=r['fuel_ratio']
        R=c['gas_constant_J_kgK'];cpa=c['gamma_air']*R/(c['gamma_air']-1);cpg=c['gamma_gas']*R/(c['gamma_gas']-1)
        self.assertAlmostEqual(m*cpa*r['stations'][2]['Tt_K']+m*f*c['combustion_efficiency']*c['fuel_LHV_J_kg'],m*(1+f)*cpg*c['turbine_inlet_K'],places=6)
        self.assertAlmostEqual(r['shaft_residual_W'],0,places=6)
        exit_mass=r['exit_pressure_Pa']/(R*r['exit_temperature_K'])*r['exit_velocity_m_s']*r['nozzle_area_m2']
        self.assertAlmostEqual(exit_mass,m*(1+f),places=12)
        independent=exit_mass*r['exit_velocity_m_s']-m*r['flight_velocity_m_s']+(r['exit_pressure_Pa']-atmosphere(c['altitude_m'])[1])*r['nozzle_area_m2']
        self.assertAlmostEqual(independent,r['thrust_N'],places=9)
    def test_sizing_is_not_prediction(self):
        r=cycle(self.c);self.assertAlmostEqual(r['thrust_N'],20*LBF,places=9)
        rr=cycle(self.c,nozzle_area=r['nozzle_area_m2']);self.assertAlmostEqual(rr['thrust_N'],r['thrust_N'],places=9)
        larger=cycle(self.c,nozzle_area=r['nozzle_area_m2']*1.1);self.assertAlmostEqual(larger['thrust_N'],r['thrust_N']*1.1,places=9)
    def test_nozzle_branches(self):
        r=cycle(self.c);self.assertFalse(r['nozzle_choked'])
        r=cycle(self.c|{'turbine_inlet_K':1500.});self.assertTrue(r['nozzle_choked']);self.assertGreater(r['pressure_thrust_N'],0)
        self.assertAlmostEqual(r['exit_velocity_m_s']/math.sqrt(self.c['gamma_gas']*self.c['gas_constant_J_kgK']*r['exit_temperature_K']),1,places=9)
    def test_geometry_and_euler(self):
        r=cycle(self.c);g=meanline(self.c,r)
        self.assertLess(g['eye_tip_radius_m'],g['impeller_radius_m'])
        self.assertLess(g['eye_relative_tip_mach'],1)
        self.assertGreater(g['turbine_hub_radius_m'],g['shaft_radius_m'])
        self.assertAlmostEqual(g['impeller_tip_speed_m_s']*g['impeller_exit_swirl_m_s'],r['compressor_work_J_kg'],places=8)
        self.assertAlmostEqual(g['turbine_mean_speed_m_s']*(g['turbine_inlet_swirl_m_s']-g['turbine_exit_swirl_m_s']),r['turbine_work_J_kg'],places=8)
    def test_invalid_efficiency_rejected(self):
        with self.assertRaises(ValueError):cycle(self.c|{'compressor_efficiency':1.1})

if __name__=='__main__':unittest.main(verbosity=2)
