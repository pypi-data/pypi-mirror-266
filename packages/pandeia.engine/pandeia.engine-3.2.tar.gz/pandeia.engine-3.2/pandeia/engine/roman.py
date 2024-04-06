# Licensed under a 3-clause BSD style license - see LICENSE.rst

from .telescope import Telescope
from .instrument import Instrument
from .custom_exceptions import EngineInputError
from .pandeia_warnings import instrument_warning_messages

class Roman(Telescope):

    """
    Currently a dummy class for directory/file discovery, but could eventually contain Roman-specific methods
    """
    pass


class RomanInstrument(Instrument):

    """
    Generic Roman Instrument class
    """

    def __init__(self, mode=None, config={}, **kwargs):
        telescope = Roman()
        # these are the required sections and need to be passed via API in webapp mode
        self.instrument_pars = {}
        self.instrument_pars['detector'] = ["nexp", "nresultants", "ma_table_name", "subarray"]
        self.instrument_pars['instrument'] = ["aperture", "disperser", "filter", "instrument", "mode"]
        self.api_parameters = list(self.instrument_pars.keys())

        # these are required for calculation, but ok to live with config file defaults
        self.api_ignore = ['dynamic_scene', 'max_scene_size', 'scene_size']

        Instrument.__init__(self, telescope=telescope, mode=mode, config=config, **kwargs)

    def read_detector(self):
        """
        Read in the detector keyword from the aperture parameter in the config json file.
        Put the detector keyword in self.instrument['detector'].
        """
        self.instrument['detector'] = self.aperture_config[self.get_aperture()]['detector']


class WFI(RomanInstrument):

    """
    Currently, the Roman WFI requires only one method beyond those provided by the generic
    Instrument class

    This is also the optimal place to check agreement of MA table and mode, and to
    implement the nresultants=-1 special behavior.
    """
    def __init__(self, mode=None, config={}, webapp=False, **kwargs):

        # We will stick with our own terminology, but allow for someone simply using "optical_element"
        # If present, it supercedes filter and disperser.
        if "optical_element" in config["instrument"]:
            if config["instrument"]["mode"] == "imaging":
                config["instrument"]["filter"] = config["instrument"]["optical_element"]
                config["instrument"]["disperser"] = None
            elif config["instrument"]["mode"] == "spectroscopy":
                config["instrument"]["disperser"] = config["instrument"]["optical_element"]
                config["instrument"]["filter"] = None

        RomanInstrument.__init__(self, mode=mode, config=config, webapp=webapp, **kwargs)
        self._loadpsfs()

        if config["instrument"]["mode"] == "imaging" and config["instrument"]["filter"] not in self.filters:
            raise EngineInputError(f'Invalid filter: {config["instrument"]["filter"]}')
        elif config["instrument"]["mode"] == "spectroscopy" and config["instrument"]["disperser"] not in self.dispersers:
            raise EngineInputError(f'Invalid disperser: {config["instrument"]["disperser"]}')

        # Mixing the MA tables will not be allowed, so it should error.
        if self.instrument["mode"] == "imaging" and self.the_detector.exposure_spec.ma_table["observing_mode"] != "WIM":
            raise EngineInputError(f"Invalid MA table {self.the_detector.exposure_spec.ma_table_name} for imaging.")
        if self.instrument["mode"] == "spectroscopy" and self.the_detector.exposure_spec.ma_table["observing_mode"] != "WSM":
            raise EngineInputError(f"Invalid MA table {self.the_detector.exposure_spec.ma_table_name} for spectroscopy.")
        
        if self.the_detector.exposure_spec.nresultants < self.the_detector.exposure_spec.min_resultants:
            key = "roman_min_resultants"
            self.warnings[key] = instrument_warning_messages[key].format(self.the_detector.exposure_spec.nresultants, self.the_detector.exposure_spec.min_resultants)

    def _loadpsfs(self):
        """
        Short-wavelength filters need PSFs with the skinny pupil mask.
        Long-wavelength filters (just f184 and f213 for now) need the wide pupil mask.
        The grism and prism both have their own pupil masks.
        Because the ranges overlap, we need to switch between PSF libraries.
        The mask is attached to the actual glass, so selecting by filter seems appropriate
        """
        if self.instrument['mode'] == 'imaging':
            psf_key = self.instrument['filter']
        elif self.instrument['mode'] == 'spectroscopy':
            psf_key = self.instrument['disperser']
        else:
            message = "Invalid mode specification: {}".format(str(self.instrument['mode']))
            raise EngineInputError(value=message)

        self.psf_library = self._load_psf_library(psf_key)


class IFU(RomanInstrument):

    """
    Currently the Roman IFU (deprecated) requires no extra methods beyond those provided by the generic Instrument class
    """
    pass
