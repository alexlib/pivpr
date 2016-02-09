__author__ = 'Jwely'

from py.tex import TeXRunFigurePage
from py.piv import construct_experiments
from py.piv import shorthand_to_tex as stt
from py.config import *
from py.utils import merge_dicts


def build_tex_figs_by_run(run_id, include_cartesian=False, include_dynamic=False, force_recalc=False):
    """
    Creates a separate tex document for every figure to include in the discussion section where lots 
    of text will be manually placed between images.
    
    At this point, everything has become a little convoluted, but running this
    function will complete all processing for input run_id and produce all the relevant figures and
    create individual tex files that can be called and referenced with a one liner wherever they are 
    needed in the main tex document with:
    
        # \include{figs\...}
        # \ref{figs:...}
    
    The hierarchy at this point is:
        TeXRunFigurePage extends
        TexWriter invokes
        TexFigureGenerator wraps
        construct_experiments returns
        Experiment with attribute
        AxialVortex which has plotting methods to produce figures of interest.
    """

    contour_width = '4.25in'
    scatter_width = '6in'
    stream_width = '4.25in'

    # create the experiment.
    exp = construct_experiments(experiment_table_path=EXPERIMENT_TABLE_PATH,
                                experiment_directory_path=DATA_FULL_DIR,
                                ids=[run_id],
                                min_points=DEFAULT_MIN_POINTS,
                                force_recalc=force_recalc,
                                include_dynamic=include_dynamic)[0]
    tfp = TeXRunFigurePage(TEX_MAIN_PATH, "run_{0}".format(run_id), exp, force_recalc=force_recalc)

    av = exp.axial_vortex
    station_id = (int((run_id - 1) / 10) + 1)
    z_location = "{0:2.2f}".format(av.z_location / 101.6)

    # add a comparison plot to theoretical profile
    caption = "Theoretical vortex profile fits to experimental data at $z/c$={0}, $V_{{free}}$={1}, station {2}."\
        .format(z_location, av.velocity_fs, station_id)
    tfp.add_comparison_plot(caption, scatter_width, write_unique=True)


    # add stream plot
    caption = "Stream plot at $z/c$={0}, $V_{{free}}$={1}, station {2}.".format(z_location, av.velocity_fs, station_id)
    tfp.add_stream_plot(caption, stream_width)

    # full contour plots with no radial or angular subseting
    components = ['R', 'T', 'W', 'rt', 'rw', 'tw', 'rr', 'tt', 'ww', 'ctke', 'num']
    if include_cartesian:
        components += ['U', 'V', 'W']

    for component in components:
        contour_kwargs = {"r_range": ('0r', '6r')}
        caption_fmt = "Contour plot of {0} at $z/c$={2}, $V_{{free}}$={3}, station {1}."
        caption = caption_fmt.format(stt(component), station_id, z_location, av.velocity_fs)
        tfp.add_contour_plot(component, caption, contour_width, create_kwargs=contour_kwargs, write_unique=True)

    # radius scatter plots with kwargs
    scatter_kwargs = {"x_range": (0, 4)}

    t_kwargs = merge_dicts(scatter_kwargs, {"title": "Azimuthal Velocity vs Radius"})
    caption = "Scatter plot of azimuthal velocity vs radius at $z/c$={0}, $V_{{free}}$={1}, station{2}.".format(
        z_location, av.velocity_fs, station_id)
    tfp.add_scatter_plot('r_mesh', 'T', caption, scatter_width, create_kwargs=t_kwargs, write_unique=True)

    t_kwargs = merge_dicts(scatter_kwargs, {"title": "Azimuthal Velocity vs Radius", "component_c": "ctke"})
    caption = "Scatter plot of azimuthal velocity vs radius, turbulent kinetic energy, " \
              "at $z/c$={0}, $V_{{free}}$={1}, station {2}.".format(z_location, av.velocity_fs, station_id)
    tfp.add_scatter_plot('r_mesh', 'T', caption, scatter_width, special_tag='ctke', create_kwargs=t_kwargs, write_unique=True)

    k_kwargs = merge_dicts(scatter_kwargs, {"title": "Turbulent Kinetic Energy"})
    caption = "Scatter plot of turbulent kinetic energy vs radius at $z/c$={0}, $V_{{free}}$={1}, station {2}.".format(
        z_location, av.velocity_fs, station_id)
    tfp.add_scatter_plot('r_mesh', 'ctke', caption, scatter_width, create_kwargs=k_kwargs, write_unique=True)


    # logarithmic plots with kwqargs
    log_kwargs = merge_dicts(scatter_kwargs, {"log_y": True,
                                              "y_range": (1e2, 1e9),
                                              "y_label": " ",
                                              "t_range": (10, 80),
                                              "symmetric": True})

    kwargs = merge_dicts(log_kwargs, {"title": r"$\frac{1}{r^2}\frac{d}{dr}[r^2 \overline{t^\prime r^\prime}]$"})
    caption = "Scatter plot of $\nu_T$ reynolds stress term vs radius at $z/c$={0}, $V_{{free}}$={1}, station {2}.".format(
        z_location, av.velocity_fs, station_id)
    tfp.add_scatter_plot('r_mesh', 'turb_visc_reynolds', caption, scatter_width, create_kwargs=kwargs, write_unique=True)

    kwargs = merge_dicts(log_kwargs, {"title": r"$\frac{d^2\bar{t}}{dr^2} + \frac{d}{dr}(\frac{\bar{t}}{r})$"})
    caption = "Scatter plot of $\\nu_T$ velocity gradient term vs radius at $z/c$={0}, $V_{{free}}$={1}, station {2}.".format(
        z_location, av.velocity_fs, station_id)
    tfp.add_scatter_plot('r_mesh', 'turb_visc_vel_grad', caption, scatter_width, create_kwargs=kwargs, write_unique=True)

    kwargs = merge_dicts(log_kwargs, {"title": r"$\eta_P \bar{t}[\overline{r^\prime r^\prime} - \overline{t^\prime t^\prime}"
                                               r" + \frac{d(\overline{r^\prime r^\prime})}{dr}]$"})
    kwargs['y_range'] = (1e-5, 1e3)     # much much much smaller.
    caption = "Scatter plot of $\\nu_T$ pressure relaxation term vs radius at $z/c$={0}, $V_{{free}}$={1}, station {2}.".format(
        z_location, av.velocity_fs, station_id)
    tfp.add_scatter_plot('r_mesh', 'turb_visc_ettap', caption, scatter_width, create_kwargs=kwargs, write_unique=True)

    kwargs['y_range'] = (-1, 30)
    caption = "Scatter plot of non-equilibrium based $\\nu_T$ radius at $z/c$={0}, $V_{{free}}$={1}, station {2}.".format(
        z_location, av.velocity_fs, station_id)
    tfp.add_scatter_plot('r_mesh', 'turb_visc_total', caption, scatter_width, create_kwargs=kwargs, write_unique=True)

    # plots of turbulent viscosity as calculated by turbulent viscosity hypothesis
    kwargs = {"y_range": (0, 0.6), "x_range": (0, 5), "title": "Radial profile of $\\nu_T$"}
    caption = "Scatter plot of $\\nu_T$ as calculated from the turbulent viscosity hypothesis. " \
              "$z/c$={0}, $V_{{free}}$={1}, station {2}.".format(z_location, av.velocity_fs, station_id)
    tfp.add_scatter_plot('r_mesh', 'turb_visc', caption, scatter_width, create_kwargs=kwargs, write_unique=True)


    # include dynamic plots
    if include_dynamic:
        dynamic_kwargs = {"r_range": ('0r', '1r')}
        caption = "Plot showing dynamic variations in turbulent kinetic energy within the core. " \
                  "$z/c$={0}, $V_{{free}}$={1}, station {2}.".format(z_location, av.velocity_fs, station_id)
        tfp.add_dynamic_plot('ctke', caption, scatter_width, special_tag="01r", create_kwargs=dynamic_kwargs, write_unique=True)

        dynamic_kwargs = {"r_range": ('1r', '2r')}
        caption = "Plot showing dynamic variations in turbulent kinetic energy between 1 and 2 core radii. " \
                  "$z/c$={0}, $V_{{free}}$={1}, station {2}.".format(z_location, av.velocity_fs, station_id)
        tfp.add_dynamic_plot('ctke', caption, scatter_width, special_tag="12r", create_kwargs=dynamic_kwargs, write_unique=True)

        dynamic_kwargs = {"r_range": ('0r', '0.5r')}
        caption = "Plot showing dynamic variations in turbulent kinetic energy between 0 and 0.5 core radii. " \
                  "$z/c$={0}, $V_{{free}}$={1}, station {2}.".format(z_location, av.velocity_fs, station_id)
        tfp.add_dynamic_plot('ctke', caption, scatter_width, special_tag="005r", create_kwargs=dynamic_kwargs, write_unique=True)

    # and write the appendix index file with all of the plots.
    tfp.write(include_labels=False)


def main():
    # build tex figs for all trials
    run_ids = range(1, 71)
    run_ids = [55, 56]
    for run_id in run_ids:
        build_tex_figs_by_run(run_id, include_dynamic=True, force_recalc=False)

    # include cartesian coordinate tex figs for example run number 55
    #build_tex_figs_by_run(55, include_cartesian=True)




if __name__ == "__main__":
    main()
