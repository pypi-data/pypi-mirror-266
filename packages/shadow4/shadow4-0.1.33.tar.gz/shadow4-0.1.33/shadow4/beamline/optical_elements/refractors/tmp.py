
from shadow4.sources.source_geometrical.source_geometrical import SourceGeometrical

light_source = SourceGeometrical(name='SourceGeometrical', nrays=5000, seed=5676561)
light_source.set_spatial_type_rectangle(width=0.001000, height=0.001000)
light_source.set_angular_distribution_flat(hdiv1=0.000000, hdiv2=0.000000, vdiv1=0.000000, vdiv2=0.000000)
light_source.set_energy_distribution_singleline(5000.000000, unit='eV')
light_source.set_polarization(polarization_degree=1.000000, phase_diff=0.000000, coherent_beam=0)
beam = light_source.get_beam()



# optical element number XX
boundary_shape = None

from shadow4.beamline.optical_elements.refractors.s4_conic_interface import S4ConicInterface
optical_element = S4ConicInterface(name='Conic Refractive Interface', boundary_shape=boundary_shape,
    material_object='', material_image='',
    f_r_ind=2, r_ind_obj=1, r_ind_ima=1,
    r_attenuation_obj=0, r_attenuation_ima=0,
    file_r_ind_obj='', file_r_ind_ima='/nobackup/gurb1/srio/Oasys/Be.dat',
    conic_coefficients=[1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.35, 0.0])

from syned.beamline.element_coordinates import ElementCoordinates
coordinates = ElementCoordinates(p=0, q=0.005, angle_radial=0, angle_azimuthal=0, angle_radial_out=3.14159)
from shadow4.beamline.optical_elements.refractors.s4_conic_interface import S4ConicInterfaceElement
beamline_element = S4ConicInterfaceElement(optical_element=optical_element, coordinates=coordinates, input_beam=beam)

beam, mirr = beamline_element.trace_beam()
from shadow4.tools.graphics import plotxy
plotxy(beam, 1, 3, nbins=100, title="FOCAL PLANE")
plotxy(mirr, 1, 3, nbins=100, title="LENS HEIGHT")
