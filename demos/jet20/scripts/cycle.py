"""Constant-property turbojet sizing model. SI throughout. No component maps."""
from __future__ import annotations
import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LBF = 4.4482216152605

def atmosphere(altitude_m, offset_K=0):
    if not 0 <= altitude_m <= 11000:
        raise ValueError("Troposphere model supports 0 to 11000 m")
    standard_T = 288.15 - 0.0065 * altitude_m
    pressure = 101325 * (standard_T / 288.15) ** (9.80665 / (287.05 * 0.0065))
    return standard_T + offset_K, pressure

def cycle(c, air_mass_flow=None, nozzle_area=None):
    """Supply neither flow nor area to size for thrust; supply one for a study.

    Fixed nozzle area closes mass continuity at imposed PR and TIT. It does not
    establish compressor/turbine map matching or off-design shaft speed.
    """
    R=c['gas_constant_J_kgK']; ga=c['gamma_air']; gg=c['gamma_gas']
    cpa=ga*R/(ga-1); cpg=gg*R/(gg-1)
    if air_mass_flow is not None and nozzle_area is not None:
        raise ValueError('Specify mass flow or nozzle area, not both')
    for k in ['compressor_efficiency','turbine_efficiency','combustion_efficiency','mechanical_efficiency','inlet_recovery','burner_pressure_ratio','nozzle_pressure_ratio']:
        if not 0<c[k]<=1:raise ValueError(k)
    T0,p0=atmosphere(c['altitude_m'],c['isa_offset_K'])
    V0=c['mach']*math.sqrt(ga*R*T0)
    T2=T0*(1+(ga-1)/2*c['mach']**2)
    p2=p0*(T2/T0)**(ga/(ga-1))*c['inlet_recovery']
    T3=T2*(1+(c['compressor_pressure_ratio']**((ga-1)/ga)-1)/c['compressor_efficiency'])
    p3=p2*c['compressor_pressure_ratio']; wc=cpa*(T3-T2)
    T4=c['turbine_inlet_K'];p4=p3*c['burner_pressure_ratio']
    f=(cpg*T4-cpa*T3)/(c['combustion_efficiency']*c['fuel_LHV_J_kg']-cpg*T4)
    if f<=0:raise ValueError('No positive fuel flow')
    wt=wc/((1+f)*c['mechanical_efficiency']);T5=T4-wt/cpg
    T5s=T4-(T4-T5)/c['turbine_efficiency']
    if T5s<=0:raise ValueError('Insufficient turbine enthalpy')
    p5=p4*(T5s/T4)**(gg/(gg-1));p8=p5*c['nozzle_pressure_ratio']
    critical=((gg+1)/2)**(gg/(gg-1));npr=p8/p0
    if npr<=1:raise ValueError('No positive nozzle pressure head')
    choked=npr>=critical
    pe=p8/critical if choked else p0
    Te=T5*(pe/p8)**((gg-1)/gg)
    Ve=math.sqrt(2*cpg*(T5-Te));rhoe=pe/(R*Te)
    massflux=rhoe*Ve
    specific=(1+f)*(Ve+(pe-p0)/massflux)-V0
    if specific<=0:raise ValueError('Nonpositive net specific thrust')
    if nozzle_area is not None:air_mass_flow=nozzle_area*massflux/(1+f)
    if air_mass_flow is None:air_mass_flow=(c['target_thrust_lbf']*LBF+c['external_installation_drag_N'])/specific
    area=air_mass_flow*(1+f)/massflux
    momentum=air_mass_flow*((1+f)*Ve-V0);pressure=(pe-p0)*area
    F=momentum+pressure-c['external_installation_drag_N']
    stations=[{'station':s,'Tt_K':T,'pt_Pa':p} for s,T,p in [('0 ambient',T0,p0),('2 compressor inlet',T2,p2),('3 compressor exit',T3,p3),('4 turbine inlet',T4,p4),('5 turbine exit',T5,p5),('8 nozzle inlet',T5,p8)]]
    return dict(thrust_N=F,thrust_lbf=F/LBF,air_mass_flow_kg_s=air_mass_flow,fuel_ratio=f,
        fuel_kg_s=air_mass_flow*f,fuel_kg_min=air_mass_flow*f*60,sfc_kg_N_h=air_mass_flow*f*3600/F,
        nozzle_area_m2=area,nozzle_diameter_m=math.sqrt(4*area/math.pi),nozzle_choked=choked,
        nozzle_pressure_ratio=npr,critical_pressure_ratio=critical,exit_pressure_Pa=pe,exit_temperature_K=Te,
        exit_velocity_m_s=Ve,flight_velocity_m_s=V0,compressor_work_J_kg=wc,turbine_work_J_kg=wt,
        compressor_power_W=air_mass_flow*wc,turbine_power_W=air_mass_flow*(1+f)*wt,
        shaft_residual_W=air_mass_flow*(1+f)*wt*c['mechanical_efficiency']-air_mass_flow*wc,
        momentum_thrust_N=momentum,pressure_thrust_N=pressure,stations=stations)

