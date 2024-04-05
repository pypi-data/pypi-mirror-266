from shadow4.beamline.s4_beamline import S4Beamline

beamline = S4Beamline()

#
#
#
from shadow4.sources.source_geometrical.source_geometrical import SourceGeometrical

light_source = SourceGeometrical(name='SourceGeometrical', nrays=5000, seed=5676561)
light_source.set_spatial_type_rectangle(width=0.000001, height=0.000001)
light_source.set_depth_distribution_off()
light_source.set_angular_distribution_uniform(hdiv1=-0.000005, hdiv2=0.000005, vdiv1=-0.000005, vdiv2=0.000005)
light_source.set_energy_distribution_singleline(10000.000000, unit='eV')
light_source.set_polarization(polarization_degree=1.000000, phase_diff=0.000000, coherent_beam=0)
beam = light_source.get_beam()

beamline.set_light_source(light_source)

# optical element number XX
boundary_shape = None

from shadow4.beamline.optical_elements.mirrors.s4_toroid_mirror import S4ToroidMirror

optical_element = S4ToroidMirror(name='Toroid Mirror', boundary_shape=boundary_shape,
                                 surface_calculation=1,
                                 min_radius=0.006347,  # min_radius = sagittal
                                 maj_radius=52000.9,  # maj_radius = tangential
                                 f_torus=2,
                                 p_focus=10, q_focus=1, grazing_angle=0.00349066,
                                 f_reflec=0, f_refl=0, file_refl='<none>', refraction_index=0.99999 + 0.001j,
                                 coating_material='Si', coating_density=2.33, coating_roughness=0)

from syned.beamline.element_coordinates import ElementCoordinates

coordinates = ElementCoordinates(p=10, q=1, angle_radial=1.567305668, angle_azimuthal=0, angle_radial_out=1.567305668)
movements = None
from shadow4.beamline.optical_elements.mirrors.s4_toroid_mirror import S4ToroidMirrorElement

beamline_element = S4ToroidMirrorElement(optical_element=optical_element, coordinates=coordinates, movements=movements,
                                         input_beam=beam)

beam, mirr = beamline_element.trace_beam()

beamline.append_beamline_element(beamline_element)

# test plot
if True:
    from srxraylib.plot.gol import plot_scatter

    plot_scatter(beam.get_photon_energy_eV(nolost=1), beam.get_column(23, nolost=1), title='(Intensity,Photon Energy)',
                 plot_histograms=0)
    plot_scatter(1e6 * beam.get_column(1, nolost=1), 1e6 * beam.get_column(3, nolost=1), title='(X,Z) in microns')