def meanline(c,r):
    R=c['gas_constant_J_kgK'];ga=c['gamma_air'];gg=c['gamma_gas'];cpa=ga*R/(ga-1);cpg=gg*R/(gg-1)
    omega=c['shaft_rpm']*math.pi/30
    U2=math.sqrt(r['compressor_work_J_kg']/c['compressor_work_coefficient']);r2=U2/omega
    Cm=c['compressor_exit_flow_coefficient']*U2;Cu=r['compressor_work_J_kg']/U2
    T3=r['stations'][2]['Tt_K'];p3=r['stations'][2]['pt_Pa']
    Ts=T3-(Cm**2+Cu**2)/(2*cpa)
    ps=p3*(Ts/T3)**(ga/(ga-1));rho=ps/(R*Ts)
    b2=r['air_mass_flow_kg_s']/(rho*Cm*2*math.pi*r2*c['compressor_exit_blockage'])
    # Inlet eye is sized at a study axial velocity of 125 m/s and hub/tip ratio 0.35.
    Cin=125.;ratio=.35;T2=r['stations'][1]['Tt_K'];p2=r['stations'][1]['pt_Pa']
    Tin=T2-Cin**2/(2*cpa);pin=p2*(Tin/T2)**(ga/(ga-1));rhoin=pin/(R*Tin)
    eye_r=math.sqrt(r['air_mass_flow_kg_s']/(rhoin*Cin*math.pi*(1-ratio**2)*.95))
    Um=math.sqrt(r['turbine_work_J_kg']/c['turbine_loading_coefficient']);rm=Um/omega
    Ca=c['turbine_axial_velocity_m_s'];dCu=r['turbine_work_J_kg']/Um
    avgCu=Um*(1-c['turbine_reaction']);Cu1=avgCu+dCu/2;Cu2=avgCu-dCu/2
    Tt=r['stations'][3]['Tt_K'];pt=r['stations'][3]['pt_Pa']
    Tstat=Tt-(Ca**2+Cu1**2)/(2*cpg);pstat=pt*(Tstat/Tt)**(gg/(gg-1))
    rho_t=pstat/(R*Tstat)
    annulus=r['air_mass_flow_kg_s']*(1+r['fuel_ratio'])/(rho_t*Ca*c['turbine_blockage'])
    span=annulus/(2*math.pi*rm)
    if span/2>=rm:raise ValueError('Turbine annulus has no hub; revise loading or speed')
    turbine_tip=rm+span/2;hub=rm-span/2
    slip_required=c['compressor_work_coefficient']/(1-c['compressor_exit_flow_coefficient']*math.tan(math.radians(c['compressor_backsweep_deg'])))
    case_r=max(r2*1.5,turbine_tip+0.012)
    return dict(impeller_tip_speed_m_s=U2,impeller_radius_m=r2,impeller_diameter_m=2*r2,
        impeller_exit_width_m=b2,impeller_exit_meridional_m_s=Cm,impeller_exit_swirl_m_s=Cu,
        impeller_required_slip_factor=slip_required,eye_tip_radius_m=eye_r,eye_hub_radius_m=eye_r*ratio,
        eye_axial_velocity_m_s=Cin,eye_relative_tip_mach=math.hypot(Cin,omega*eye_r)/math.sqrt(ga*R*Tin),
        turbine_mean_radius_m=rm,turbine_span_m=span,turbine_hub_radius_m=hub,turbine_tip_radius_m=turbine_tip,
        turbine_mean_speed_m_s=Um,turbine_inlet_swirl_m_s=Cu1,turbine_exit_swirl_m_s=Cu2,
        stator_exit_angle_deg=math.degrees(math.atan2(Cu1,Ca)),
        rotor_inlet_angle_deg=math.degrees(math.atan2(Cu1-Um,Ca)),
        rotor_exit_angle_deg=math.degrees(math.atan2(Cu2-Um,Ca)),
        turbine_solidity=c['turbine_axial_chord_m']*c['turbine_rotor_blades']/(2*math.pi*rm),
        case_radius_m=case_r,case_length_m=case_r*4.5,shaft_radius_m=0.004,
        notes='Derived meanline geometry. Uniform velocity and blockage study inputs. No slip correlation, radial equilibrium, deviation, or stress model.')

def main():
    c=json.loads((ROOT/'inputs/design.json').read_text());r=cycle(c);g=meanline(c,r)
    (ROOT/'output/results').mkdir(exist_ok=True)
    points=[]
    for h in [0,1524,3048]:
        for mach in [0,.25,.5]:
            cc=c|{'altitude_m':h,'mach':mach}
            rr=cycle(cc,nozzle_area=r['nozzle_area_m2'])
            points.append({'altitude_m':h,'mach':mach,**rr})
    out={'inputs':c,'design':r,'geometry':g,'fixed_nozzle_study':points,
        'limitations':['No component maps or off-design speed matching','Constant specific heats','No cooling or bleed','No accessory shaft power','External installation drag is unresolved','No hardware validation']}
    (ROOT/'output/results/design.json').write_text(json.dumps(out,indent=2))
    print(json.dumps({'design':r,'geometry':g},indent=2))
    return out

if __name__=='__main__':main()
